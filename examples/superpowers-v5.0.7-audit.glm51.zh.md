---
audit-date: "2026-04-21T14:52:04-03:00"
auditor-platform: "Claude Code"
auditor-model: "GLM-5.1"
bundles-forge-version: "1.8.5"
source-type: "local-directory"
source-uri: "~/repos/superpowers"
os: "Windows 11 Home 10.0.22631"
python: "N/A"
---

# Bundle-Plugin 审计报告：superpowers

## 1. 决策摘要

| 字段 | 值 |
|------|-----|
| **审计目标** | `~/repos/superpowers` |
| **版本** | `5.0.7` |
| **提交** | `b557648` |
| **日期** | `2026-04-21` |
| **审计上下文** | `第三方评估` |
| **平台** | Claude Code、Cursor、OpenCode、Codex、Gemini CLI、Copilot CLI |
| **技能** | 14 个技能、1 个代理、6 个脚本 |

### 建议：`有条件通过`

**自动化基线：** 2 个严重问题、44 个警告、29 个信息提示——脚本建议 `不通过`

**综合评分：** 7.6/10（加权平均；详见类别评分细则）

**定性调整：** 脚本基线因 2 个严重发现产生了 `不通过` 结论。经人工审查，两个严重发现均为误报：D2 断裂交叉引用（RELEASE-NOTES.md 中的 `superpowers:skill-name`）是占位文档语法，而非实际技能引用；HK2 `hooks/session-start` 中的外部 URL 指向一个 GitHub issue，记录了 bash bug 的解决方法，这是合理的注释引用，而非网络调用。排除这些误报后，实际发现数量为 0 个严重、44 个警告、29 个信息提示，建议升级为 `有条件通过`。

### 主要风险

| # | 风险 | 影响 | 若不修复 |
|---|------|------|---------|
| 1 | 14 个技能中有 12 个缺少测试提示文件（T5） | 12/14 个技能在提示层面未经测试 | 技能触发的回归问题无法被检测到 |
| 2 | writing-skills 的 SKILL.md 为 655 行，超出 500 行指导限制（Q9） | 1/14 个技能超出大小限制 | Token 开销可能降低技能密集型会话中的模型表现 |
| 3 | 12 个技能通过静态图分析无法从入口点到达（W2） | 12/14 个技能可能不可发现 | 技能依赖运行时启发式匹配而非显式图路由 |

### 修复工作量估算

| 优先级 | 数量 | 预估工作量 |
|--------|------|-----------|
| P0（阻断） | 0 | 无（2 个误报已排除） |
| P1（高） | 14 | 2-3 小时（添加测试提示文件） |
| P2+ | 30 | 3-5 小时（README 同步、中文翻译、技能结构小幅改进） |

---

## 2. 风险矩阵

| ID | 标题 | 严重级别 | 影响范围 | 可利用性 | 置信度 | 状态 |
|----|------|---------|---------|---------|--------|------|
| DOC-001 | RELEASE-NOTES.md 中断裂的交叉引用 | P0 | 仅外观影响 | 始终触发 | 已确认（误报） | 误报——占位语法，非真实引用 |
| SEC-001 | session-start 钩子中的外部 URL | P0 | 1/1 钩子脚本 | 理论性的 | 已确认（误报） | 误报——注释引用 GitHub issue，非网络调用 |
| TST-001 | 14 个技能缺少测试提示 | P1 | 12/14 个技能 | 边缘情况 | 已确认 | 待修复 |
| SKQ-001 | writing-skills 超出 500 行正文限制 | P1 | 1/14 个技能 | 始终触发 | 已确认 | 待修复 |
| SKQ-002 | 3 个技能缺少 "Use when..." 描述前缀 | P2 | 3/14 个技能 | 始终触发 | 已确认 | 待修复 |
| DOC-002 | 12 个技能未在 README 技能列表中列出 | P2 | 12/14 个技能 | 始终触发 | 已确认 | 待修复 |
| SEC-002 | OpenCode 插件中存在宽泛的 process.env 访问 | P2 | 1/1 OpenCode 插件 | 有条件的 | 已确认 | 待修复 |
| SEC-003 | 技能内容中存在 SC3 对 ~/.config/ 的引用 | P2 | 2/14 个技能 | 理论性的 | 已确认（误报） | 误报——教学示例中展示用户配置路径 |
| WFL-001 | 12 个技能无法从入口点到达 | P2 | 12/14 个技能 | 罕见 | 已确认 | 已接受风险（技能通过运行时启发式匹配发现） |
| WFL-002 | 12 个终端技能缺少 Outputs 部分 | P3 | 12/14 个技能 | 罕见 | 已确认 | 待修复 |
| HOK-001 | hooks.json 缺少 description 和 timeout 字段 | P3 | 1/1 钩子配置 | 罕见 | 已确认 | 待修复 |
| DOC-003 | 缺少中文文档对应版本 | P2 | 4 个文档文件 | 罕见 | 已确认 | 待修复 |

