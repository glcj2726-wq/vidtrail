# Setup and actual capabilities

Follow the repository README for an isolated Python environment, dependencies, doctor, and skill installation. The doctor checks command presence/version only: not authentication, MCP connectivity, platform access, or learning quality.

Python 3.10+ is required. requirements.txt pins the acquisition tool baseline. Media merging, audio/frame extraction need ffmpeg/ffprobe. Check yt-dlp's current [EJS guidance](https://github.com/yt-dlp/yt-dlp/wiki/EJS) for a supported JS runtime; do not assume a tool update preserves previous validation. Paths come from the current host/project, with acquisition data outside the distribution and notes at the user's chosen destination.

Record installed, connected, authenticated, and tested separately. Keep tokens, cookies and signed URLs out of logs/source. GitHub authentication is unrelated to Bilibili, Google, or Quark authentication.

| Optional capability | Check on the execution host | Without it |
| --- | --- | --- |
| Bili23 MCP | Official setup, real schema, source resolution, task terminal state; service must actually run | Report unavailable; a necessary media target may use yt-dlp |
| Access to another host's local service | Explicit authorization, reachable host, narrowly scoped private tunnel/configuration | Remote localhost does not reach the user's computer |
| Browser | Real host-exposed control tool and target page access; plugin-specific methods only if exposed | Report missing route; installing a browser alone does not provide agent control |
| Local transcription | Installed engine, cached model, hardware/language, output and timing support | Choose another authorized route or request text |
| Cloud transcription | Selected service, existing account, upload/cost authorization | Do not enable automatically |
| Drive processing/export | User-selected service, configured tools, explicit upload scope | Existing text remains usable; otherwise report gap |
| Notion or other destination | Real connector, selected destination, write authorization and read-back | Deliver in conversation or authorized local files |

Optional capabilities do not all need installation. Configure only a route actually needed. Model downloads, installs, logins, external uploads and costs are distinct actions; reuse authorization when it already covers them, not the maintainer's historical permissions.

Only reuse/transfer credentials if permitted, using a private secret channel and minimal compatible files outside the repository; never an entire browser profile. Cookie expiry/network changes may invalidate reuse. Use bili's actual format or yt-dlp's Netscape format as appropriate. Quark binding is separate; copying local state is not proof a server is authenticated. A documented relevant login change can justify one retry of the failed target, retaining the earlier receipt.

Reference: [Bili23 MCP official documentation](https://bili23.scott-sloan.cn/doc/mcp-server.html). No browser, GUI downloader, model, external service, or account state is installed by this skill.
