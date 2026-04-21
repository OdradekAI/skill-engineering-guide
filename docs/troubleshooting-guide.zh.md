# 故障排除指南

[English](troubleshooting-guide.md)

> **Canonical source:** 退出码语义定义在 `skills/auditing/scripts/_cli.py`。平台 hook 行为定义在 `hooks/session-start`（Bash）+ `hooks/run-hook.cmd`（跨平台包装器）。本指南汇总了项目各处的故障排除信息。

使用 Bundles Forge 时的常见问题及解决方案。退出码和审计相关行为请参见[审计指南](auditing-guide.zh.md)。发布流程问题请参见[发布指南](releasing-guide.zh.md)。

## 系统要求

| 要求 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.9+ | 脚本使用 `Path.is_relative_to()` 等 3.9+ 特性 |
| 外部依赖 | 无 | 所有脚本仅使用标准库，无需 `pip install` |

### Python 版本错误

**症状：** `AttributeError: 'PosixPath' object has no attribute 'is_relative_to'` 或类似错误。

**原因：** 使用了 Python 3.8 或更早版本。CLI 入口守卫会打印 `bundles-forge requires Python 3.9+` 并退出。

**解决：** 安装 Python 3.9+ 并确保在 PATH 中。多版本共存时请显式使用 `python3.9` 或 `python3`。

## 退出码

所有审计脚本遵循统一的退出码规范：

| 退出码 | 含义 | 操作 |
|--------|------|------|
| `0` | 通过 — 无问题 | 无需处理 |
| `1` | 发现警告 | 建议检查，不阻塞 |
| `2` | 发现严重问题 | 必须解决后才能继续 |

配置验证脚本（如 `checklists --check`、`bump-version --check`）使用：`0` = 一致，`1` = 检测到漂移。

## 安装与配置

### 未知命令

**症状：** `bundles-forge: unknown command 'xxx'`

**解决：** 使用 `bundles-forge -h` 查看可用命令。完整命令列表请参见 [CLI 参考](cli-reference.zh.md)。

### 脚本未找到

**症状：** `bundles-forge: script not found: ...`

**原因：** 插件目录结构不完整或二进制文件未从正确位置运行。

**解决：** 确保完整的 `skills/` 目录树存在。必要时重新克隆或重新安装。

### Windows 路径问题

**症状：** Windows 上出现路径相关错误或输出不一致。

**说明：** 所有脚本使用 `pathlib.Path` 实现跨平台兼容，输出路径统一使用正斜杠。如遇路径问题，请通过 `bundles-forge` 或 `python bin/bundles-forge` 调用脚本，而非直接运行。

## 审计问题

### 安全扫描误报

**症状：** 安全扫描标记了合法的文档引用（如 SKILL.md 中在"不要这样做"语境下提到 `.env`）。

**说明：** 来自 SKILL.md 和 references 的发现被归类为 `suspicious`（非 `deterministic`）。它们出现在独立的"需要审查"部分，需要人工判断。

**处理：** 查看被标记行的上下文。如果引用是禁止性的（如"绝不要访问 .env 文件"），则为误报。suspicious 发现仍影响退出码，但有明确标记。

### 版本漂移

**症状：** `bump-version --check` 报告漂移。

**原因：** 版本号被手动编辑而非使用 bump 脚本，或新的清单文件未添加到 `.version-bump.json`。

**解决：** 运行 `bundles-forge bump-version <正确版本号>` 重新同步所有声明文件。如需跟踪新文件，先添加到 `.version-bump.json`。

### 清单漂移

**症状：** `checklists --check` 以退出码 1 退出。

**原因：** `audit-checks.json` 中的审计检查定义已更新，但生成的清单 markdown 表格未重新生成。

**解决：** 运行 `bundles-forge checklists .` 重新生成，然后提交更新的文件。

### 文档审计失败 (D1-D9)

**症状：** `audit-docs` 报告不匹配。

**常见原因：**
- **D1 (CLAUDE.md)：** CLAUDE.md 中的 skill 列表与实际 `skills/` 目录不匹配
- **D3（平台清单）：** CLAUDE.md 平台清单表与 `.version-bump.json` 不匹配
- **D6（README 同步）：** 添加/删除 skill 后 README 的 skill 表格过时
- **D7 (双语对称)：** 某个指南只更新了一种语言版本

**解决：** 更新引用的文档使其与 `skills/` 和清单的当前状态匹配。

## 平台特有问题

### Claude Code

- Hook 输出必须是包含 `hookSpecificOutput` 封装的有效 JSON
- Hook 失败时以退出码 0 静默降级，避免阻塞 IDE 启动

### Cursor

- Hook 输出使用 `additional_context` 封装（与 Claude Code 不同）
- Hook 配置位于 `hooks-cursor.json`（独立 schema，无 timeout/description 字段）

### Codex / OpenCode / Gemini CLI

- 这些平台有各自的平台清单，但共享相同的 skill 内容
- 版本同步覆盖 `gemini-extension.json`，但不覆盖所有平台安装指南

## 另见

- [CLI 参考](cli-reference.zh.md) — 完整命令文档
- [审计指南](auditing-guide.zh.md) — 审计范围和工作流
- [发布指南](releasing-guide.zh.md) — 发布流程故障排除
- [概念指南](concepts-guide.zh.md) — 架构和术语
