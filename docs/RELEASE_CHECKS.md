# v0.1.0 private preview checks

This record concerns the English VidTrail distribution and rename, not a claim of universal platform success. The repository remains private. Final independent release review is pending.

## Source baseline

The integration starts from the existing main commit and the previously accepted 22-file VPS candidate. All 22 live VPS source files matched that candidate before integration. The accepted acquisition helper is unchanged (SHA256 `5f5214931b194ee15190cac22dbff111a1cc360d1615efd97df1a4a670d15147`); dependency pins are unchanged. Installer/test references follow the renamed skill path. The original maintainer working tree and installed skills are separate, preserved versions.

## Existing-material walkthroughs

These were performed by the implementing agent using existing source files. They are not blind evaluations by a separate agent, fresh platform acquisitions, full audiovisual reviews, or executions of the videos' procedures. Raw transcripts, private notes and material receipts are excluded from this repository.

| Case | Actual material / request | Result and boundary |
| --- | --- | --- |
| Learning note; Chinese output | YouTube `0vZ_UVLhSQQ`, all retained English auto-captions 00:04–05:12 | [Chinese learning note](examples/learning-note.zh-CN.md): one report example connects task, context and output; historical product/model claims are not current recommendations; visuals remain unverified |
| Creator workflow; Chinese output | Bilibili `BV1vDeK6wEZL` P1, all 517 retained caption items, 00:00.12–16:44.92 | [Chinese workflow](examples/creator-workflow.zh-CN.md): prerequisites, input/output/dependencies, review points and feedback loop; uncertain tool names are retained as gaps; no visual or execution claims |
| Candidate-only | Existing metadata fixtures; request to compare only | Stops with metadata comparison and “full text not read”; no acquisition/transcription/note generation. No live search was performed |
| Reuse | Same original transcripts used for these new questions | Originals/hash checks reused; no new platform subprocess or download |
| Insufficient material | Supplied description/short excerpt only; full workflow requested | Partial scope, no invented steps; requests complete text and necessary visual evidence. Implementer-authored scenario, not an independent model eval |

## Mechanical verification

Final machine results are appended after execution below. Windows intentionally skips POSIX executable-stub tests; the independent Linux copy is required for the full regression result. Temporary installation checks do not install into the maintainer's active skill directories.

Results on 2026-11-08:

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
