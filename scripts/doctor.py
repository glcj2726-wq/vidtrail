"""Read-only tool inventory; never logs in or prints credential content."""
import json
import shutil
import subprocess
import sys


def inventory():
    result = {"python": sys.version.split()[0], "tools": {}}
    for name, flag in (("bili", "--version"), ("yt-dlp", "--version"), ("node", "--version"), ("ffmpeg", "-version"), ("ffprobe", "-version"), ("codex", "--version")):
        exe = shutil.which(name)
        item = {"installed": bool(exe), "version": None}
        if exe:
            try:
                p = subprocess.run([exe, flag], capture_output=True, text=True, timeout=15)
                line = (p.stdout or "").splitlines()
                item["version"] = line[0][:160] if line else None
            except (OSError, subprocess.TimeoutExpired):
                item["inspection"] = "failed"
        result["tools"][name] = item
    result["boundaries"] = "No platform login, MCP, browser connectivity or download has been verified."
    return result


if __name__ == "__main__":
    print(json.dumps(inventory(), ensure_ascii=False, indent=2))
