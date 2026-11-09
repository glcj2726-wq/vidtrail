> **Historical log — not current verification.** The current checks, test counts and limits are in [RELEASE_CHECKS.md](RELEASE_CHECKS.md). The entries below, mostly in Chinese and dated 2026-10-01 to 2026-11-08, are kept unchanged as history. Their test counts, knowledge-base registration step and Tongji workflow do not describe the current skill. New evidence is appended at the end.

# 验证与实际能力

发布准备：2026-10-01。维护源是本仓库中的可移植技能，已有私人本地技能保留，不自动覆盖。

## 本轮验证范围

验证结果：5 项离线测试全部通过，Skill 格式、内部链接和 Python 语法检查通过。本机 doctor 已确认工具版本；服务器实际可用性未验证。

- 离线测试：稳定视频身份与分集、单次失败复用、禁止以简介当字幕、原件哈希变化后的停止、安装不覆盖已有技能。
- Skill 格式与内部引用、脚本语法、仓库文件无个人绝对路径或凭据。
- 工具依据：源环境 bili 0.6.2 的 help 与结构化字幕字段，yt-dlp help 的重试参数；安装目录依据 Codex 官方文档。

离线检查不证明远端已经安装、不证明登录有效、不证明 YouTube/B站当前网络能访问。不能将 acquired 状态作为全文已核验。

## 继承的获取经验

已有工作流中 B站取得过平台字幕；YouTube 在 yt-dlp 下遇到登录验证。Chrome 工具暴露字幕导出接口，但此前连接失败，接口的目标视频完整导出未验证。这些是路线设计依据，不是本仓库远端平台验收。

## 服务器验收步骤

1. 新任务 `/skills` 能发现并显式调用技能；doctor 确认工具、Node与ffmpeg，记录版本和实际可用的 MCP/浏览器。
2. 用户给一条 B站视频：核对 ID/分集，取得完整字幕；若明确要媒体，核对规格、时长和文件哈希。不得将 P1 字幕作为 P2 正文。
3. 用户给一条 YouTube 视频：一次命令后按实情回退；没有远端浏览器就登记缺口，不循环试参数。成功时核对文稿起止、语言、覆盖及时间码。
4. 用全文交付一篇与实际问题有关的笔记，抽查关键结论定位；再用同一来源的另一问题验证复用，不能重复下载。
5. 按目标知识库规则登记来源、草稿与回链。用户授权后再提交/推送；凭据与视频不加入 Git。

服务器登录态配置和两平台实时验收尚待目标环境执行。

## 完整流程补充（2026-10-01）

新增 setup、workflow、quark、transcription-visual参考和来源字段模板；平台参考与入口接上下载失败、无字幕转写、夸克等待/人工导出/精确取回、恢复和知识库登记。私人课堂自动化不纳入。官方夸克安装源与本次可见官方 Skill 1.0.22 的上传/检索/助手文档核对；当前文档没有充分下载参数，因此要求执行端核对 download help，未猜命令。

Bili23官方页面本轮抓取超时；连接指导保留已知默认地址，实际 schema/目标主机部署仍待核验。yt-dlp官方说明可访问。未安装或更新官方夸克技能、未上传、未重新获取视频、未运行转写或浏览器，也没有平台端到端成功声明。

场景核对：字幕齐全直接蒸馏；无字幕有媒体接转写/授权夸克；无媒体尝试独立下载目标/正常来源网页；已上传续接任务；已导出取回文稿而非summary；缺授权/工具标待补；同源新问题不重复获取。所有分支在 workflow 有下一动作与完成证据。

补充后验证结果：5项离线测试通过，Skill格式、Markdown内部链接、Python/JSON语法和个人本机路径检查通过。doctor新增 ffprobe，已在维护端确认版本；未将维护端能力算作远端能力。无凭据或实际用户材料加入本次文件。

## 同济流程补充（2026-10-02）

用户本轮明确纳入同济，替代上一轮“同济不纳入”的范围约定；旧记录保留为历史。新增tongji参考及技能、README、平台、完整流程和配置入口。流程为Agent下载与上传、用户生成并导出、Agent精确取回并蒸馏。仓颉方法用于普通内容蒸馏，Skill编译仍需指定来源的明确Skill化需求。

