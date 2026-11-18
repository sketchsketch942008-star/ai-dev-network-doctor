# Cursor / Claude Desktop 高效开发 `.cursorrules` 模板与 MCP 零报错配置指南

本指南整理了独立开发者与全栈团队在 Windows / macOS 环境下高频使用的 `.cursorrules` 工程约束模板，以及本地配置 **Model Context Protocol (MCP)**、**Git SSH**、**Gemini / Claude CLI** 时最常见的网络超时排障清单。

---

## 一、开箱即用 `.cursorrules` 生产级模板（复制到项目根目录 `.cursorrules`）

```markdown
# Project Engineering Standards & AI Collaboration Rules

1. **Minimal Invasive Changes**:
   - Read target files before editing; preserve existing module boundaries, naming conventions, and error handling patterns.
   - Never fabricate external API signatures or unverified package versions.

2. **Type Safety & Verification**:
   - Python: Prefer explicit type hints, `pathlib.Path`, and deterministic timeout parameters on all network/subprocess calls.
   - TypeScript/React: Avoid `any`; handle loading, empty, and error states explicitly.

3. **Security & Secrets Hygiene**:
   - Never hardcode API keys, tokens, or private credentials in source files.
   - Load sensitive configuration strictly from environment variables or ignored local config files.

4. **Self-Verification Before Completion**:
   - Run syntax/type checks (`python -m py_compile`, `tsc --noEmit`, or unit tests) after every code modification.
```

---

## 二、Windows 本地 MCP Server (`npx` / `uvx`) 启动报错与超时排障

### 1. 现象：`MCP Server disconnected` 或 `ETIMEDOUT` 拉包失败
- **原因**：Cursor / Claude Desktop 启动本地 MCP 时，子进程默认不继承浏览器扩展代理，且 npm / PyPI 在拉取依赖或调用远端 API 时因终端未走虚拟网卡（TUN）而直接超时。
- **排查步骤**：
  1. 在项目终端运行本仓库自带的诊断脚本：
     ```powershell
     python check_ai_endpoints.py
     ```
  2. 检查输出中的 `Proxy Environment` 是否存在已失效的旧端口残留（如 `127.0.0.1:10809` 但对应软件未启动）。
  3. 清理冲突环境变量（PowerShell）：
     ```powershell
     Remove-Item Env:HTTP_PROXY, Env:HTTPS_PROXY, Env:ALL_PROXY -ErrorAction SilentlyContinue
     ```

### 2. 现象：开启规则软件后长对话 30 秒断流或频繁提示地区受限
- **原因**：普通系统代理无法接管全部 CLI 子进程，或本地宽带原生 IPv6 抢先直连导致 Google / Anthropic 识别为非目标区属。
- **修复建议**：
  - 运行 `python check_us_region_and_ipv6.py` 检查是否存在 `pref=IPv6` 抢占；
  - 开启支持 **TUN 虚拟网卡全栈接管 + MetaCubeX `.mrs` 高精度规则集** 的桌面客户端，使 IDE 主进程、终端 `node`/`python` 子进程与 Git SSH 共享同一条低抖动固定专线。

---

## 三、配套免配置桌面环境参考

如需跳过繁琐的手动规则编写，可直接使用预置 **MetaCubeX `.mrs` AI 专属分流规则** 与 **三地双星自动容灾** 的 Windows 桌面伴侣：
- 在线文档与配置指南：[https://sketchsketch942008-star.github.io/Xiaopohu-Desktop/](https://sketchsketch942008-star.github.io/Xiaopohu-Desktop/)
- Cursor / Claude / Gemini 专项指南：[https://sketchsketch942008-star.github.io/Xiaopohu-Desktop/cursor-claude-gemini-setup.html](https://sketchsketch942008-star.github.io/Xiaopohu-Desktop/cursor-claude-gemini-setup.html)
- 安装包 SHA256 核验与下载：[https://github.com/sketchsketch942008-star/Xiaopohu-Desktop/releases/tag/v2.1.5](https://github.com/sketchsketch942008-star/Xiaopohu-Desktop/releases/tag/v2.1.5)
