# Acquire selected content

Scope: selected Bilibili and YouTube videos. For discovery see [Search](search.md). Run the repository doctor when needed, inspect real CLI help/tool schemas, and reuse checks for the same version. Each source ID + part + target gets one attempt per route. A new thread or format is not a reason to repeat a failed request; document a relevant tool, login, or source change before a retry. Stop acquiring when reliable text is sufficient.

## Bilibili

Follow this order, recording success, failure, not applicable, or unavailable:

1. **Existing text:** reuse reliable material matching BV + part/cid.
2. **CLI captions once:** for part 1, `bili video BV_ID --subtitle-timeline --subtitle-format srt --json`; inspect `data.subtitle` (or legacy top-level `subtitle`), availability and usable text/items. This pinned CLI defaults to part 1. For another part, record this route as not applicable; never substitute P1 text. Authentication failure does not itself justify downloading media.
3. **Browser transcript:** use real browser tools in the host's configured order, once each, through normal captions/transcript UI. Verify BV, part, language, and text coverage. Do not guess internal endpoints, bypass challenges, or install a browser to pretend that an authenticated session exists.
4. **Media only when still needed:** choose an actual media route. With configured Bili23 MCP, resolve once, create one task, retain its ID, and inspect terminal state/files. Resolution does not prove captions exist; verify any returned subtitles. Otherwise report Bili23 unavailable and use yt-dlp media once if available. Preserve `?p=N` and select `--playlist-items N`. The helper does not keep yt-dlp's extractor metadata, so it cannot confirm part/cid; confirm the part from source evidence actually inspected (for example the player page or the media itself), otherwise record the part as requested, not verified. A normal source-page download entry is a later option when available; saving HTML is not obtaining MP4.

With media but no text, follow [Transcription and visuals](transcription-visual.md). Do not automatically enable ASR. If no authorized route exists, return partial. A video-only request goes directly to the media target without forced subtitles or notes.

Request the highest available media up to 1080p by default; report actual quality. Check duration and ffprobe metadata, and identity/part from inspected source evidence; ffprobe metadata does not establish source identity. A shared BV ID alone cannot establish the correct part. The helper's `--route bili` supports only first-part captions. Bili23 is an external service, not a bundled server component.

## YouTube

For selected captions, yt-dlp uses `--write-subs --write-auto-subs --sub-langs "zh.*,en.*" --skip-download` with `--retries 0 --extractor-retries 0`. Check current EJS/runtime requirements; installed dependencies do not guarantee platform access.

After an access challenge, empty text, or caption failure, try actually exposed browser transcript routes in the host's configured order, once each, before choosing media. A plugin-specific transcript method may be used only when the tool really exposes it; otherwise use the normal transcript panel. Verify video ID, language, timing, and coverage. Do not invent APIs or assume desktop plugins exist on a server. Explicit absence of captions is an evidence gap.

For necessary media, choose `media` explicitly, defaulting to the highest available quality up to 1080p. Merging audio/video requires ffmpeg. Caption failure neither proves nor disproves media availability: a distinct necessary media target may be tried once, reusing any prior failure. With media and no text, choose an authorized transcription route. Uploading or transcription cannot solve an inaccessible source download.

## Credentials and helper behavior

Keep credentials outside the repository and notes; never print them. Reuse or transfer credentials only with applicable user authorization, through a private channel, without copying entire browser profiles. bili 0.6.2 uses `~/.bilibili-cli/credential.json`; use its actual format. A YouTube Netscape Cookie file is different. The helper's `--cookies-file` applies only to yt-dlp. The path is checked before any data directory is created. The helper never stores stderr or command arguments, and it passes `--no-write-info-json` in both modes because yt-dlp's raw `.info.json` can embed cookie values (offline check with pinned 2026.8.19 and a synthetic cookie). Receipts therefore keep the requested canonical URL, ID and part, status, file sizes and hashes, not extractor metadata such as cid, uploader or duration. `.info.json` files written by earlier helper versions are kept where they are, left out of `files`, and reported under `sensitive_metadata_retained` with `metadata_warning`; review them privately before sharing materials. They are not deleted, rewritten or refetched automatically. Expiry and network changes can invalidate reuse. GitHub authentication is separate from video-platform authentication.

Do not repeatedly switch clients, cookies, or proxies after failure. Reuse user-provided transcripts/exports or report the minimum gap.

The helper reads the bili response envelope tolerantly and separates subtitle/media flags. Before reading or creating anything, it resolves the data root and every existing level below it (platform, video, part, target and `receipt.json`); a link that leaves the chosen root or enters the source checkout/installed skill stops the run with exit 1 without touching the link or its target. Root aliases and links that stay inside the root keep working. These are ordinary path checks, not an OS sandbox or protection against concurrent hostile filesystem changes. Exit codes: 0 acquired, 1 stopped before acquisition, 2 failed/unavailable/invalidated, 3 partial. A nonzero caption process can leave usable caption files: partial retains hashes, requires content verification, and is reused without another platform call while hashes match. Changed hashes invalidate reuse. `--retry-reason` is an explicit new attempt, not an automatic recovery step. Nonzero media exit remains failed because a stream may be incomplete or unmerged.

## Optional Quark route and primary references

[Quark](quark.md) is optional and user-selected. Upload, processing, complete transcript export, retrieval, and full-text verification are separate stages. AI summary/QA is not a transcript export.

- [bilibili-cli](https://github.com/public-clis/bilibili-cli)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [EJS requirements](https://github.com/yt-dlp/yt-dlp/wiki/EJS)
- [Bili23 MCP](https://bili23.scott-sloan.cn/doc/mcp-server.html)