命令示例对照维护端实际Tongji脚本参数定义；list-replays只读已缓存会话，download-video可能认证回退，未把no-workspace-prompt误写为no-login。不捆绑脚本、不宣称上游同名工具或目标服务器一定支持，不继承本机自动任务与删除例外。本轮未登录、下载、上传录课或制作课程笔记；只更新分发流程文档。

本轮检查：5项既有测试通过，Skill格式验证、Markdown内部链接、JSON模板和个人本机路径扫描通过。同济路线为流程文档核对，不等于服务器端到端实测通过。

## 获取修复（2026-11-06）

修改 acquire.py：读取 bilibili-cli 0.6.2 真实信封 `data.subtitle`，保留无信封的顶层 `subtitle` 旧响应；缺失、null 或畸形的 payload/data/subtitle 不再崩溃，回执记录 `diagnostic`。数据目录边界改为：源码检出（含其中的 `scripts/install_skill.py` 指向本技能）排除整个仓库；复制安装只排除技能目录本身，不排除家目录或目标知识库；符号链接安装解析回源码检出。yt-dlp 字幕参数只在 subtitles 模式出现，media 模式不再请求字幕。

字幕模式命令失败（非零退出或超时）但已有非空字幕文件时记 `partial`：保留文件与哈希，写入 `usable_files` 和 `failure`，`content_verification` 仍为 `not_performed`。partial 不是 acquired，也不代表正文已核验。media 模式非零退出仍记 failed，因为此时的 mp4 可能只是未合并的单路流。

CLI 退出码有一处窄幅变更：partial 从 2 改为新增的 3；0（acquired）、1（获取前停止）、2（failed/unavailable/invalidated）含义不变，`--help` 已列出。复用规则：partial 且哈希一致时直接复用、不运行工具、退出 3；哈希变化记 invalidated、退出 2；只有显式 `--retry-reason` 才再运行一次，没有自动重试；重试后的回执用 `prior_partial` 保留原文件和哈希。

本轮验证结果：`python -m unittest discover -s tests` 36 项全部通过（既有 5 项 + 新增 31 项）。同一新测试在修改前的 acquire.py 上有 21 项不通过。真实信封结构另用已安装 bili 0.6.2 的 payloads/formatter 函数离线生成核对；yt-dlp 2026.08.19 的 `parse_options` 离线解析两种模式的命令。平台工具在测试中均为临时存根，本轮未登录、未联网获取、未下载视频、未安装依赖；B站/YouTube 真实平台端到端仍未验证，服务器运行未验证。修改前写下的 failed 回执不会自动重新分类，需用 `--retry-reason` 记明解析已修复后再试一次。

## 学习与工作流蒸馏重定位（2026-11-08）

本轮只改分发技能的 Markdown 文档，范围改为：发现 B站/YouTube 视频、复用已有材料、读完可得全文、按需核对画面，产出学习笔记或作者工作流说明；只要候选时交付候选即止。脚本、测试、依赖、模板和 quark 参考未改。

- 新增 `references/search.md`：多方向搜索与候选交付。按 requirements 固定版本的实际 help 写明 `bili search` 0.6.2 只有 `--type/--page/--max/--json/--yaml`；排序、日期、时长等筛选来自未合入本仓库的本地补丁，标为不可假定存在。
- `distillation.md` 增加五类证据标注（来源主张、画面所见、推断、外部佐证、实际执行）、作者工作流说明结构和方法来源；`teaching.md` 改为学习笔记写法；`transcription-visual.md` 把转写写成在已授权方式中选择，夸克为可选项之一；`storage.md`/`setup.md` 改为交付到用户指定位置，不要求新建知识库、总账或固定目录；Notion 只作为可选交付接口。
- 移除分发技能的 `references/tongji.md` 及 README、SKILL、platforms、workflow、storage、setup 中的同济流程。上文 2026-10-02 的同济记录是历史证据，保留不改，不再代表当前分发范围。
- 普通蒸馏自包含，不需要仓颉或其他学习技能；参考来源在 distillation.md 注明出处与取舍，未安装或打包这些项目。

本轮验证：`python -m unittest discover -s tests -v` 36 项全部通过；Markdown 相对链接与锚点、Skill 前置信息、旧流程与个人路径扫描通过。另用标注为合成的示例演示了学习笔记、作者工作流、只要候选和材料不足四种行为（见本轮交付的 validation.md），这些是文档写法示范，不是独立模型评测，也不是平台实测。本轮未联网、未调用视频平台、未安装、未登录、未转写、未上传。

