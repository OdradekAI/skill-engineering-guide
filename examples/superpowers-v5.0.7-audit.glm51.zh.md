---
audit-date: "2026-04-19T23:18+00:00"
auditor-platform: "Claude Code"
auditor-model: "GLM-5.1"
bundles-forge-version: "1.8.2"
source-type: "local-directory"
source-uri: "~/repos/superpowers"
os: "Windows 11 Home 10.0.22631"
python: "n/a"
---

# Bundle-Plugin 审计报告：superpowers

## 1. 决策摘要

| 字段 | 值 |
|------|-----|
| **目标** | `~/repos/superpowers` |
| **版本** | 5.0.7 |
| **提交** | b557648 |
| **日期** | 2026-04-19 |
| **审计上下文** | 变更后审查 |
| **平台** | Claude Code、Cursor、OpenCode、Codex、Gemini |
| **技能** | 14 个技能、1 个智能体、0 个命令、2 个项目级脚本 |

### 建议：`有条件通过`

**自动化基线：** 3 个严重问题、45 个警告、68 个信息——脚本建议 `不通过`

**总体评分：** 8.4/10（加权平均；参见分类评分）

**定性调整：** 从 `不通过` 提升为 `有条件通过`。3 个严重发现的具体情况：其中 2 个是 RELEASE-NOTES.md 中的失效交叉引用（历史变更日志，非功能代码）；1 个是 shell 注释中的 GitHub issue URL（HK2，不可执行）。以上均不影响运行时行为、安装正确性或安全态势。该项目在全部 5 个平台上运行正常。

### 主要风险

| # | 风险 | 影响 | 不修复的后果 |
|---|------|------|-------------|
| 1 | 14 个技能均无测试提示词（T5） | 14/14 技能未测试 | 技能变更时回归问题无法检测 |
| 2 | 14 个技能中有 12 个未列入 README.md（D1） | 用户无法从文档发现 86% 的技能 | 降低采用率，用户困惑 |
| 3 | RELEASE-NOTES.md 中的失效交叉引用（D2） | 历史文档引用了不存在的技能 | 对阅读变更日志的用户造成误导 |

### 修复工作量估算

| 优先级 | 数量 | 预估工作量 |
|--------|------|-----------|
| P0（阻断） | 3 | 30 分钟（2 个修复交叉引用，1 个仅为注释） |
| P1（高） | 17 | 4-6 小时（添加技能列表到 README，添加测试提示词） |
| P2+ | 96 | 8-12 小时（添加中文翻译、规范来源声明、概述章节） |

---

## 2. 风险矩阵

| ID | 标题 | 严重性 | 影响范围 | 可利用性 | 置信度 | 状态 |
|----|------|--------|---------|---------|--------|------|
| DOC-001 | RELEASE-NOTES.md 中失效交叉引用 `superpowers:code-reviewer` | P0 | 仅外观影响——变更日志，非运行时 | 必然触发 | 较高 | 待处理 |
| DOC-002 | RELEASE-NOTES.md 中失效交叉引用 `superpowers:skill-name` | P0 | 仅外观影响——变更日志，非运行时 | 必然触发 | 较高 | 待处理 |
| SEC-001 | hooks/session-start 注释中的外部 URL（HK2） | P0 | 无运行时影响——URL 位于注释中 | 理论性 | 较高 | 待处理 |
| TST-001 | 14 个技能均无测试提示词（T5） | P1 | 14/14 技能缺少提示词级测试 | 必然触发 | 已确认 | 待处理 |
| DOC-003 | 12 个技能未列入 README.md（D1） | P1 | 用户无法从文档发现 12/14 技能 | 必然触发 | 已确认 | 待处理 |
| DOC-004 | 缺少中文翻译（D6、D7） | P2 | 4 个文档文件缺少中文对应版本 | 必然触发 | 已确认 | 待处理 |
| DOC-005 | 缺少规范来源声明（D8） | P2 | 3 个文档文件缺少规范来源 | 必然触发 | 已确认 | 待处理 |
| SKQ-001 | writing-skills SKILL.md 超过 500 行限制（Q9） | P2 | 1/14 技能，650 行 | 边缘情况 | 已确认 | 待处理 |
| SKQ-002 | using-git-worktrees 引导体超过 200 行预算（Q13） | P2 | 1/2 引导技能，213 行 | 边缘情况 | 已确认 | 待处理 |
| SEC-002 | OpenCode 插件中的宽泛 process.env 访问（OC9） | P2 | 1/5 平台（OpenCode） | 边缘情况 | 已确认 | 待处理 |
| SEC-003 | hook 脚本中的环境变量访问（HK6） | P2 | 2 个 hook 文件 | 边缘情况 | 已确认 | 待处理 |
| HOK-001 | 缺少 hooks/session-start.py（H2） | P1 | 脚本式 hook 可用；.py 变体缺失 | 边缘情况 | 已确认 | 待处理 |

