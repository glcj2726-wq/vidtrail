# Optional Quark upload, processing, export and retrieval

Use this route only when selected by the user, configured on the execution host, and authorized for the specific material. Existing reliable text bypasses it. This reference describes coordination, not a bundled Quark client or promise of automatic transcription/export.

Use the current official [quarkclouddrive skill and CLI](https://github.com/quark-clouddrive/quarkclouddrive_offical). Read installed skill/help for exact authentication, upload, search, download and required session arguments. Do not guess subcommands or copy account configuration. Installation or an updater may download/replace files and needs applicable authorization; do not run it as a supposedly read-only check. Follow the official runtime's required checks only within that authorization, and reuse their result for the current input.

Run external tools in the authorized material/task directory outside this distribution, so their artifacts do not enter Git. Pass user input as correctly quoted data, not shell code. Use the actual official session format and parameters. Establish the target folder or reuse a confirmed one; never guess root FID 0 or silently change directories.

## State and next action

| State | Next action | Avoid |
| --- | --- | --- |
| No text or cloud original | Verify available media, upload authorization and destination; deduplicate then upload | Uploading a URL as though it were a local file |
| Upload incomplete/paused | Inspect the original record/task and resume when supported | Creating another upload for the same file |
| Upload terminal success; no export | Record uploaded_waiting_export; process or request supported manual export | Treating 100% progress as success or promising a fixed wait |
| Export exists | Search stable source identity and inspect full results; retrieve matching material | Calling summary instead of finding the export |
| Text retrieved | Check identity/full coverage and distill | Treating an AI summary as full text |

Use media names containing stable video ID and part; create a non-overwriting derivative upload copy if necessary. Preserve original hash/name mapping. Match downloaded metadata and platform ID/part/cid to the cloud hit. Do not rename or alter cloud history automatically.

Verify upload terminal results for each subtask: overall success, filename, size, file ID/FID and target path. Save actual IDs, path, byte count, local hash and receipt in the user's private project. Progress alone is insufficient. Do not repeat successful uploads after partial failure. A missing cloud hash cannot support a two-sided hash claim; an empty directory response does not establish root.

## Summary is not export

Cloud summary/QA returns generated understanding, not necessarily verbatim text or an exported file. Only use those features when requested. Automatic full export has not been validated for the target server; preserve the manual step where necessary: the user generates/saves a complete transcript through a supported interface, then the agent retrieves it. Slides, mind maps and summaries are optional.

Follow official stopping rules after a cloud assistant failure. Do not repeatedly request summary or switch to web to complete the same failed query. Retrieval of an independently existing export is a distinct authorized action. An empty response or error does not prove completion or future readiness.

## Retrieve precisely and resume safely

Search using the original platform ID and part and inspect complete returned artifacts, not a truncated preview. If the exact search has no match, report it; broaden only with a new relevant condition from the user. Verify identity and material role before merging similarly named files.

Use current download help to retrieve authorized matching FIDs outside the repository. Retain original format, ID, size and SHA256; reuse a matching existing file with valid hash. The transcript is primary evidence; a summary document is navigation. Read time bounds, obvious gaps and duration alignment before calling it complete. Resume [Workflow](workflow.md) after verification.

CLI/environment errors do not establish account failure. Diagnose only the returned evidence; do not bypass unsupported hosts, loop authentication, or automatically operate Quark's website. Video-source browser fallback and Quark web operation are separate permissions. Retain the waiting state and original task for the next turn instead of downloading/uploading/summarizing again. Cleanup is separately authorized and must protect the only evidence.