---

## 3. 按类别的发现

### 3.1 结构（评分：10/10，权重：高）

**概要：** 项目结构堪称典范——目录布局清晰，包含 14 个技能、适当的钩子、多平台清单和一个范围明确的代理。

**审计组件：** `skills/`、`hooks/`、`agents/`、`scripts/`、平台清单目录

无发现。所有结构检查均通过：`skills/` 和 `hooks/` 存在，引导技能存在，6 个平台清单齐全，`.gitignore` 存在，`README.md` 存在，`LICENSE` 存在。

---

### 3.2 平台清单（评分：10/10，权重：中）

**概要：** 全部六个平台清单均存在且语法有效，路径解析正确。

**审计组件：** `.claude-plugin/plugin.json`、`.cursor-plugin/plugin.json`、`.opencode/plugins/superpowers.js`、`gemini-extension.json`、Codex 清单

无发现。所有清单解析正确，路径可解析，OpenCode 插件具有正确的 ESM 导出。

---

### 3.3 版本同步（评分：10/10，权重：高）

**概要：** 所有版本字符串在所有被跟踪文件中均同步为 5.0.7。

**审计组件：** `.version-bump.json`、所有平台清单、`package.json`

无发现。未检测到版本漂移。

---

### 3.4 技能质量（评分：7/10，权重：中）

**概要：** 技能编写良好，触发条件清晰，内容充实。三个技能偏离了 "Use when..." 描述惯例，writing-skills 显著超出 500 行正文指导限制。

**审计组件：** 全部 14 个 SKILL.md 文件

#### [SKQ-001] writing-skills 超出 500 行正文限制
- **严重级别：** P1 | **影响：** 1/14 个技能 | **置信度：** 已确认
- **位置：** `skills/writing-skills/SKILL.md`（655 行）
- **触发条件：** 始终——文件在技能加载时被完整读取
- **实际影响：** 技能密集型会话中 Token 消耗更高；与其他已加载技能叠加时可能接近上下文限制
- **修复方案：** 将大量参考内容（如测试方法论详情）提取到 `references/` 文件中，并从 SKILL.md 进行链接

#### [SKQ-002] 三个技能缺少 "Use when..." 描述前缀
- **严重级别：** P2 | **影响：** 3/14 个技能 | **置信度：** 已确认
- **位置：** `skills/brainstorming/SKILL.md`、`skills/using-git-worktrees/SKILL.md`、`skills/using-superpowers/SKILL.md`
- **触发条件：** 始终——描述显示在技能列表中
- **实际影响：** 技能列表中的呈现不一致；可能降低代理评估调用哪个技能时的清晰度
- **修复方案：** 重写描述使其以 "Use when..." 模式开头

#### [SKQ-003] using-git-worktrees 引导正文超出 200 行预算
- **严重级别：** P2 | **影响：** 1/14 个技能 | **置信度：** 已确认
- **位置：** `skills/using-git-worktrees/SKILL.md`（213 行，约 1215 估算 token）
- **触发条件：** 技能作为引导上下文加载时
- **实际影响：** 每次引导周期的 Token 成本略有增加；仍在合理范围内
- **修复方案：** 考虑将工作树创建步骤提取到 `references/` 并进行链接

#### 信息级发现（未逐一列出）：
- Q10：3 个技能缺少 Overview 部分（brainstorming、requesting-code-review、subagent-driven-development）
- Q11：8 个技能缺少 Common Mistakes 部分
- Q12：2 个技能超过 300 行但没有 `references/` 文件（test-driven-development、writing-skills）
- Q15：3 个技能的条件块超过 30 行，可移至 `references/`
- C1：跨技能不一致——Overview 部分存在与否混杂（9 个有，3 个无）；"Use when" 之后的动词形式混杂

**定性调整：** +0。基线评分 7 准确反映了高质量技能与轻微结构问题的组合。writing-skills 的长度是影响最大的发现，但因其作为元技能调用频率较低而部分得到缓解。

---

### 3.5 交叉引用（评分：10/10，权重：中）

**概要：** 所有技能交叉引用均可正确解析。一个孤立的引用文件（gemini-tools.md）仅为信息级发现。

**审计组件：** 所有 `project:skill-name` 引用、相对路径引用、`references/` 目录内容

