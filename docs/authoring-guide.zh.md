# 内容编写指南

[English](authoring-guide.md)

面向用户的指南，介绍如何使用 Bundles Forge 编写、完成、改进和适配 bundle-plugin 中的 SKILL.md 和代理定义。涵盖路径选择、编写规范、代理编写、验证和常见陷阱。

## 概述

内容编写（authoring）负责 bundle-plugin 的内容层：编写 SKILL.md 文件、代理定义（`agents/*.md`）和支持资源（`references/`）。它是**执行层**中的**执行器**：单一职责工作者，负责内容创建和改进。编排技能（`blueprinting`、`optimizing`）会在流水线中调度它，你也可以直接调用它进行独立的内容工作。

**重要性：** 良好的内容编写决定了 Agent 能否持续发现、加载和遵循你的指令。描述（description）决定可发现性；正文决定执行质量。

> **权威来源：** 完整的执行协议（入口检测、路径步骤、验证清单）在 `skills/authoring/SKILL.md` 中。本指南帮助你决定*哪条路径适用*和*预期什么结果* — 技能本身负责执行。

---

## 选择路径

内容编写支持四条路径。选择取决于你的起点：

| 上下文 | 路径 | 适用场景 |
|--------|------|---------|
| 来自 blueprinting 的技能清单，或从头编写 | **路径 1：新建内容** | 需要全新的 SKILL.md 或代理定义 |
| 外部/已有技能需要引入项目 | **路径 2：集成内容** | 将第三方或独立技能适配到项目规范 |
| 脚手架生成的空白 stub 目录 | **路径 3：完成内容** | 填充 scaffolding 创建但几乎为空的 SKILL.md |
| 项目内已有技能需要改进 | **路径 4：改进内容** | 重写描述、减少 token、修复结构或应用优化规格 |

### 决策流程

```
你是否从 blueprinting 带着技能清单过来？
  ├─ 是 → 路径 1：新建内容（编写所有技能 + 代理）
  └─ 否 → SKILL.md 是否已存在？
            ├─ 否 → 是否有脚手架生成的 stub 目录？
            │        ├─ 是 → 路径 3：完成内容
            │        └─ 否 → 路径 1：新建内容
            ├─ 是，来自项目外部 → 路径 2：集成内容
            └─ 是，在本项目内 → 路径 4：改进内容
```

---

## 路径 1：新建内容

最适合：从头编写技能或代理定义，无论是作为 blueprinting 流水线的一部分还是独立操作。

**你提供的：** 对技能功能的描述 — 用途、触发场景、预期输入/输出、与其他技能的关系。

**你得到的：** 完整的 SKILL.md，包含 frontmatter、描述、执行流程、常见错误和 Integration 章节 — 全部遵循项目规范（独立编写时使用默认规范）。

**Agent 执行的关键步骤：**
1. 从你的描述或 blueprinting 技能清单收集需求
2. 读取现有项目技能（如有）以匹配规范
3. 编写 frontmatter，描述以"Use when..."开头，不超过 250 字符
4. 编写完整正文：概述、流程步骤、常见错误、Inputs/Outputs/Integration
5. 检查外部依赖 — 如果技能引用了 MCP 工具或 CLI 命令，遵循编写指南中的声明语法和回退模式
6. 评估 token 预算 — 正文超过 500 行或重内容段超过 100 行时提取到 `references/`
7. 运行 `lint_skills.py` 验证

**代理定义：** 同样的路径适用，但 Agent 会遵循 `references/agent-authoring-guide.md` 中的规范 — 不同的 frontmatter 字段（`maxTurns`、`disallowedTools`）、面向报告的正文和 `.bundles-forge/` 输出格式。

---

## 路径 2：集成内容

最适合：将外部或第三方技能适配到项目的规范和工作流图。

**你提供的：** 要集成的技能（文件路径、URL 或粘贴内容），以及可选的目标项目。

**你得到的：** 技能被重写为匹配项目的描述风格、章节结构、交叉引用格式和 Integration 接线。

**Agent 执行的关键步骤：**
1. 读取传入技能和项目现有规范
2. 重写 frontmatter（描述风格、命名规范）
3. 重组正文以匹配项目模式
4. 接线 Integration 章节，添加与现有技能的交叉引用
5. 评估 token 预算
6. 运行验证

**何时用路径 2 vs 路径 4：** 技能来自项目*外部*时用路径 2。改进项目*内部*已有技能时用路径 4。

---

## 路径 3：完成内容

最适合：填充脚手架生成的 stub 目录，这些目录有正确的结构但内容很少。

**你提供的：** 一个脚手架项目（来自 `bundles-forge:scaffolding`），包含几乎为空的 SKILL.md 文件的技能目录。

**你得到的：** 每个 stub 的完整 SKILL.md，遵循项目规范和设计文档中每个技能的预期用途。

