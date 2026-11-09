"""Offline regressions for acquire.py; every platform tool is a temporary stub with synthetic text."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/vidtrail"
SCRIPT = SKILL / "scripts/acquire.py"
BILI_URL = "https://www.bilibili.com/video/BV1CMMh62EVA/"
YT_URL = "https://youtu.be/3UgXWMQtB8E"
SRT = "1\n00:00:00,000 --> 00:00:01,000\nSynthetic line\n"
VTT = "WEBVTT\n\n00:00.000 --> 00:01.000\nSynthetic line\n"


def load():
    spec = importlib.util.spec_from_file_location("acquire_regressions", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


acq = load()

# bilibili-cli 0.6.2: formatter.success_payload around payloads.normalize_video_command_payload.
REAL_ENVELOPE = {"ok": True, "schema_version": "1", "data": {
    "video": {"bvid": "BV1CMMh62EVA", "title": "Synthetic"},
    "subtitle": {"available": True, "format": "srt", "text": SRT,
                 "items": [{"from": 0.0, "to": 1.0, "content": "Synthetic line"}]},
    "ai_summary": "", "comments": [], "related": [], "warnings": []}}

STUB = """#!{python}
import json, os, sys
from pathlib import Path
argv = sys.argv[1:]
with open(os.environ["STUB_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(argv) + "\\n")
scene = json.loads(Path(os.environ["STUB_SCENE"]).read_text(encoding="utf-8"))
if scene.get("subtitle_error_cancels_run") and "--write-subs" in argv:
    sys.stderr.write("ERROR: Unable to download video subtitles: HTTP Error 429\\n")
    raise SystemExit(1)
if "-o" in argv:
    for name, body in scene.get("write", {{}}).items():
        Path(argv[argv.index("-o") + 1].replace("%(id)s.%(ext)s", name)).write_text(body, encoding="utf-8")
sys.stdout.write(scene.get("stdout", ""))
sys.stderr.write(scene.get("stderr", ""))
raise SystemExit(scene.get("exit", 0))
"""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Workspace(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name).resolve()
        self.bin = self.tmp / "stub-bin"
        self.bin.mkdir()
        self.log = self.tmp / "stub.log"
        self.scene_path = self.tmp / "scene.json"
        self.scene()
        for tool in ("bili", "yt-dlp", "ffmpeg"):
            path = self.bin / tool
            path.write_text(STUB.format(python=sys.executable), encoding="utf-8")
            path.chmod(path.stat().st_mode | stat.S_IEXEC)
        self.data = self.tmp / "materials"

    def scene(self, **values):
        self.scene_path.write_text(json.dumps(values), encoding="utf-8")

    def calls(self):
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()] if self.log.exists() else []

    def cli(self, *args, script=SCRIPT, url=YT_URL, route="yt-dlp", mode="subtitles", data=None):
        env = {"PATH": str(self.bin), "STUB_LOG": str(self.log), "STUB_SCENE": str(self.scene_path), "HOME": str(self.tmp), "PYTHONDONTWRITEBYTECODE": "1"}
        run = subprocess.run([sys.executable, "-I", str(script), "--url", url, "--route", route, "--mode", mode, "--data-root", str(data or self.data), *args],
                             capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
        self.assertNotIn("Traceback", run.stderr)
        return run

    def result(self, run, code):
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        return json.loads(run.stdout)


@unittest.skipIf(os.name == "nt", "POSIX executable stubs")
class BiliSchemaTests(Workspace):
    def bili(self, stdout, exit_code=0, data=None):
        self.scene(stdout=stdout, exit=exit_code)
        return self.cli(url=BILI_URL, route="bili", data=data)

    def test_real_0_6_2_envelope_is_acquired_with_receipt_and_hash(self):
        text = json.dumps(REAL_ENVELOPE)
        receipt = self.result(self.bili(text), 0)
        self.assertEqual(receipt["status"], "acquired")
        self.assertEqual(receipt["reason"], "files_need_content_verification")
        self.assertEqual(receipt["content_verification"], "not_performed")
        self.assertNotIn("diagnostic", receipt)
        self.assertEqual(self.calls()[0], ["video", "BV1CMMh62EVA", "--subtitle-timeline", "--subtitle-format", "srt", "--json"])
        saved = Path(receipt["files"][0]["path"])
        self.assertEqual(saved.name, "bili-response.json")
        self.assertEqual(saved.read_text(encoding="utf-8"), text)
        self.assertEqual(receipt["files"][0]["sha256"], sha256(saved))

    def test_real_envelope_with_items_only_is_acquired(self):
        payload = json.loads(json.dumps(REAL_ENVELOPE))
        payload["data"]["subtitle"]["text"] = ""
        self.assertEqual(self.result(self.bili(json.dumps(payload)), 0)["status"], "acquired")

    def test_top_level_legacy_response_is_still_supported(self):
        legacy = {"title": "Synthetic", "subtitle": {"available": True, "text": "Synthetic line", "items": []}}
        self.assertEqual(self.result(self.bili(json.dumps(legacy)), 0)["status"], "acquired")

    def test_bad_payloads_leave_a_diagnostic_receipt_and_never_crash(self):
        def envelope(**data):
            return json.dumps({"ok": True, "schema_version": "1", "data": data})
        cases = {
            "": "empty_output",
            "  \n": "empty_output",
            "not json": "invalid_json",
            "[" * 200000: "invalid_json",
            "null": "payload_malformed",
            "[]": "payload_malformed",
            "7": "payload_malformed",
            '"text"': "payload_malformed",
            "{}": "subtitle_missing",
            '{"subtitle":null}': "subtitle_null",
            '{"subtitle":"text"}': "subtitle_malformed",
            '{"title":"Synthetic","subtitle":{"available":false}}': "subtitle_unavailable",
            '{"ok":true,"schema_version":"1"}': "data_missing",
            '{"ok":true,"subtitle":{"available":true,"text":"top-level in an envelope"}}': "data_missing",
            '{"ok":true,"schema_version":"1","data":null}': "data_null",
            '{"ok":true,"schema_version":"1","data":[]}': "data_malformed",
            '{"ok":true,"schema_version":"1","data":"text"}': "data_malformed",
            envelope(): "subtitle_missing",
            envelope(subtitle=None): "subtitle_null",
            envelope(subtitle=[]): "subtitle_malformed",
            envelope(subtitle="text"): "subtitle_malformed",
            envelope(subtitle={}): "subtitle_unavailable",
            envelope(subtitle={"available": "false", "text": "Synthetic"}): "subtitle_unavailable",
            envelope(subtitle={"available": False, "text": "Synthetic"}): "subtitle_unavailable",
            envelope(subtitle={"available": True}): "subtitle_empty",
            envelope(subtitle={"available": True, "text": None, "items": None}): "subtitle_empty",
            envelope(subtitle={"available": True, "text": "", "items": []}): "subtitle_empty",
            envelope(subtitle={"available": True, "text": "   ", "items": []}): "subtitle_malformed",
            envelope(subtitle={"available": True, "text": 7, "items": {"a": 1}}): "subtitle_malformed",
            envelope(subtitle={"available": True, "text": "", "items": [None, "text"]}): "subtitle_malformed",
            envelope(subtitle={"available": True, "text": "", "items": [{"from": 0, "to": 1, "content": ""}]}): "subtitle_malformed",
            json.dumps({"ok": False, "schema_version": "1", "data": REAL_ENVELOPE["data"]}): "envelope_not_ok",
            '{"ok":"true","data":{}}': "envelope_not_ok",
        }
        for index, (stdout, diagnostic) in enumerate(cases.items()):
            with self.subTest(stdout=stdout[:80]):
                data = self.tmp / f"case-{index}"
                receipt = self.result(self.bili(stdout, data=data), 2)
                self.assertEqual(receipt["status"], "failed")
                self.assertEqual(receipt["diagnostic"], diagnostic)
                self.assertEqual(receipt["reason"], "no_usable_target_or_command_failed")
                self.assertEqual(receipt["exit_code"], 0)
                # Failed/malformed responses are diagnostics, not subtitle content.
                # Preserve the fixed diagnostic and status without retaining raw data.
                self.assertEqual(receipt["files"], [])
                self.assertFalse(list(data.rglob('bili-response.json')))
                for path in data.rglob('receipt.json'):
                    self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['diagnostic'], diagnostic)

    def test_failed_payload_is_reused_without_another_call(self):
        self.result(self.bili("null"), 2)
        again = self.result(self.bili(json.dumps(REAL_ENVELOPE)), 2)
        self.assertTrue(again["reused"])
        self.assertEqual(again["diagnostic"], "payload_malformed")
        self.assertEqual(len(self.calls()), 1)

    def test_nonzero_error_envelope_is_diagnosed_but_not_stored_raw(self):
        error = {"ok": False, "schema_version": "1", "error": {"code": "not_authenticated", "message": "synthetic-account-note"}}
        run = self.bili(json.dumps(error), 1)
        receipt = self.result(run, 2)
        self.assertEqual((receipt["status"], receipt["diagnostic"], receipt["exit_code"], receipt["files"]), ("failed", "envelope_not_ok", 1, []))
        self.assertNotIn("synthetic-account-note", run.stdout)

    def test_usable_response_with_nonzero_exit_is_partial(self):
        receipt = self.result(self.bili(json.dumps(REAL_ENVELOPE), 1), 3)
        self.assertEqual(receipt["status"], "partial")
        self.assertEqual(receipt["usable_files"], ["bili-response.json"])
        self.assertEqual(receipt["failure"], {"exit_code": 1, "reason": "command_failed"})
        self.assertEqual(receipt["files"][0]["sha256"], sha256(receipt["files"][0]["path"]))


@unittest.skipIf(os.name == "nt", "POSIX executable stubs")
class DataRootGuardTests(Workspace):
    def setUp(self):
        super().setUp()
        self.scene(write={"video.zh.vtt": VTT})

    def copy_skill(self, skills_dir):
        target = Path(skills_dir) / SKILL.name
        shutil.copytree(SKILL, target, ignore=shutil.ignore_patterns("__pycache__"))
        return target

    def allowed(self, script, data):
        self.assertEqual(self.result(self.cli(script=script, data=data), 0)["status"], "acquired")

    def rejected(self, script, data):
        before = len(self.calls())
        run = self.cli(script=script, data=data)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("outside the skill distribution", run.stderr)
        self.assertEqual(len(self.calls()), before)
        self.assertFalse(Path(data, "youtube").exists())

    def test_source_checkout_excludes_the_repository(self):
        for data in (ROOT, ROOT / "data", SKILL, SKILL / "data"):
            self.rejected(SCRIPT, data)
        self.allowed(SCRIPT, self.tmp / "elsewhere")

    def test_data_root_symlink_cannot_alias_into_the_repository(self):
        alias = self.tmp / "alias"
        alias.symlink_to(ROOT, target_is_directory=True)
        self.rejected(SCRIPT, alias)
        self.rejected(SCRIPT, alias / "data")

    def test_exported_checkout_without_git_is_still_a_distribution(self):
        checkout = self.tmp / "checkout"
        (checkout / "scripts").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts/install_skill.py", checkout / "scripts/install_skill.py")
        skill = self.copy_skill(checkout / ".agents/skills")
        self.rejected(skill / "scripts/acquire.py", checkout / "data")
        self.allowed(skill / "scripts/acquire.py", self.tmp / "elsewhere")

    def test_symlink_install_guards_source_but_allows_destination_project(self):
        project = self.tmp / "knowledge"
        skills = project / ".agents/skills"
        skills.mkdir(parents=True)
        (skills / SKILL.name).symlink_to(SKILL, target_is_directory=True)
        script = skills / SKILL.name / "scripts/acquire.py"
        self.allowed(script, project / "materials")
        self.allowed(script, project)
        self.rejected(script, ROOT / "data")
        self.rejected(script, skills / SKILL.name / "data")

    def test_copy_in_knowledge_project_guards_skill_not_project(self):
        project = self.tmp / "knowledge"
        project.mkdir()
        (project / "AGENTS.md").write_text("Knowledge project", encoding="utf-8")
        skill = self.copy_skill(project / ".agents/skills")
        script = skill / "scripts/acquire.py"
        self.allowed(script, project / "materials")
        self.allowed(script, project)
        self.rejected(script, skill)
        self.rejected(script, skill / "data")

    def test_copy_in_user_skill_directories_does_not_exclude_home(self):
        for skills in (".codex/skills", ".agents/skills"):
            with self.subTest(skills=skills):
                home = self.tmp / ("home-" + skills[1:6])
                skill = self.copy_skill(home / skills)
                script = skill / "scripts/acquire.py"
                self.allowed(script, home)
                self.allowed(script, home / "knowledge")
                self.rejected(script, skill / "data")

    def test_unrelated_project_installer_is_not_mistaken_for_the_distribution(self):
        project = self.tmp / "knowledge"
        (project / "scripts").mkdir(parents=True)
        (project / "scripts/install_skill.py").write_text("print('another skill')\n", encoding="utf-8")
        (project / "scripts/doctor.py").write_text("", encoding="utf-8")
        skill = self.copy_skill(project / ".agents/skills")
        self.allowed(skill / "scripts/acquire.py", project / "materials")

    def test_shallow_skill_location_does_not_crash_the_guard(self):
        with patch.object(acq, "__file__", "/skill/scripts/acquire.py"), patch.object(acq.shutil, "which", return_value=None):
            self.assertEqual(acq.acquire(YT_URL, "yt-dlp", "subtitles", self.data)["reason"], "tool_missing")
            with self.assertRaises(ValueError):
                acq.acquire(YT_URL, "yt-dlp", "subtitles", "/skill/data")

    def test_cookie_guard_follows_the_same_boundary(self):
        project = self.tmp / "knowledge"
        skill = self.copy_skill(project / ".agents/skills")
        outside = project / "private.txt"
        outside.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        inside = skill / "private.txt"
        shutil.copy2(outside, inside)
        script = skill / "scripts/acquire.py"
        self.result(self.cli("--cookies-file", str(outside), script=script), 0)
        self.assertEqual(self.calls()[-1][self.calls()[-1].index("--cookies") + 1], str(outside))
        run = self.cli("--cookies-file", str(inside), script=script, data=self.tmp / "other")
        self.assertEqual(run.returncode, 1)
        self.assertIn("Cookie file must exist outside", run.stderr)


@unittest.skipIf(os.name == "nt", "POSIX executable stubs")
class MediaSeparationTests(Workspace):
    SUBTITLE_FLAGS = ("--write-subs", "--write-auto-subs", "--sub-langs", "--sub-format")

    def test_subtitle_service_error_cannot_cancel_media(self):
        self.scene(subtitle_error_cancels_run=True, write={"video.mp4": "synthetic media", "video.info.json": "{}"})
        receipt = self.result(self.cli(mode="media"), 0)
        self.assertEqual(receipt["status"], "acquired")
        command = self.calls()[0]
        for flag in self.SUBTITLE_FLAGS:
            self.assertNotIn(flag, command)
        self.assertNotIn("--skip-download", command)
        self.assertIn("-f", command)
        self.assertIn("--no-write-info-json", command)
        self.assertNotIn("--write-info-json", command)
        media = [f for f in receipt["files"] if f["path"].endswith(".mp4")]
        self.assertEqual(media[0]["sha256"], sha256(media[0]["path"]))

    def test_subtitle_request_keeps_its_flags_and_downloads_no_media(self):
        self.scene(write={"video.zh.vtt": VTT})
        self.result(self.cli(), 0)
        command = self.calls()[0]
        for flag in self.SUBTITLE_FLAGS + ("--skip-download",):
            self.assertIn(flag, command)
        self.assertEqual(command[command.index("--sub-langs") + 1], "zh.*,en.*")
        self.assertNotIn("-f", command)
        self.assertNotIn("--merge-output-format", command)

    def test_failed_subtitle_target_does_not_block_media_target(self):
        self.scene(subtitle_error_cancels_run=True, write={"video.mp4": "synthetic media"})
        self.assertEqual(self.result(self.cli(), 2)["mode"], "subtitles")
        media = self.result(self.cli(mode="media"), 0)
        self.assertEqual((media["mode"], media["status"]), ("media", "acquired"))
        self.assertEqual(len(self.calls()), 2)
        target = self.data / "youtube/3UgXWMQtB8E/p1"
        self.assertEqual(json.loads((target / "yt-dlp-subtitles/receipt.json").read_text(encoding="utf-8"))["status"], "failed")
        self.assertEqual(json.loads((target / "yt-dlp-media/receipt.json").read_text(encoding="utf-8"))["status"], "acquired")

    def test_nonzero_media_with_a_stream_file_is_not_partial(self):
        self.scene(write={"video.f137.mp4": "unmerged stream"}, exit=1)
        receipt = self.result(self.cli(mode="media"), 2)
        self.assertEqual((receipt["status"], receipt["reason"]), ("failed", "no_usable_target_or_command_failed"))
        self.assertNotIn("failure", receipt)
        self.assertEqual(len(receipt["files"]), 1)


@unittest.skipIf(os.name == "nt", "POSIX executable stubs")
class PartialAcquisitionTests(Workspace):
    def partial(self, **scene):
        self.scene(write={"video.zh.vtt": VTT, "video.info.json": "{}"}, exit=1, **scene)
        return self.result(self.cli(), 3)

    def test_partial_receipt_preserves_files_hashes_and_failure(self):
        receipt = self.partial(stderr="ERROR: Unable to download video subtitles for 'en': HTTP Error 429\n")
        self.assertEqual(receipt["status"], "partial")
        self.assertEqual(receipt["reason"], "usable_files_after_command_failure")
        self.assertEqual(receipt["exit_code"], 1)
        self.assertEqual(receipt["failure"], {"exit_code": 1, "reason": "command_failed"})
        self.assertEqual(receipt["usable_files"], ["video.zh.vtt"])
        self.assertEqual(receipt["content_verification"], "not_performed")
        # A stray raw .info.json is kept on disk but reported only as sensitive metadata, never as an artifact.
        self.assertEqual({Path(f["path"]).name for f in receipt["files"]}, {"video.zh.vtt"})
        self.assertEqual({Path(p).name for p in receipt["sensitive_metadata_retained"]}, {"video.info.json"})
        for entry in receipt["files"]:
            self.assertEqual(entry["sha256"], sha256(entry["path"]))
            self.assertEqual(entry["bytes"], Path(entry["path"]).stat().st_size)
        attempt = Path(receipt["files"][0]["path"]).parent
        for path in (attempt / "receipt.json", attempt.parent / "receipt.json"):
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), receipt)
        self.assertEqual(len(self.calls()), 1)

    def test_failure_classification_is_recorded_without_raw_stderr(self):
        self.scene(write={"video.zh.vtt": VTT}, exit=1, stderr="Sign in; synthetic-secret-value")
        run = self.cli()
        receipt = self.result(run, 3)
        self.assertEqual(receipt["failure"], {"exit_code": 1, "reason": "login_verification_required"})
        self.assertNotIn("synthetic-secret-value", run.stdout)

    def test_partial_is_reused_explicitly_without_running_the_tool(self):
        first = self.partial()
        run = self.cli()
        reused = self.result(run, 3)
        self.assertTrue(reused["reused"])
        self.assertEqual(reused["status"], "partial")
        self.assertIn("--retry-reason", reused["action"])
        self.assertEqual(reused["files"], first["files"])
        self.assertEqual(len(self.calls()), 1)

    def test_changed_partial_file_is_invalidated_without_running_the_tool(self):
        first = self.partial()
        Path(first["files"][0]["path"]).write_text("changed", encoding="utf-8")
        invalid = self.result(self.cli(), 2)
        self.assertEqual(invalid["status"], "invalidated")
        self.assertEqual(invalid["failure"], first["failure"])
        self.assertEqual(len(self.calls()), 1)

    def test_retry_reason_runs_once_and_keeps_partial_evidence(self):
        first = self.partial()
        self.scene(write={"video.zh.vtt": VTT, "video.en.vtt": VTT})
        second = self.result(self.cli("--retry-reason", "synthetic source change"), 0)
        self.assertEqual(second["status"], "acquired")
        self.assertEqual(second["retry_reason"], "synthetic source change")
        self.assertEqual(second["prior_partial"]["files"], first["files"])
        self.assertTrue(all(Path(f["path"]).is_file() for f in first["files"]))
        self.assertEqual(len(self.calls()), 2)
        self.assertTrue(self.result(self.cli(), 0)["reused"])
        self.assertEqual(len(self.calls()), 2)

    def test_failed_retries_do_not_lose_the_partial_pointer(self):
        first = self.partial()
        self.scene(exit=1)
        for reason in ("synthetic change one", "synthetic change two"):
            failed = self.result(self.cli("--retry-reason", reason), 2)
            self.assertEqual(failed["status"], "failed")
            self.assertEqual(failed["prior_partial"]["failure"], first["failure"])
            self.assertEqual(failed["prior_partial"]["files"], first["files"])
        self.assertEqual(self.result(self.cli(), 2)["prior_partial"]["usable_files"], ["video.zh.vtt"])
        self.assertEqual(len(self.calls()), 3)

    def test_timeout_with_subtitle_files_is_partial(self):
        def run(command, **_):
            Path(command[command.index("-o") + 1].replace("%(id)s.%(ext)s", "video.zh.vtt")).write_text(VTT, encoding="utf-8")
            raise subprocess.TimeoutExpired(command, 120)
        with patch.object(acq.shutil, "which", return_value="yt-dlp"), patch.object(acq.subprocess, "run", side_effect=run):
            receipt = acq.acquire(YT_URL, "yt-dlp", "subtitles", self.data)
        self.assertEqual(receipt["status"], "partial")
        self.assertEqual(receipt["failure"], {"exit_code": None, "reason": "timeout"})
        self.assertNotIn("exit_code", receipt)

    def test_unusable_files_with_nonzero_exit_stay_failed(self):
        for name, files in {"empty": {"video.zh.vtt": ""}, "metadata": {"video.info.json": "{}"}, "unfinished": {"video.zh.vtt.part": VTT}}.items():
            with self.subTest(name):
                self.scene(write=files, exit=1)
                receipt = self.result(self.cli(data=self.tmp / name), 2)
                self.assertEqual((receipt["status"], receipt["reason"]), ("failed", "no_usable_target_or_command_failed"))
                self.assertNotIn("failure", receipt)
                self.assertEqual(len(receipt["files"]) + len(receipt.get("sensitive_metadata_retained", [])), 1)

    def test_exit_zero_stays_acquired_and_reuse_exits_zero(self):
        self.scene(write={"video.zh.vtt": VTT})
        first = self.result(self.cli(), 0)
        self.assertEqual((first["status"], first["reason"]), ("acquired", "files_need_content_verification"))
        self.assertNotIn("failure", first)
        self.assertTrue(self.result(self.cli(), 0)["reused"])
        self.assertEqual(len(self.calls()), 1)

    def test_exit_zero_without_target_stays_exit_two(self):
        self.assertEqual(self.result(self.cli(), 2)["status"], "failed")

    def test_help_documents_exit_codes(self):
        run = subprocess.run([sys.executable, "-I", str(SCRIPT), "--help"], capture_output=True, text=True, encoding="utf-8",
                             env={"PYTHONDONTWRITEBYTECODE": "1", "COLUMNS": "400"})
        self.assertEqual(run.returncode, 0)
        self.assertIn("3 partial", run.stdout)


if __name__ == "__main__":
    unittest.main()
