# CLI 参考

[English](cli-reference.md)

> **权威信源：** 命令定义位于 `bin/bundles-forge`。参数 schema 定义在各脚本的 `main()` 函数或通过 `_cli.make_parser()` 提供。

`bundles-forge` CLI 调度器及所有子命令的完整参考。

## 用法

```bash
bundles-forge <command> [args...]
bundles-forge -h | --help
```

调度器将子命令路由到插件内的对应 Python 脚本。退出码从目标脚本原样传播。

## 通用选项

大多数审计命令共享以下选项（由 `_cli.make_parser()` 提供）：

| 选项 | 说明 |
|------|------|
| `project_root` | 位置参数，可选。Bundle-plugin 根目录（默认：`.`） |
| `--json` | 输出 JSON 而非 Markdown |

## 命令

### audit-skill

单个 skill 或整个项目的质量审计。

```bash
bundles-forge audit-skill [project-root]
bundles-forge audit-skill [skill-directory]
bundles-forge audit-skill --all [project-root]
bundles-forge audit-skill --json [project-root]
```

| 选项 | 说明 |
|------|------|
| `project_root` | 项目根目录、skill 目录或 SKILL.md 文件路径 |
| `--all` | 强制项目级模式（审计所有 skills） |
| `--json` | 输出 JSON |

**范围检测：** 接受项目根目录（包含 `skills/` 目录）、单个 skill 目录（包含 `SKILL.md`）或直接的 `SKILL.md` 文件路径。项目模式对所有 skills 运行全部 10 个审计类别；skill 模式对单个 skill 运行 4 个适用类别。

**交叉引用检查：** 包含 X1（skill 引用）、X2（相对路径）、X3（目录引用）和 X4（孤儿检测 — 查找 `references/` 中未被 `SKILL.md` 或兄弟 reference 文件链接的文件）。项目模式下，C1 包含跨 skill 的段落哈希冗余检测。

**退出码：** `0` 通过，`1` 有警告，`2` 有严重问题。

---

### audit-security

基于模式的 7 攻击面安全扫描。

```bash
bundles-forge audit-security [project-root]
bundles-forge audit-security --json [project-root]
```

扫描 SKILL.md 文件、hook 脚本、hook 配置、OpenCode 插件、agent 提示词、捆绑脚本和 MCP 配置，检测危险模式（网络调用、eval、敏感文件引用、安全覆盖）。

发现按置信度分类：`deterministic`（在可执行代码中明确匹配）或 `suspicious`（上下文相关，需人工审查）。

**退出码：** `0` 通过，`1` 有警告，`2` 有严重问题。

---

### audit-docs

文档一致性检查（D1-D9）。

```bash
bundles-forge audit-docs [project-root]
bundles-forge audit-docs --json [project-root]
```

验证文档文件（CLAUDE.md、AGENTS.md、README、指南）与实际项目结构（skills、清单、平台配置）的对齐情况。

**退出码：** `0` 通过，`1` 有警告，`2` 有严重问题。

---

### audit-plugin

组合审计 — 编排 skill、安全、工作流和文档审计，加上插件健康检查。

```bash
bundles-forge audit-plugin [project-root]
bundles-forge audit-plugin --json [project-root]
```

按顺序运行所有审计脚本，生成涵盖结构、版本、hooks、测试和所有审计维度的 10 类健康报告。

**退出码：** `0` 通过，`1` 有警告，`2` 有严重问题。

---

### audit-workflow

工作流完整性审计（W1-W11）。

```bash
bundles-forge audit-workflow [project-root]
bundles-forge audit-workflow --focus-skills skill1,skill2 [project-root]
bundles-forge audit-workflow --json [project-root]
```

| 选项 | 说明 |
|------|------|
| `--focus-skills` | 逗号分隔的 skill 名称，用于聚焦分析 |
| `--json` | 输出 JSON |

三层审计：静态图分析（W1-W5）、语义接口检查（W6-W9）、行为验证（W10-W11）。输出包含 skill 工作流的 Mermaid 依赖图（JSON 和 Markdown 模式均包含）。

**退出码：** `0` 通过，`1` 有警告，`2` 有严重问题。

---

### checklists

从审计检查注册表生成或验证清单表格。

```bash
bundles-forge checklists [project-root]
bundles-forge checklists --check [project-root]
```

| 选项 | 说明 |
|------|------|
| `--check` | 检测漂移而不写入文件（如过时则退出码 1） |

不带 `--check` 时，从 `skills/auditing/references/audit-checks.json` 重新生成 markdown 清单表格。带 `--check` 时，将当前表格与注册表比较，不一致则以非零退出码退出。

**退出码：** `0` 一致/已更新，`1` 检测到漂移（使用 `--check` 时），`2` 注册表错误（ID 重复或文件缺失）。

---

### bump-version

跨所有平台清单的版本同步。

```bash
bundles-forge bump-version --check [project-root]
bundles-forge bump-version --audit [project-root]
bundles-forge bump-version <version> [project-root]
bundles-forge bump-version --dry-run <version> [project-root]
```

| 选项 | 说明 |
|------|------|
| `--check` | 报告当前版本并检测漂移 |
| `--audit` | 检查 + 扫描仓库中未声明的版本字符串 |
| `--dry-run` | 预览版本变更而不写入文件 |
| `version` | 新版本号，格式为 `X.Y.Z` 或 `X.Y.Z-pre.N` |

更新 `.version-bump.json` 中声明的所有文件到指定版本。`--audit` 模式还会扫描仓库中包含当前版本字符串但未被配置跟踪的文件。

**退出码：** `0` 成功/一致，`1` 检测到漂移或输入无效。

## 另见

- [故障排除指南](troubleshooting-guide.zh.md) — 常见问题和解决方案
- [审计指南](auditing-guide.zh.md) — 审计范围和工作流
- [发布指南](releasing-guide.zh.md) — 使用这些命令的发布流程