**Agent 执行的关键步骤：**
1. 读取脚手架结构，识别 stub（< 10 行非空内容）
2. 匹配项目中已完成技能的风格
3. 为每个 stub 编写完整内容
4. 按需创建支持资源（`references/`）
5. 运行验证

---

## 路径 4：改进内容

最适合：基于用户反馈或 `bundles-forge:optimizing` 的优化规格，对项目内已有技能进行针对性改进。

**你提供的：** 要改进的技能，以及具体请求（"重写描述"）或来自 optimizing 的 `optimization-spec`。

**你得到的：** 保留有效内容、修复问题的针对性改动 — 而非全面重写。

**常见改进目标：**
- 描述触发不可靠 → 按描述规则重写
- Token 预算超标 → 将重内容提取到 `references/`
- 缺少章节 → 添加概述、常见错误、Inputs/Outputs
- 指令风格问题 → 将指令改为推理式，增加示例

**Agent 执行的关键步骤：**
1. 读取并理解现有内容
2. 识别具体改进目标
3. 进行针对性修改（保留有效内容）
4. 验证 Integration 章节仍然正确解析
5. 运行验证

---

## 编写规范一览

以下是 authoring 技能执行的核心规范。完整参考见 `skills/authoring/references/skill-writing-guide.md`。

### 描述规则

- 以"Use when..."开头 — 描述触发条件，而非工作流步骤
- 不超过 250 字符
- 要积极 — 列出相关场景、边缘情况、替代表达
- 适当限定范围（如"bundle-plugins"而非"any project"）

### 正文结构

良好的 SKILL.md 遵循以下模式：

1. **Frontmatter** — `name`、`description`、可选字段（`allowed-tools` 等）
2. **Overview** — 1-3 句话：技能做什么、核心原则、技能类型
3. **Entry Detection**（多路径时）— 上下文到执行路径的映射表
4. **Process** — 祈使句式的逐步执行流程
5. **Common Mistakes** — 陷阱和修复的表格（至少 3 条）
6. **Inputs / Outputs** — 带描述的 artifact ID
7. **Integration** — Called by / Calls / Pairs with

### Token 效率

| 目标 | 预算 |
|------|------|
| Bootstrap 技能（始终加载） | < 200 行 |
| 常规技能正文 | < 500 行 |
| 描述（始终在上下文中） | < 250 字符 |
| Frontmatter 总量 | < 1024 字符 |

在 300+ 行时，lint（Q12）建议将重内容段提取到 `references/` — 这是软阈值而非硬限制。将参考内容（100+ 行）提取出来以保持主文件可扫描。使用渐进披露：核心指令放在 SKILL.md 中，细节放在 references 中。

### 指令风格

- 使用祈使句（"Read the file"，而非"You should read the file"）
- 解释*为什么*，而不仅仅是*做什么* — 理解胜过遵从
- 每个关键指令至少包含一个具体示例
- 避免堆砌 MUST/ALWAYS/NEVER 而不解释原因

### 高级特性

编写指南涵盖了多项高级能力。详细说明见 `skills/authoring/references/skill-writing-guide.md`：

