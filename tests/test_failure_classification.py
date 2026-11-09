"""Portable, offline classification and receipt/reuse regressions; synthetic diagnostics only."""
import importlib.util
import importlib.metadata
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / '.agents/skills/vidtrail/scripts/acquire.py'
spec = importlib.util.spec_from_file_location('failure_classification_acquire', SCRIPT)
acq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acq)
URL = 'https://www.youtube.com/watch?v=P57Bg5yIkdA'
VTT = 'WEBVTT\n\n00:00.000 --> 00:01.000\nSynthetic line\n'


class ClassificationTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('yt_dlp') and importlib.metadata.version('yt-dlp') == '2026.8.19', 'requires the pinned yt-dlp library')
    def test_pinned_tool_really_emits_caption_absence_to_stdout(self):
        from yt_dlp import YoutubeDL
        class Offline(YoutubeDL):
            def urlopen(self, *args, **kwargs):
                raise AssertionError('network is forbidden in this fixture')
        out, err = io.StringIO(), io.StringIO()
        fixture = {'id': 'P57Bg5yIkdA', 'title': 'Synthetic', 'extractor': 'Generic',
                   'extractor_key': 'Generic', 'webpage_url': URL,
                   'formats': [{'format_id': '0', 'url': 'https://example.invalid/synthetic.mp4',
                                'ext': 'mp4', 'vcodec': 'h264', 'acodec': 'aac'}]}
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with Offline({'skip_download': True, 'writesubtitles': True, 'writeautomaticsub': True,
                          'subtitleslangs': ['en'], 'cachedir': False, 'no_warnings': True,
                          'outtmpl': str(Path(directory)/'%(id)s.%(ext)s')}) as tool:
                tool.process_ie_result(fixture, download=True)
        self.assertIn('[info] There are no subtitles for the requested languages', out.getvalue())
        # Python 3.10 emits a yt-dlp deprecation warning; it is not a caption
        # diagnostic and must not hide the normal stdout result.
        self.assertNotIn('There are no subtitles', err.getvalue())
        self.assertEqual(acq.failure_kind(err.getvalue(), 'subtitles', yt_dlp_stdout=out.getvalue()), 'no_subtitles')

    def test_explicit_auth_and_missing_credentials(self):
        for text, expected in [
            ('Please sign in to watch this video', 'missing_login'),
            ('Authentication required', 'missing_login'),
            ('未登录，请先登录', 'missing_login'),
            ('missing SESSDATA', 'missing_login'),
            ('Your cookies are no longer valid', 'expired_login'),
            ('Session has expired', 'expired_login'),
            ('登录已过期', 'expired_login'),
        ]:
            with self.subTest(text=text):
                self.assertEqual(acq.failure_kind(text, 'subtitles'), expected)

    def test_access_challenge_is_not_proof_of_expired_login(self):
        for text in ('Sign in to confirm you are not a bot', 'Please login; CAPTCHA verification required', '需要登录，完成人机验证'):
            with self.subTest(text=text):
                self.assertEqual(acq.failure_kind(text, 'subtitles'), 'access_verification')

    def test_rate_limit_takes_precedence_over_login_and_missing_captions(self):
        self.assertEqual(acq.failure_kind('HTTP Error 429; login required; no subtitles available', 'subtitles'), 'rate_limited')

    def test_network_errors_are_not_authentication_failures(self):
        for text in ('Connection reset by peer', 'Temporary failure in name resolution', 'The read operation timed out', 'certificate verify failed'):
            with self.subTest(text=text):
                self.assertEqual(acq.failure_kind(text, 'subtitles'), 'network_error')

    def test_only_explicit_caption_absence_and_only_caption_target(self):
        self.assertEqual(acq.failure_kind('There are no subtitles for the requested languages', 'subtitles'), 'no_subtitles')
        self.assertEqual(acq.failure_kind('There are no subtitles for the requested languages', 'media'), 'unknown')

    def test_ambiguous_diagnostics_stay_unknown(self):
        for text in ('', 'HTTP Error 403: Forbidden', 'subtitle_unavailable', 'Could not read Chrome cookie database', 'login helper crashed', '0 files received'):
            with self.subTest(text=text):
                self.assertEqual(acq.failure_kind(text, 'subtitles'), 'unknown')

    def test_identifiers_and_uncertain_auth_are_not_diagnoses(self):
        for text, expected in [
            ("ERROR: [youtube] abc-429-def: Sign in to confirm you're not a bot", 'access_verification'),
            ('ERROR: https://example.test/?p=429 HTTP Error 403', 'unknown'),
            ('Failed to download robots.txt: HTTP Error 403', 'unknown'),
            ('WARNING: Your cookies may have expired; HTTP Error 403', 'unknown'),
            ('WARNING: cookies might be expired', 'unknown'),
            ('The certificate has expired; session request failed', 'network_error'),
            ('Session request failed. The certificate has expired', 'network_error'),
            ('The provided YouTube account cookies are no longer valid', 'expired_login'),
        ]:
            with self.subTest(text=text):
                self.assertEqual(acq.failure_kind(text, 'subtitles'), expected)

    def test_requested_caption_stdout_is_exact_and_target_specific(self):
        diagnostic = '[info] P57Bg5yIkdA: Downloading 1 format(s): 0\n[info] There are no subtitles for the requested languages\n'
        self.assertEqual(acq.failure_kind('', 'subtitles', yt_dlp_stdout=diagnostic), 'no_subtitles')
        self.assertEqual(acq.failure_kind('', 'media', yt_dlp_stdout=diagnostic), 'unknown')
        for text in ('[info] title: There are no subtitles for the requested languages',
                     'There are no subtitles for the requested languages',
                     '[download] There are no subtitles for the requested languages',
                     '[info] A title about HTTP Error 429 and expired cookies'):
            with self.subTest(text=text):
                self.assertEqual(acq.failure_kind('', 'subtitles', yt_dlp_stdout=text), 'unknown')
        self.assertEqual(acq.failure_kind('HTTP Error 429', 'subtitles', yt_dlp_stdout=diagnostic), 'rate_limited')

    def test_bili_structured_error_message_is_classified_not_saved(self):
        payload = json.dumps({'ok': False, 'error': {'code': 'auth_required', 'message': '请先登录', 'details': 'SYNTHETIC-PRIVATE'}})
        self.assertEqual(acq.failure_kind('', 'subtitles', payload), 'missing_login')

    def test_bili_caption_and_title_are_never_used_as_error_diagnostics(self):
        payload = json.dumps({'ok': True, 'data': {'video': {'title': 'Session expired'}, 'subtitle': {'text': 'HTTP Error 429; Please login'}}})
        self.assertEqual(acq.failure_kind('', 'subtitles', payload), 'unknown')
        self.assertEqual(acq.failure_kind('', 'subtitles', 'not json'), 'unknown')


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.secret = 'SYNTHETIC-COOKIE-DO-NOT-STORE'

    def call(self, stderr='', write=False, code=1, mode='subtitles', timeout=False, stdout=''):
        def run(cmd, **kwargs):
            if write:
                template = cmd[cmd.index('-o') + 1]
                Path(template.replace('%(id)s.%(ext)s', 'sample.en.vtt' if mode == 'subtitles' else 'sample.mp4')).write_text(VTT, encoding='utf-8')
            if timeout:
                raise subprocess.TimeoutExpired(cmd, 120, stderr=self.secret)
            return subprocess.CompletedProcess(cmd, code, stdout, stderr)
        with patch.object(acq.shutil, 'which', return_value='synthetic-tool'), patch.object(acq.subprocess, 'run', side_effect=run) as invoked:
            receipt = acq.acquire(URL, 'yt-dlp', mode, self.root / 'data')
        return receipt, invoked

    def test_bot_receipt_keeps_legacy_reason_and_adds_precise_kind(self):
        receipt, _ = self.call('Sign in to confirm you are not a bot; ' + self.secret)
        self.assertEqual(receipt['reason'], 'login_verification_required')
        self.assertEqual(receipt['failure_kind'], 'access_verification')
        self.assertNotIn(self.secret, json.dumps(receipt))
        for file in (self.root/'data').rglob('*.json'):
            self.assertNotIn(self.secret, file.read_text(encoding='utf-8'))

    def test_partial_retains_files_failure_class_and_is_reused_without_call(self):
        receipt, invoked = self.call('HTTP Error 429; ' + self.secret, write=True)
        self.assertEqual(receipt['status'], 'partial')
        self.assertEqual(receipt['reason'], 'usable_files_after_command_failure')
        self.assertEqual(receipt['failure'], {'exit_code': 1, 'reason': 'command_failed'})
        self.assertEqual(receipt['failure_kind'], 'rate_limited')
        with patch.object(acq.subprocess, 'run') as later:
            reused = acq.acquire(URL, 'yt-dlp', 'subtitles', self.root/'data')
        later.assert_not_called()
        self.assertEqual(invoked.call_count, 1)
        self.assertTrue(reused['reused'])
        self.assertEqual(reused['files'], receipt['files'])
        self.assertEqual(reused['failure_kind'], 'rate_limited')

    def test_explicit_no_captions_does_not_claim_success(self):
        receipt, _ = self.call('There are no subtitles for the requested languages', code=0)
        self.assertEqual(receipt['status'], 'failed')
        self.assertEqual(receipt['failure_kind'], 'no_subtitles')

    def test_empty_output_is_unknown_not_no_captions(self):
        receipt, _ = self.call('', code=0)
        self.assertEqual(receipt['failure_kind'], 'unknown')

    def test_real_stream_layout_reports_absent_requested_language_and_reuses(self):
        diagnostic = '[info] P57Bg5yIkdA: Downloading 1 format(s): 0\n[info] There are no subtitles for the requested languages\n'
        receipt, invoked = self.call(code=0, stdout=diagnostic + self.secret)
        self.assertEqual(receipt['status'], 'failed')
        self.assertEqual(receipt['failure_kind'], 'no_subtitles')
        self.assertNotIn(self.secret, json.dumps(receipt))
        with patch.object(acq.subprocess, 'run') as later:
            reused = acq.acquire(URL, 'yt-dlp', 'subtitles', self.root/'data')
        later.assert_not_called()
        self.assertEqual(invoked.call_count, 1)
        self.assertEqual(reused['failure_kind'], 'no_subtitles')
        for file in (self.root/'data').rglob('*'):
            if file.is_file():
                self.assertNotIn(self.secret, file.read_text(encoding='utf-8'))

    def test_success_does_not_misclassify_nonfatal_warning(self):
        receipt, _ = self.call('WARNING: no subtitles available for another language', write=True, code=0)
        self.assertEqual(receipt['status'], 'acquired')
        self.assertNotIn('failure_kind', receipt)

    def test_media_failure_stays_failed_with_existing_bytes(self):
        receipt, _ = self.call('HTTP Error 429', write=True, mode='media')
        self.assertEqual(receipt['status'], 'failed')
        self.assertEqual(receipt['failure_kind'], 'rate_limited')
        self.assertNotIn('failure', receipt)

    def test_timeout_does_not_save_raw_output_and_preserves_partial(self):
        receipt, _ = self.call(write=True, timeout=True)
        self.assertEqual(receipt['status'], 'partial')
        self.assertEqual(receipt['reason'], 'usable_files_after_command_failure')
        self.assertEqual(receipt['failure_kind'], 'unknown')
        self.assertNotIn(self.secret, json.dumps(receipt))

    def test_failed_legacy_receipt_is_reused_without_backfilling_a_guess(self):
        target = self.root/'data/youtube/P57Bg5yIkdA/p1/yt-dlp-subtitles'
        target.mkdir(parents=True)
        old = {'status':'failed', 'reason':'login_verification_required', 'files':[], 'timestamp':'old'}
        path = target/'receipt.json'
        path.write_text(json.dumps(old), encoding='utf-8')
        original = path.read_bytes()
        with patch.object(acq.subprocess, 'run') as run:
            result = acq.acquire(URL, 'yt-dlp', 'subtitles', self.root/'data')
        run.assert_not_called()
        self.assertTrue(result['reused'])
        self.assertNotIn('failure_kind', result)
        self.assertEqual(path.read_bytes(), original)

    def test_missing_tool_has_specific_code_without_running(self):
        with patch.object(acq.shutil, 'which', return_value=None), patch.object(acq.subprocess, 'run') as run:
            result = acq.acquire(URL, 'yt-dlp', 'subtitles', self.root/'data')
        run.assert_not_called()
        self.assertEqual(result['reason'], 'tool_missing')
        self.assertEqual(result['failure_kind'], 'tool_unavailable')

    def test_changed_partial_hash_is_invalidated_without_refetch(self):
        first, _ = self.call('HTTP Error 429', write=True)
        Path(first['files'][0]['path']).write_text('changed', encoding='utf-8')
        with patch.object(acq.subprocess, 'run') as run:
            result = acq.acquire(URL, 'yt-dlp', 'subtitles', self.root/'data')
        run.assert_not_called()
        self.assertEqual(result['status'], 'invalidated')

    def test_bili_json_error_is_not_retained_and_preserves_legacy_reason(self):
        payload = json.dumps({'ok': False, 'error': {'message': '请先登录', 'details': self.secret}})
        with patch.object(acq.shutil, 'which', return_value='synthetic-tool'), patch.object(acq.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, payload, '')):
            result = acq.acquire('https://www.bilibili.com/video/BV1xFnt6zE3K/', 'bili', 'subtitles', self.root/'data')
        self.assertEqual(result['failure_kind'], 'missing_login')
        self.assertEqual(result['reason'], 'no_usable_target_or_command_failed')
        self.assertNotIn(self.secret, json.dumps(result))
        self.assertFalse(list((self.root/'data').rglob('bili-response.json')))

    def test_exit_zero_bili_error_envelope_never_becomes_content(self):
        payload = json.dumps({'ok': False, 'error': {'message': '请先登录', 'details': self.secret},
                              'data': {'subtitle': {'body': [{'content': 'not usable', 'from': 0, 'to': 1}]}}})
        with patch.object(acq.shutil, 'which', return_value='synthetic-tool'), patch.object(acq.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, payload, '')):
            result = acq.acquire('https://www.bilibili.com/video/BV1xFnt6zE3K/', 'bili', 'subtitles', self.root/'data')
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['failure_kind'], 'missing_login')
        self.assertFalse(list((self.root/'data').rglob('bili-response.json')))
        for file in (self.root/'data').rglob('*.json'):
            self.assertNotIn(self.secret, file.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
