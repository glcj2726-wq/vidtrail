# Transcription and visual evidence

Transcription requires media that is actually available. It cannot retrieve a source blocked by a platform. Reuse reliable existing text before transcribing. Download substantial media only for needed transcription, visual evidence, or an explicit media request.

## Check the media

ffprobe establishes readable container/stream metadata, duration, resolution and audio tracks. It does not prove the whole file decodes or plays correctly. If a full decode/playback check is needed, record its separate scope and result. ffprobe metadata does not establish source identity, and helper receipts record only the requested URL/ID/part, not extractor metadata. Establish identity and part/cid from source evidence actually inspected; otherwise label them requested, not verified.

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

Before acquiring more media, name the questions that need images: for example, which template field receives the PDF, whether a filter applies to all views, or how a keyframe edit changes adjacent clips. For each inspected point, retain source/part, actual time, image path, what it confirms, and anything still unreadable. Keep these evidence details outside the distributed skill.

Use existing images or media first, then normal source-page playback/seeking. A readable still is usually enough for a field or final result. Inspect a continuous segment or meaningful before/after frames for dragging, animation, timing, and changes between states. When the browser or stills cannot answer a necessary question, use an existing media route in [Platforms](platforms.md), with authorization and a chosen material directory. A separate explicit media-validation request may also exercise that route once. Do not download just because a CLI login failed, a browser lacks an interface, or the user said "deep". Text being ready stops redundant caption requests, not justified visual investigation.

The helper currently retrieves media files, not an intelligent range-only download or an automatic whole-video analysis. Do not promise either. Downloads do not remove IP/account restrictions. Do not install a new downloader, model, or ASR system just to fill a visual gap. If the route fails, keep the supported text result and explain the remaining image question.

## Screenshots and source jumps in the result

Place time links next to important claims and workflow steps. For example, use `https://www.youtube.com/watch?v=VIDEO_ID&t=1004s` or `https://www.bilibili.com/video/BV_ID/?p=1&t=1537`, substituting the verified source/part and relevant seconds. These are navigation links, not proof a target is accessible. For a range, link its beginning and print the end time. Verify identity and the displayed position when inspecting a link.

Embed selected frames using paths relative to the note, so the note and its assets can move together. Captions identify creator/video, actual time, and what the image demonstrates. Crop only irrelevant surrounding browser/account UI; do not hide a relevant control, warning, or state. Open the actual saved image at a readable size before delivery. Check relevant controls and values survived cropping; a correct live browser view does not prove the saved crop is correct. If a value is supported only by narration, say so rather than calling it visible. Avoid unreadable thumbnail collections and decorative screenshot quotas. A linked video time remains useful when an image is unnecessary.

Label original frames, annotated source frames, and agent-created teaching diagrams distinctly. Preserve the underlying frame if annotated. Video/screenshot rights remain with their owners; the skill's MIT license does not relicense them. Keep substantial media, complete captions and private evidence outside the distribution source.

State unverified visual areas or illegibility. Text read, images inspected, and workflow executed are separate outcomes; this skill does not execute the creator's workflow.