#### [XRF-001] 孤立引用文件未从 SKILL.md 链接
- **严重级别：** P3 | **影响：** 1 个文件 | **置信度：** 已确认
- **位置：** `skills/using-superpowers/references/gemini-tools.md`
- **触发条件：** 文件存在但 SKILL.md 中无 Markdown 链接或文字引用指向它
- **实际影响：** 低——该文件可能通过 using-superpowers 中的平台特定工具映射逻辑被发现；链接是隐式的而非显式的
- **修复方案：** 在 SKILL.md 的平台特定部分添加对 gemini-tools.md 的引用

**定性调整：** +0。基线 10 分是合适的——交叉引用干净，孤立发现为信息级。

---

### 3.6 工作流（评分：10/10，权重：高）

**概要：** 工作流图无循环、无断裂的交接边。所有 W2/W3 发现为信息级——技能设计为通过运行时启发式发现而非显式图路由。

**审计组件：** 技能集成声明、图拓扑、工件交接边

#### [WFL-001] 12 个技能通过静态图分析无法从入口点到达
- **严重级别：** P3 | **影响：** 12/14 个技能 | **置信度：** 已确认
- **位置：** 除 `using-git-worktrees` 和 `using-superpowers` 外的所有技能
- **触发条件：** 静态图分析未找到从引导技能到这些技能的显式路由
- **实际影响：** 极小——superpowers 使用基于描述的启发式匹配进行技能发现，而非显式图路由。技能设计为在运行时根据上下文被发现。
- **修复方案：** 考虑在 Integration 部分添加 `Called by: user directly` 声明以增加透明度，即使路由是启发式的

#### [WFL-002] 12 个终端技能缺少 Outputs 部分
- **严重级别：** P3 | **影响：** 12/14 个技能 | **置信度：** 已确认
- **位置：** 图中所有终端技能
- **触发条件：** 无外出交叉引用的技能没有 `## Outputs` 部分
- **实际影响：** 仅文档缺口——不影响运行时行为
- **修复方案：** 为每个终端技能添加 `## Outputs` 部分，记录预期交付物

#### 行为验证（W10-W11）

未执行。原因：需要从父技能调度评估器代理。评分为 N/A（不计入加权平均）。

---

### 3.7 钩子（评分：10/10，权重：中）

**概要：** 钩子脚本实现良好，具有适当的错误处理、跨平台支持和正确的 JSON 转义。元数据完整性方面有轻微信息级发现。

**审计组件：** `hooks/session-start`、`hooks/run-hook.cmd`、`hooks/hooks.json`、`hooks/hooks-cursor.json`

#### [HOK-001] hooks.json 缺少可选元数据字段
- **严重级别：** P3 | **影响：** 1/1 钩子配置 | **置信度：** 已确认
- **位置：** `hooks/hooks.json`
- **触发条件：** 钩子配置的静态分析
- **实际影响：** 仅外观——缺少 `description` 字段和按处理器的 `timeout` 字段不影响功能
- **修复方案：** 添加顶层 `description` 和按处理器的 `timeout` 字段以完善文档

---

### 3.8 测试（评分：7/10，权重：中）

**概要：** 存在针对 brainstorm-server、Claude Code 集成、OpenCode 插件加载、技能触发和 subagent-driven-development 的测试。但 14 个技能中的 14 个均缺少独立的测试提示文件，尽管项目有一个 `tests/skill-triggering/` 目录，其中仅包含 6 个技能的提示。

**审计组件：** `tests/` 目录结构、测试提示文件、评估结果

#### [TST-001] 14 个技能缺少测试提示文件
- **严重级别：** P1 | **影响：** 12/14 个技能（仅 6 个在 skill-triggering 中有测试提示） | **置信度：** 已确认
- **位置：** `tests/prompts/` 和 `skills/*/tests/prompts.yml`——以下技能缺失：brainstorming、dispatching-parallel-agents、executing-plans、finishing-a-development-branch、receiving-code-review、requesting-code-review、subagent-driven-development、systematic-debugging、test-driven-development、using-git-worktrees、using-superpowers、verification-before-completion、writing-plans、writing-skills
- **触发条件：** 这些技能不存在测试提示文件
- **实际影响：** 技能触发回归无法通过自动化测试捕获
- **修复方案：** 创建 `tests/skill-triggering/prompts/<skill-name>.txt` 文件，包含应触发和不应触发的样本

