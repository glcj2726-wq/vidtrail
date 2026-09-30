# coco-video-research-distill

给 Codex CLI 的可移植视频调研与蒸馏技能。输入 B站 / YouTube 链接、主题或已有文稿，取得正文、核验证据、围绕当前问题提炼可理解可照做的笔记，再接入使用者的知识库。

本仓库保存技能和工具辅助脚本；知识正文与原件由目标知识库保存。没有任何作者电脑路径、账号凭据、课程原件或特定自动任务授权。当前为私有仓库，发布公开版本须另行确认。

## 远端开始使用

```sh
gh repo clone glcj2726-wq/coco-video-research-distill
cd coco-video-research-distill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/doctor.py
```

Windows 使用 `py -m venv .venv`、`.venv\Scripts\Activate.ps1`。Python 需要 3.10+。完整 YouTube 支持还需 Node 22+；视频合并需系统安装 ffmpeg。脚本不会自动安装系统软件、登录或启用收费服务。

在本仓库启动 Codex，会发现 `.agents/skills/coco-video-research-distill`。在知识库里使用时，把技能安装到那个仓库：

```sh
python scripts/install_skill.py --project /absolute/path/to/your-knowledge-repo
```

安装使用指向本仓库的符号链接，`git pull --ff-only` 更新本仓库后技能随之更新；已有同名技能时停止，不覆盖。也可以用 `--skills-dir` 指定自己的 Codex 技能目录。重启/新开 Codex 任务，查看 `/skills` 并显式调用 `$coco-video-research-distill`。仓库内技能发现路径依据 [Codex 官方文档](https://learn.chatgpt.com/docs/build-skills)。

把这段话交给远端 Codex：

> 读取本仓库 AGENTS.md、README.md 和视频技能。先执行 doctor 检查实际工具；按目标知识库规则配置原件、临时视频和笔记位置。处理我给的 B站/YouTube 链接，查重后获取全文，核对来源与覆盖范围，再蒸馏并更新现有知识库；不能仅看标题/简介。缺工具或字幕时报告具体缺口，复用已有尝试，不反复重跑。安装命令不等于平台实测通过。

## 获取示例

在虚拟环境已激活的 shell 中运行，数据位置由使用者指定，不能是本仓库内部：

```sh
python .agents/skills/coco-video-research-distill/scripts/acquire.py --route bili --url https://www.bilibili.com/video/BV1CMMh62EVA/ --mode subtitles --data-root /absolute/path/to/materials
python .agents/skills/coco-video-research-distill/scripts/acquire.py --route yt-dlp --url 'https://www.youtube.com/watch?v=3UgXWMQtB8E' --mode subtitles --data-root /absolute/path/to/materials
# 明确需要下载视频时使用 media；完整高清需要 ffmpeg 与平台账号权限。
python .agents/skills/coco-video-research-distill/scripts/acquire.py --route yt-dlp --url 'https://www.youtube.com/watch?v=3UgXWMQtB8E' --mode media --data-root /absolute/path/to/materials
```

脚本只做一次获取并登记原件、哈希和结果；`acquired` 表示文件取得，正文仍须由 Agent 核验后才能记 `ready`。脚本不会生成总结、上传、删除、提交 Git 或自动切换工具。路线由技能明确选择。

## 能力与限制

- B站：`bili search` 发现；`bili video` 取第一分集字幕；其他分集须核对 cid/分集，不能把首集字幕当成目标集。Bili23 MCP 可用时复用一个任务；无 MCP 的服务器可用 yt-dlp 一次下载媒体，须明确这是服务器替代路线。
- YouTube：yt-dlp 一次失败转已连接 Chrome；浏览器插件确实暴露接口时才调用 `exportYouTubeTranscript()`。Chrome 不可用时内置浏览器试一次。无浏览器工具的 CLI 不具有桌面插件能力。
- 登录：GitHub 登录只用于克隆。本地凭据可经用户授权用 SSH 单独配置到服务器，具体位置见平台参考；Cookie 在另一网络环境可能失效，不能保证永远免登录。
- 缺全文：只交付已核实范围；按用户已有授权选择转写或云端处理，不自动开启付费转写/夸克。私人课堂平台与特定定时任务授权不随技能移植。

验证记录见 [docs/VALIDATION.md](docs/VALIDATION.md)。

## 完整工作流入口

首次配置读 [远端配置](.agents/skills/coco-video-research-distill/references/setup.md)，每次任务读 [流程与续接](.agents/skills/coco-video-research-distill/references/workflow.md)，平台选择读 [获取路线](.agents/skills/coco-video-research-distill/references/platforms.md)。只加载当前分支，不全量读所有参考。

```text
给链接/主题 → 选定视频身份与分集 → 知识库/云端记录查重
  ├─ 已有完整正文 → 核验 → 全文理解与按需画面 → 笔记与来源登记
  └─ 没有正文 → 平台字幕 → 实际可用浏览器正文
       ├─ 正文取得 → 核验后蒸馏
       └─ 没有正文 → 获取/复用视频
            ├─ 已配置本地转写 → 全文与时间码 → 核验后蒸馏
            ├─ 已授权夸克 → 上传验收 → 等待处理/人工导出
            │                → ID精确取回文稿 → 核验后蒸馏
            └─ 缺工具/材料/授权 → 保留当前状态与最少补充步骤
```

平台具体顺序以 platforms 为准：Bili23 的字幕任务可能先取得媒体；浏览器没有工具则跳过记录。每路线一次，不循环；不同目标（字幕/媒体）分别登记。成功就停止不必要的获取。用户只要下载时只验收视频，不强制全文蒸馏。

- 无字幕与画面核验：[转写和画面](.agents/skills/coco-video-research-distill/references/transcription-visual.md)。不捆绑模型，不默认付费；无字幕不能拿简介代替。
- 夸克完整操作：[上传、处理与精确取回](.agents/skills/coco-video-research-distill/references/quark.md)。提供官方安装源、会话参数、上传验收、断点续接与导出检索。summary/qa 与完整文稿导出分开，自动导出未验证，人工导出节点保留。
- 单一来源记录：[字段模板](.agents/skills/coco-video-research-distill/templates/source-record.example.json)。映射目标库已有清单，不新建第二套总账；媒体、Cookie、实际材料回执不进分发仓库。

当前只实现 B站/YouTube 工作流与单路线获取辅助。Bili23、浏览器、夸克、ASR是可选外部能力，需要执行端配置和验收；文档完整不等于这些服务已在服务器跑通。不包含私人课堂平台自动化。
