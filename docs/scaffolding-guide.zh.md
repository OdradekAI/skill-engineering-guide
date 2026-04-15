# 脚手架指南

[English](scaffolding-guide.md)

面向用户的指南，介绍如何使用 Bundles Forge 生成 bundle-plugin 项目和管理平台支持。涵盖模式选择、新建项目、平台适配、平台对比和常见陷阱。

## 概述

脚手架（scaffolding）负责两项相关工作：从设计蓝图生成新的 bundle-plugin 项目，以及管理现有项目的平台支持（添加、修复、迁移、移除）。它是**执行层**中的**执行器**：单一职责工作者，负责结构生成、平台适配与 inspector 自检。编排技能（`blueprinting`、`optimizing`）会在流水线中调度它，你也可以直接调用它进行平台操作与新建项目。

**重要性：** 良好的脚手架确保项目从第一天起就有正确的文件结构 — 清单、钩子、版本同步和引导。事后修复结构问题远比一开始做对要困难得多。

> **权威来源：** 完整的执行协议（生成步骤、平台适配流程、验证清单）在 `skills/scaffolding/SKILL.md` 中。本指南帮助你决定*选择哪种模式*和*预期什么结果* — 技能本身负责执行。

---

## 选择模式

脚手架支持三种模式。正确的选择取决于你的情况：

| 模式 | 适用场景 | 产出 | 平台 |
|------|---------|------|------|
| **Minimal** | 快速打包独立技能 | 插件清单 + 技能 + README + LICENSE | 仅 Claude Code |
| **Intelligent** | 大多数新项目 — Agent 推荐架构 | 基于描述生成完整项目 | 所选平台 |
| **Custom** | 你想显式控制每个组件 | 完整选项菜单逐一询问 | 所选平台 |

### 决策流程

```
你是否从 blueprinting 带着设计文档过来？
  ├─ 是 → 模式已确定（minimal 或 intelligent）
  └─ 否 → 这是新项目还是平台适配？
            ├─ 新项目 → 你想让 AI 推荐架构吗？
            │           ├─ 是 → Intelligent 模式
            │           └─ 否 → Custom 模式
            └─ 平台适配 → 见下方"平台适配"章节
```

### 端到端流程

所有六种脚手架操作都遵循相同的三阶段结构：检测上下文、生成/修改文件、验证输出。

| 操作 | 入口条件 | 阶段 1 | 阶段 2 | 阶段 3 |
|------|---------|--------|--------|--------|
| 新建项目（minimal） | 设计文档或用户 + 无项目 | 加载 Claude Code 模板 | 生成清单 + 技能 + 文档 | git init，验证 JSON |
| 新建项目（intelligent） | 设计文档或用户 + 无项目 | 加载模板索引、模板、项目结构参考 | 替换占位符，按平台生成，技能、命令、引导、可选组件 | git init，版本检查 |
| 新建项目（custom） | 用户 + 无项目 | 同 intelligent | 同上，但每个组件需交互确认 | git init，版本检查 |
| 添加平台 | 现有项目 + 目标平台 | 检测当前平台，读取适配器参考 | 生成适配器文件，更新版本同步 + 钩子 + 文档 | 验证清单，版本检查 |
| 移除平台 | 现有项目 + 目标平台 | 识别待移除文件 | 删除清单，清理钩子，更新文档 | 版本检查，inspector 验证 |
| 管理可选组件 | 现有项目 + 组件类型 | 读取 external-integration 决策树 | 生成/移除组件文件，更新清单 + 技能 + 文档 | inspector 验证 |

每次操作后，脚手架都会运行确定性检查（`bundles-forge audit-skill`）并调度 inspector 代理进行语义验证。

### Minimal 模式

最适合：将 1-3 个独立技能打包到市场发布，零基础设施开销。

**生成的文件：**

| 文件 | 用途 |
|------|------|
| `.claude-plugin/plugin.json` | Claude Code 插件身份 |
| `skills/<name>/SKILL.md` | 每个技能一个目录 |
| `README.md` | 安装说明和技能目录 |
| `LICENSE` | 默认 MIT |