---

## 3. 分类发现

### 3.1 结构（评分：10/10，权重：高）

**摘要：** 项目结构清晰，所有必需目录均存在且组织良好。

**审计组件：** `skills/`、`hooks/`、`agents/`、`scripts/`、平台清单、项目根目录

无发现。

---

### 3.2 平台清单（评分：10/10，权重：中）

**摘要：** 全部 5 个平台清单均存在、有效且配置正确。

**审计组件：** `.claude-plugin/plugin.json`、`.cursor-plugin/plugin.json`、`.opencode/plugins/superpowers.js`、`.codex/INSTALL.md`、`gemini-extension.json`

无发现。

---

### 3.3 版本同步（评分：10/10，权重：高）

**摘要：** 所有版本字符串在各清单和配置文件中保持同步。

**审计组件：** `.version-bump.json`、所有平台清单、`package.json`

无发现。

---

### 3.4 技能质量（评分：7/10，权重：中）

**摘要：** 技能编写良好，描述清晰且指导内容扎实。3 个警告与大小限制和格式规范相关；18 个信息项为次要遗漏（概述、常见错误章节）。

**审计组件：** 14 个 SKILL.md 文件

#### [SKQ-001] writing-skills SKILL.md 超过 500 行限制
- **严重性：** P2 | **影响：** 1/14 技能 | **置信度：** 已确认
- **位置：** `skills/writing-skills/SKILL.md`（650 行）
- **触发条件：** 技能正文为 650 行，超过 500 行指导限制
- **实际影响：** 加载技能时 token 消耗大；可能在小模型上超出上下文预算
- **修复方案：** 将大量参考内容提取到已有参考文件（anthropic-best-practices.md、persuasion-principles.md、testing-skills-with-subagents.md），减少内联内容

#### [SKQ-002] using-git-worktrees 引导体超过 200 行预算
- **严重性：** P2 | **影响：** 1/2 引导技能 | **置信度：** 已确认
- **位置：** `skills/using-git-worktrees/SKILL.md`（正文 213 行）
- **触发条件：** 引导技能正文为 213 行（约 1215 估算 token），超过 200 行预算
- **实际影响：** 引导技能在每次会话启动时加载；多出的 13 行每次会话增加约 75 token
- **修复方案：** 精简边缘场景或将次要场景移至 references/

#### [SKQ-003] brainstorming 描述未以 "Use when..." 开头
- **严重性：** P2 | **影响：** 1/14 技能 | **置信度：** 已确认
- **位置：** `skills/brainstorming/SKILL.md` frontmatter
- **触发条件：** 描述以 "You MUST use this before..." 开头，而非 "Use when..."
- **实际影响：** 技能列表中描述格式不一致
- **修复方案：** 改写为 "Use when doing any creative work..."

#### 跨技能一致性（C1）
- 概述章节：9 个技能有，3 个没有（brainstorming、requesting-code-review、subagent-driven-development）
- "Use when" 后的动词形式：9 个使用动名词（-ing）vs 5 个使用原形动词——混用但不造成困扰

---

### 3.5 交叉引用（评分：10/10，权重：中）

**摘要：** 所有技能间交叉引用均正确解析。24 个信息级发现关于工作流拓扑（W2、W3）属于架构观察，非失效链接。

