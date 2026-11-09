# v0.1.0 private preview checks

This record concerns the English VidTrail distribution and rename, not a claim of universal platform success. The repository remains private. Final independent release review is pending.

## Current status: independently verified privacy/path repair (2026-11-09)

This revision incorporates the twelve-file repair based on `997dda9c0368672822ecf273bb0245ec58ee0cb1`. The repository remains a private preview. The patch and full-file archive matched exactly, all source changes stayed within the approved twelve paths, and the earlier `VALIDATION.md` body was retained byte-for-byte.

The coordinator independently ran the collected source in a separate Linux copy with the existing pinned yt-dlp 2026.8.19 environment: **59 tests passed, zero skipped**. The same 23 new regression methods on the old helper produced **18 failing methods and 5 passing controls** (23 failure records including subtests). A separate behavioral oracle prepared before inspecting this patch passed **15/15** on the fixed helper; the same oracle passed 1 and failed 14 on the base helper. These are test cases for the two known defects, not fourteen separate product defects.

The oracle checks nested directory/receipt links, preserved outside sentinels, a valid root alias, legacy-metadata exclusion with history preserved, and the real pinned yt-dlp option parser/API in both modes with and without a synthetic cookie. It blocks network access and uses no real credential or platform material. Source hashes and the ten supplied inputs were unchanged after validation.

Windows rerun: **59 tests total, 5 passed, 54 POSIX-stub/symlink tests skipped**. The full Linux result is required; Windows skips do not count as passes. The implementation-stage system-Python result below likewise means 56 passed plus 3 skipped out of 59 total.

No new live platform request, login, audiovisual review, or execution of a source video's workflow was performed. The installed maintainer skills and original working tree were preserved. The recorded implementation-stage statements below about an uncommitted patch and the absence of an independent/Windows run describe that earlier stage only. A final public-release decision remains separate.

## Implementation-stage record: base `997dda9` plus the repair patch (2026-11-08 UTC)

This historical implementation-stage section describes base commit `997dda9c0368672822ecf273bb0245ec58ee0cb1` with an uncommitted privacy/path/documentation patch prepared for coordinator review. The patch has no commit ID yet and has not been pushed, published or run against a live platform. Later sections record checks made on the base before this patch.

**Metadata privacy.** Base `997dda9` always passed `--write-info-json`. An offline run of pinned yt-dlp 2026.8.19 with a synthetic Netscape cookie wrote the cookie value into the resulting `.info.json`, at top level and in each format. The helper now passes `--no-write-info-json` in subtitles and media modes, with or without `--cookies-file`. Nothing is written and then scrubbed. Receipts keep the requested canonical URL, platform ID and part, status, sizes and SHA256; yt-dlp receipts add `extractor_metadata: not_retained`, because the helper no longer keeps or checks extractor data such as cid, uploader or duration. An explicit cookie path is validated before any data or attempt directory is created, even when yt-dlp is missing. `.info.json` files left by earlier versions are not deleted, rewritten or refetched: helper output and new receipts leave them out of `files` and list them under `sensitive_metadata_retained` with `metadata_warning`.

**Path boundary.** Before any read, mkdir or write, the helper resolves the data root and every existing level below it (platform, video, part, target) plus an existing `receipt.json`. A link that leaves the chosen root, or enters the source checkout or installed skill, stops the run with exit 1; the link and its target are left unchanged and no platform tool runs. A receipt whose recorded files now resolve outside the root is treated as invalidated without reading them. Root aliases, links that stay inside the root, copy and symlink installs, bili parsing, partial reuse and media handling are unchanged. These are ordinary path checks, not an OS sandbox or protection against concurrent hostile filesystem changes.

**Unchanged.** CLI options, exit codes 0/1/2/3, reuse rules and dependency pins.

**Examples.** Both example notes were corrected against the retained captions: the AI as the actor that collects post-publication data, the authenticated creator-backend prerequisite (a source prerequisite, not an action of the example), publishing materials largely delegated to AI including the popular-tag instruction, the early-cut versus later meaning-preservation rule, the GUI-editing tradeoff without guessing garbled names, dated author claims with separate publication and retrieval dates, and evidence labels. Visual gaps remain stated.

Offline results for this patch (Linux, Python 3.10.12; platform tools are temporary stubs; no network, authentication or real credentials):

| Run | Result |
| --- | --- |
| Base `997dda9`, original tests | 36 passed, 0 skipped |
| Patched tree, system Python without yt-dlp | 59 run: 56 passed, 3 skipped (the pinned-yt-dlp class needs the library) |
| Patched tree, existing project environment with yt-dlp 2026.8.19 | 59 passed, 0 skipped |
| New `tests/test_privacy_and_paths.py` on the base helper | 23 tests: 18 fail as intended (nested links, receipt links, cookie-path order, `--no-write-info-json`, legacy metadata, synthetic cookie written to `.info.json` by real yt-dlp); 5 pass (4 safe-path controls; broken link, which the base also stopped) |
| Original, unmodified 36-test files on the patched helper | 32 pass; 4 fail because they asserted the old `--write-info-json` flag or raw `.info.json` in `files`. Those 4 assertions are updated in this patch; no test was removed |

