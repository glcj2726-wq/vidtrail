# Method references and provenance

VidTrail's ordinary distillation workflow is self-contained. It does not install, vendor, or execute the projects below. The current release expresses independently written workflow/writing guidance; none of their source code, models, original transcripts, private notes, or assets is bundled.

| Reference | Ideas used | Deliberate boundary |
| --- | --- | --- |
| [Paldom/video-to-skill · video-notes](https://github.com/Paldom/video-to-skill/blob/main/skills/video-notes/SKILL.md) | Genre-aware visual effort, readable evidence-linked notes, transcript provenance | No dependency on sibling skills, fixed output tree, overwrite rule, or image quota |
| [ResistanceDown/watch-and-learn · watch](https://github.com/ResistanceDown/watch-and-learn/blob/main/skills/watch/SKILL.md) and [evaluate-video](https://github.com/ResistanceDown/watch-and-learn/blob/main/skills/evaluate-video/SKILL.md) | Inputs, steps, dependencies, observable results, missing details; separate evidence types | No bundled reader, execution/build pipeline, or approval system |
| [Fabric · extract_instructions](https://github.com/danielmiessler/Fabric/blob/main/data/patterns/extract_instructions/system.md) | Lightweight extraction of procedural content from text | Text alone cannot verify visuals; no fixed output quota |
| [Aurum807/dsh-bilibili-video-summary](https://github.com/Aurum807/dsh-bilibili-video-summary) | Coarse visual orientation followed by targeted frame inspection | No bundled plugin, mandatory full-media download, or dense sampling |
| [Cangjie](https://github.com/kangarooking/cangjie-skill) | Early full-content understanding, method extraction and evidence discipline | No runtime dependency, skill compiler, artifact tree, multi-agent workflow, or quantity threshold |
| Maintainer's local learning-writing practice | Connected examples, nearby explanations of terms, transitions and explicit limits | No private learning notes, personal paths, tutoring engine or learning-state records |

The Paldom, Watch and Learn, Fabric and Cangjie repository LICENSE files were read on 2026-11-08 and identify MIT terms. Their own licenses remain authoritative for their content. No license conclusion is assumed for another project merely because it is publicly readable; the DSH reference is an idea/source link only. Any future copied code/assets require their own provenance and license review.

The bili and yt-dlp tools are external dependencies, installed separately under their respective terms; Quark, Bili23, browser integrations and source videos are not relicensed by this repository. Source claims and video quotations retain their original attribution. Real source materials used for local validation are not distributed.

Original VidTrail source and documentation are covered by the root [MIT license](LICENSE). This release retains the repository's history; the previous project name was coco-video-research-distill.