无钩子、无引导、无版本基础设施。你可以稍后再次调用脚手架进行平台适配来添加这些。

### Intelligent 模式

最适合：大多数新项目。告诉 Agent 你在构建什么，它会推荐合适的组件 — 不过度工程化。

**预期体验：** Agent 会询问你在构建什么、使用哪些平台、有多少技能。根据你的回答，它只生成必要的内容 — 不引入不必要的可选组件。

**生成层次：**
1. **核心** — `package.json`、`.gitignore`、`.version-bump.json`、技能、命令
2. **平台适配器** — 仅针对所选平台（清单、钩子、安装文档）
3. **引导** — 如果有 3 个以上技能或工作流链
4. **可选组件** — 仅在 Agent 检测到需要时（MCP 服务器、LSP 服务器、可执行文件、输出样式、默认设置、用户配置、市场条目）

### Custom 模式

最适合：经验丰富的用户或非常规项目配置。

**预期体验：** Agent 展示完整的架构选项集，逐一询问每个组件。耗时更长但给予你完全控制。

---

## 新建项目：预期流程

### 从 Blueprinting 过来

如果你先运行了 `/bundles-blueprint`，设计文档已包含模式、平台、技能清单和组件选择。脚手架读取设计文档并自动生成一切 — 无需额外提问。

```
/bundles-blueprint
  → 访谈完成，设计批准
  → 脚手架自动调用（附带设计文档）
  → 项目生成
  → Inspector 验证结构（如子代理可用）
  → 编排技能（blueprinting 或 optimizing）负责后续步骤
```

### 直接调用

如果你直接调用脚手架（通过 `/bundles-scaffold` 或直接向 Agent 描述），它会检测是否存在项目：

- **无现有项目** → 进入新建项目流程，询问模式偏好
- **有现有项目** → 进入平台适配流程

### 脚手架后验证

生成后，脚手架会调度 **inspector 代理** 验证产出。Inspector 检查：

- 目录结构匹配目标平台
- 所有 JSON 清单可正常解析
- 版本同步配置覆盖所有版本承载文件
- 钩子脚本引用正确的引导路径
- 技能 frontmatter 遵循规范

如果子代理不可用，Agent 会提供内联运行验证的选项。

---

## 可选组件

大多数项目只需要核心文件和平台适配器。可选组件仅在设计文档指定或 Agent 在 intelligent/custom 模式中检测到明确需要时才会生成。

### 组件总览

| 组件 | 文件 | 何时包含 |
|------|------|---------|
| 可执行文件 | `bin/<tool-name>` | 技能引用需要加入 `$PATH` 的 CLI 工具 |
| MCP 服务器 | `.mcp.json` | 技能需要有状态连接、丰富发现或认证的外部服务 |
| LSP 服务器 | `.lsp.json` | 技能涉及语言级代码智能 |
| 输出样式 | `output-styles/<style>.md` | 自定义 Agent 响应的输出格式 |
| 默认设置 | `settings.json` | 插件根目录的默认 Agent 激活 |
| 用户配置 | `plugin.json` 中的 `userConfig` | 技能需要用户提供的 API 密钥、端点或令牌（仅 Claude Code） |
| 市场条目 | `.claude-plugin/marketplace.json` | 插件目标为市场发布 |

### 选择正确的集成级别

当技能需要访问外部工具时，选择能满足需求的最轻量集成：

```
技能是否需要外部工具访问？
├─ 否 → 无需集成
└─ 是 → 它是无状态、单次执行、输入输出明确的吗？
   ├─ 是 → Level 1: CLI（bin/ 可执行文件 + allowed-tools）
   └─ 否 → 它需要持久连接、丰富查询或认证服务吗？
      ├─ 是 → Level 2: MCP 服务器（.mcp.json）
      └─ 兼有 → Level 3: CLI 封装启动 MCP stdio 服务器
```

完整的决策树（含示例和平台特定的接线细节）详见脚手架技能中的 `references/external-integration.md`。

---

## 平台适配

使用脚手架在现有项目上添加或移除平台支持。这是最主要的直接调用场景。

### 添加平台

