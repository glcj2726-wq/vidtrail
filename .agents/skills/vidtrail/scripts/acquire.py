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


def files_valid(receipt):
    files = receipt.get("files", [])
    return bool(files) and all(Path(f["path"]).is_file() and digest(Path(f["path"])) == f["sha256"] for f in files)


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
    return sorted(f.name for f in attempt.iterdir() if f.is_file() and f.suffix in endings and f.stat().st_size)


def acquire(url, route, mode, data_root, cookies_file=None, retry_reason=None):
    platform, video_id, part, canonical = identity(url)
    if route == "bili" and (platform != "bilibili" or part != 1 or mode != "subtitles" or cookies_file):
        raise ValueError("bili route supports Bilibili P1 subtitles only; choose an explicit alternate route for other targets.")
    root = Path(data_root).expanduser().resolve()
    distribution = distribution_root()
    if root == distribution or distribution in root.parents:
        raise ValueError("Data must be stored outside the skill distribution repository.")
    target = root / platform / video_id / f"p{part}" / f"{route}-{mode}"
    target.mkdir(parents=True, exist_ok=True)
    receipt_path = target / "receipt.json"
    prior_partial = None
    if receipt_path.exists():
        old = json.loads(receipt_path.read_text(encoding="utf-8"))
        kept = old.get("status") in ("acquired", "partial")
        valid = kept and files_valid(old)
        if valid and old["status"] == "acquired":
            return {**old, "reused": True}
        if not retry_reason:
            if valid:
                return {**old, "reused": True, "action": "Verify the retained files; the failed remainder needs the next skill route or --retry-reason after an actual environment/source change."}
            return {**old, "status": "invalidated" if kept else old["status"],
                    "reused": True, "action": "Use the next skill route; retry only after an actual environment/source change."}
        # A later attempt replaces receipt.json, so it must keep pointing at earlier partial evidence.
        prior_partial = old.get("prior_partial")
        if old.get("status") == "partial":
            prior_partial = {k: old.get(k) for k in ("timestamp", "reason", "failure", "usable_files", "files")}
    attempt = target / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    attempt.mkdir()
    receipt = {"platform": platform, "video_id": video_id, "part": part, "url": canonical,
               "route": route, "mode": mode, "timestamp": datetime.now(timezone.utc).isoformat(),
               "status": "unavailable", "files": [], "retry_reason": retry_reason,
               "content_verification": "not_performed"}
    if prior_partial:
        receipt["prior_partial"] = prior_partial
    executable = shutil.which(route)
    if mode == "media" and not shutil.which("ffmpeg"):
        receipt["reason"] = "ffmpeg_missing"
    elif not executable:
        receipt["reason"] = "tool_missing"
    else:
        if route == "bili":
            cmd = [executable, "video", video_id, "--subtitle-timeline", "--subtitle-format", "srt", "--json"]
        else:
            cmd = [executable, "--retries", "0", "--extractor-retries", "0", "--fragment-retries", "0",
                   "--file-access-retries", "0", "--socket-timeout", "20", "--no-progress", "--write-info-json",
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
            if cookies_file:
                cookie = Path(cookies_file).expanduser().resolve()
                if not cookie.is_file() or cookie == distribution or distribution in cookie.parents:
                    raise ValueError("Cookie file must exist outside the distribution repository.")
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
                if process.returncode == 0 or has_subtitle:
                    (attempt / "bili-response.json").write_text(process.stdout, encoding="utf-8")
                usable = ["bili-response.json"] if has_subtitle else []
            else:
                usable = target_files(attempt, mode)
            receipt["status"] = "acquired" if process.returncode == 0 and usable else "failed"
            receipt["reason"] = ("files_need_content_verification" if receipt["status"] == "acquired" else
                                 "command_failed" if usable and mode == "subtitles" else "no_usable_target_or_command_failed")
            if receipt["status"] == "failed" and any(t in process.stderr.lower() for t in ("sign in", "not a bot", "login")):
                receipt["reason"] = "login_verification_required"
        except subprocess.TimeoutExpired:
            receipt.update(status="failed", reason="timeout")
            usable = target_files(attempt, mode)
        except OSError:
            receipt.update(status="failed", reason="invocation_failed")
        # Media stays failed: after a nonzero exit a .mp4 may be one unmerged stream.
        if receipt["status"] == "failed" and usable and mode == "subtitles":
            receipt["failure"] = {"exit_code": receipt.get("exit_code"), "reason": receipt["reason"]}
            receipt.update(status="partial", reason="usable_files_after_command_failure", usable_files=usable)
        # Raw stderr and command arguments are deliberately not stored: credentials may occur there.
    for path in sorted(attempt.iterdir()):
        if path.is_file():
            receipt["files"].append({"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)})
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