- **字符串替换** — 使用 `$ARGUMENTS`、`$0`/`$1`、`${CLAUDE_SKILL_DIR}` 和 `${CLAUDE_SESSION_ID}` 在技能调用时注入动态值
- **动态上下文注入** — `` !` `` 语法在技能加载前运行 shell 命令；Agent 接收的是命令输出而非命令本身（适用于注入 git 状态、API 响应或环境数据）
- **技能内容生命周期** — 技能加载一次后持续存在于对话中；上下文满时自动压缩保留每个技能的前 5,000 token。将关键指令前置以提高压缩存活率
- **Frontmatter Hooks**（仅 Claude Code）— 在 YAML frontmatter 中定义作用于技能调用的生命周期钩子（`PreToolUse`、`Stop` 等）
- **用户配置**（`userConfig`）— 通过 `${user_config.KEY}` 在技能内容中引用非敏感的插件配置值；敏感值仅限于 MCP/hook/script 环境
- **外部工具引用** — 通过 `allowed-tools: Bash(...)` 或 `Python(...)` 声明 CLI 工具，通过 `mcp__server__tool` 声明 MCP 工具；当 MCP 服务器可能不可用时包含回退块

---

## 代理编写

编写代理定义（`agents/*.md`）时，同样的四条路径适用，但使用不同的规范：

| 方面 | SKILL.md | agents/*.md |
|------|----------|-------------|
| Frontmatter | `name`、`description`、可选字段 | `name`、`description`、`model`、`maxTurns`、`disallowedTools`，+ 高级：`effort`、`tools`、`skills`、`memory`、`background`、`isolation` |
| 正文 | 交互式使用的执行流程 | 自主检查的执行协议 |
| 输出 | 直接文件修改或指导 | 报告输出到 `.bundles-forge/` |
| 可链接 | 是（调用其他技能） | 默认否；可通过 `skills` frontmatter 字段启用 agent-to-skill 委托 |

### 代理类型

| 类型 | 关键 Frontmatter | 用途 |
|------|-----------------|------|
| **只读**（默认） | `disallowedTools: Edit` | 检查、审计、报告 — 不能修改文件 |
| **可写** | 省略 `disallowedTools`，设置 `isolation: "worktree"` | 在隔离的 git worktree 中修改文件以防止冲突 |
| **带技能委托** | 添加 `skills` 字段 | 代理可调用列出的技能，实现 agent-to-skill 分派 |

完整的代理编写参考见 `skills/authoring/references/agent-authoring-guide.md`。

---

## 验证

编写完成后，技能始终运行 `python scripts/lint_skills.py` 来验证结果。

### 检查内容

| 严重性 | 检查项 | 操作 |
|--------|--------|------|
| **Critical** | Q1-Q3：缺少 frontmatter、name、description | 立即修复 |
| **Warning** | Q4-Q9、Q14、X1-X3：命名规范、描述规则、token 预算、工具路径、断裂引用 | 可简单修复则修复 |
| **Info** | Q10-Q13、Q15-Q17、S9：缺少章节、重内联内容、目录名不匹配 | 报告为建议 |

完整的逐项检查参考见 `skills/authoring/references/quality-checklist.md`。

---

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 描述总结工作流 | 为人类而非 Agent 编写 | 只描述触发条件 — Agent 会直接读取描述 |
| 堆砌 MUST/ALWAYS/NEVER | 想要面面俱到 | 解释规则存在的原因 — 理解胜过遵从 |
| 所有内容塞进 SKILL.md | 不了解 `references/` | 将重内容（100+ 行）提取到 `references/`；正文保持在 500 行以下 |
| 只有抽象规则没有示例 | 匆忙编写 | 每个关键指令至少一个具体示例 |
| 跳过项目规范 | 孤立工作 | 在已有项目中先读 2-3 个现有技能 |
| 不接线 Integration 章节 | 把技能当独立体 | 每个技能都需要 Called by / Calls / Pairs with |
| 忘记验证 | 假设内容正确 | 始终运行 `lint_skills.py` — 在传播前捕获问题 |
| 描述太窄 | 过于具体 | 积极列出相关场景和边缘情况 |
| 描述太宽 | 过于模糊 | 限定到正确的上下文（如"bundle-plugins"而非"any project"） |

---

## 常见问题

**问：我有一个不在任何项目中的独立技能。可以使用 authoring 吗？**

可以。直接调用 authoring — 它检测到没有项目根目录后会使用编写指南中的默认规范。你会得到一个遵循最佳实践的结构良好的 SKILL.md。

**问：authoring 和 optimizing 有什么区别？**

authoring 是*内容编写者* — 创建和改进 SKILL.md 文件。optimizing 是*编排者* — 诊断问题、决定修复什么、将内容改动委托给 authoring。如果你确切知道要写什么或修什么，直接用 authoring。如果需要先诊断，用 optimizing。

**问：如何编写代理定义而非技能？**

使用相同的 authoring 路径。当目标是 `agents/*.md` 时，Agent 会自动切换到代理规范 — 不同的 frontmatter 字段、面向报告的正文和只读约束。详见 `references/agent-authoring-guide.md`。

**问：我的技能接近行数预算了。这有问题吗？**

硬限制是 500 行（Q9 警告）。在 300+ 行时，lint（Q12）建议提取到 `references/` — 这是软建议而非阻断。具有复杂流程的编排技能（如 `blueprinting` 或 `releasing`）可能合理地更长。但如果你的技能有大量参考内容（表格、模板、示例），请将超过 100 行的章节提取到 `references/` 以保持主文件可扫描。Bootstrap 技能（`using-*`）有更严格的 200 行预算。

**问：可以在流水线中运行 authoring 吗？**

可以。blueprinting 将 authoring 调度为阶段 2（scaffolding 之后）。optimizing 为内容改动调度 authoring。两种情况下，authoring 都从编排者接收上下文，并返回编写好的内容供下一阶段使用。

---

## 相关技能

| 技能 | 何时使用 |
|------|---------|
| `bundles-forge:blueprinting` | 你需要在编写内容之前*规划*新项目 |
| `bundles-forge:scaffolding` | 你需要先生成目录结构再填充内容 |
| `bundles-forge:optimizing` | 你需要*诊断*改进方向，而不仅是编写内容 |
| `bundles-forge:auditing` | 验证编写内容的质量和安全性 |
| `bundles-forge:releasing` | 发布 — 包含审计、优化和版本同步 |