遗留：`templates/source-record.example.json` 仍含 `tongji` 平台占位与 `course_id`/`sub_id` 字段，不在本轮可改范围内；workflow 已说明公开平台视频留空即可。B站/YouTube 真实平台端到端与服务器运行仍未验证。

## 学习与工作流蒸馏重定位：校正（2026-11-08）

同一授权范围内的复核校正，仍只改允许的 Markdown。

- `platforms.md` B站顺序改为：复用已有正文 → 一次 CLI 字幕 → 执行端实际可用的浏览器字幕/文字稿（按执行端配置顺序）→ 仅当正文仍不可得且确需媒体时选一条媒体路线（Bili23 MCP 或 yt-dlp media）并转已授权转写。CLI 认证失败本身不触发下载视频。只要视频的请求、分集身份、每路线一次和能力如实说明保留。YouTube 段去掉 Chrome 示例，改为按执行端配置顺序；README 的 B站说明同步。
- `transcription-visual.md`：ffprobe 只说明容器与流元数据可读（时长、分辨率、音轨），不证明整段媒体可完整解码或播放；完整解码/播放是另一项需授权的检查。元数据可读、媒体可播放、正文已核读分别登记。
- 交付 validation.md 中三个作者编写的合成示例已修正（链表推断收窄、候选示例补占位链接/平台/分集并去掉计数矛盾）；它们仍是合成示例，不是独立模型评测或平台实测。

校正后验证：`python -m unittest discover -s tests -v` 运行一次，36 项通过；以原始基线重放新补丁并比对整个源码树，Markdown 链接/锚点与范围扫描通过。未联网、未调用平台、未安装、未改脚本/测试/模板。模板中的 `tongji`/`course_id`/`sub_id` 占位仍为范围外遗留。


## VidTrail private v0.1.0 preview (2026-11-08)

The distribution is renamed to vidtrail. Skill instructions and runtime references are maintained in English, with English and Chinese repository introductions. Prior entries above are historical; their former platform scope and unresolved template placeholders are superseded by the current skill and template. The acquisition helper and dependency pins retain the previously accepted baseline. Current tests, existing-material replays, installer checks, limitations and the public-release review gap are recorded in [RELEASE_CHECKS.md](RELEASE_CHECKS.md). No new video-platform requests, authentication, ASR, cloud uploads or source-derived workflow execution were authorized for this batch.

## Privacy and path repair (2026-11-08 UTC, uncommitted patch on 997dda9)

Appended record; the historical text above is unchanged. The helper now passes `--no-write-info-json` in both yt-dlp modes, validates an explicit cookie path before creating any directory, leaves older `.info.json` files in place while listing them under `sensitive_metadata_retained` instead of `files`, and checks that every existing level below the data root and an existing `receipt.json` stay inside the chosen root and outside the source checkout or installed skill. Offline results: 59 tests passed with pinned yt-dlp 2026.8.19 (59 passed with 3 skipped without it). The new privacy/path tests fail on the base helper as intended, including real yt-dlp writing a per-run synthetic cookie into `.info.json`. No live platform request, authentication, real credential or visual review was involved. Details and limits: [RELEASE_CHECKS.md](RELEASE_CHECKS.md).

## Coordinator verification addendum — 2026-11-09

The collected repair was independently checked in a separate Linux copy: 59 tests passed with zero skips in the pinned yt-dlp 2026.8.19 environment, and a separate prewritten 15-case behavioral oracle passed in full (the same oracle fails 14 cases on the old helper). On the old helper, the 23 new regression methods have 18 failing methods and 5 passing controls. Windows rerun: 59 total, 5 passed and 54 skipped. The system-Python result above is 59 total: 56 passed and 3 skipped, not 59 passes plus skips. These are offline/synthetic checks; no fresh platform access, real credentials, visual review or source-workflow execution. See [current release checks](RELEASE_CHECKS.md).

## Readability, failure guidance and visual candidate — 2026-11-09

