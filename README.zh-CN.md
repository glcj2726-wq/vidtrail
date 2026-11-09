# 观迹 · VidTrail

[English](README.md)

**把视频变成能理解、能借鉴的知识。** 让 Agent 帮你找 B站和 YouTube 视频，读懂完整可用内容，整理成学习笔记或作者工作流。

可以只找候选，也可以提供链接或已有字幕。成果沿作者的例子讲清方法，保留来源定位和必要画面，方便回看与实践。

## 能得到什么

| 学习笔记 | 作者工作流 |
| --- | --- |
| 讲清问题、概念联系、为什么这样做和适用边界。 | 说明前提、输入、行动、步骤依赖、中间产物和人工判断。 |
| [查看中文示例](docs/examples/learning-note.zh-CN.md) · [English](docs/examples/learning-note.md) | [查看中文示例](docs/examples/creator-workflow.zh-CN.md) · [English](docs/examples/creator-workflow.md) |

![学习笔记的英文示例渲染](docs/assets/learning-note-preview.png)

![作者工作流的英文示例渲染](docs/assets/creator-workflow-preview.png)

配图是我们自己所写示例的实际渲染，不是原视频截图，也不代表执行过作者的方法。示例保留作者署名和视频时间链接。

## 开始使用

需要能加载 Agent Skills、读取文件的 Agent；安装程序和可选获取脚本使用 Python 3.10+。

```sh
git clone https://github.com/glcj2726-wq/vidtrail.git
cd vidtrail
python scripts/install_skill.py --project /你的项目绝对路径 --copy
```

在目标项目新开聊天，Codex 中可用 `$vidtrail` 调用。其他宿主的加载与调用方式以其实际支持为准；尚未验证所有 Agent 的自动识别。安装保留已有技能。提供已有字幕时，不需要先安装平台工具或登录账号。

> 用 $vidtrail 读这份字幕，沿作者的例子写中文学习笔记，讲清概念联系，保存到项目已有笔记目录。

> 用 $vidtrail 找几条搭建 Agent 工作流的教程，只比较候选，先不下载、不写笔记。

> 用 $vidtrail 整理这个视频的作者工作流，说明输入、依赖、中间结果、人工决策和缺失步骤。

在线获取前检查实际工具和已有授权。[配置说明](.agents/skills/vidtrail/references/setup.md)介绍固定依赖、环境检查、复制/链接安装与可选媒体工具。获取脚本负责拿材料，Agent负责阅读和解释；技能不自动安装或登录。

## 完整流程

**寻找或选定 → 复用材料 → 获取缺失正文 → 阅读全部可用内容 → 核对必要画面 → 写作并交付。**

- 只要候选就止于候选；完整蒸馏读取全部可用正文，材料不全则限定结论。
- 学习笔记说明“为什么”，工作流说明“如何衔接行动”；可以分别交付，也可同时交付，语言跟随用户要求。
- 先用已有图片或媒体，再查网页画面，必要且获授权时才下载。浏览器、Bili23、ffmpeg和转写工具由实际环境提供。
- 关键结论保留定位。看不清的参数、缺失的步骤不补造，也不自动执行视频里的操作。
- 沿用你指定的位置和项目组织，不强制新建知识库，不捆绑带学、夸克或Notion流程。

## 登录与能力边界

公开视频不一定都需要登录，也不保证匿名可抓取。账号、IP、限流和访问验证均可能影响结果。技能解释观察到的原因，不自动登录、导出浏览器Cookie、绕过验证或反复请求。只有403，不能断言登录过期。详见[平台路线与失败提醒](.agents/skills/vidtrail/references/platforms.md)。

离线测试、已有正文蒸馏、局部画面核查和真实下载分别报告。长视频试验中，本机已登录环境的B站媒体获取成功；YouTube媒体请求遇403，但正常浏览器能播放。这不代表匿名VPS或新机器同样成功。详见[当前验证](docs/RELEASE_CHECKS.md)。

## 更多与反馈

[完整技能](.agents/skills/vidtrail/SKILL.md) · [配置](.agents/skills/vidtrail/references/setup.md) · [验证结果](docs/RELEASE_CHECKS.md) · [方法来源](ATTRIBUTION.md)

反馈问题请说明预期、最小复现和检查结果，不附凭据、平台原始错误包或私人材料。修改代码后运行 `python -m unittest discover -s tests`。

原创代码、文档和示例渲染采用 [MIT](LICENSE)；外部工具和原视频保留各自条款。当前仍在私有仓库完成公开准备，实际公开另行决定。
