# Workflow and resumption

This is an agent-guided sequence, not a fully automated pipeline. `acquire.py` implements only a single bili/yt-dlp acquisition route. Use the execution host's real capabilities for the other steps.

```text
topic → discover / compare → candidate-only: deliver and stop
selected link / existing transcript → identify source and part → reuse
→ reliable text: existing full text → captions → available browser transcript
  → when needed, media plus an available authorized transcription route
→ read all available text → check important visual evidence
→ learning notes / creator workflow / both → chosen destination
insufficient text or visuals → explicit partial result and smallest useful addition
```

1. Establish the question, deliverable, and destination. A supplied link does not require candidate discovery. Candidate-only requests stop after comparison.
2. Check stable source identity (platform ID and part/cid), existing materials, receipts, notes, and any already-authorized external task. Reuse a complete result for the same question; a different question needs incremental analysis.
3. For existing text, verify identity, language, beginning/end, and obvious gaps. An AI summary or description is only navigation. Reliable text goes directly to full reading.
4. Otherwise use [Platforms](platforms.md), once per route and target. Distinguish missing tool, command failure, access challenge, and confirmed lack of captions. Subtitles and media are separate targets. A download-only request ends after media checks.
5. With media but no text, choose an existing authorized route in [Transcription and visuals](transcription-visual.md). Without one, report partial and the minimum missing material or permission. Transcription cannot obtain inaccessible source media.
6. Read the full available text in chunks, track the read range, establish the causal structure, and name questions that need visual evidence. Reuse images/media, inspect normal source-page visuals, then use necessary local media for continuous changes or illegible browser details. Full text does not by itself settle visual questions. See [Distillation](distillation.md) and [Transcription and visuals](transcription-visual.md).
7. Write [learning notes](teaching.md), a [creator workflow](distillation.md#creator-workflow), or both. Notes explain the problem and causal understanding; workflows make inputs, dependencies, outputs and decisions usable. For both, preserve the same example without duplicating the full explanation. Offer deeper teaching only when requested.
8. Follow [Storage](storage.md). Add clickable source-time links and necessary readable screenshots with explanatory captions. State shared coverage briefly and keep specific gaps near affected claims; put detailed test evidence in a separate report when needed. Use the user's requested language or otherwise the conversation language.

## State follows actual evidence

Reuse the project's existing records; the [source template](../templates/source-record.example.json) is optional and does not mandate a new catalog.

| Fact | Suggested stage | Next action |
| --- | --- | --- |
| Candidate not selected | candidate | Compare; stop if candidate-only |
| One route failed; a different route exists | acquiring | Use the different route |
| Media available; text missing | media_ready | Authorized transcription or request minimum addition |
| External processing pending | waiting_external | Check the original task; do not submit again |
| Optional Quark upload complete; no export | uploaded_waiting_export | Retain IDs; process or wait for user export |
| User reports an export | exported_pending_retrieval | Retrieve by stable identity |
| Text obtained, not verified | transcript_acquired | Check identity and coverage |
| Reliable text available | ready_to_distill | Full reading and necessary visual checks |
| Result delivered | distilled | Incremental analysis for new questions |
| Tool, authorization, or evidence missing | partial / blocked | Explain scope, gap, and minimum addition |

Resume from the existing record and task. Bounded polling of an existing task does not create another task; stop waiting when no progress can be established. Do not promise a fixed completion time. Reuse failure receipts as well as successes. Retry a route only after a documented relevant change in tool, authentication, or source conditions.
