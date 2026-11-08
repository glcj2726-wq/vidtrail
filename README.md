# VidTrail · 观迹

[中文说明](README.zh-CN.md)

An Agent Skill for finding relevant Bilibili and YouTube videos, understanding their available full content, and turning it into readable learning notes or a faithful explanation of the creator's workflow.

**v0.1.0 preview — private development repository.** The portable workflow has offline checks and existing-material replays; authenticated platform access and optional integrations depend on the execution environment. Final independent release review remains pending.

## What it does

- Discover and compare videos for a task, or work directly from a link/transcript. Candidate-only requests stop after candidates.
- Reuse existing materials before acquisition. Read all available text for full-video distillation; inspect relevant visuals for exact code, settings and demonstrated results.
- Write coherent learning notes explaining a problem through the creator's example, or preserve workflow inputs, dependencies, actions, intermediate outputs, checks and gaps.
- Trace conclusions to source evidence, distinguish claims/observations/inference, and label incomplete results.
- Deliver where the user or current project chooses. Reply in the requested language, otherwise the conversation language. English skill instructions support Chinese outputs.

It explains the creator's procedure; execution, deployment and installation of that procedure are separate tasks. No fixed knowledge-base structure, private classroom flow, bundled tutoring skill, mandatory Quark/Notion service, or automatic paid transcription.

## Get started

Python 3.10+ is required. Clone into a location you choose:

```sh
git clone https://github.com/glcj2726-wq/vidtrail.git
cd vidtrail
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/doctor.py
python scripts/install_skill.py --project /absolute/path/to/your-project
```

Windows: `py -m venv .venv`, then `.venv\Scripts\Activate.ps1`. Installs need your authorization and network access; the commands above are instructions, not actions the skill runs automatically. The doctor checks command presence/version, not accounts or platform reachability. yt-dlp JS support follows its current [EJS requirements](https://github.com/yt-dlp/yt-dlp/wiki/EJS); media merging/extraction needs ffmpeg/ffprobe.

The installer links `.agents/skills/vidtrail` into the chosen project's `.agents/skills`; `--skills-dir` selects an explicit skill directory. `--copy` makes a standalone copy instead of a symlink. Existing destinations are preserved. On Windows without symlink privileges (WinError 1314), rerun with `--copy`; elevation or system configuration changes are unnecessary. Updating a linked checkout updates the link; copies need deliberate replacement. Restart/open a new Codex task as needed and explicitly invoke `$vidtrail`. Host discovery beyond the tested packaging is environment-dependent.

## Example requests

> Use $vidtrail to find a few practical tutorials about building an agent workflow. Compare candidates only; do not download or distill them yet.

> Use $vidtrail with this video link. Explain the creator's workflow, including inputs, dependencies, intermediate outputs and missing details. Save it in this project's existing notes location.

> 用 $vidtrail 阅读这份已有字幕，写成中文学习笔记。沿用作者的例子，讲清概念之间的联系，注明哪些画面还没核对。

## Acquisition helper

Use a material directory **outside this repository**. Only run a route that is appropriate and authorized:

```sh
python .agents/skills/vidtrail/scripts/acquire.py --route bili --url 'https://www.bilibili.com/video/BV1CMMh62EVA/' --mode subtitles --data-root /absolute/path/to/materials
python .agents/skills/vidtrail/scripts/acquire.py --route yt-dlp --url 'https://www.youtube.com/watch?v=3UgXWMQtB8E' --mode subtitles --data-root /absolute/path/to/materials
```

These are invocation examples, not claims those sources were fetched in this release. The helper makes one acquisition attempt and retains receipts/hashes; it does not generate notes, provide ASR, control a browser, upload, or implement the creator's workflow. `acquired` means files obtained, not text verified. Exit codes: 0 acquired; 1 pre-acquisition stop; 2 failed/unavailable/invalidated; 3 partial. Hash-valid partial subtitles can be reused without another platform call. See [Platforms](.agents/skills/vidtrail/references/platforms.md).

## Boundaries and verification

Bilibili CLI subtitles support only part 1 in the pinned baseline; never substitute it for another part. Stock bili search lacks the maintainer's enhanced sorting/date/duration patch. Browser control, Bili23, platform credentials and transcription are host-provided optional capabilities. Cookies may fail after expiry or a network change. GitHub login is unrelated to platform login.

Quark and Notion are optional. No transcription engine/model is bundled. With unavailable text or important visuals, deliver a limited result and name the gap rather than inventing steps. No universal claim of fresh-machine or anonymous VPS platform success is made.

See [verification](docs/VALIDATION.md), [method attribution](ATTRIBUTION.md), and [the full skill](.agents/skills/vidtrail/SKILL.md). Source and documentation are MIT licensed; linked projects and source videos retain their own terms. Final public-release review is a separate next step.