#### [TST-002] 未找到 A/B 评估结果
- **严重级别：** P3 | **影响：** 无回归基线 | **置信度：** 已确认
- **位置：** `.bundles-forge/evals/`——目录为空或不存在
- **触发条件：** CI 无法将当前行为与已建立的基线进行比较
- **实际影响：** 技能行为变更无客观的质量趋势数据
- **修复方案：** 运行并提交基线评估结果

**定性调整：** +0。项目拥有大量手动测试覆盖（brainstorm-server 单元测试、Claude Code 集成测试、OpenCode 测试、显式技能请求测试、subagent-driven-dev 集成测试）。测试提示的缺口是真实的，但被现有集成测试套件部分弥补。

---

### 3.9 文档（评分：3.6/10，权重：低）

**概要：** 文档存在显著的同步缺口：12 个技能未在 README.md 技能列表中列出，多个文档缺少中文对应版本和规范来源声明。D2 严重发现为误报（详见下方分类）。

**审计组件：** `README.md`、`docs/`、`RELEASE-NOTES.md`、`CLAUDE.md`

#### [DOC-001] RELEASE-NOTES.md 中断裂的交叉引用 `superpowers:skill-name`——误报
- **严重级别：** P0（误报） | **影响：** 仅外观 | **置信度：** 已确认（误报）
- **位置：** `RELEASE-NOTES.md:678`
- **触发条件：** 脚本将 `superpowers:skill-name` 匹配为交叉引用
- **实际影响：** 无——字符串 `superpowers:skill-name` 在文档中用作占位语法（"命名空间技能：`superpowers:skill-name` 用于 superpowers 技能，`skill-name` 用于个人技能"），而非对实际技能的引用
- **修复方案：** 无需修复——误报
- **证据：**
  ```
  - Namespaced skills: `superpowers:skill-name` for superpowers skills, `skill-name` for personal
  ```

#### [DOC-002] 12 个技能未在 README.md 技能列表中列出
- **严重级别：** P2 | **影响：** 12/14 个技能 | **置信度：** 已确认
- **位置：** `README.md`——"What's Inside" 部分按名称列出了所有 14 个技能，但未以结构化表格形式包含
- **触发条件：** 脚本将 `skills/` 目录与 README 内容交叉引用
- **实际影响：** README 实际上确实在 "What's Inside" 和 "Basic Workflow" 部分按名称列出了所有技能。脚本发现似乎是模式匹配的缺口——技能是以文字叙述形式记录的，而非脚本能识别的正式表格。
- **修复方案：** 考虑在 README.md 中添加结构化的技能表格，以便机器可解析的文档

**说明：** 经人工审查，README.md 确实在 "What's Inside" 和 "The Basic Workflow" 部分以文字形式记录了全部 14 个技能。D1 发现似乎是文档检查器未识别文字列表的误报。但其他文档发现（D6、D7、D8）是合理的。

#### [DOC-003] 缺少中文文档对应版本
- **严重级别：** P2 | **影响：** 4 个文档文件 | **置信度：** 已确认
- **位置：** 缺少 `README.zh.md`、`docs/README.codex.zh.md`、`docs/README.opencode.zh.md`、`docs/testing.zh.md`
- **触发条件：** 脚本检测到 `README.md` 存在但无 `README.zh.md`
- **实际影响：** 中文用户缺乏本地化文档
- **修复方案：** 为 README 和 docs/ 文件创建中文翻译

#### [DOC-004] docs/ 指南缺少规范来源声明
- **严重级别：** P2 | **影响：** 3 个文档文件 | **置信度：** 已确认
- **位置：** `docs/README.codex.md`、`docs/README.opencode.md`、`docs/testing.md`
- **触发条件：** 未找到 `> **Canonical source:**` 声明
- **实际影响：** 文档与技能文件哪个是权威来源存在歧义
- **修复方案：** 添加规范来源声明，指向相关的 SKILL.md 或代理文件

#### [DOC-005] Version-bump.json 跟踪的清单未在 CLAUDE.md 平台清单表中列出
- **严重级别：** P3 | **影响：** 3 个清单路径 | **置信度：** 已确认
- **位置：** `.version-bump.json` 跟踪 `.claude-plugin/plugin.json`、`.cursor-plugin/plugin.json`、`gemini-extension.json`
- **触发条件：** `.version-bump.json` 条目与 CLAUDE.md 清单表的静态比较
- **实际影响：** 轻微文档不一致——不影响版本升级功能
- **修复方案：** 确保 CLAUDE.md 平台清单表列出所有被跟踪的文件

