# VidTrail · 观迹

[中文](README.zh-CN.md)

**Turn videos into understanding you can use.** An Agent Skill for finding Bilibili and YouTube videos, reading their available full content, and distilling learning notes or a creator’s workflow.

Ask for candidates, bring a video link, or start from a transcript you already have. Your agent follows the material through to a readable explanation, with source times and relevant visuals—not just a list of timestamps.

## What you get

| Learning note | Creator workflow |
| --- | --- |
| Understand the problem, concepts, connections and limits through the creator’s example. | Follow prerequisites, inputs, actions, dependencies, outputs and human decisions. |
| [Read the example](docs/examples/learning-note.md) · [中文](docs/examples/learning-note.zh-CN.md) | [Read the example](docs/examples/creator-workflow.md) · [中文](docs/examples/creator-workflow.zh-CN.md) |

### Learning note: why the method works

![Rendered learning-note excerpt](docs/assets/learning-note-preview.png)

### Creator workflow: what each stage hands to the next

![Rendered creator-workflow excerpt](docs/assets/creator-workflow-preview.png)

These previews render VidTrail’s own written examples; they are not video frames or proof that the creator’s workflow was executed. Examples link to the original creators and source times.

## Quick start

Use an agent that can load Agent Skills and read files. Python 3.10+ runs the installer and optional acquisition helper.

```sh
git clone https://github.com/glcj2726-wq/vidtrail.git
cd vidtrail
python scripts/install_skill.py --project /absolute/path/to/your-project --copy
```

Open a new agent chat in that project and invoke `$vidtrail` in Codex. Other hosts may use a different invocation/discovery convention; automatic loading across hosts has not been verified. Existing skills are preserved. No platform tools or accounts are required to work from a supplied transcript.

> Use $vidtrail with this transcript. Explain the method through the creator’s example, in Chinese. Save the learning note in this project’s existing notes folder.

> Use $vidtrail to find tutorials about building an agent workflow. Compare candidates only; stop before downloading or writing notes.

> Use $vidtrail with this video link. Explain the creator’s workflow: inputs, dependencies, outputs, decisions and missing details.

For live acquisition, first check available tools and authorized access. [Setup](.agents/skills/vidtrail/references/setup.md) covers pinned dependencies, the doctor, copy/link installs and optional media tools. The helper retrieves materials; the agent reads and explains them. Installation and authentication are deliberate actions, never automatic prerequisites imposed by the skill.

## How it works

**Find or select → reuse materials → obtain missing content → read the full available text → inspect necessary visuals → write and deliver.**

- Candidate-only requests stop at candidates. Full-video distillation reads all available text and states incomplete coverage.
- Learning notes explain why; workflows explain how. Ask for either or both, in your preferred language.
- Use existing images/media first, then source-page views; download only when needed and authorized. Browser control, Bili23, ffmpeg and transcription are host-provided capabilities, not bundled services.
- Keep conclusions traceable. Unreadable parameters and missing steps stay explicit; the skill does not execute procedures found in a video.
- Save into your chosen location and existing project organization. No fixed knowledge base, tutoring system, Quark or Notion account is required.

## Access and limits

Some public videos work without login; others encounter account, IP, rate-limit or verification restrictions. VidTrail explains the observed failure and does not automatically log in, export browser cookies, bypass challenges or repeat failed requests. A bare 403 does not prove an expired session. See [platform routes and failure guidance](.agents/skills/vidtrail/references/platforms.md).

Offline regressions, existing-transcript distillation, selected visual checks and live downloads are different results. Local authenticated Bilibili media retrieval succeeded in the long-video trial; the YouTube media attempt returned 403, while normal browser playback worked. These are observations in the tested environment, not promises of anonymous or fresh-machine success. See [current checks](docs/RELEASE_CHECKS.md).

## More

[Full skill](.agents/skills/vidtrail/SKILL.md) · [Setup](.agents/skills/vidtrail/references/setup.md) · [Verification](docs/RELEASE_CHECKS.md) · [Method sources](ATTRIBUTION.md)

To contribute, describe the expected behavior, a minimal reproducible case and the checks you ran; do not attach credentials, raw platform responses or private source materials. Run `python -m unittest discover -s tests` before proposing code changes.

VidTrail’s original code, documentation and rendered examples use the [MIT license](LICENSE). External tools and source videos retain their own terms. The repository remains private during final release preparation; visibility changes are a separate maintainer decision.
