# Acquire selected content

Scope: selected Bilibili and YouTube videos. For discovery see [Search](search.md). Run the repository doctor when needed, inspect real CLI help/tool schemas, and reuse checks for the same version. Each source ID + part + target gets one attempt per route. A new thread or format is not a reason to repeat a failed request; document a relevant tool, login, or source change before a retry. Stop redundant text acquisition when reliable text is sufficient; necessary visual evidence is a separate target.

## Bilibili

Follow this order, recording success, failure, not applicable, or unavailable:

1. **Existing text:** reuse reliable material matching BV + part/cid.
2. **CLI captions once:** for part 1, `bili video BV_ID --subtitle-timeline --subtitle-format srt --json`; inspect `data.subtitle` (or legacy top-level `subtitle`), availability and usable text/items. This pinned CLI defaults to part 1. For another part, record this route as not applicable; never substitute P1 text. Authentication failure does not itself justify downloading media.
3. **Browser transcript:** use real browser tools in the host's configured order, once each, through normal captions/transcript UI. Verify BV, part, language, and text coverage. Do not guess internal endpoints, bypass challenges, or install a browser to pretend that an authenticated session exists.
4. **Media only when still needed:** obtain necessary text/transcription or visual evidence, or satisfy an explicit media request. Choose an actual media route. With configured and actually exposed Bili23 MCP, resolve once, create one task, retain its ID, and inspect terminal state/files. Resolution does not prove captions exist; verify any returned subtitles. Otherwise report Bili23 unavailable and use yt-dlp media once if available. Preserve `?p=N` and select `--playlist-items N`. The helper does not keep yt-dlp's extractor metadata, so it cannot confirm part/cid; confirm the part from source evidence actually inspected (for example the player page or the media itself), otherwise record the part as requested, not verified. A normal source-page download entry is a later option when available; saving HTML is not obtaining MP4.

With media but no text, follow [Transcription and visuals](transcription-visual.md). Do not automatically enable ASR. If no authorized route exists, return partial. A video-only request goes directly to the media target without forced subtitles or notes.

Request the highest available media up to 1080p by default; report actual quality. Check duration and ffprobe metadata, and identity/part from inspected source evidence; ffprobe metadata does not establish source identity. A shared BV ID alone cannot establish the correct part. The helper's `--route bili` supports only first-part captions. Bili23 is an external service, not a bundled server component.

## YouTube

For selected captions, yt-dlp uses `--write-subs --write-auto-subs --sub-langs "zh.*,en.*" --skip-download` with `--retries 0 --extractor-retries 0`. Check current EJS/runtime requirements; installed dependencies do not guarantee platform access.

After an access challenge, empty text, or caption failure, try actually exposed browser transcript routes in the host's configured order, once each, before choosing media. A plugin-specific transcript method may be used only when the tool really exposes it; otherwise use the normal transcript panel. Verify video ID, language, timing, and coverage. Do not invent APIs or assume desktop plugins exist on a server. Explicit absence of captions is an evidence gap.

For necessary media, choose `media` explicitly, defaulting to the highest available quality up to 1080p. Merging audio/video requires ffmpeg. Caption failure neither proves nor disproves media availability: a distinct necessary media target may be tried once, reusing any prior failure. With media and no text, choose an authorized transcription route. Uploading or transcription cannot solve an inaccessible source download.

## Explain the actual failure before asking for login

Public accessibility is source-, network- and tool-dependent; some public videos can be retrieved without login, others cannot. Do not require every user to log in first, or promise anonymous success. Reuse an already-authorized session without automatic login, Cookie export, browser-profile scans, or credential transfer.

The helper adds an optional `failure_kind` to new failed/unavailable/partial receipts. It keeps legacy `reason`, `failure`, status, CLI arguments and exit codes unchanged. The legacy `login_verification_required` is broad and is not proof of expired login. Prefer the precise code below. Old receipts without this field are still reused without a new request or a guessed classification.