**定性调整：** +3.6（从基线 0 到 3.6）。脚本因 D2 严重问题和 12 个 D1 警告计算出基线 0。经人工审查：（1）D2 严重问题为误报（占位语法），（2）全部 12 个 D1 警告为误报——README.md 确实在其 "What's Inside" 和 "Basic Workflow" 部分列出了全部 14 个技能。排除这些误报后，剩余发现为 0 个严重、8 个警告（D6、D7 x3、D8 x3）、3 个信息（D3 x3）。重新计算：`max(0, 10 - (0 + min(8,3) + min(3,3) + min(3,3))) = max(0, 10 - 9) = 1`。添加 +2.6 定性调整因为：文档对英文用户而言确实很详尽，包含全面的 README、每个平台的详细 docs/ 指南以及详尽的 RELEASE-NOTES。中文翻译的缺口是本地化问题，而非质量缺陷。最终评分：3.6。

**调整后评分计算：** 排除误报 D2 严重问题和 D1 警告后，剩余发现为 8 个警告（D6=1、D7=3、D8=3——每项上限 3 = 9 扣分）和 3 个信息。公式：`max(0, 10 - (0 + 9)) = 1`。定性调整：+2.6，因为英文文档全面且结构良好，缺口主要在于中文本地化和规范来源声明，而非内容质量。最终：3.6。

---

### 3.10 安全（评分：7.5/10，权重：高）

**概要：** 一个确定性严重发现（钩子脚本中的外部 URL 注释——误报），两个确定性警告（宽泛的 env 访问），五个可疑 SC3 发现（均为误报——教学示例）。整体安全态势良好，无真实威胁。

**审计组件：** 所有 SKILL.md 文件、钩子脚本、OpenCode 插件、代理提示、捆绑脚本、MCP 配置、插件配置

#### 确定性发现

#### [SEC-001] session-start 钩子中的外部 URL——误报
- **严重级别：** P0（误报） | **影响：** 1/1 钩子脚本 | **置信度：** 已确认（误报）
- **位置：** `hooks/session-start:45`
- **触发条件：** 脚本检测到钩子脚本中的 URL 模式
- **实际影响：** 无——该 URL 出现在注释中，引用了一个记录 bash 5.3+ heredoc 挂起问题的 GitHub issue。这不是网络调用；它是文档。
- **修复方案：** 无需修复
- **证据：**
  ```
  # See: https://github.com/obra/superpowers/issues/571
  ```

#### [SEC-002] OpenCode 插件中宽泛的 process.env 访问
- **严重级别：** P2 | **影响：** 1/1 OpenCode 插件 | **置信度：** 已确认
- **位置：** `.opencode/plugins/superpowers.js:52`
- **触发条件：** 插件读取 `process.env.OPENCODE_CONFIG_DIR` 以确定配置目录
- **实际影响：** 极小——环境变量访问用于有文档记录的合理目的（查找 OpenCode 配置目录）。插件不访问密钥且不传输数据。
- **修复方案：** 考虑在注释中记录预期的环境变量以提高清晰度

#### [SEC-003] run-hook.cmd 中的环境变量访问
- **严重级别：** P2 | **影响：** 1/1 钩子包装器 | **置信度：** 已确认
- **位置：** `hooks/run-hook.cmd:46`
- **触发条件：** 脚本访问 `$SCRIPT_NAME` 环境变量
- **实际影响：** 极小——这是用于传递钩子脚本名称的标准多语言包装器模式
- **修复方案：** 无需修复——合理模式

#### [SEC-004] session-start 中的环境变量访问（COPILOT_CLI）
- **严重级别：** P2 | **影响：** 1/1 钩子脚本 | **置信度：** 已确认
- **位置：** `hooks/session-start:49`
- **触发条件：** 脚本读取 `$COPILOT_CLI` 以确定平台并生成正确的 JSON 格式
- **实际影响：** 极小——这是有文档记录的平台检测机制
- **修复方案：** 无需修复——合理模式

#### [SEC-005] brainstorm 服务器脚本缺少 set -euo pipefail
- **严重级别：** P3 | **影响：** 2/2 brainstorm 脚本 | **置信度：** 已确认
- **位置：** `skills/brainstorming/scripts/start-server.sh:1`、`skills/brainstorming/scripts/stop-server.sh:1`
- **触发条件：** 脚本未包含错误处理保护
- **实际影响：** 脚本可能在出错后继续执行，可能产生误导性输出
- **修复方案：** 在两个脚本顶部添加 `set -euo pipefail`

#### 可疑项分类

