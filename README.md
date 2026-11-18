# AI-Dev-Connectivity-Doctor (AI 开发与终端网络自检工具箱)

一个**零第三方依赖、开源只读**的 Windows PowerShell 与 Python 网络连通性诊断脚本集合，用于快速排查 **OpenAI / Google Gemini / Anthropic Claude / GitHub / npm / PyPI** 在开发者本机、终端 CLI 与 IDE 中的 DNS 解析偏差、IPv6 抢占超时、WinINet/环境变量冲突以及 TLS 握手延迟问题。

![License](https://img.shields.io/badge/License-MIT-10b981)
![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-0284c7)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-6366f1)

---

## 为什么做这个工具？

很多开发者在配置 **Cursor、Antigravity、Gemini CLI、Git** 时经常遇到：
- 浏览器可以打开网页，但终端工具报超时或 SSL 握手失败；
- 一到晚高峰（20:00 - 次日 02:00）长对话频繁中断；
- 开启某些规则工具后，反而因为环境变量残留或 DNS 链路错配导致整体变慢。

运行本仓库任意一个单文件脚本即可在 3 秒内定位究竟卡在 **本机环境变量冲突 / DNS 解析 / TCP 连接 / TLS 握手** 哪一层。

---

## 快速开始

### 1. Windows PowerShell 一键检测（无需安装 Python）
```powershell
powershell -ExecutionPolicy Bypass -File .\check_ai_endpoints.ps1
```

### 2. Python 3 跨平台检测（支持 JSON 输出）
```bash
python check_ai_endpoints.py
python check_ai_endpoints.py --json
```

### 3. 美区账号区属与 IPv6 抢道送中一键自检（Google 家庭组 / Gemini / Claude）
```bash
python check_us_region_and_ipv6.py
```

### 4. Cursor / Claude 生产级 `.cursorrules` 模板与 Windows 本地 MCP 排障手册
- 详见本仓库内文档：[CURSOR_CLAUDE_MCP_RULES_STARTER.md](./CURSOR_CLAUDE_MCP_RULES_STARTER.md)（包含防幻觉工程规范模板与 `npx`/`uvx` MCP 超时排障清单）。

---

## 常见异常对照与处理建议

| 检测现象 | 常见根因 | 推荐处理思路 |
| --- | --- | --- |
| `DNS resolution failed` 或返回异常保留 IP | 本地 DNS 缓存污染或分流规则失效 | 刷新本地 DNS 缓存，确认分流规则覆盖完整 AI 认证及 API 域 |
| `TCP timeout`（尤其仅 `v6` 有地址或 `v6` 抢先） | 家庭宽带 IPv6 国际出口丢包，或未开 TUN 接管 | 关闭冲突代理环境变量、检查虚拟网卡 TUN 接管，或在本地优先级抑制异常 IPv6 |
| `tls=...` 晚高峰超过 1500ms 且频繁重置 | 单一国际路线晚高峰拥塞，无自动容灾 | 使用带有健康探测与双星容灾切换的网络客户端，避免人工反复换点 |

---

## 配套桌面方案参考

如果你希望跳过繁琐的手动规则维护与 CLI 环境变量排查，可以参考我们日常配套使用的开箱即用 Windows 桌面方案：**小泡狐桌面端（Xiaopohu Desktop v2.1.5）**：
- 内置 **MetaCubeX `.mrs` 分流规则引擎** 与 24 小时规则热更新；
- 支持 **TUN 全栈接管 + 自动容灾切换 + 桌面 AI 宠物伴侣**；
- 新邮箱支持免密体验 5 GB / 24h 并全网公开校验哈希：
  - 官方文档与指南页：[https://sketchsketch942008-star.github.io/Xiaopohu-Desktop/](https://sketchsketch942008-star.github.io/Xiaopohu-Desktop/)
  - Cursor / Claude / Gemini 分流专题：[https://xph-vip.pages.dev/guides/cursor-claude-gemini-setup.html](https://xph-vip.pages.dev/guides/cursor-claude-gemini-setup.html)
  - AI 连接排障专题：[https://xph-vip.pages.dev/guides/ai-troubleshooting.html](https://xph-vip.pages.dev/guides/ai-troubleshooting.html)
  - 官方 X 动态与答疑：[https://x.com/xiaopaohu_cloud](https://x.com/xiaopaohu_cloud)
  - 官方 Telegram 用户交流群：[https://t.me/+RN6ywCiU4_piYzVl](https://t.me/+RN6ywCiU4_piYzVl)
  - 发布仓库与 SHA256 校验：[https://github.com/sketchsketch942008-star/Xiaopohu-Desktop](https://github.com/sketchsketch942008-star/Xiaopohu-Desktop)