| `failure_kind` | Evidence and user-facing response |
| --- | --- |
| `missing_login` | Explicit tool requirement or missing credential diagnostic. Say this route needs login and ask the user to complete normal login in their own environment if they want to continue. |
| `expired_login` | Explicit expired/no-longer-valid session diagnostic. Explain that this route rejected the saved session; suggest normal renewal, not deletion of unrelated sessions. |
| `rate_limited` | HTTP 429 or explicit rate limit. Stop repeated requests; login is not the prescribed fix. |
| `access_verification` | Bot/CAPTCHA/access challenge, including "sign in to confirm you are not a bot". Report verification, not assumed Cookie expiry; do not bypass it. |
| `network_error` | Explicit connection, DNS, TLS or network-timeout diagnostic. Report a connection problem, not an expired account. |
| `no_subtitles` | Explicit absence of requested subtitles on a subtitle target, not merely empty output or bili `available: false`. Offer existing text or a separately authorized transcription option; other languages may exist. |
| `tool_unavailable` | Required executable or ffmpeg missing. Explain the missing local tool; no automatic install. |
| `unknown` | Ambiguous/empty output, bare 403, unreadable Cookie database, invocation error or generic subprocess deadline. State what failed and that its cause is undetermined. Do not invent a login or no-caption diagnosis. |

If multiple diagnostics occur, rate limits and access challenges take precedence over login phrases. Classification inspects stderr, the exact yt-dlp `[info] There are no subtitles for the requested languages` stdout line for subtitle targets, and only the explicit error message of a bili `ok: false` envelope. It retains a fixed code, not raw diagnostics. A 429 inside a URL/ID is not an HTTP status; `robots.txt` is not a bot challenge; uncertain Cookie-expiry wording is not confirmed expiry. Explicit bili error envelopes are not saved as content, even on exit zero. It never classifies a video title or transcript as an error message. A Cookie file's existence says nothing about validity. A timeout of the whole subprocess can include local processing and is therefore unknown without an explicit network diagnostic.

Explain failures as: what was observed → what it establishes → the smallest useful next step. For example: "The platform requested bot verification. This does not establish that your Cookie expired. This attempt stopped; we can continue from the existing transcript." If usable captions remain after failure, keep and verify that partial material instead of reacquiring it. Online acquisition and text distillation are reported separately.

## Credentials and helper behavior

Keep credentials outside the repository and notes; never print them. Reuse or transfer credentials only with applicable user authorization, through a private channel, without copying entire browser profiles. bili 0.6.2 uses `~/.bilibili-cli/credential.json`; use its actual format. A Netscape Cookie file is different: never pass bili's JSON directly as yt-dlp cookies. A compatible minimal copy/conversion is a host-side, explicitly authorized action, not a bundled automatic authentication feature. The helper's `--cookies-file` applies only to yt-dlp, on either supported platform. The path is checked before any data directory is created. The helper never stores stderr or command arguments, and it passes `--no-write-info-json` in both modes because yt-dlp's raw `.info.json` can embed cookie values (offline check with pinned 2026.8.19 and a synthetic cookie). Receipts therefore keep the requested canonical URL, ID and part, status, file sizes and hashes, not extractor metadata such as cid, uploader or duration. `.info.json` files written by earlier helper versions are kept where they are, left out of `files`, and reported under `sensitive_metadata_retained` with `metadata_warning`; review them privately before sharing materials. They are not deleted, rewritten or refetched automatically. Expiry and network changes can invalidate reuse. GitHub authentication is separate from video-platform authentication.

Do not repeatedly switch clients, cookies, or proxies after failure. Reuse user-provided transcripts/exports or report the minimum gap.

The helper reads the bili response envelope tolerantly and separates subtitle/media flags. Before reading or creating anything, it resolves the data root and every existing level below it (platform, video, part, target and `receipt.json`); a link that leaves the chosen root or enters the source checkout/installed skill stops the run with exit 1 without touching the link or its target. Root aliases and links that stay inside the root keep working. These are ordinary path checks, not an OS sandbox or protection against concurrent hostile filesystem changes. Exit codes: 0 acquired, 1 stopped before acquisition, 2 failed/unavailable/invalidated, 3 partial. A nonzero caption process can leave usable caption files: partial retains hashes, requires content verification, and is reused without another platform call while hashes match. Changed hashes invalidate reuse. `--retry-reason` is an explicit new attempt, not an automatic recovery step. Nonzero media exit remains failed because a stream may be incomplete or unmerged.

## Optional Quark route and primary references

[Quark](quark.md) is optional and user-selected. Upload, processing, complete transcript export, retrieval, and full-text verification are separate stages. AI summary/QA is not a transcript export.

- [bilibili-cli](https://github.com/public-clis/bilibili-cli)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [EJS requirements](https://github.com/yt-dlp/yt-dlp/wiki/EJS)
- [Bili23 MCP](https://bili23.scott-sloan.cn/doc/mcp-server.html)