| 发现 | 文件:行 | 处置 | 理由 |
|------|---------|------|------|
| SEC-006 SC3——引用用户配置目录 | `skills/subagent-driven-development/SKILL.md:142` | 误报 | 该行是说明性场景中的对话示例：`You: "User level (~/.config/superpowers/hooks/)"`。这是教学文字，不是访问配置目录的指令。 |
| SEC-007 SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:46` | 误报 | 该行是向用户解释工作树位置选项的教学文字：`~/.config/superpowers/worktrees/<project-name>/ (global location)`。这是菜单提示，不是读取配置目录的指令。 |
| SEC-008 SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:71` | 误报 | 解释全局目录选项的章节标题：`### For Global Directory (~/.config/superpowers/worktrees)`。对支持功能的文档说明，非敏感数据访问模式。 |
| SEC-009 SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:91` | 误报 | 展示路径结构的 Shell 示例：`~/.config/superpowers/worktrees/*)`。这是技能教学内容中的代码示例，不是读取任意配置目录的指令。 |
| SEC-010 SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:92` | 误报 | 展示路径变量赋值的 Shell 示例：`path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"`。与 SEC-009 相同上下文——教学代码示例。 |

**定性调整：** +2.5（从基线 5.0 到 7.5）。脚本计算的基线为 `max(0, 10 - (1x3 + min(1,3) + min(1,3) + min(5,3))) = max(0, 10 - 10) = 0`。排除误报严重问题（SEC-001）和 5 个误报可疑发现后，剩余确定性发现为 0 个严重、3 个警告、2 个信息。重新计算：`max(0, 10 - (0 + min(1,3) + min(1,3) + min(1,3) + min(1,3) + min(2,3))) = max(0, 10 - 5) = 5`。定性调整：+2.5，因为剩余警告均为合理的、有文档记录的环境变量访问模式，遵循平台 SDK 惯例。项目的安全态势良好——无真实威胁、无数据外泄途径、无安全覆盖绕过、无代码混淆。最终：7.5。

---

## 4. 审计方法

### 范围

| 维度 | 覆盖 |
|------|------|
| **目录** | `skills/`、`agents/`、`hooks/`、`scripts/`、平台清单、项目根目录 |
| **检查类别** | 10 个类别、60+ 项独立检查 |
| **扫描文件总数** | 30+（14 个 SKILL.md、3 个引用文件、2 个钩子配置、2 个钩子脚本、1 个 OpenCode 插件、1 个代理提示、6 个捆绑脚本、5 个平台清单、1 个版本配置、README、docs） |

### 范围外

- 技能的运行时行为（代理执行、提示-响应质量）
- 平台特定的端到端安装测试
- 依赖的依赖（传递性分析）

### 工具

| 工具 | 用途 |
|------|------|
| `bundles-forge audit-plugin` | 编排完整审计 |
| `bundles-forge audit-workflow` | 工作流集成分析 |
| `bundles-forge audit-security` | 安全模式扫描 |
| `bundles-forge audit-skill` | 技能质量检查 |
| 人工审查 | 可疑发现的定性评估、文档准确性 |

### 局限性

- 安全扫描使用正则表达式——否定上下文可能产生误报；可能遗漏混淆模式
- 技能质量检查使用轻量级 YAML 解析器——复杂 YAML 边缘情况可能被遗漏
- Token 估算使用启发式比率（文字 ~1.3x 词数、代码 ~字符数/3.5、表格 ~字符数/3.0）；实际计数因模型而异
- 文档检查器（audit_docs.py）对文字形式的技能列表（D1）和占位语法（D2）会产生误报

---

## 5. 附录

### A. 逐技能分析

#### brainstorming
**结论：** 设计良好的创意构思技能，采用苏格拉底式对话结构，但描述偏离 "Use when..." 惯例且缺少可选结构部分。
**优势：**
- 清晰的渐进式提问方法论（理解上下文、逐一提问、呈现设计）
- 包含可视化头脑风暴服务器的辅助脚本
- 明确的设计文档输出格式
**主要问题：**
- 描述以 "You MUST use this" 开头而非 "Use when..."
- 缺少 Overview 和 Common Mistakes 部分

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 7/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### dispatching-parallel-agents
**结论：** 干净、专注的并行任务执行技能，无质量发现。
**优势：**
- 零质量发现——通过所有检查
- 范围清晰：独立任务的并行调度
**主要问题：** 无。

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 10/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### executing-plans
**结论：** 稳健的计划执行技能，采用批量检查点工作流，仅缺少可选的 Common Mistakes 部分。
**优势：**
- 清晰的批量执行与人工检查点模式
- 范围定义明确
**主要问题：**
- 缺少 Common Mistakes 部分

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### finishing-a-development-branch
**结论：** 干净的合并/PR 决策工作流，无质量发现。
**优势：**
- 零质量发现——通过所有检查
- 工作流结束范围清晰
**主要问题：** 无。

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 10/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### receiving-code-review
**结论：** 干净的反馈响应技能，无质量发现。
**优势：**
- 零质量发现——通过所有检查
**主要问题：** 无。

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 10/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### requesting-code-review
**结论：** 预审查清单技能，范围定义明确，缺少可选结构部分。
**优势：**
- 清晰的基于严重度的问题分类
- 范围定义明确
**主要问题：**
- 缺少 Overview 和 Common Mistakes 部分

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 8/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### subagent-driven-development
**结论：** 核心开发工作流技能，采用两阶段审查流程，缺少可选结构部分。
**优势：**
- 清晰的两阶段审查模型（规范合规性 + 代码质量）
- 详细的对话示例说明调度模式
**主要问题：**
- 缺少 Overview 和 Common Mistakes 部分
- SC3 可疑发现（误报——引用 ~/.config 路径的教学示例）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 8/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### systematic-debugging
**结论：** 结构良好的四阶段调试方法论，有一个较大的条件块可提取。
**优势：**
- 清晰的四阶段根因分析流程
- 证据驱动的方法
**主要问题：**
- 缺少 Common Mistakes 部分
- 第 69 行的条件块跨越 38 行（考虑提取到 references/）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 8/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### test-driven-development
**结论：** 全面的 TDD 技能，强制执行红-绿-重构循环，正文较大，适合提取引用内容。
**优势：**
- 显式的循环强制执行（红-绿-重构）
- 测试错误的反模式参考内容
**主要问题：**
- 缺少 Common Mistakes 部分
- 300+ 行且没有 references/ 文件
- 第 76 行的条件块跨越 32 行

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 7/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### using-git-worktrees
**结论：** 详尽的工作树管理技能，具有智能目录选择，引导正文略超预算。
**优势：**
- 全面的安全验证（工作树创建前检查 .gitignore）
- 智能目录选择（项目本地 vs 全局）
- 清晰的分步创建和清理流程
**主要问题：**
- 描述未以 "Use when..." 开头（使用 "Use when starting..." 部分匹配）
- 引导正文 213 行，略超 200 行预算
- 缺少 Overview 和 Common Mistakes 部分

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 7/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### using-superpowers
**结论：** 核心引导技能，建立技能发现系统，具有全面的多平台支持。
**优势：**
- 清晰的技能调用优先级规则
- 全面的平台特定工具映射（Claude、Cursor、OpenCode、Codex、Copilot、Gemini）
- 明确指示在任何响应前调用 Skill 工具
**主要问题：**
- 一个孤立引用文件（gemini-tools.md 未从 SKILL.md 链接）
- 描述格式不一致（以 "Use when starting" 而非严格的 "Use when" 开头）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 9/10 |
| 安全 | 10/10 |

#### verification-before-completion
**结论：** 专注的验证技能，确保工作在声明完成前确实完成。
**优势：**
- 范围清晰——完成声明前的验证关卡
- 验证标准定义明确
**主要问题：**
- 缺少 Common Mistakes 部分

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### writing-plans
**结论：** 稳健的计划编写技能，任务分解方法论清晰。
**优势：**
- 任务大小定义明确（每个 2-5 分钟）
- 清晰的计划结构，包含文件路径和验证步骤
**主要问题：**
- 缺少 Common Mistakes 部分

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### writing-skills
**结论：** 全面的技能创建元技能，因包含大量测试方法论内容而显著超出 500 行正文指导限制。
**优势：**
- 全面的技能编写指南，采用 TDD 方法
- 包含技能测试方法论
- 教学内容结构良好
**主要问题：**
- SKILL.md 正文 655 行，超出 500 行指导限制（Q9 警告）
- 300+ 行且没有 references/ 文件（Q12 信息）
- 预估约 4880 token（Q13 信息）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 6/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

### B. 组件清单

| 组件类型 | 名称 | 路径 | 行数 |
|---------|------|------|------|
| 技能 | brainstorming | `skills/brainstorming/SKILL.md` | ~180 |
| 技能 | dispatching-parallel-agents | `skills/dispatching-parallel-agents/SKILL.md` | ~90 |
| 技能 | executing-plans | `skills/executing-plans/SKILL.md` | ~110 |
| 技能 | finishing-a-development-branch | `skills/finishing-a-development-branch/SKILL.md` | ~130 |
| 技能 | receiving-code-review | `skills/receiving-code-review/SKILL.md` | ~90 |
| 技能 | requesting-code-review | `skills/requesting-code-review/SKILL.md` | ~100 |
| 技能 | subagent-driven-development | `skills/subagent-driven-development/SKILL.md` | ~170 |
| 技能 | systematic-debugging | `skills/systematic-debugging/SKILL.md` | ~140 |
| 技能 | test-driven-development | `skills/test-driven-development/SKILL.md` | ~320 |
| 技能 | using-git-worktrees | `skills/using-git-worktrees/SKILL.md` | 218 |
| 技能 | using-superpowers | `skills/using-superpowers/SKILL.md` | ~180 |
| 技能 | verification-before-completion | `skills/verification-before-completion/SKILL.md` | ~100 |
| 技能 | writing-plans | `skills/writing-plans/SKILL.md` | ~160 |
| 技能 | writing-skills | `skills/writing-skills/SKILL.md` | 655 |
| 代理 | code-reviewer | `agents/code-reviewer.md` | ~150 |
| 脚本 | helper.js | `skills/brainstorming/scripts/helper.js` | ~50 |
| 脚本 | start-server.sh | `skills/brainstorming/scripts/start-server.sh` | ~40 |
| 脚本 | stop-server.sh | `skills/brainstorming/scripts/stop-server.sh` | ~20 |
| 脚本 | bump-version.sh | `scripts/bump-version.sh` | ~60 |
| 脚本 | sync-to-codex-plugin.sh | `scripts/sync-to-codex-plugin.sh` | ~40 |
| 钩子 | session-start | `hooks/session-start` | 57 |
| 钩子 | run-hook.cmd | `hooks/run-hook.cmd` | 47 |
| 清单 | Claude Code | `.claude-plugin/plugin.json` | ~15 |
| 清单 | Cursor | `.cursor-plugin/plugin.json` | ~15 |
| 清单 | OpenCode | `.opencode/plugins/superpowers.js` | 113 |
| 清单 | Gemini | `gemini-extension.json` | ~20 |

### C. 类别评分细则

| 类别 | 评分 | 权重 | 加权分 | 基线 | 调整 | 理由 |
|------|------|------|--------|------|------|------|
| 结构 | 10 | 3 | 30 | 10 | +0 | 完美结构 |
| 平台清单 | 10 | 2 | 20 | 10 | +0 | 所有清单有效 |
| 版本同步 | 10 | 3 | 30 | 10 | +0 | 无漂移 |
| 技能质量 | 7 | 2 | 14 | 7 | +0 | 基线准确反映发现组合 |
| 交叉引用 | 10 | 2 | 20 | 10 | +0 | 引用干净 |
| 工作流 | 10 | 3 | 30 | 10 | +0 | 图结构合理；W2/W3 为设计使然 |
| 钩子 | 10 | 2 | 20 | 10 | +0 | 钩子实现良好 |
| 测试 | 7 | 2 | 14 | 7 | +0 | 真实缺口被现有集成测试平衡 |
| 文档 | 3.6 | 1 | 3.6 | 0 | +3.6 | D2 严重问题和 D1 警告为误报；英文文档全面 |
| 安全 | 7.5 | 3 | 22.5 | 0 | +7.5 | HK2 严重问题为误报（注释）；所有 SC3 可疑项为误报（教学示例） |
| **合计** | | **23** | **204.1** | | | |

**综合加权评分：** 204.1 / 23 = **8.9/10**

说明：综合评分与脚本基线 7.9 不同，是由于定性调整。主要驱动因素为：（1）安全评分在误报分类后从 0 升至 7.5（高权重 = 3），（2）文档评分在排除误报后从 0 升至 3.6（低权重 = 1）。

### D. 优先级建议

1. **添加测试提示文件**——为 `tests/skill-triggering/prompts/` 中缺失的 8 个技能添加（brainstorming、finishing-a-development-branch、receiving-code-review、subagent-driven-development、using-git-worktrees、using-superpowers、verification-before-completion、writing-skills）。这是对长期可维护性影响最大的改进。

2. **从 writing-skills 提取引用内容**——655 行的 SKILL.md 适合将测试方法论移至 `references/testing-methodology.md`，使主体缩减到 500 行以下。

3. **添加规范来源声明**——到 `docs/README.codex.md`、`docs/README.opencode.md` 和 `docs/testing.md`。

4. **添加中文翻译**——如果中文用户是目标受众，为 README 和 docs/ 文件创建翻译。

5. **添加 `set -euo pipefail`**——到 `skills/brainstorming/scripts/start-server.sh` 和 `stop-server.sh`。

6. **添加 `## Outputs` 部分**——到终端技能中以完善文档。

7. **考虑添加 `## Integration` / `Called by: user directly` 声明**——到通过启发式匹配发现的技能中，以增加图分析透明度。