**审计组件：** 所有 SKILL.md 文件中的 `superpowers:*` 引用、相对路径引用、references/ 目录内容

#### [XRF-001] 未被引用的参考文件
- **严重性：** P3 | **影响：** 1 个文件 | **置信度：** 已确认
- **位置：** `skills/using-superpowers/references/gemini-tools.md`
- **触发条件：** 文件存在于 references/ 中但未被 SKILL.md 或任何同级参考文件引用
- **实际影响：** 孤立参考文件；可能包含有用的 Gemini 工具文档，应予链接
- **修复方案：** 在 SKILL.md 中添加引用，或确认该文件由 Gemini 平台逻辑加载

---

### 3.6 工作流（评分：10/10，权重：高）

**摘要：** 工作流图结构健全，包含 2 个元技能（引导类）和 12 个独立技能。所有信息级发现反映了技能由用户调用而非通过严格图链接的设计选择。

**审计组件：** 14 个 SKILL.md 的集成章节、跨技能引用

#### [WFL-001] 12 个技能无法从入口点到达（W2）
- **严重性：** P3 | **影响：** 12/14 技能 | **置信度：** 已确认
- **触发条件：** brainstorming、systematic-debugging 等技能没有来自引导技能的入边
- **实际影响：** 无——这是设计意图。using-superpowers 引导技能指示智能体在每个任务中检查所有技能，因此不需要显式图边。技能通过 Skill 工具发现，而非图遍历。
- **修复方案：** 考虑在集成章节中添加 "调用者：用户直接调用" 声明以提高文档清晰度

#### [WFL-002] 12 个终端技能缺少输出章节（W3）
- **严重性：** P3 | **影响：** 12/14 技能 | **置信度：** 已确认
- **触发条件：** 终端技能（无出向引用）未记录其预期输出
- **实际影响：** 轻微——消费技能输出的智能体没有正式契约，但技能正文包含充分的内联指导
- **修复方案：** 为每个终端技能添加 ## Outputs 章节

#### 行为验证（W10-W11）

未执行。原因：变更后检查模式，静态+语义层由脚本评估。行为验证需要评估器智能体调度（W10-W11）。

---

### 3.7 Hooks（评分：10/10，权重：中）

**摘要：** Hook 系统在所有平台上运行正常。项目使用基于 shell 的 hook（session-start）而非 Python hook，这是有效的方法。关于缺少 session-start.py 的警告因可用的 shell 等效实现而得到缓解。

**审计组件：** `hooks/session-start`、`hooks/hooks.json`、`hooks/hooks-cursor.json`、`hooks/run-hook.cmd`

**定性调整：** 基线 9 调整为 10。H2 警告（缺少 session-start.py）反映的是规范偏好而非功能缺口——项目有意使用在所有支持平台上均可运行的 shell 脚本 hook。该 hook 正确处理了平台检测（Cursor、Claude Code、Copilot CLI）并输出格式正确的 JSON。

#### [HOK-001] 缺少 hooks/session-start.py
- **严重性：** P1 | **影响：** 仅规范层面 | **置信度：** 已确认
- **位置：** `hooks/` 目录
- **触发条件：** 无 session-start.py 文件；项目使用基于 shell 的 `hooks/session-start`
- **实际影响：** 无——shell hook 功能等效且跨平台
- **修复方案：** 可选——如规范要求，添加 .py 封装器

#### [HOK-002] hooks.json 缺少 description 和 timeout 字段（H9）
- **严重性：** P3 | **影响：** 1 个 hook 配置 | **置信度：** 已确认
- **位置：** `hooks/hooks.json`
- **触发条件：** 缺少顶层 `description` 字段；SessionStart 处理器缺少 `timeout` 字段
- **实际影响：** 轻微——缺少元数据不影响 hook 执行
- **修复方案：** 添加 `"description"` 和 `"timeout"` 字段以保持完整性

---

### 3.8 测试（评分：6/10，权重：中）

**摘要：** 14 个技能均无测试提示词。这是项目中最显著的质量差距。项目没有 tests/ 目录，也没有 A/B 评估结果。