```
用户："给我的项目添加 Cursor 支持"
  → 脚手架检测到现有项目
  → 扫描当前平台清单
  → 从模板生成 Cursor 适配器文件
  → 更新 .version-bump.json
  → 更新钩子（如需要）
  → 在 README 中添加安装说明
  → 运行验证
```

### 移除平台

```
用户："移除 Codex 支持"
  → 脚手架检测到现有项目
  → 删除 Codex 清单文件（.codex/INSTALL.md）
  → 从 .version-bump.json 中移除条目
  → 清理平台特定的钩子配置
  → 从 README 中移除安装说明
  → 运行验证
```

### 管理可选组件

除了平台之外，脚手架还可以在现有项目上添加或移除可选组件。

**添加组件：**

```
用户："给我的项目添加 MCP 服务器支持"
  → 脚手架检测到现有项目
  → 参考 external-integration.md 决策树
  → 从模板生成 .mcp.json
  → 更新插件清单（Cursor 需要显式路径）
  → 更新技能 frontmatter（allowed-tools）
  → 在 README 中添加设置说明
  → 运行验证
```

**移除组件：**

脚手架可以移除 MCP 服务器、CLI 可执行文件或 LSP 服务器 — 包括在不再需要完整服务器时将 MCP 降级为更轻量的 CLI 替代方案。移除流程会清理清单条目、技能引用和文档。详见 `references/external-integration.md` 的逐步移除说明。

### 各平台生成的文件

| 平台 | 清单 | 钩子 | 安装文档 | 版本追踪 |
|------|------|------|---------|:--------:|
| Claude Code | `.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`（可选） | `hooks/hooks.json` + 共享钩子 | — | 是 |
| Cursor | `.cursor-plugin/plugin.json` | `hooks/hooks-cursor.json` + 共享钩子 | — | 是 |
| Codex | — | — | `.codex/INSTALL.md` | 否 |
| OpenCode | `.opencode/plugins/<name>.js` | —（JS 插件处理引导） | `.opencode/INSTALL.md` | 否 |
| Gemini CLI | `gemini-extension.json` | — | `GEMINI.md` | 是 |

**共享钩子：** `hooks/session-start.py` 在 Claude Code 和 Cursor 之间共享。当任一平台被选为目标时都会创建。使用 Python 实现以确保跨平台兼容性。

**`marketplace.json`：** 仅在插件目标为市场发布时生成。它声明市场索引的插件元数据，并通过 `.version-bump.json` 进行版本追踪。

**`AGENTS.md`：** 如果项目根目录还没有 `AGENTS.md`，脚手架会生成一个指向 `CLAUDE.md` 的轻量级版本。该文件是共享的项目文档（被 Codex 和其他平台使用），而非某个平台的专属安装产物 — 移除单个平台时不应删除它。

**钩子配置特性：** Claude Code 的 `hooks.json` 支持顶层 `description` 字段（显示在 `/hooks` 菜单中）和每个 handler 的 `timeout`（默认 600 秒 — 快速引导钩子建议设为 10）。详见 `platform-adapters.md` 的完整字段参考和 Claude vs Cursor 对比表。

---

## 平台对比

理解平台差异有助于选择支持哪些平台。

### 发现机制

| 平台 | 技能发现方式 | 引导工作方式 |
|------|------------|------------|
| Claude Code | 约定 — 自动发现 `skills/`、`agents/`、`commands/` | Shell 钩子在 `SessionStart` 时输出 JSON |
| Cursor | 在 `plugin.json` 中显式声明路径 | 相同的 Shell 钩子，不同的 JSON 格式 |
| Codex | 符号链接到 `~/.agents/skills/` | `AGENTS.md` → `CLAUDE.md`（无钩子注入） |
| OpenCode | JS 插件在配置中注册路径 | JS 插件将内容前置到第一条用户消息 |
| Gemini CLI | `GEMINI.md` 上下文文件使用 `@` 引用 | `@` 语法在会话启动时拉取技能内容 |

### 关键差异