New local candidate on `4738262`, not committed, pushed or public. Optional failure classifications preserve legacy reasons/status/exit codes and partial reuse. Natural notes and creator workflows have separate purposes; source-time links, selected screenshots and necessary existing media routes are documented. Windows: 78 total, 24 passed, 54 skipped. Existing WSL Ubuntu: 78 total, 75 passed, 3 pinned-library fixtures skipped because yt-dlp is absent there; no dependencies installed. Skill-format validation passed. Real authenticated media tests used one Bilibili and one YouTube target: Bilibili succeeded; YouTube HTTP 403 with no media, no automatic retry or expiry claim. Existing full captions were reused without subtitle calls; selected Bilibili and YouTube visuals informed four Chinese artifacts held outside the distribution. Full audiovisual coverage, anonymous success, creator-method execution and final release approval are not established. The complete preceding history is preserved. See [current release checks](RELEASE_CHECKS.md).


## 2026-11-09 — final review corrections and private release preparation

CoCo integrated the reviewed candidate on 4738262, tightened failure classification, accepted the pinned yt-dlp requested-caption stdout diagnostic, and stopped retaining failed/malformed bili envelopes as content. CLI/exit codes, legacy status/reasons, old receipts, partial reuse and path guards remain compatible. Existing Linux pinned environment: 83 passed, zero skipped; Windows: 29 passed and 54 POSIX cases skipped out of 83. No dependencies were installed. A real pinned-library offline fixture verifies the stdout channel; inputs and cookies in regressions are synthetic.

Four local Chinese outputs were corrected against retained text, including note creation before content insertion. Two normal-browser settings frames were recaptured and the saved JPEGs inspected. No new caption or media acquisition, login, full audiovisual review or execution of a creator workflow occurred. English/Chinese READMEs and bilingual public excerpts now link two rendered previews of original VidTrail writing; original video frames and private materials remain outside the distribution. Skill format, temporary installation/conflict preservation, relative links and source-time links passed. Bounded proposed-tree/history checks found no common token/private-key patterns or maintainer-specific paths. See RELEASE_CHECKS.md for the current result and limits; earlier sections remain historical. The repository remains private and public visibility requires a separate decision.


## 2026-11-10 — README and bilingual example presentation

Documentation/assets only, based on private commit 93339fc. The selected paper-cut banner is reused without a new character/style generation. Both homepages now show a request, an actual browser-rendered example excerpt and its full document link for learning notes and creator workflows. Each example contains an original source-attributed explanatory diagram; English and Chinese homepages use their own language screenshots. Original video frames, complete captions, credentials and private reports remain outside the distribution.

The two homepages were checked at 1440×1080 and 390×844; all three images on each page loaded without horizontal page overflow. All four examples also passed narrow-screen layout checks. Clicking a screenshot opened its original-size image, and the full-example link opened the rendered Markdown. Saved PNGs were reopened; a long English workflow label was shortened before final capture. This is local browser rendering, not a claim of GitHub UI or additional platform testing. Chinese prose was revised with human-writing and humanizer-zh; the writing checker found no hard-rule violations, with a sentence-rhythm advisory reviewed manually.

Acquisition code, skill instructions, dependency pins and tests are unchanged. The prior Linux 83-pass/no-skip and Windows 29-pass/54-skip results remain inherited evidence, not rerun results for this documentation update. Link/source-time, image/crop, allowed-file and privacy checks are recorded in the owning private task. The repository remains private; no platform acquisition, dependency install, login or public-release action is part of this update.


## 2026-11-10 - pre-publication source and history review

The maintainer authorized public visibility after a final check. On e787d37, all 42 current files, 8 commits and 109 reachable blobs were reviewed for common credentials, private keys, personal paths/contact details and sensitive repository surfaces. No blocking finding remained. Git identities use GitHub noreply addresses; historical images match previously inspected original/rendered assets. The only branch is main; there are no tags, releases, issues/PRs/comments, Actions runs/artifacts or deployments, with wiki/Pages/discussions disabled. Historical classroom documentation contains generic procedures/placeholders, not course materials or account data, and is absent from the current skill.

Only current README visibility wording and release records changed; all program, dependency, test and installed-skill hashes are preserved. Earlier 83-test Linux evidence is reused, not rerun. No new platform acquisition, login, installation or publication of source video frames is implied. GitHub visibility and the exact final commit are checked through real receipts outside distribution source after the change. Previous validation entries remain byte-for-byte intact.