Helper SHA256 after the patch: `32a6888a5e67bf3fd7484b65698715f963abbab6e2bdb6d3330b0d8ce7504705` (base: `5f5214931b194ee15190cac22dbff111a1cc360d1615efd97df1a4a670d15147`). No live Bilibili/YouTube request, visual review, Windows run or independent release review was performed for this patch.

## Source baseline (base `997dda9`, before the repair patch)

The integration starts from the existing main commit and the previously accepted 22-file VPS candidate. All 22 live VPS source files matched that candidate before integration. The accepted acquisition helper is unchanged (SHA256 `5f5214931b194ee15190cac22dbff111a1cc360d1615efd97df1a4a670d15147`); dependency pins are unchanged. Installer/test references follow the renamed skill path. The original maintainer working tree and installed skills are separate, preserved versions.

## Existing-material walkthroughs

These were performed by the implementing agent using existing source files. They are not blind evaluations by a separate agent, fresh platform acquisitions, full audiovisual reviews, or executions of the videos' procedures. Raw transcripts, private notes and material receipts are excluded from this repository.

| Case | Actual material / request | Result and boundary |
| --- | --- | --- |
| Learning note; Chinese output | YouTube `0vZ_UVLhSQQ`, all retained English auto-captions 00:04–05:12 | [Chinese learning note](examples/learning-note.zh-CN.md): one report example connects task, context and output; historical product/model claims are dated and not current recommendations; inferences are labelled; visuals remain unverified. Corrected in the repair patch |
| Creator workflow; Chinese output | Bilibili `BV1vDeK6wEZL` P1, all 517 retained caption items, 00:00.12–16:44.92 | [Chinese workflow](examples/creator-workflow.zh-CN.md): prerequisites, input/output/dependencies, review points and feedback loop; AI as the data-collection actor with the authenticated creator-backend prerequisite; uncertain tool names are retained as gaps; no visual or execution claims. Corrected in the repair patch |
| Candidate-only | Existing metadata fixtures; request to compare only | Stops with metadata comparison and “full text not read”; no acquisition/transcription/note generation. No live search was performed |
| Reuse | Same original transcripts used for these new questions | Originals/hash checks reused; no new platform subprocess or download |
| Insufficient material | Supplied description/short excerpt only; full workflow requested | Partial scope, no invented steps; requests complete text and necessary visual evidence. Implementer-authored scenario, not an independent model eval |

## Mechanical verification

Final machine results are appended after execution below. Windows intentionally skips POSIX executable-stub tests; the independent Linux copy is required for the full regression result. Temporary installation checks do not install into the maintainer's active skill directories.

Results on 2026-11-08 for base `997dda9`, before the repair patch above:

- Linux Python 3.10.12, workspace UID 1001, separate verified source copy: **36 tests passed, zero skips**, unittest time 8.106 seconds. Source hashes were unchanged by the tests.
- Actual installer CLI on Linux: copy and link succeeded; a second copy preserved the existing destination and exited 1, while the same link was idempotent and exited 0.
- Windows Python 3.13: 5 tests passed and 31 POSIX executable-stub cases were skipped. Copy installation, destination conflict preservation, copied helper boundary and self-contained skill references passed. Linking reported WinError 1314 (missing host privilege); the documented `--copy` route works without changing system settings.
- Official skill-format validator passed. All 39 relative links/anchors resolved. The acquisition helper hash matches the accepted baseline, and the copied skill's runtime links remain inside the installed skill.
- Current source and all 62 reachable pre-update history objects were checked for common GitHub-token/private-key patterns, credential values and maintainer-specific absolute paths, with no matches. This is a bounded content check, not a guarantee against every possible secret or a final publication approval.

No optional integration, live platform operation, automatic host discovery, or separate-agent behavioral evaluation is implied by these results.

## Remaining release boundary

- No new Bilibili/YouTube access, authentication, media download, ASR or cloud upload in this batch. Historical anonymous VPS acquisition was blocked; local successes are not proof the VPS is authenticated.
- Optional browser/Bili23/Quark/Notion/transcription integrations have not been newly validated. No tutoring/mastery evaluation or source-derived workflow execution.
- The maintainer's enhanced bili search, local authentication automation and transcription wrapper are not bundled. Private classroom workflows are excluded.
- History includes earlier scope and verification records. Those records are historical, not current capability claims. Final review must cover the exact pushed commit and public-facing content before visibility changes.
- VidTrail is a project name, not a claim of a globally unique brand or an available domain.
