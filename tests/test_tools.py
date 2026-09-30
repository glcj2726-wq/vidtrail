import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


acq = load("acquire", ROOT / ".agents/skills/coco-video-research-distill/scripts/acquire.py")
installer = load("install_skill", ROOT / "scripts/install_skill.py")


class ToolTests(unittest.TestCase):
    def test_identity_is_stable_and_part_specific(self):
        self.assertEqual(acq.identity("https://www.bilibili.com/video/BV1CMMh62EVA/?p=2&tracking=123")[:3], ("bilibili", "BV1CMMh62EVA", 2))
        self.assertEqual(acq.identity("https://youtu.be/3UgXWMQtB8E")[1], "3UgXWMQtB8E")
        with self.assertRaises(ValueError):
            acq.identity("https://example.com/watch?v=3UgXWMQtB8E")

    def test_failed_route_is_not_run_again(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(acq.shutil, "which", return_value="yt-dlp"), patch.object(acq.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "Sign in to confirm not a bot")) as run:
            first = acq.acquire("https://youtu.be/3UgXWMQtB8E", "yt-dlp", "subtitles", directory)
            second = acq.acquire("https://youtu.be/3UgXWMQtB8E", "yt-dlp", "subtitles", directory)
            self.assertEqual(first["reason"], "login_verification_required")
            self.assertTrue(second["reused"])
            self.assertEqual(run.call_count, 1)
            command = run.call_args.args[0]
            self.assertEqual(command[command.index("--extractor-retries") + 1], "0")

    def test_bili_caption_requires_body_and_reuses_hash(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(acq.shutil, "which", return_value="bili"), patch.object(acq.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps({"subtitle": {"available": True, "text": "Example", "items": []}}), "")) as run:
            first = acq.acquire("https://www.bilibili.com/video/BV1CMMh62EVA/", "bili", "subtitles", directory)
            self.assertEqual(first["status"], "acquired")
            self.assertEqual(first["content_verification"], "not_performed")
            self.assertTrue(acq.acquire(first["url"], "bili", "subtitles", directory)["reused"])
            Path(first["files"][0]["path"]).write_text("changed", encoding="utf-8")
            damaged = acq.acquire(first["url"], "bili", "subtitles", directory)
            self.assertIn("action", damaged)
            self.assertEqual(damaged["status"], "invalidated")
            self.assertEqual(run.call_count, 1)

    def test_metadata_only_and_wrong_part_not_ready(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(acq.shutil, "which", return_value="bili"), patch.object(acq.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '{"title":"example","subtitle":{"available":false}}', "")):
            self.assertEqual(acq.acquire("https://www.bilibili.com/video/BV1CMMh62EVA/", "bili", "subtitles", directory)["status"], "failed")
            with self.assertRaises(ValueError):
                acq.acquire("https://www.bilibili.com/video/BV1CMMh62EVA/?p=2", "bili", "subtitles", directory)

    def test_install_preserves_existing_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "coco-video-research-distill"
            target.mkdir()
            (target / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                installer.install(directory, copy=True)
            self.assertEqual((target / "keep.txt").read_text(), "keep")
        with tempfile.TemporaryDirectory() as directory:
            target = installer.install(directory, copy=True)
            self.assertTrue((target / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