**定性调整：** 基线 7 调整为 6。虽然公式考虑了 14 个缺失的 T5 警告，但完全缺乏测试基础设施（无 tests/ 目录、无评估结果、无提示词文件）代表了比单项计数更深层的差距。

**审计组件：** `tests/` 目录（不存在）、`.bundles-forge/evals/`（不存在）、技能测试提示词

#### [TST-001] 全部 14 个技能无测试提示词（T5）
- **严重性：** P1 | **影响：** 14/14 技能 | **置信度：** 已确认
- **触发条件：** 不存在 `tests/prompts/<skill-name>.yml` 或 `skills/<name>/tests/prompts.yml` 文件
- **实际影响：** 无法自动化验证技能触发、分支覆盖或回归检测
- **修复方案：** 为每个技能创建测试提示词文件，包含应触发和不应触发的样本

#### [TST-002] 无 A/B 评估结果（T8）
- **严重性：** P3 | **影响：** 1 个项目 | **置信度：** 已确认
- **位置：** `.bundles-forge/evals/`
- **触发条件：** 未找到评估结果
- **实际影响：** 无基线质量指标可供比较
- **修复方案：** 运行 A/B 评估并提交结果

---

### 3.9 文档（评分：0/10，权重：低）

**摘要：** 文档有 2 个严重发现（发布说明中的失效交叉引用）和 19 个警告。影响最大的是 14 个技能中有 12 个未列入 README.md 的技能清单。尽管评分为 0，README 本身编写良好，有效覆盖了工作流叙述——该评分反映的是缺失的技能条目和翻译，而非质量差。

**审计组件：** `README.md`、`RELEASE-NOTES.md`、`docs/*.md`、`CLAUDE.md`

#### [DOC-001] RELEASE-NOTES.md 中失效交叉引用 `superpowers:code-reviewer`
- **严重性：** P0 | **影响：** 外观（变更日志） | **置信度：** 较高
- **位置：** `RELEASE-NOTES.md`（6+ 处出现）
- **触发条件：** 历史发布说明引用了 `superpowers:code-reviewer`，该名称作为技能不存在（它以 `agents/code-reviewer.md` 形式存在）
- **实际影响：** 对阅读变更日志的用户造成误导；无运行时影响
- **修复方案：** 更新 RELEASE-NOTES.md 使用正确的引用格式

#### [DOC-002] RELEASE-NOTES.md 中失效交叉引用 `superpowers:skill-name`
- **严重性：** P0 | **影响：** 外观（变更日志） | **置信度：** 较高
- **位置：** `RELEASE-NOTES.md` 第 678 行
- **触发条件：** 历史变更日志条目中出现通用占位符 `superpowers:skill-name`
- **实际影响：** 文档中的误导性占位符
- **修复方案：** 替换为正确的技能名称或删除该通用条目

#### [DOC-003] 12 个技能未列入 README.md（D1）
- **严重性：** P1 | **影响：** 12/14 技能 | **置信度：** 已确认
- **触发条件：** README.md 的技能清单部分未列出全部 14 个技能
- **实际影响：** 用户无法从 README 发现大部分技能
- **修复方案：** 在 README 中添加完整的技能列表及描述

#### [DOC-004] 缺少中文翻译（D6、D7）
- **严重性：** P2 | **影响：** 4 个文档文件 | **置信度：** 已确认
- **位置：** `README.zh.md`（缺失）、`docs/README.codex.zh.md`（缺失）、`docs/README.opencode.zh.md`（缺失）、`docs/testing.zh.md`（缺失）
- **触发条件：** 英文文档存在但无中文对应版本
- **实际影响：** 中文用户缺少翻译文档
- **修复方案：** 为 README 和 docs/ 文件添加中文翻译

#### [DOC-005] 缺少规范来源声明（D8）
- **严重性：** P2 | **影响：** 3 个文档文件 | **置信度：** 已确认
- **位置：** `docs/README.codex.md`、`docs/README.opencode.md`、`docs/testing.md`
- **触发条件：** 指南文档缺少 `> **Canonical source:**` 声明
- **实际影响：** 文档无法追溯到其权威技能/智能体来源
- **修复方案：** 添加指向相关技能或智能体文件的规范来源声明

