# 夸克：上传、处理、导出取回

这是可选正文补充路线，不是默认必经步骤。已有可靠全文直接蒸馏。这里只编排我们的流程，第三方 CLI 命令、安装与结果展示仍以执行端当前官方 Skill/help 为准，不复制官方运行时或账号配置。

## 安装及调用

官方源：[quarkclouddrive_offical](https://github.com/quark-clouddrive/quarkclouddrive_offical)。在已授权安装的执行端，从官方源取得 quarkclouddrive 并安装到当前 Agent 全局技能目录；按官方 README 当前命令，例如：

```sh
npx skills add https://github.com/quark-clouddrive/quarkclouddrive_offical/skills --skill quarkclouddrive
```

确认安装位置与版本，再读其 SKILL.md、auth、file-upload、file-search 和下载说明。官方安装检查可能下载新版并覆盖文档；先只读比较当前本地和远端版本，有升级差异且无升级授权时停止检查，不静默覆盖。允许检查后，每次用户输入首次调用 CLI 前按官方要求运行 install.sh，成功结果在本次输入中复用；失败停止，不并发安装与操作。本仓库不执行安装或绑定。

以下为经官方文档核对的操作示例，QUARK_CLI 为执行端官方脚本绝对路径，不是本仓库脚本；运行目录为仓库外的任务材料目录，避免 CLI Artifact 混入分发仓库。SESSION_INPUT 原样保留本次用户请求；SESSION_ID 按官方格式 Unix秒时间戳-6位随机字母数字生成，同一对话复用。参数用数组或正确 shell 引号传递，勿将原话拼成可执行命令。

```sh
node "$QUARK_CLI" upload "$VIDEO_FILE" --parent-fid "$CONFIRMED_PARENT_FID" --session-input "$SESSION_INPUT" --session-id "$SESSION_ID"
node "$QUARK_CLI" upload list --session-input "$SESSION_INPUT" --session-id "$SESSION_ID"
node "$QUARK_CLI" upload resume --record-id "$UPLOAD_RECORD_ID" --session-input "$SESSION_INPUT" --session-id "$SESSION_ID"
node "$QUARK_CLI" search --keyword "$VIDEO_ID" --stdout-only --session-input "$SESSION_INPUT" --session-id "$SESSION_ID"
```

目录参数只有用户明确给目录/FID 或已有确认配置时才传。未指定时不能擅填 0 或猜目录；为维持固定工作流优先一次确认目标完整目录，之后复用，不静默换目录。下载的当前参数需运行 download --help 并读官方说明后确定；若文档缺下载参数，明确缺口，不猜 --output/--fid-list。所有 CLI 子命令包括 help 按官方要求传公共会话参数。

## 状态与唯一下一动作

| 状态 | 下一动作 | 不允许的替代 |
| --- | --- | --- |
| 无正文、无云端原件 | 核实媒体/上传授权/目录，查重后上传 | 直接对网页链接当作本地文件上传 |
| 上传未完成/已暂停 | 查询原 recordId，按实际状态续传 | 再建同文件上传任务 |
| 上传终态成功、无导出 | 登记 uploaded_waiting_export，按实际界面/接口处理；需要时请用户导出完整文稿 | 进度100%当成功、重复上传、固定等待24小时保证成功 |
| 用户已生成/导出 | 视频 ID 精确搜索，读取完整 Artifact，取回匹配材料 | 对原视频调用 summary 来代替找回 |
| 文稿已取回 | 核对身份/全文覆盖，再蒸馏 | AI总结当完整正文 |

上传前保证媒体文件名含稳定视频 ID 与分集，必要时在任务材料目录创建不覆盖原件的派生上传文件。保存原件哈希与命名映射，不改云端历史文件。下载的 metadata ID、BV+分集/cid 或 YouTube ID 必须与云端命中身份对应。

上传验收读每个子任务终态和最终 result：全局成功且目标 fileName/fileSize 与本地对应、返回 fileId/FID。progress 100%不够；部分失败仅登记实际成功项，不重复上传成功项。保存任务 ID、实际云端目录/路径、字节数、本地 SHA256及回执；云端未返回哈希不能声称两端哈希一致，目录返回为空不能猜根目录。

## AI总结与全文导出是两种能力

官方 summary/qa 是云端内容理解请求，其返回文本不等于逐字文稿或已导出文件。用户明确要云端 AI 回复时按官方助手流程；此视频蒸馏默认要取得证据正文，不默认调用 summary。自动生成/导出全文尚未在目标服务器验收，必须保留人工节点：用户在实际支持的夸克界面生成并保存/导出完整文稿，再由 Agent 找回；不强制同时导课件、脑图、AI总结。

summary 失败时遵守官方结束规则，不在当前输入中反复请求或切网页完成同一云端问答；已有独立导出文件的取回按其单独授权与状态处理。-1505/空结果不算处理完成，不能承诺24小时后一定就绪。

## 精确取回

1. 保持原平台 ID 和分集，search 中间步骤用 --stdout-only。无结果报告原精确条件无匹配，不擅自换“总结”或标题。只有用户给新条件才重新搜索。
2. 读取返回完整 JSONL Artifact 后选匹配文件 FID，不能只用前5条预览。核对分集/材料角色；文件名缺身份且无法佐证时先确认，不能合并同名视频材料。
3. 已授权取回范围内用官方 download 当前命令下载到仓库外原件目录，记录原格式、FID、字节数和 SHA256。已有同 FID且哈希有效的原件复用。文稿 txt 是主要证据；AI总结 docx 作导航；课件/脑图只按需取回。必要时用已安装文档工具或标准库解包提取 docx 文本，原始 docx不改写。
4. 核验正文起止、明显缺段、时长/时间码对应，不以文件存在当全文完整。缺文稿而仅有总结仍 partial。完成后回填来源记录，再进入 workflow 的全文理解步骤。

## 故障与恢复

- -104 无法识别 Agent 环境：判为环境问题。Windows 误用 WSL/Linux Node时，只允许同参数改原生 node.exe一次；Linux 原生调用仍报错时记录不支持/识别失败，不声称 Windows 方案已解决服务器。程序存在不等于该 Agent 被支持。
- 安装失败/CLI错误不证明账号异常，不自动转夸克网页。只有官方认证返回能判登录失效；在当前授权内按官方 auth处理，无授权则给最少绑定步骤，不循环登录。
- 浏览器读取视频来源的回退与夸克回退是两条不同分支。夸克网页操作只在用户明确指定或补充授权且工具实际可用时进行，不默认让服务器操控本机界面。
- 保存等待状态和原任务，下一次先找导出/查询原任务，不重新下载、上传或总结。临时视频清理只提醒准确路径，未保存可靠原件前不建议删除唯一文件。
