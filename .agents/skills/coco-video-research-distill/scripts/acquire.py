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


def acquire(url, route, mode, data_root, cookies_file=None, retry_reason=None):
    platform, video_id, part, canonical = identity(url)
    if route == "bili" and (platform != "bilibili" or part != 1 or mode != "subtitles" or cookies_file):
        raise ValueError("bili route supports Bilibili P1 subtitles only; choose an explicit alternate route for other targets.")
    root = Path(data_root).expanduser().resolve()
    distribution = Path(__file__).resolve().parents[4]
    if root == distribution or distribution in root.parents:
        raise ValueError("Data must be stored outside the skill distribution repository.")
    target = root / platform / video_id / f"p{part}" / f"{route}-{mode}"
    target.mkdir(parents=True, exist_ok=True)
    receipt_path = target / "receipt.json"
    if receipt_path.exists():
        old = json.loads(receipt_path.read_text(encoding="utf-8"))
        if old.get("status") == "acquired" and files_valid(old):
            return {**old, "reused": True}
        if not retry_reason:
            return {**old, "status": "invalidated" if old.get("status") == "acquired" else old["status"],
                    "reused": True, "action": "Use the next skill route; retry only after an actual environment/source change."}
    attempt = target / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    attempt.mkdir()
    receipt = {"platform": platform, "video_id": video_id, "part": part, "url": canonical,
               "route": route, "mode": mode, "timestamp": datetime.now(timezone.utc).isoformat(),
               "status": "unavailable", "files": [], "retry_reason": retry_reason,
               "content_verification": "not_performed"}
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
                   "--write-subs", "--write-auto-subs", "--sub-langs", "zh.*,en.*", "--sub-format", "vtt",
                   "-o", str(attempt / "%(id)s.%(ext)s")]
            if shutil.which("node"):
                cmd += ["--js-runtimes", "node"]
            if platform == "bilibili":
                cmd += ["--playlist-items", str(part)]
            else:
                cmd += ["--no-playlist"]
            cmd += ["--skip-download"] if mode == "subtitles" else ["-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4"]
            if cookies_file:
                cookie = Path(cookies_file).expanduser().resolve()
                if not cookie.is_file() or cookie == distribution or distribution in cookie.parents:
                    raise ValueError("Cookie file must exist outside the distribution repository.")
                cmd += ["--cookies", str(cookie)]
            cmd.append(canonical)
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600 if mode == "media" else 120)
            receipt["exit_code"] = process.returncode
            if route == "bili" and process.returncode == 0:
                try:
                    payload = json.loads(process.stdout)
                except json.JSONDecodeError:
                    payload = {}
                subtitle = payload.get("subtitle", {})
                usable = bool(subtitle.get("available") and (subtitle.get("text") or subtitle.get("items")))
                (attempt / "bili-response.json").write_text(process.stdout, encoding="utf-8")
            else:
                endings = (".vtt", ".srt", ".ass") if mode == "subtitles" else (".mp4", ".mkv", ".webm")
                usable = any(f.suffix in endings and f.stat().st_size for f in attempt.iterdir() if f.is_file())
            receipt["status"] = "acquired" if process.returncode == 0 and usable else "failed"
            receipt["reason"] = "files_need_content_verification" if receipt["status"] == "acquired" else "no_usable_target_or_command_failed"
            if receipt["status"] == "failed" and any(t in process.stderr.lower() for t in ("sign in", "not a bot", "login")):
                receipt["reason"] = "login_verification_required"
        except subprocess.TimeoutExpired:
            receipt.update(status="failed", reason="timeout")
        except OSError:
            receipt.update(status="failed", reason="invocation_failed")
        # Raw stderr and command arguments are deliberately not stored: credentials may occur there.
    for path in sorted(attempt.iterdir()):
        if path.is_file():
            receipt["files"].append({"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)})
    text = json.dumps(receipt, ensure_ascii=False, indent=2)
    (attempt / "receipt.json").write_text(text, encoding="utf-8")
    receipt_path.write_text(text, encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
        raise SystemExit(0 if result["status"] == "acquired" else 2)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Acquisition stopped: {exc}\n")