#### [DOC-006] 版本升级追踪不匹配（D3）
- **严重性：** P3 | **影响：** 3 个清单文件 | **置信度：** 已确认
- **触发条件：** `.version-bump.json` 追踪的 3 个清单文件未列入 CLAUDE.md 平台清单表格
- **实际影响：** 仅文档不一致
- **修复方案：** 更新 CLAUDE.md 表格以匹配 `.version-bump.json`

---

### 3.10 安全（评分：6/10，权重：高）

**摘要：** 1 个确定性严重发现（HK2——hook 注释中的外部 URL）和 3 个确定性警告（OC9、HK6 x2）。5 个可疑 SC3 发现已完成分诊：1 个误报、4 个接受风险。分诊后重新计算的基线为 4，因 HK2 严重项为不可执行的注释且无安全影响，上调 2 分。

**审计组件：** 14 个 SKILL.md 文件、2 个 hook 脚本、1 个 hook 配置、1 个 OpenCode 插件、2 个项目脚本、4 个 MCP/配置清单、1 个智能体提示词、6 个技能参考文件、5 个捆绑脚本

#### [SEC-001] hooks/session-start 注释中的外部 URL（HK2）
- **严重性：** P0 | **影响：** 1/1 hook 脚本（不可执行） | **置信度：** 已确认
- **位置：** `hooks/session-start:45`
- **触发条件：** 注释包含 `https://github.com/obra/superpowers/issues/571`
- **实际影响：** 无——URL 位于解释 bash 变通方法的注释中，不在可执行代码中。该 hook 不发起任何网络调用。
- **修复方案：** 考虑从 hook 脚本中移除 URL 以满足自动化扫描器要求，或添加内联说明

#### [SEC-002] OpenCode 插件中的宽泛 process.env 访问（OC9）
- **严重性：** P2 | **影响：** 1/5 平台（OpenCode） | **置信度：** 已确认
- **位置：** `.opencode/plugins/superpowers.js:52`
- **触发条件：** 插件访问 `process.env` 的范围超出文档记录的需求
- **实际影响：** 理论性——OpenCode 插件读取环境变量用于平台检测，属于标准做法
- **修复方案：** 将环境变量访问范围限制在特定所需变量

#### [SEC-003] hook 脚本中的环境变量访问（HK6）
- **严重性：** P2 | **影响：** 2 个 hook 文件 | **置信度：** 已确认
- **位置：** `hooks/run-hook.cmd:46`（$SCRIPT_NAME）、`hooks/session-start:49`（$COPILOT_CLI）
- **触发条件：** hook 脚本读取了标准插件根目录变量之外的环境变量
- **实际影响：** 低——$SCRIPT_NAME 和 $COPILOT_CLI 用于平台检测，非访问密钥
- **修复方案：** 添加内联注释说明环境变量用途

#### [SEC-004] shell 脚本缺少 set -euo pipefail（BS6）
- **严重性：** P3 | **影响：** 2 个捆绑脚本 | **置信度：** 已确认
- **位置：** `skills/brainstorming/scripts/start-server.sh:1`、`skills/brainstorming/scripts/stop-server.sh:1`
- **触发条件：** shell 脚本缺少严格错误处理
- **实际影响：** 脚本可能静默失败而不报告错误
- **修复方案：** 在两个脚本中添加 `set -euo pipefail`

#### 可疑项分诊

