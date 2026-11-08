# Repository maintenance

This repository distributes VidTrail. Start at `.agents/skills/vidtrail/SKILL.md`; load only the references needed for the current task. Follow the consumer project's own rules and paths, not the maintainer's machine configuration.

- Candidate-only requests stop at candidates. Full-video distillation reads all available text and checks important visuals as needed. Acquisition does not establish understanding.
- Reuse by stable platform ID + part/cid + target. Retain attempts; do not repeat a failed route without a relevant documented change. Stop unnecessary acquisition once text is sufficient.
- Keep originals, media, credentials, actual user-material receipts, private notes and execution records outside distribution source. Optional tools, uploads, authentication, installs and costs need applicable authorization.
- Respect the user's destination and current project organization. Do not create a second knowledge base or imply permission to execute a video's procedures.
- After changes, run `python -m unittest discover -s tests`, validate skill format, and check references and installer behavior. Separate offline tests, existing-material replays, live platform tests and user acceptance.
- Preserve pre-existing modifications. Stage explicit intended files only; no automatic commits/pushes without user authorization. Scan the complete staged diff, including untracked additions, for private material and secrets.

Current verification and limits: [docs/VALIDATION.md](docs/VALIDATION.md). Method references: [ATTRIBUTION.md](ATTRIBUTION.md).
