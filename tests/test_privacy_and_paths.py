"""Offline privacy and path-boundary regressions for acquire.py.

Every platform tool is a temporary stub. The yt-dlp cases run the pinned yt-dlp library inside that stub on a
synthetic fixture with sockets and urlopen blocked. Cookie values are generated per run and clearly synthetic;
no real credential, browser profile or platform material is read. Links point only into disposable copies.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/vidtrail"
YT_ID = "3UgXWMQtB8E"
YT_URL = f"https://youtu.be/{YT_ID}"
BILI_ID = "BV1CMMh62EVA"
BILI_URL = f"https://www.bilibili.com/video/{BILI_ID}/"
VTT = "WEBVTT\n\n00:00.000 --> 00:01.000\nSynthetic line\n"
PINNED = "2026.8.19"

LOGGING_STUB = """#!{python}
import json, os, sys
from pathlib import Path
argv = sys.argv[1:]
with open(os.environ["STUB_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps([Path(sys.argv[0]).name] + argv) + "\\n")
scene = json.loads(Path(os.environ["STUB_SCENE"]).read_text(encoding="utf-8"))
if "-o" in argv:
    for name, body in scene.get("write", {{}}).items():
        Path(argv[argv.index("-o") + 1].replace("%(id)s.%(ext)s", name)).write_text(body, encoding="utf-8")
sys.stdout.write(scene.get("stdout", ""))
raise SystemExit(scene.get("exit", 0))
"""

# Runs the pinned yt-dlp option parser and YoutubeDL on the exact argv the helper passes. Extraction would need
# the network, so a synthetic info dict is processed instead; media "download" writes synthetic bytes.
PINNED_STUB = """#!{python} -I
import hashlib, json, os, socket, sys
from pathlib import Path
with open(os.environ["STUB_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(["yt-dlp"] + sys.argv[1:]) + "\\n")
def blocked(*args, **kwargs):
    with open(os.environ["NET_LOG"], "a", encoding="utf-8") as log:
        log.write("blocked\\n")
    raise OSError("network blocked in offline test")
socket.socket.connect = socket.create_connection = socket.getaddrinfo = blocked
import importlib.metadata
from yt_dlp import YoutubeDL, parse_options
options = parse_options(sys.argv[1:])
params = dict(options.ydl_opts)
class Offline(YoutubeDL):
    def urlopen(self, *args, **kwargs):
        blocked()
    def dl(self, name, info, subtitle=False, test=False):
        Path(name).write_bytes(b"synthetic media bytes")
        return True, False
url = options.urls[-1]
video_id = url.split("v=")[-1] if "v=" in url else url.split("/video/")[1].split("/")[0]
host = "www.youtube.com" if "youtube" in url else "www.bilibili.com"
fixture = {{"id": video_id, "title": "Synthetic fixture", "extractor": "Generic", "extractor_key": "Generic",
           "webpage_url": url,
           "formats": [{{"format_id": "http", "url": "https://" + host + "/synthetic.mp4", "ext": "mp4",
                        "vcodec": "h264", "acodec": "aac", "height": 360}}],
           "subtitles": {{"en": [{{"ext": "vtt", "data": {vtt!r}}}]}}}}
with Offline(params) as tool:
    info = tool.process_ie_result(fixture, download=True)
    wanted = os.environ.get("SECRET_SHA256", "")
    report = {{"version": importlib.metadata.version("yt-dlp"), "writeinfojson": bool(params.get("writeinfojson")),
              "cookiefile": bool(params.get("cookiefile")), "skip_download": bool(params.get("skip_download")),
              "writesubtitles": bool(params.get("writesubtitles")),
              "secret_loaded": any(hashlib.sha256(c.value.encode()).hexdigest() == wanted for c in tool.cookiejar),
              "info_has_cookie_field": "cookies" in info or any("cookies" in f for f in info.get("formats", []))}}
with open(os.environ["REPORT"], "a", encoding="utf-8") as out:
    out.write(json.dumps(report) + "\\n")
"""


def pinned_ytdlp():
    try:
        import importlib.metadata
        return importlib.util.find_spec("yt_dlp") is not None and importlib.metadata.version("yt-dlp") == PINNED
    except Exception:
        return False


def snapshot(base):
    """Map every entry below base to its link target, file hash or directory marker, without following links."""
    base = Path(base)
    state = {}
    if not (base.exists() or base.is_symlink()):
        return state
    for directory, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            path = Path(directory, name)
            key = str(path.relative_to(base))
            if path.is_symlink():
                state[key] = ("link", os.readlink(path))
            elif path.is_dir():
                state[key] = ("dir",)
            else:
                state[key] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
    return state


@unittest.skipIf(os.name == "nt", "POSIX executable stubs and symlinks")
class Workspace(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="vidtrail-privacy-")
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name).resolve()
        self.bin = self.tmp / "stub-bin"
        self.bin.mkdir()
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.log = self.tmp / "stub.log"
        self.scene_path = self.tmp / "scene.json"
        self.scene(write={f"{YT_ID}.zh.vtt": VTT})
        for tool in ("bili", "yt-dlp", "ffmpeg"):
            self.stub(tool, LOGGING_STUB.format(python=sys.executable))
        # Disposable distribution copy: the copied helper guards this copy, so no link ever reaches the real checkout.
        self.source = self.tmp / "source"
        (self.source / "scripts").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts/install_skill.py", self.source / "scripts/install_skill.py")
        self.skill = self.source / ".agents/skills" / SKILL.name
        shutil.copytree(SKILL, self.skill, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.script = self.skill / "scripts/acquire.py"
        self.outside = self.tmp / "outside"
        self.outside.mkdir()
        (self.outside / "sentinel.txt").write_text("outside sentinel; must stay unchanged\n", encoding="utf-8")
        self.data = self.tmp / "materials"

    def stub(self, tool, text):
        path = self.bin / tool
        path.write_text(text, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IEXEC)

    def scene(self, **values):
        self.scene_path.write_text(json.dumps(values), encoding="utf-8")

    def calls(self):
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()] if self.log.exists() else []

    def cli(self, *args, url=YT_URL, route="yt-dlp", mode="subtitles", data=None, script=None, path=None, env=None):
        environment = {"PATH": str(path or self.bin), "STUB_LOG": str(self.log), "STUB_SCENE": str(self.scene_path),
                       "HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1", **(env or {})}
        run = subprocess.run([sys.executable, "-I", str(script or self.script), "--url", url, "--route", route,
                              "--mode", mode, "--data-root", str(data or self.data), *args],
                             capture_output=True, text=True, encoding="utf-8", env=environment, timeout=120)
        self.assertNotIn("Traceback", run.stderr)
        return run

    def result(self, run, code):
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        return json.loads(run.stdout)


class NestedLinkBoundaryTests(Workspace):
    """Links below the data root must not redirect reads or writes outside it or into the distribution."""

    def link(self, path, target):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target, target_is_directory=Path(target).is_dir())
        return path

    def rejected(self, *links, url=YT_URL, route="yt-dlp", mode="subtitles", data=None, extra=(), watched=()):
        watched = [self.source, self.outside, *watched]
        before = {str(w): snapshot(w) for w in watched}
        links_before = {str(l): os.readlink(l) for l in links}
        run = self.cli(*extra, url=url, route=route, mode=mode, data=data)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("Acquisition stopped", run.stderr)
        self.assertEqual(self.calls(), [], "no platform tool may run after a rejected path")
        for w in watched:
            self.assertEqual(snapshot(w), before[str(w)], f"{w} changed")
        for l, target in links_before.items():
            self.assertTrue(Path(l).is_symlink(), "the user's link must be preserved")
            self.assertEqual(os.readlink(l), target)
        return run

    def target(self, platform="youtube", video=YT_ID, route="yt-dlp", mode="subtitles"):
        return self.data / platform / video / "p1" / f"{route}-{mode}"

    def test_platform_level_link_into_source_is_rejected(self):
        self.rejected(self.link(self.data / "youtube", self.source))

    def test_video_level_link_into_installed_skill_is_rejected(self):
        self.rejected(self.link(self.data / "youtube" / YT_ID, self.skill))

    def test_part_level_link_escaping_the_root_is_rejected(self):
        self.rejected(self.link(self.data / "youtube" / YT_ID / "p1", self.outside))

    def test_target_level_link_escaping_the_root_is_rejected(self):
        self.rejected(self.link(self.target(), self.outside))

    def test_generic_escape_and_media_mode_are_rejected(self):
        self.rejected(self.link(self.data / "youtube", self.outside), mode="media")

    def test_bili_route_link_into_source_is_rejected(self):
        self.scene(stdout=json.dumps({"subtitle": {"available": True, "text": "Synthetic line"}}))
        self.rejected(self.link(self.data / "bilibili", self.source / "scripts"), url=BILI_URL, route="bili")

    def test_receipt_file_link_outside_is_neither_read_nor_written(self):
        outside_receipt = self.outside / "receipt.json"
        outside_receipt.write_text(json.dumps({"status": "failed", "files": []}), encoding="utf-8")
        link = self.link(self.target() / "receipt.json", outside_receipt)
        self.rejected(link)
        self.rejected(link, extra=("--retry-reason", "synthetic environment change"))

    def test_receipt_file_link_into_source_is_rejected(self):
        planted = self.source / "receipt.json"
        planted.write_text(json.dumps({"status": "acquired", "files": [{"path": str(self.source / "LICENSE-x"), "sha256": "0"}]}), encoding="utf-8")
        self.rejected(self.link(self.target() / "receipt.json", planted))

    def test_in_root_link_into_a_copied_install_is_rejected(self):
        project = self.tmp / "knowledge"
        skill = project / ".agents/skills" / SKILL.name
        shutil.copytree(SKILL, skill, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.script = skill / "scripts/acquire.py"
        self.rejected(self.link(project / "youtube", skill), data=project, watched=(skill,))

    def test_broken_link_is_rejected_and_left_in_place(self):
        self.rejected(self.link(self.data / "youtube", self.tmp / "missing-directory"))
        self.assertFalse((self.tmp / "missing-directory").exists())

    def test_recorded_file_outside_the_root_is_not_reused(self):
        target = self.target()
        target.mkdir(parents=True)
        sentinel = self.outside / "sentinel.txt"
        digest = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        (target / "receipt.json").write_text(json.dumps({"status": "acquired", "files": [{"path": str(sentinel), "bytes": 1, "sha256": digest}]}), encoding="utf-8")
        before = snapshot(self.outside)
        receipt = self.result(self.cli(), 2)
        self.assertEqual(receipt["status"], "invalidated")
        self.assertEqual(self.calls(), [])
        self.assertEqual(snapshot(self.outside), before)


class SafePathControlTests(Workspace):
    """Legitimate layouts keep working: root aliases, in-root links and both install modes."""

    def acquired_then_reused(self, data, script=None):
        first = self.result(self.cli(data=data, script=script), 0)
        self.assertEqual(first["status"], "acquired")
        again = self.result(self.cli(data=data, script=script), 0)
        self.assertTrue(again["reused"])
        self.assertEqual(len(self.calls()), 1)
        return first

    def test_data_root_alias_is_allowed_and_stores_under_the_real_root(self):
        real = self.tmp / "real-materials"
        real.mkdir()
        alias = self.tmp / "alias"
        alias.symlink_to(real, target_is_directory=True)
        first = self.acquired_then_reused(alias)
        self.assertTrue(all(Path(f["path"]).resolve().is_relative_to(real) for f in first["files"]))
        self.assertTrue(self.result(self.cli(data=real), 0)["reused"])
        self.assertEqual(len(self.calls()), 1)

    def test_links_that_stay_inside_the_root_are_allowed(self):
        store = self.data / "store"
        (store / "youtube").mkdir(parents=True)
        (self.data / "youtube").symlink_to(store / "youtube", target_is_directory=True)
        first = self.acquired_then_reused(self.data)
        self.assertTrue(all(Path(f["path"]).resolve().is_relative_to(store) for f in first["files"]))
        self.assertTrue((store / "youtube" / YT_ID / "p1/yt-dlp-subtitles/receipt.json").is_file())

    def test_symlink_install_writes_to_project_materials(self):
        project = self.tmp / "knowledge"
        skills = project / ".agents/skills"
        skills.mkdir(parents=True)
        (skills / SKILL.name).symlink_to(self.skill, target_is_directory=True)
        self.acquired_then_reused(project / "materials", script=skills / SKILL.name / "scripts/acquire.py")

    def test_copy_install_allows_project_root_and_in_root_links(self):
        project = self.tmp / "knowledge"
        skill = project / ".agents/skills" / SKILL.name
        shutil.copytree(SKILL, skill, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (project / "store").mkdir()
        (project / "youtube").symlink_to(project / "store", target_is_directory=True)
        first = self.acquired_then_reused(project, script=skill / "scripts/acquire.py")
        self.assertTrue(all(Path(f["path"]).resolve().is_relative_to(project / "store") for f in first["files"]))


class LegacyMetadataTests(Workspace):
    """Receipts from the earlier --write-info-json helper are reused without presenting raw metadata as safe."""

    def legacy(self, status="acquired"):
        target = self.data / "youtube" / YT_ID / "p1/yt-dlp-subtitles"
        attempt = target / "20261001T000000-legacy00"
        attempt.mkdir(parents=True)
        files = []
        for name, body in ((f"{YT_ID}.info.json", '{"cookies": "vidtrail-synthetic-legacy-marker"}'), (f"{YT_ID}.zh.vtt", VTT)):
            (attempt / name).write_text(body, encoding="utf-8")
            files.append({"path": str(attempt / name), "bytes": len(body.encode()), "sha256": hashlib.sha256(body.encode()).hexdigest()})
        receipt = {"platform": "youtube", "video_id": YT_ID, "part": 1, "url": f"https://www.youtube.com/watch?v={YT_ID}",
                   "route": "yt-dlp", "mode": "subtitles", "timestamp": "2026-10-01T00:00:00+00:00", "status": status,
                   "files": files, "retry_reason": None, "content_verification": "not_performed"}
        if status == "partial":
            receipt.update(usable_files=[f"{YT_ID}.zh.vtt"], failure={"exit_code": 1, "reason": "command_failed"})
        text = json.dumps(receipt, indent=2)
        (attempt / "receipt.json").write_text(text, encoding="utf-8")
        (target / "receipt.json").write_text(text, encoding="utf-8")
        return attempt

    def test_legacy_acquired_receipt_is_reused_with_warning_and_untouched(self):
        attempt = self.legacy()
        before = snapshot(self.data)
        run = self.cli()
        receipt = self.result(run, 0)
        self.assertTrue(receipt["reused"])
        self.assertEqual([Path(f["path"]).name for f in receipt["files"]], [f"{YT_ID}.zh.vtt"])
        self.assertEqual(receipt["sensitive_metadata_retained"], [str(attempt / f"{YT_ID}.info.json")])
        self.assertIn("may contain cookies", receipt["metadata_warning"])
        self.assertNotIn("legacy-marker", run.stdout)
        self.assertEqual(self.calls(), [])
        self.assertEqual(snapshot(self.data), before, "legacy files and receipts are preserved, not rewritten or deleted")

    def test_legacy_partial_retry_keeps_history_and_excludes_raw_metadata(self):
        attempt = self.legacy("partial")
        legacy_state = snapshot(attempt)
        receipt = self.result(self.cli("--retry-reason", "synthetic environment change"), 0)
        self.assertEqual(receipt["status"], "acquired")
        self.assertEqual([Path(f["path"]).name for f in receipt["prior_partial"]["files"]], [f"{YT_ID}.zh.vtt"])
        self.assertIn(str(attempt / f"{YT_ID}.info.json"), receipt["sensitive_metadata_retained"])
        self.assertIn("--no-write-info-json", self.calls()[0])
        self.assertEqual(snapshot(attempt), legacy_state)
        target_receipt = json.loads((attempt.parent / "receipt.json").read_text(encoding="utf-8"))
        self.assertFalse(any(f["path"].endswith(".info.json") for f in target_receipt["files"] + target_receipt["prior_partial"]["files"]))


class CookieOptionTests(Workspace):
    def cookie(self):
        directory = self.tmp / "input"
        directory.mkdir(exist_ok=True)
        path = directory / "cookies.txt"
        path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        return path

    def test_missing_cookie_file_stops_before_any_directory_even_without_the_tool(self):
        empty = self.tmp / "empty-bin"
        empty.mkdir()
        run = self.cli("--cookies-file", str(self.tmp / "input/missing.txt"), path=empty)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("Cookie file must exist", run.stderr)
        self.assertFalse(self.data.exists())

    def test_cookie_inside_distribution_stops_before_any_directory(self):
        inside = self.skill / "private.txt"
        shutil.copy2(self.cookie(), inside)
        run = self.cli("--cookies-file", str(inside))
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertFalse(self.data.exists())
        self.assertEqual(self.calls(), [])

    def test_info_json_is_explicitly_disabled_in_both_modes_with_and_without_cookies(self):
        cookie = self.cookie()
        self.scene(write={f"{YT_ID}.zh.vtt": VTT, f"{YT_ID}.mp4": "synthetic media"})
        for mode in ("subtitles", "media"):
            for with_cookie in (False, True):
                with self.subTest(mode=mode, cookie=with_cookie):
                    data = self.tmp / f"data-{mode}-{with_cookie}"
                    extra = ("--cookies-file", str(cookie)) if with_cookie else ()
                    self.result(self.cli(*extra, mode=mode, data=data), 0)
                    command = self.calls()[-1]
                    self.assertIn("--no-write-info-json", command)
                    self.assertNotIn("--write-info-json", command)
                    self.assertEqual("--cookies" in command, with_cookie)


@unittest.skipUnless(pinned_ytdlp(), f"needs the pinned yt-dlp=={PINNED} importable by this interpreter")
class PinnedYtDlpCookieTests(Workspace):
    """The helper's real argv drives pinned yt-dlp; a fresh synthetic cookie must never reach outputs."""

    def setUp(self):
        super().setUp()
        self.stub("yt-dlp", PINNED_STUB.format(python=sys.executable, vtt=VTT))
        self.secret = "vidtrail-synthetic-" + secrets.token_hex(16)
        self.input = self.tmp / "input"
        self.input.mkdir()
        self.cookie = self.input / "synthetic.cookies.txt"
        self.cookie.write_text("# Netscape HTTP Cookie File\n"
                               f".youtube.com\tTRUE\t/\tTRUE\t9999999999\tsession\t{self.secret}\n"
                               f".bilibili.com\tTRUE\t/\tTRUE\t9999999999\tSESSDATA\t{self.secret}\n", encoding="utf-8")
        self.report = self.tmp / "report.jsonl"
        self.net = self.tmp / "network.log"

    def run_case(self, mode, with_cookie, url=YT_URL):
        data = self.tmp / f"materials-{mode}-{with_cookie}"
        extra = ("--cookies-file", str(self.cookie)) if with_cookie else ()
        env = {"NET_LOG": str(self.net), "REPORT": str(self.report),
               "SECRET_SHA256": hashlib.sha256(self.secret.encode()).hexdigest()}
        run = self.cli(*extra, mode=mode, data=data, url=url, env=env)
        receipt = self.result(run, 0)
        report = json.loads(self.report.read_text(encoding="utf-8").splitlines()[-1])
        command = [c for c in self.calls() if c[0] == "yt-dlp"][-1]
        self.assertEqual(report["version"], PINNED)
        self.assertEqual(("--cookies" in command, report["cookiefile"]), (with_cookie, with_cookie))
        # Positive control: yt-dlp really loaded the secret and attached it to the in-memory info dict.
        self.assertEqual(report["secret_loaded"], with_cookie)
        self.assertEqual(report["info_has_cookie_field"], with_cookie)
        self.assertFalse(self.net.exists(), "a network call was attempted")
        # Boolean checks keep the synthetic value itself out of failure output.
        self.assertFalse(self.secret in run.stdout + run.stderr, "synthetic cookie printed by the helper")
        for path in self.tmp.rglob("*"):
            if path.is_file() and not path.is_symlink() and self.input not in path.parents:
                self.assertFalse(self.secret.encode() in path.read_bytes(), f"synthetic cookie leaked into {path}")
        self.assertEqual(list(data.rglob("*.info.json")), [])
        self.assertFalse(report["writeinfojson"])
        self.assertEqual(report["skip_download"], mode == "subtitles")
        self.assertEqual(report["writesubtitles"], mode == "subtitles")
        suffix = ".vtt" if mode == "subtitles" else ".mp4"
        self.assertTrue(any(f["path"].endswith(suffix) for f in receipt["files"]))
        self.assertEqual(receipt["extractor_metadata"], "not_retained")
        self.assertNotIn("sensitive_metadata_retained", receipt)
        return receipt

    def test_subtitles_without_and_with_cookie(self):
        for with_cookie in (False, True):
            with self.subTest(cookie=with_cookie):
                self.run_case("subtitles", with_cookie)

    def test_media_without_and_with_cookie(self):
        for with_cookie in (False, True):
            with self.subTest(cookie=with_cookie):
                self.run_case("media", with_cookie)

    def test_bilibili_later_part_media_with_cookie(self):
        receipt = self.run_case("media", True, url=f"https://www.bilibili.com/video/{BILI_ID}/?p=2")
        self.assertEqual((receipt["platform"], receipt["part"]), ("bilibili", 2))
        command = [c for c in self.calls() if c[0] == "yt-dlp"][-1]
        self.assertEqual(command[command.index("--playlist-items") + 1], "2")


if __name__ == "__main__":
    unittest.main()
