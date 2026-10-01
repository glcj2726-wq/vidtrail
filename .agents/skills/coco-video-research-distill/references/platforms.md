# 获取与回退

同济授权录课有单独的 [tongji.md](tongji.md)：下载视频与可选课件、上传夸克、用户生成/导出、取回蒸馏。下面的字幕优先顺序仅用于B站/YouTube。

先运行仓库 doctor 核对程序，检查实际 CLI help/MCP schema。已读同版本说明复用。B站/YouTube 同一 ID+分集+目标每条路线只试一次；失败证据可续接，不因换格式、换线程重跑。工具、登录或来源内容实际变化后，记录变化原因才再试。已有正文足够时停止获取。

## B站

1. 主题请求 `bili search "主题" --type video --max 5 --yaml`；链接不再搜索。对第一分集用 `bili video BV_ID --subtitle-timeline --subtitle-format srt --json` 一次，检查 `subtitle.available`、`subtitle.text/items` 与目标分集。该版本 CLI 取字幕默认首集，P2 等不能借 P1 正文交付。
2. 实际有 Bili23 MCP 时解析一次、创建一个带字幕的下载任务，保留任务 ID，查终态与字幕文件；解析成功不等于有字幕。现有路线没有独立字幕下载，不在缺字幕时自动 ASR。轮询原任务不重复建任务；长时间无进展保留状态结束本轮等待。
3. 服务器没有 Bili23 时不假装可用：明确记录 skipped/unavailable；用户要求媒体或确需获取时，可用 yt-dlp 服务器替代路线一次，URL 保持 `?p=N`，用 `--playlist-items N` 选择分集并核对 metadata 的 cid。默认最高可用且不超过 1080P，账号/来源不足时记录实际规格，不宣称 1080P。
4. 获取仍失败用实际连通 Chrome 的正常页面字幕；Chrome 连接不可用时内置浏览器只试一次。没有浏览器工具的远端 CLI 记录不可用，不下载或安装新浏览器来冒充原登录态。

字幕路线耗尽但需要完整蒸馏时，不止于“无字幕”：已有 Bili23 视频直接复用；还无媒体且未运行该媒体目标时用服务器 yt-dlp media 一次。媒体也失败才从来源页面正常下载入口取媒体，不能靠保存网页替代 MP4；无入口则记录获取缺口。取得视频且无字幕转 [transcription-visual.md](transcription-visual.md)，按具体授权转写或夸克。用户只要下载时直接选择媒体目标，不强制先取字幕。查 metadata 的分集/cid、时长与实际 ffprobe规格，不能凭 BV相同把首集当目标分集。

本仓库 `acquire.py --route bili` 仅首集字幕；多分集用实际可选分集路线。`--route yt-dlp --mode media` 可用于服务器媒体替代路线。Bili23 服务不是随仓库分发的服务器程序。

## YouTube

候选发现可用 `yt-dlp --flat-playlist --dump-single-json --skip-download "ytsearch5:主题"`。选定视频后获取目标内容一次；字幕用 `--write-subs --write-auto-subs --sub-langs "zh.*,en.*" --skip-download`；显式 `--retries 0 --extractor-retries 0`。Node 22+ 与 yt-dlp-ejs 供 JS 验证使用，存在不证明平台一定放行。

登录验证、风控或空正文后直接转已连通 Chrome。插件实际暴露接口时，在同一 watch 页尝试 `tab.content.exportYouTubeTranscript()`，核对 ID、语言、正文起止、时间码；未暴露则按正常文字稿面板读取，不猜 API。Chrome 连接不可用时内置浏览器只试一次；页面明确没有字幕时记录材料不足。桌面插件不会通过克隆仓库出现在服务器。

需要视频时显式选择 media，默认最高可用不超过1080P，ffmpeg 用于视频音频合并。取得文件、字幕就绪、全文已读、画面已核验分别登记。

字幕失败不代表媒体下载一定失败，也不证明媒体一定可下；确需媒体时同 ID 的 media 目标可尝试一次，已有媒体失败证据则复用。浏览器只按正常页面功能读取正文/关键画面或下载入口，不猜内部接口、不绕验证。有媒体无字幕接转写/夸克；没媒体且平台拒绝访问时保留缺口，不能声称上传夸克能解决来源下载限制。

## 凭据

不提交 Cookie/令牌，不打印凭据，不从其他任务取得授权。用户明确允许复用时，通过 SSH/私有秘密配置渠道传到仓库外，权限仅当前用户；不携带整个浏览器 profile。

`bilibili-cli 0.6.2` 使用 `~/.bilibili-cli/credential.json`（配置路径，非用户个人路径）。既有同版本文件可按授权安全配置；文件格式依据实际 CLI，不把 YouTube Netscape cookies.txt 当成它的凭据。YouTube 可显式向 yt-dlp 提供仓库外的 Netscape Cookie 文件；脚本 `--cookies-file` 仅用于 yt-dlp，日志不保存原值。Cookie 在服务器网络或过期后可能失效，不能保证复用成功。GitHub 登录与平台登录无关。

不要在初次失败后自动反复更换客户端、Cookie 或代理。缺全文时复用用户已有转写/导出；没有已授权的 ASR 或云端路线时交付 partial 与最少补充。

## 已有夸克导出（可选）

完整流程见 [quark.md](quark.md)：安装与绑定 → 精确查重 → 已授权上传与终态核验 → 处理/人工导出 → 精确检索下载 → 正文核验。每步保留状态，已有导出直接取回，不再 summary。不把云端问答当全文导出，不静默换目录、不从 CLI错误猜账号状态。浏览器的视频来源回退不等于夸克网页回退。

## 官方来源

- [bilibili-cli](https://github.com/public-clis/bilibili-cli)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)，[JS 支持](https://github.com/yt-dlp/yt-dlp/wiki/EJS)
- [Bili23 MCP](https://bili23.scott-sloan.cn/doc/mcp-server.html)
