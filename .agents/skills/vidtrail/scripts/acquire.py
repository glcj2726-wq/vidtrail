"""Single-route acquisition, immutable attempts, hash-checked reuse. Stdlib only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import parse_qs, urlparse
import uuid


def identity(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        raise ValueError("Use a normal HTTPS public video URL without embedded credentials.")
    host = (parsed.hostname or "").lower()
    query = parse_qs(parsed.query)
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"):
        video_id = parsed.path.strip("/") if host == "youtu.be" else query.get("v", [""])[0]
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValueError("Provide a YouTube watch URL or youtu.be video link.")
        return "youtube", video_id, 1, f"https://www.youtube.com/watch?v={video_id}"
    if host in ("bilibili.com", "www.bilibili.com", "m.bilibili.com"):
        match = re.fullmatch(r"/video/(BV[0-9A-Za-z]{10})/?", parsed.path)
        if not match:
            raise ValueError("Provide a canonical Bilibili BV video link; resolve short links first.")
        part = int(query.get("p", ["1"])[0])
        if part < 1:
            raise ValueError("Bilibili part must be positive.")
        video_id = match[1]
        return "bilibili", video_id, part, f"https://www.bilibili.com/video/{video_id}/?p={part}"
    raise ValueError("Only canonical Bilibili and YouTube video links are supported.")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inside(path, parent):
    return path == parent or parent in path.parents


def checked(path, root, distribution):
    """Resolve an existing entry; it must stay inside the canonical data root and outside the distribution.

    These are ordinary pre-use checks, not an OS sandbox or protection against concurrent hostile renames."""
    if path.is_symlink() and not path.exists():
        raise ValueError(f"Data path is a broken link; fix or remove it yourself: {path}")
    resolved = path.resolve()
    if not inside(resolved, root) or inside(resolved, distribution):
        raise ValueError(f"Data path leaves the chosen data root or enters the skill distribution through a link: {path}")
    return resolved


def files_valid(receipt, root, distribution):
    files = receipt.get("files", [])
    for f in files:
        path = Path(f["path"])
        try:
            path = checked(path, root, distribution) if path.exists() or path.is_symlink() else path
        except ValueError:
            return False  # A recorded file now redirected outside the root is not read.
        if not path.is_file() or digest(path) != f["sha256"]:
            return False
    return bool(files)


# Earlier helper versions requested yt-dlp --write-info-json; that raw metadata can embed cookies.
RAW_METADATA = ".info.json"
METADATA_WARNING = ("Raw yt-dlp .info.json metadata from an earlier helper version or an unexpected tool output is kept "
                    "where it was and excluded from files. It may contain cookies or account data: review it privately "
                    "before sharing or uploading these materials. It was not deleted, rewritten or refetched.")


def outward(receipt):
    """Copy a receipt without raw metadata in artifact lists; report those paths only with a warning."""
    result = dict(receipt)
    sensitive = set(receipt.get("sensitive_metadata_retained") or [])

    def split(entries):
        entries = entries if isinstance(entries, list) else []
        for entry in entries:
            if isinstance(entry, dict) and str(entry.get("path", "")).endswith(RAW_METADATA):
                sensitive.add(str(entry["path"]))
        return [e for e in entries if not (isinstance(e, dict) and str(e.get("path", "")).endswith(RAW_METADATA))]

    if "files" in receipt:
        result["files"] = split(receipt["files"])
    if isinstance(receipt.get("prior_partial"), dict) and "files" in receipt["prior_partial"]:
        result["prior_partial"] = {**receipt["prior_partial"], "files": split(receipt["prior_partial"]["files"])}
    if sensitive:
        result["sensitive_metadata_retained"] = sorted(sensitive)
        result["metadata_warning"] = METADATA_WARNING
    return result


def prepare_target(root, names, distribution):
    """Check every existing level below the data root before creating anything; return the resolved target."""
    current = root
    for name in names:
        candidate = current / name
        if candidate.exists() or candidate.is_symlink():
            current = checked(candidate, root, distribution)
            if not current.is_dir():
                raise ValueError(f"Data path exists but is not a directory: {candidate}")
        else:
            current = candidate
    return current


def distribution_root():
    """Source checkouts guard the whole repository; a copied skill guards only itself, never its host."""
    skill = Path(__file__).resolve().parents[1]
    if skill.parent.name == "skills" and skill.parent.parent.name == ".agents":
        installer = skill.parents[2] / "scripts" / "install_skill.py"
        if installer.is_file() and f".agents/skills/{skill.name}" in installer.read_text(encoding="utf-8", errors="replace"):
            return skill.parents[2]
    return skill


def bili_subtitle(stdout):
    """Return (usable, diagnostic); bilibili-cli 0.6.2 nests data.subtitle, older output has it top-level."""
    if not stdout.strip():
        return False, "empty_output"
    try:
        payload = json.loads(stdout)
    except (ValueError, RecursionError):
        return False, "invalid_json"
    if not isinstance(payload, dict):
        return False, "payload_malformed"
    body = payload
    if any(key in payload for key in ("ok", "schema_version", "data")):
        if payload.get("ok", True) is not True:
            return False, "envelope_not_ok"
        if "data" not in payload:
            return False, "data_missing"
        body = payload["data"]
        if body is None:
            return False, "data_null"
        if not isinstance(body, dict):
            return False, "data_malformed"
    if "subtitle" not in body:
        return False, "subtitle_missing"
    subtitle = body["subtitle"]
    if subtitle is None:
        return False, "subtitle_null"
    if not isinstance(subtitle, dict):
        return False, "subtitle_malformed"
    if subtitle.get("available") is not True:
        return False, "subtitle_unavailable"
    text, items = subtitle.get("text"), subtitle.get("items")
    if isinstance(text, str) and text.strip():
        return True, None
    if isinstance(items, list) and any(isinstance(i, dict) and isinstance(i.get("content"), str) and i["content"].strip() for i in items):
        return True, None
    return False, "subtitle_empty" if not text and not items else "subtitle_malformed"


def target_files(attempt, mode):
    endings = (".vtt", ".srt", ".ass") if mode == "subtitles" else (".mp4", ".mkv", ".webm")
    return sorted(f.name for f in attempt.iterdir() if f.is_file() and not f.is_symlink() and f.suffix in endings and f.stat().st_size)


def failure_kind(stderr, mode, bili_stdout=None, yt_dlp_stdout=None):
    """Classify explicit tool diagnostics, never transcript text or the presence of a Cookie file.

    Return only a fixed code: diagnostics can contain secrets and must not enter receipts.
    A 403/empty result alone does not establish missing login or absent captions.
    """
    text = stderr.lower()
    if bili_stdout:
        try:
            envelope = json.loads(bili_stdout)
        except (ValueError, RecursionError):
            envelope = None
        # bili --json emits its structured error on stdout. Inspect only the
        # explicit error message, never a title, caption, summary or arbitrary data.
        if isinstance(envelope, dict) and envelope.get('ok') is False:
            error = envelope.get('error')
            if isinstance(error, dict) and isinstance(error.get('message'), str):
                text += '\n' + error['message'].lower()
    rules = (
        ("rate_limited", r"\bhttp(?:\s+error|\s+status(?:\s+code)?|\s+response(?:\s+code)?)?\s*[:=]?\s*429\b|\bstatus(?:\s+code)?\s*[:=]?\s+429\b|too many requests|rate[ -]?limit(?:ed|ing| exceeded)?|请求过于频繁|请求太频繁"),
        ("access_verification", r"not a bot|captcha|robot verification|verify (?:you are|you're|that you are)|verification (?:required|challenge)|access challenge|机器人|人机验证|验证码"),
        ("network_error", r"timed? ?out|timeout|connection (?:refused|reset|aborted)|name resolution|resolve (?:host|hostname)|network is unreachable|certificate (?:verify failed|(?:has |is )?expired)|网络超时|连接超时|无法解析"),
        # Require an asserted authentication state, not 'may/might have expired',
        # an unrelated expired certificate, or words joined across diagnostics.
        ("expired_login", r"\b(?:cookies?|session|credentials?|login|authentication)\s+(?:(?:is|are|has|have)\s+)?(?:already\s+)?(?:expired|invalidated|no longer valid)\b|登录(?:已)?(?:失效|过期)|凭据(?:已)?过期"),
        ("missing_login", r"not logged in|login required|log[ -]?in is required|authentication required|please (?:log in|login|sign in)|sign in to (?:view|watch|access)|未登录|请先登录|需要登录|(?:缺少|未提供)\s*sessdata|sessdata.{0,20}(?:未提供|为空|缺失)|missing\s+sessdata"),
    )
    for kind, pattern in rules:
        if re.search(pattern, text):
            return kind
    if mode == "subtitles" and re.search(r"there are no subtitles|no (?:subtitles|captions)(?: are)? available|(?:subtitles|captions) (?:are )?not available|no subtitles for the requested languages|没有(?:可用)?字幕|无可用字幕", text):
        return "no_subtitles"
    # yt-dlp 2026.8.19 normally prints this diagnostic to stdout. Only this
    # complete tool-log line is accepted; arbitrary titles/content are not errors.
    if mode == "subtitles" and yt_dlp_stdout and any(
        re.fullmatch(r"\[info\] There are no subtitles for the requested languages", line.strip())
        for line in yt_dlp_stdout.splitlines()
    ):
        return "no_subtitles"
    return "unknown"


def acquire(url, route, mode, data_root, cookies_file=None, retry_reason=None):
    platform, video_id, part, canonical = identity(url)
    if route == "bili" and (platform != "bilibili" or part != 1 or mode != "subtitles" or cookies_file):
        raise ValueError("bili route supports Bilibili P1 subtitles only; choose an explicit alternate route for other targets.")
    root = Path(data_root).expanduser().resolve()
    distribution = distribution_root()
    if inside(root, distribution):
        raise ValueError("Data must be stored outside the skill distribution repository.")
    cookie = None
    if cookies_file:
        # Checked before any data directory or attempt exists, even when yt-dlp is not installed.
        cookie = Path(cookies_file).expanduser().resolve()
        if not cookie.is_file() or inside(cookie, distribution):
            raise ValueError("Cookie file must exist outside the distribution repository.")
    target = prepare_target(root, (platform, video_id, f"p{part}", f"{route}-{mode}"), distribution)
    receipt_path = target / "receipt.json"
    if receipt_path.exists() or receipt_path.is_symlink():
        receipt_path = checked(receipt_path, root, distribution)
        if not receipt_path.is_file():
            raise ValueError(f"Receipt path exists but is not a file: {target / 'receipt.json'}")
    target.mkdir(parents=True, exist_ok=True)
    prior_partial = None
    if receipt_path.exists():
        old = json.loads(receipt_path.read_text(encoding="utf-8"))
        kept = old.get("status") in ("acquired", "partial")
        valid = kept and files_valid(old, root, distribution)
        if valid and old["status"] == "acquired":
            return {**outward(old), "reused": True}
        if not retry_reason:
            if valid:
                return {**outward(old), "reused": True, "action": "Verify the retained files; the failed remainder needs the next skill route or --retry-reason after an actual environment/source change."}
            return {**outward(old), "status": "invalidated" if kept else old["status"],
                    "reused": True, "action": "Use the next skill route; retry only after an actual environment/source change."}
        # A later attempt replaces receipt.json, so it must keep pointing at earlier partial evidence.
        prior_partial = old.get("prior_partial")
        if old.get("status") == "partial":
            prior_partial = {k: old.get(k) for k in ("timestamp", "reason", "failure", "usable_files", "files")}
            if "failure_kind" in old:
                prior_partial["failure_kind"] = old["failure_kind"]
    attempt = target / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    attempt.mkdir()
    receipt = {"platform": platform, "video_id": video_id, "part": part, "url": canonical,
               "route": route, "mode": mode, "timestamp": datetime.now(timezone.utc).isoformat(),
               "status": "unavailable", "files": [], "retry_reason": retry_reason,
               "content_verification": "not_performed"}
    if route == "yt-dlp":
        # Identity is the requested canonical URL/ID/part; extractor metadata (e.g. cid) is not kept or checked.
        receipt["extractor_metadata"] = "not_retained"
    if prior_partial:
        receipt["prior_partial"] = prior_partial
    executable = shutil.which(route)
    if mode == "media" and not shutil.which("ffmpeg"):
        receipt["reason"] = "ffmpeg_missing"
        receipt["failure_kind"] = "tool_unavailable"
    elif not executable:
        receipt["reason"] = "tool_missing"
        receipt["failure_kind"] = "tool_unavailable"
    else:
        if route == "bili":
            cmd = [executable, "video", video_id, "--subtitle-timeline", "--subtitle-format", "srt", "--json"]
        else:
            # Raw yt-dlp info.json can embed cookies, so it is never requested; receipts keep the canonical identity.
            cmd = [executable, "--retries", "0", "--extractor-retries", "0", "--fragment-retries", "0",
                   "--file-access-retries", "0", "--socket-timeout", "20", "--no-progress", "--no-write-info-json",
                   "-o", str(attempt / "%(id)s.%(ext)s")]
            if shutil.which("node"):
                cmd += ["--js-runtimes", "node"]
            if platform == "bilibili":
                cmd += ["--playlist-items", str(part)]
            else:
                cmd += ["--no-playlist"]
            if mode == "subtitles":
                cmd += ["--write-subs", "--write-auto-subs", "--sub-langs", "zh.*,en.*", "--sub-format", "vtt", "--skip-download"]
            else:
                # A subtitle-service error must not cancel an otherwise available media target.
                cmd += ["-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4"]
            if cookie:
                cmd += ["--cookies", str(cookie)]
            cmd.append(canonical)
        usable = []
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600 if mode == "media" else 120)
            receipt["exit_code"] = process.returncode
            if route == "bili":
                has_subtitle, diagnostic = bili_subtitle(process.stdout)
                if diagnostic:
                    receipt["diagnostic"] = diagnostic
                # An unusable nonzero response stays unsaved like stderr; it may echo account details.
                if has_subtitle:
                    (attempt / "bili-response.json").write_text(process.stdout, encoding="utf-8")
                usable = ["bili-response.json"] if has_subtitle else []
            else:
                usable = target_files(attempt, mode)
            receipt["status"] = "acquired" if process.returncode == 0 and usable else "failed"
            receipt["reason"] = ("files_need_content_verification" if receipt["status"] == "acquired" else
                                 "command_failed" if usable and mode == "subtitles" else "no_usable_target_or_command_failed")
            if receipt["status"] == "failed" and any(t in process.stderr.lower() for t in ("sign in", "not a bot", "login")):
                receipt["reason"] = "login_verification_required"
            if receipt["status"] == "failed":
                receipt["failure_kind"] = failure_kind(
                    process.stderr, mode,
                    bili_stdout=process.stdout if route == "bili" else None,
                    yt_dlp_stdout=process.stdout if route == "yt-dlp" else None,
                )
        except subprocess.TimeoutExpired:
            # A subprocess deadline can also be local processing; do not assert a network cause.
            receipt.update(status="failed", reason="timeout", failure_kind="unknown")
            usable = target_files(attempt, mode)
        except OSError:
            receipt.update(status="failed", reason="invocation_failed", failure_kind="unknown")
        # Media stays failed: after a nonzero exit a .mp4 may be one unmerged stream.
        if receipt["status"] == "failed" and usable and mode == "subtitles":
            receipt["failure"] = {"exit_code": receipt.get("exit_code"), "reason": receipt["reason"]}
            receipt.update(status="partial", reason="usable_files_after_command_failure", usable_files=usable)
        # Raw stderr and command arguments are deliberately not stored: credentials may occur there.
    for path in sorted(attempt.iterdir()):
        if path.is_file() and not path.is_symlink():
            receipt["files"].append({"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)})
    receipt = outward(receipt)
    text = json.dumps(receipt, ensure_ascii=False, indent=2)
    (attempt / "receipt.json").write_text(text, encoding="utf-8")
    receipt_path.write_text(text, encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(epilog="Exit codes: 0 acquired; 1 stopped before acquisition; 2 no usable target (failed, unavailable or invalidated); 3 partial: usable files kept, command failure recorded. Existing receipts are reused without running the tool; a partial or failed target reruns only once per explicit --retry-reason.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--route", choices=["bili", "yt-dlp"], required=True)
    parser.add_argument("--mode", choices=["subtitles", "media"], default="subtitles")
    parser.add_argument("--data-root", default=os.environ.get("VIDEO_RESEARCH_DATA_ROOT"))
    parser.add_argument("--cookies-file")
    parser.add_argument("--retry-reason", help="Actual tool/login/source change; do not use to bypass failed-route reuse.")
    args = parser.parse_args()
    if not args.data_root:
        parser.error("Provide --data-root or VIDEO_RESEARCH_DATA_ROOT.")
    try:
        result = acquire(args.url, args.route, args.mode, args.data_root, args.cookies_file, args.retry_reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit({"acquired": 0, "partial": 3}.get(result["status"], 2))
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Acquisition stopped: {exc}\n")
