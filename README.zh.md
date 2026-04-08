# Bundles Forge

[English](README.md)

技能项目工程化工具包：脚手架搭建、多平台适配、版本管理、质量审计，以及技能全生命周期管理，覆盖所有主流 AI 编程平台。

## 安装

### Claude Code

```bash
claude plugin install bundles-forge
```

开发模式：

```bash
git clone https://github.com/odradekai/bundles-forge.git
cd bundles-forge
claude plugin link .
```

### Cursor

在 Cursor 插件市场搜索 `bundles-forge`，或使用 `/add-plugin bundles-forge`。

### Codex

参见 [`.codex/INSTALL.md`](.codex/INSTALL.md)

### OpenCode

参见 [`.opencode/INSTALL.md`](.opencode/INSTALL.md)

### Copilot CLI

```bash
copilot plugin install bundles-forge
```

### Gemini CLI

```bash
gemini extensions install https://github.com/odradekai/bundles-forge.git
```

## 技能一览

| 技能 | 说明 |
|------|------|
| `using-bundles-forge` | 引导元技能 — 建立如何发现和使用所有其他技能的入口 |
| `designing` | 通过结构化访谈规划新技能项目，或将复杂技能拆分为项目 |
| `scaffolding` | 生成项目结构、平台清单、钩子脚本和引导技能 |
| `writing-skill` | 指导 SKILL.md 文件编写 — 结构、描述、渐进式加载 |
| `auditing` | 9 大类系统化质量评估与评分 |
| `optimizing` | 工程化优化 — 描述、token 效率、工作流链路 |
| `adapting-platforms` | 添加平台支持（Claude Code、Cursor、Codex、OpenCode、Copilot CLI、Gemini CLI） |
| `managing-versions` | 版本同步基础设施、漂移检测与审计 |
| `iterating-feedback` | 基于用户反馈迭代改进技能 — 验证建议、fork 外部技能、自动回审 |
| `scanning-security` | 扫描技能项目中钩子、插件、Agent 提示词和指令的安全风险 |
| `releasing` | 完整发布流水线 — 审计、安全扫描、版本升级、CHANGELOG、发布 |

## 工作流

技能覆盖技能项目的完整生命周期：

```
designing → scaffolding → writing-skill
                                                              ↓
                           auditing ← ── ── ── ┘
                                ↓               ↓
               optimizing   iterating-feedback
               （项目工程优化）              （单技能效果迭代）
                                ↓               ↓
                           releasing
                                    ↑
              scanning-security（被 audit 和 release 调用）
              adapting-platforms（任意阶段均可添加平台）
              managing-versions（支撑所有阶段）
```

1. **设计** — 通过访谈确定项目范围，或将复杂技能拆解为项目
2. **搭建** — 根据设计方案生成完整的项目结构
3. **编写** — 撰写有效的 SKILL.md 文件：描述、指令、渐进式加载
4. **审计** — 跨 9 大类验证质量（结构、清单、版本、技能、安全等）
5. **优化** — 针对性的工程改进：描述、token 效率、工作流链路
6. **迭代** — 基于用户反馈改进单个技能的效果，含验证与自动回审
7. **安全** — 扫描钩子、插件、Agent 提示词和技能指令中的风险
8. **适配** — 添加更多平台支持
9. **版本** — 保持所有平台清单版本同步
10. **发布** — 编排完整的发布前验证和发布流水线

## Agents

| Agent | 职责 |
|-------|------|
| `scaffold-reviewer` | 验证脚手架生成的项目结构 |
| `project-auditor` | 执行系统化质量审计 |
| `security-scanner` | 跨 5 大攻击面执行安全风险评估 |

## 命令

| 命令 | 指向 |
|------|------|
| `/use-bundles-forge` | `bundles-forge:using-bundles-forge` |
| `/design-project` | `bundles-forge:designing` |
| `/scaffold-project` | `bundles-forge:scaffolding` |
| `/audit-project` | `bundles-forge:auditing` |
| `/scan-security` | `bundles-forge:scanning-security` |

其他技能通过描述自动触发，无需斜杠命令。

## 贡献

欢迎贡献。请遵循现有代码风格，并通过 `scripts/bump-version.sh --check` 确保所有平台清单版本同步。

## 许可证

MIT