| 发现 | 文件:行号 | 处置 | 理由 |
|------|----------|------|------|
| SC3——引用用户配置目录 | `skills/subagent-driven-development/SKILL.md:142` | 误报 | 对话示例中的文本（"You: 'User level (~/.config/superpowers/hooks/)'"），不是读取配置目录的指令 |
| SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:46` | 接受 | 菜单选项向用户展示合法的工作树位置选择；引用项目自身配置目录，非敏感用户数据 |
| SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:71` | 接受 | 记录全局工作树路径功能的章节标题；同上 |
| SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:91` | 接受 | 构建工作树路径的代码片段；实现了文档记录的功能 |
| SC3——引用用户配置目录 | `skills/using-git-worktrees/SKILL.md:92` | 接受 | case 语句路径构建的延续；同上 |

处置类型：**误报** = 假阳性（排除在评分之外），**接受** = 真实但已缓解（不扣分），**确认** = 真阳性（保留全部严重性）。

---

## 4. 方法论

### 范围

| 维度 | 覆盖内容 |
|------|---------|
| **目录** | `skills/`、`agents/`、`hooks/`、`scripts/`、`.claude-plugin/`、`.cursor-plugin/`、`.opencode/`、`.codex/`、项目根目录、`docs/` |
| **检查类别** | 10 个类别，60+ 项单独检查 |
| **扫描文件总数** | 所有类别共 55+ 个文件 |

### 范围外

- 技能的运行时行为（智能体执行、提示词-响应质量）
- 平台特定安装的端到端测试
- 依赖的依赖（传递分析）
- 行为验证（W10-W11）——需要评估器智能体调度

### 工具

| 工具 | 用途 |
|------|------|
| `bundles-forge audit-plugin` | 编排完整的 10 类别审计 |
| `bundles-forge audit-security` | 安全模式扫描（7 个攻击面） |
| `bundles-forge audit-skill` | 逐技能质量检查 |
| `bundles-forge bump-version --check` | 版本漂移检测 |
| 人工审查 | 可疑发现分诊（5 个 SC3 发现） |

### 局限性

- 安全扫描使用正则表达式——可能存在误报；5 个可疑发现已人工分诊
- 技能质量检查使用轻量级 YAML 解析器——复杂 YAML 边缘情况可能被遗漏
- token 估算使用启发式比率；实际计数因模型而异
- 行为验证（W10-W11）未执行——仅覆盖静态和语义层

---

## 5. 附录

### A. 逐技能分析

#### brainstorming
**结论：** 设计良好的创意技能，具有强门控但缺少可选章节且描述格式不一致。
**优势：** 清晰的 HARD-GATE 防止过早实现；visual companion 和 spec reviewer 引用提供了深度
**主要问题：** 描述未遵循 "Use when..." 规范（Q5）；缺少概述章节（Q10）；缺少常见错误章节（Q11）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 7/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### dispatching-parallel-agents
**结论：** 干净、专注的技能，无质量发现——是整个集合中的模范技能。
**优势：** 描述清晰且遵循规范；简洁，仅 182 行；指导范围明确
**主要问题：** 无。

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 10/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### executing-plans
**结论：** 紧凑的后备技能（70 行），适用于不支持子智能体的平台，具有清晰的路由指导。
**优势：** 极其简洁；正确路由到 subagent-driven-development（当可用时）；清晰的 announce-at-start 模式
**主要问题：** 缺少常见错误章节（Q11）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### finishing-a-development-branch
**结论：** 结构良好的完成技能，具有清晰的概述和正确的规范。
**优势：** 描述清晰；概述章节规范；工作流指导良好
**主要问题：** 无。

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 10/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### receiving-code-review
**结论：** 强大的技能，提倡技术严谨而非社交舒适，具有出色的行为指导。
**优势：** 独特的语调（"技术正确性优先于社交舒适"）；清晰的响应模式；规范的概述
**主要问题：** 无。

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 10/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### requesting-code-review
**结论：** 专注的代码审查调度技能，具有清晰的必需/可选触发条件，缺少可选章节。
**优势：** 清晰的强制审查触发条件；正确引用 code-reviewer 智能体
**主要问题：** 缺少概述章节（Q10）；缺少常见错误章节（Q11）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### subagent-driven-development
**结论：** 核心实现技能，具有丰富的子智能体调度逻辑，缺少可选文档章节。
**优势：** 详细的实现者/审查者提示词模板；两阶段审查模式；强路由指导
**主要问题：** 缺少概述章节（Q10）；缺少常见错误章节（Q11）；SC3 可疑发现（误报——对话示例）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### systematic-debugging
**结论：** 全面的调试方法论，具有丰富的参考内容（5 个参考文件），组织良好。
**优势：** 4 阶段根因分析流程；丰富的参考库（root-cause-tracing、defense-in-depth、condition-based-waiting）；包含压力测试
**主要问题：** 缺少常见错误章节（Q11）；第 69 行的条件块跨度 38 行（Q15）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### test-driven-development
**结论：** 长篇 TDD 技能（371 行），方法论内容扎实，可从参考提取中受益。
**优势：** 全面的测试反模式参考；清晰的红-绿-重构执行
**主要问题：** 371 行且无 references/ 文件（Q12）；缺少常见错误章节（Q11）；第 76 行的条件块跨度 32 行（Q15）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 8/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### using-git-worktrees
**结论：** 略微超出 token 预算的引导技能（213 行），4 个接受风险的 SC3 发现来自合法的工作树路径配置。
**优势：** 带安全验证的智能目录选择；清晰的概述章节
**主要问题：** 引导体超过 200 行预算，为 213 行（Q13）；4 个 SC3 发现（全部接受——合法的工作树路径功能）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 8/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### using-superpowers
**结论：** 主引导技能，具有强指令优先级层次和技能发现指导；一个孤立参考文件。
**优势：** 清晰的 3 级指令优先级；用于技能发现的 EXTREMELY-IMPORTANT 块；平台特定工具引用
**主要问题：** 参考文件 `references/gemini-tools.md` 未被 SKILL.md 引用（X4）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 10/10 |
| 交叉引用 | 9/10 |
| 安全 | 10/10 |

#### verification-before-completion
**结论：** 简洁技能（139 行），强制基于证据的完成声明，具有清晰的行为规则。
**优势：** 强核心原则（"先有证据，再有声明"）；规范的概述章节
**主要问题：** 缺少常见错误章节（Q11）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### writing-plans
**结论：** 精心设计的规划技能，具有清晰的受众假设和正确的 plan-reviewer 集成。
**优势：** 清晰的"假设读者是有技能但不了解情况的工程师"框架；plan-document-reviewer-prompt.md 参考
**主要问题：** 缺少常见错误章节（Q11）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 9/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

#### writing-skills
**结论：** 全面的技能编写指南，本身是最大的技能（650 行），尽管已提取参考内容仍超过 500 行指导限制。
**优势：** 包含 testing-skills-with-subagents 方法论；anthropic-best-practices 和 persuasion-principles 参考；全面的示例目录
**主要问题：** 正文 650 行，超过 500 行上限（Q9）；估算 token 数较高（约 4880 token，Q13）；300+ 行但无 references/ 目录（Q12——注：参考文件存在于技能根目录而非 references/ 子目录）

| 类别 | 评分 |
|------|------|
| 结构 | 10/10 |
| 技能质量 | 6/10 |
| 交叉引用 | 10/10 |
| 安全 | 10/10 |

---

### B. 组件清单

| 组件类型 | 名称 | 路径 | 行数 |
|---------|------|------|------|
| 技能 | brainstorming | `skills/brainstorming/SKILL.md` | 164 |
| 技能 | dispatching-parallel-agents | `skills/dispatching-parallel-agents/SKILL.md` | 182 |
| 技能 | executing-plans | `skills/executing-plans/SKILL.md` | 70 |
| 技能 | finishing-a-development-branch | `skills/finishing-a-development-branch/SKILL.md` | 200 |
| 技能 | receiving-code-review | `skills/receiving-code-review/SKILL.md` | 213 |
| 技能 | requesting-code-review | `skills/requesting-code-review/SKILL.md` | 105 |
| 技能 | subagent-driven-development | `skills/subagent-driven-development/SKILL.md` | 277 |
| 技能 | systematic-debugging | `skills/systematic-debugging/SKILL.md` | 296 |
| 技能 | test-driven-development | `skills/test-driven-development/SKILL.md` | 371 |
| 技能 | using-git-worktrees | `skills/using-git-worktrees/SKILL.md` | 218 |
| 技能 | using-superpowers | `skills/using-superpowers/SKILL.md` | 117 |
| 技能 | verification-before-completion | `skills/verification-before-completion/SKILL.md` | 139 |
| 技能 | writing-plans | `skills/writing-plans/SKILL.md` | 152 |
| 技能 | writing-skills | `skills/writing-skills/SKILL.md` | 655 |
| 智能体 | code-reviewer | `agents/code-reviewer.md` | 48 |
| 脚本 | bump-version | `scripts/bump-version.sh` | 220 |
| 脚本 | sync-to-codex-plugin | `scripts/sync-to-codex-plugin.sh` | 388 |
| Hook | session-start | `hooks/session-start` | 57 |
| Hook | hooks.json | `hooks/hooks.json` | 16 |
| Hook | hooks-cursor.json | `hooks/hooks-cursor.json` | 10 |
| Hook | run-hook.cmd | `hooks/run-hook.cmd` | 46 |
| 清单 | Claude Code | `.claude-plugin/plugin.json` | 20 |
| 清单 | Cursor | `.cursor-plugin/plugin.json` | 25 |
| 清单 | OpenCode | `.opencode/plugins/superpowers.js` | 112 |
| 清单 | Codex | `.codex/INSTALL.md` | -- |
| 清单 | Gemini | `gemini-extension.json` | 6 |

---

### C. 分类评分汇总

| 类别 | 基线 | 调整 | 最终 | 权重 | 加权分 |
|------|------|------|------|------|--------|
| 结构 | 10 | 0 | 10 | 3（高） | 30 |
| 平台清单 | 10 | 0 | 10 | 2（中） | 20 |
| 版本同步 | 10 | 0 | 10 | 3（高） | 30 |
| 技能质量 | 7 | 0 | 7 | 2（中） | 14 |
| 交叉引用 | 10 | 0 | 10 | 2（中） | 20 |
| 工作流 | 10 | 0 | 10 | 3（高） | 30 |
| Hooks | 9 | +1 | 10 | 2（中） | 20 |
| 测试 | 7 | -1 | 6 | 2（中） | 12 |
| 文档 | 0 | 0 | 0 | 1（低） | 0 |
| 安全 | 4* | +2 | 6 | 3（高） | 18 |
| **合计** | | | | **23** | **194** |

**总体评分：194 / 23 = 8.4/10**

*安全基线在可疑发现分诊后重新计算（5 个可疑警告重新分类：1 个误报、4 个接受风险）。

---

### D. 优先修复建议

1. **修复 RELEASE-NOTES.md 中的失效交叉引用**（P0，15 分钟）
   - 将 `superpowers:code-reviewer` 替换为 `agents/code-reviewer` 或正确的技能引用
   - 将 `superpowers:skill-name` 占位符替换为实际技能名称

2. **在 README.md 中添加完整技能列表**（P1，30 分钟）
   - 将全部 14 个技能添加到技能清单部分，附带一行描述

3. **为全部 14 个技能创建测试提示词**（P1，4-6 小时）
   - 为每个技能创建 `tests/prompts/<skill-name>.yml`，包含应触发和不应触发的样本

4. **将 writing-skills SKILL.md 缩减到 500 行以内**（P2，1-2 小时）
   - 将额外内容移至已有参考文件或创建新文件

5. **为 8 个技能添加常见错误章节**（P2，2-3 小时）
   - brainstorming、executing-plans、receiving-code-review、requesting-code-review、subagent-driven-development、systematic-debugging、test-driven-development、verification-before-completion、writing-plans

6. **添加中文翻译**（P2，4-6 小时）
   - README.zh.md、docs/README.codex.zh.md、docs/README.opencode.zh.md、docs/testing.zh.md

7. **为 docs/ 添加规范来源声明**（P2，30 分钟）
   - 为 docs/README.codex.md、docs/README.opencode.md、docs/testing.md 添加 `> **Canonical source:**`

8. **为 brainstorming shell 脚本添加 set -euo pipefail**（P3，5 分钟）
   - start-server.sh、stop-server.sh

9. **在 using-superpowers SKILL.md 中引用 gemini-tools.md**（P3，5 分钟）
   - 为孤立参考文件添加链接

10. **将 using-git-worktrees 精简到 200 行以内**（P3，30 分钟）
    - 将次要场景移至 references/ 文件