| 方面 | Claude Code | Cursor |
|------|------------|--------|
| 钩子事件大小写 | `SessionStart`（PascalCase） | `sessionStart`（camelCase） |
| 钩子重注入 | 在 `startup\|clear\|compact` 时触发 | 仅在 `sessionStart` — 上下文清除后不重注入 |
| 清单路径 | 基于约定（无需声明） | 必须显式声明 `skills`、`agents`、`commands`、`hooks` |

### 平台限制

- **Codex** 没有基于钩子的引导注入。用户完全依赖基于描述的技能匹配。
- **Cursor** 在会话中途清除上下文后不会重新注入引导。
- **OpenCode** 的引导通过 JS 转换注入，而非 Shell 钩子。

### 插件缓存

当插件通过市场安装时，它会被复制到平台管理的缓存目录。这对脚手架有重要影响：

- **`${CLAUDE_PLUGIN_ROOT}`** 指向缓存副本，每次插件更新都会变化。不要用于持久化存储。
- **`${CLAUDE_PLUGIN_DATA}`** 是稳定的持久化目录，用于缓存、已安装的依赖和生成的状态。需要跨插件更新保留的数据都应存放在这里。
- **禁止 `../` 路径** — 市场安装后，插件被隔离在缓存目录中。引用插件根目录外的文件路径（如 `../shared-lib/`）会失效。所有文件必须保持在插件根目录内。

这些约束适用于通过市场分发的插件。开发安装（`claude --plugin-dir .`）直接使用项目目录。

---

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 不管需要与否生成所有平台 | 想要面面俱到 | 只为你实际使用的平台生成 |
| 忘记 `.version-bump.json` 条目 | 手动添加了新清单 | 每个版本承载清单都需要 bump 配置条目 |
| 钩子大小写错误 | 从一个平台复制到另一个 | Claude Code: `SessionStart`，Cursor: `sessionStart` |
| 引导技能超过 200 行 | 路由表塞了太多内容 | 保持精简 — 重内容提取到 `references/` |
| 对简单打包使用 intelligent 模式 | 想为 1-2 个技能搭建完整基础设施 | Minimal 模式就是为了避免过度工程化 |
| PATH 中缺少 `python` | 钩子无法运行 | 确保 `session-start.py` 可被 `python` 调用 — 记录前置要求 |
| CLI 就够时使用 MCP | 想为简单工具搭建丰富集成 | 参考 `references/external-integration.md` 决策树 — 无状态单次工具优先用 CLI |
| 使用 `../` 路径引用插件外的文件 | 想跨项目共享文件 | 市场安装后插件被缓存 — `../` 路径会失效。所有文件保持在插件根目录内 |
| 向 `${CLAUDE_PLUGIN_ROOT}` 写入持久化数据 | 把插件根目录当作稳定存储 | `PLUGIN_ROOT` 每次更新会变。使用 `${CLAUDE_PLUGIN_DATA}` 存放缓存和生成状态 |

---

## 常见问题

**问：我用 minimal 模式搭建了项目，现在需要钩子和版本基础设施。需要重来吗？**

不需要。再次调用脚手架 — 它会检测到现有项目并提供平台适配。你可以增量添加任何平台及其关联基础设施。

**问：可以一次添加多个平台吗？**

可以。添加平台时，你可以指定多个目标，脚手架会一次性生成所有适配器文件。

**问：脚手架和蓝图有什么区别？**

蓝图（blueprinting）是*规划*阶段 — 通过访谈产出设计文档。脚手架（scaffolding）是*执行*阶段 — 读取设计并生成实际文件。对于现有项目的平台适配，你完全跳过蓝图，直接调用脚手架。

**问：我手动添加了一个平台。如何验证设置是否正确？**

运行 `/bundles-audit` — 审计技能会检查清单有效性、版本同步、钩子配置和交叉引用。或者调用脚手架让 inspector 代理验证。

---

## 相关技能

| 技能 | 关系 |
|------|------|
| `bundles-forge:blueprinting` | 上游 — 规划新项目，然后调度脚手架生成结构 |
| `bundles-forge:optimizing` | 上游 — 调度脚手架进行平台覆盖改进 |
| `bundles-forge:authoring` | 下游 — 脚手架完成后编写技能与代理内容（`SKILL.md`、`agents/*.md`） |
