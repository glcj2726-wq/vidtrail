# Transcription and visual evidence

Transcription requires media that is actually available. It cannot retrieve a source blocked by a platform. Reuse reliable existing text before transcribing. Download substantial media only for needed transcription, visual evidence, or an explicit media request.

## Check the media

ffprobe establishes readable container/stream metadata, duration, resolution and audio tracks. It does not prove the whole file decodes or plays correctly. If a full decode/playback check is needed, record its separate scope and result. Identity comes from matching source metadata and part/cid.

```sh
ffprobe -v error -show_format -show_streams -of json "$VIDEO_FILE"
ffmpeg -nostdin -n -i "$VIDEO_FILE" -vn -ac 1 -ar 16000 "$AUDIO_FILE"
ffmpeg -nostdin -n -ss "$TIMESTAMP" -i "$VIDEO_FILE" -frames:v 1 "$FRAME_FILE"
```

These are examples using host-specific paths, not commands to run automatically. Write new derivative files; `-n` avoids overwriting. Keep originals. Metadata readability, full playback, and content understanding are separate checks. Report actual quality; upscaling is not native high resolution. A spoken talk does not require HD, but unreadable text/charts remain a visual gap.

## Choose an available, authorized transcription route

| Route | Required conditions |
| --- | --- |
| Existing user transcript/export | Source identity and coverage can be checked; preferred |
| Local engine | Engine and model already available; hardware, language and output capabilities checked |
| Cloud service | User selected service and authorized the specific upload and any cost |
| Drive processing/export, such as Quark | User selected route; tools and upload authorization exist |

Respect a user-selected route. Otherwise explain available options and use one requiring no additional authorization. If all require new authorization, ask only for that missing decision. No engine or model is bundled; do not invent a universal ASR command or silently install/download/pay. Inspect actual help.

Retain original transcript, engine/model version, language, media hash, coverage, questionable words, and gaps. ASR is generated text, not author-provided captions. A summary does not replace the transcript. With no usable authorized route, return partial and the smallest useful addition.

## Inspect the visuals that matter

Read the text first, then inspect specific evidence gaps. Talks/interviews usually need only important slides, charts, or formulas; software/code tutorials need interface operations, exact commands, parameters, and results checked; visual-creation workflows need before/after evidence.

Prefer existing source slides or user screenshots when identity is clear. Otherwise inspect a coarse overview when useful, then targeted timestamps. Keep readable frames and timestamps. Describe only inspected images, not visuals imagined from narration. Extracted frames are samples, not proof all visuals were reviewed. Exact code/formulas need matching visual or other primary evidence. For transcription disagreements, consult the corresponding audio when available instead of guessing.

State unverified visual areas or illegibility. Text read, images inspected, and workflow executed are separate outcomes; this skill does not execute the creator's workflow.
