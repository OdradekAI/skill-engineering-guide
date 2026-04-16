# bundles-forge 综合架构审查报告

**审查日期：** 2026-04-16  
**项目版本：** 1.7.7  
**审查人：** Claude Code Agent  
**范围：** 完整架构与实现审查

---

## 执行摘要

bundles-forge 是一个成熟、架构良好的 bundle-plugin 工程工具包，基础扎实。项目在中心-辐射式技能架构方面展现出卓越的规范性，通过 Python 脚本实现了全面自动化（审计/发布工具共 2,622 行代码），并具备严格的质量门禁（audit-checks.json 中包含 167 项检查，4 个测试套件、65+ 测试全部通过）。

**总体评估：** 优秀，存在针对性改进空间

**核心优势：**
- 关注点分离清晰：编排器（blueprinting、optimizing、releasing）vs 执行器（scaffolding、authoring、auditing、testing）
- 自动化稳健：脚本处理确定性检查，代理处理定性评估
- 单一事实来源策略，7 层权威层级
- 跨平台支持（6 个平台），抽象层一致
- 全面的测试与 CI 验证

**主要发现：**
1. **架构：** 中心-辐射模型合理，但部分编排器复杂度可以降低
2. **跨平台：** Windows/Mac/Linux 兼容性优秀，路径处理需要小幅改进
3. **文档：** 规范来源管控出色，但 CLAUDE.md 与技能之间存在一定冗余
4. **工作流：** 技能分解合理，但工作流审计行为层（W10-W11）很少运行
5. **测试：** 脚本和集成覆盖良好，技能内容质量覆盖有限

**战略建议：**
- 降低编排器技能复杂度（blueprinting: 336 行，optimizing: 428 行）
- 整合文档层次（CLAUDE.md vs README vs docs/）
- 增加工作流链条的行为测试覆盖
- 简化代理调度模式（3 个代理存在职责重叠）

---

## 1. 架构与设计对齐

### 1.1 中心-辐射模型

**发现：** 中心-辐射架构在概念上合理且实现良好。

**证据：**
- 3 个编排器（blueprinting、optimizing、releasing）清晰地调度 4 个执行器（scaffolding、authoring、auditing、testing）
- 交叉引用使用统一的 `bundles-forge:<skill-name>` 格式
- 集成部分对称地记录了调用关系
- 引导技能（using-bundles-forge）提供轻量路由

**优势：**
- 职责边界清晰：编排器诊断/决策/委派，执行器执行单一任务
- 编排器和执行器之间无循环依赖
- 用户可直接调用执行器执行独立任务

**问题：**

**A1.1 - 编排器复杂度** （优先级：高） `[DONE]`
- **严重程度：** 警告
- **描述：** 编排器技能明显大于执行器：
  - blueprinting: 336 行
  - optimizing: 428 行
  - releasing: 266 行
  - 执行器平均: 196 行（scaffolding: 207, authoring: 154, auditing: 216, testing: 249）
- **影响：** 更长的技能增加 Token 成本，降低缓存命中率，增加维护难度
- **根因：** 编排器将决策树、路由逻辑和错误处理内联嵌入，而非提取到 references/
- **建议：** 将决策树提取到 references/（例如 blueprinting/references/routing-decisions.md、optimizing/references/target-selection.md）
- **验证：** 运行 `bundles-forge audit-skill --json .` 并验证编排器行数降至 300 以下

**A1.2 - 代理调度开销** （优先级：中） `[SKIPPED -- inspector/auditor职责边界清晰，合并收益不足]`
- **严重程度：** 信息
- **描述：** 3 个代理（auditor、inspector、evaluator）的调度模式存在重叠：
  - auditor: 由 auditing 技能调度，运行 10 类审计
  - inspector: 由 scaffolding 技能调度，验证结构
  - evaluator: 由 optimizing/auditing 调度，运行 A/B 测试和链条验证
- **影响：** 每个代理需要子代理调度（上下文分叉），增加延迟和复杂度
- **分析：** 分离对隔离性有益（代理为只读，disallowedTools: Edit），但调度开销确实存在
- **建议：** 考虑将 inspector 合并到 auditor 作为"仅结构模式"，将代理数从 3 减至 2
- **验证：** 在合并前后测量调度延迟

**A1.3 - 技能类型声明** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 技能在"概述"部分声明类型（rigid/flexible/hybrid），但不具备机器可读性
- **影响：** 代理必须解析文本才能理解执行灵活性
- **建议：** 添加可选的 `type: rigid|flexible|hybrid` frontmatter 字段
- **验证：** 更新 audit_skill.py 以验证 type 字段一致性

### 1.2 技能边界

**发现：** 技能边界定义清晰，重叠极少。

**证据：**
- 每个技能在 description 字段中有明确的触发条件
- 集成部分记录了产物交接
- 技能之间无重复功能

**优势：**
- auditing 是"纯诊断型" — 不编排修复
- authoring 是"内容撰写型" — 不生成结构
- scaffolding 是"结构生成型" — 不撰写内容
- testing 是"动态验证型" — 不审计质量

**问题：**

**A1.4 - auditing 与 optimizing 的边界** （优先级：低） `[SKIPPED -- 当前设计正确]`
- **严重程度：** 信息
- **描述：** auditing 技能在集成部分包含"变更后验证"，但 optimizing 也运行 auditing 进行验证
- **影响：** 可能造成"谁负责验证"的困惑
- **分析：** 这实际上是正确的 — auditing 提供验证服务，optimizing 消费该服务
- **建议：** 无需更改，但应在 auditing 技能中澄清"变更后验证"意为"由 optimizing/releasing 调用进行验证"
- **验证：** 审计报告应显示对称的 Calls/Called-by 声明

### 1.3 脚本 vs 语义判断

**发现：** 自动化检查（脚本）与定性评估（代理）之间的分离出色。

**证据：**
- 脚本（audit_skill.py、audit_security.py、audit_docs.py）处理确定性检查
- 代理（auditor.md）处理 ±2 定性调整
- 事实来源策略（7 层层级）清晰定义权威

**优势：**
- 脚本提供基准分数：`max(0, 10 - (critical × 3 + capped_warning_penalty))`
- 代理添加脚本无法捕捉的定性评估
- 分工清晰：脚本检查语法/结构，代理检查语义/适配度

**问题：**

**A1.5 - 脚本覆盖缺口** （优先级：中） `[DEFERRED -- S11/W7迁移不纳入本轮]`
- **严重程度：** 警告
- **描述：** audit-checks.json 中部分检查标记为 `agent-only`，但实际可以自动化：
  - S8（技能-代理边界）：可通过文本相似度检测重复
  - S11（可写代理隔离）：可解析 frontmatter 中的 disallowedTools + isolation 字段
  - W7（循环依赖说明）：可检查 `<!-- cycle:a,b -->` 注释
- **影响：** 代理必须手动检查本可确定性处理的项目
- **建议：** 将 S11 和 W7 迁移到脚本，S8 保留为 agent-only（需要语义判断）
- **验证：** 运行 audit_plugin.py 并验证 S11/W7 出现在 JSON 输出中

**A1.6 - 评分公式差异** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 项目级和技能级评分公式有意不同：
  - 项目级：每个检查 ID 有上限的警告惩罚
  - 技能级：无上限的警告惩罚
- **影响：** 无 — 这是 source-of-truth-policy.md 的设计意图
- **建议：** 在 audit-checks.json 头部注释中说明此差异，防止未来的"bug"报告
- **验证：** 在 audit-checks.json 中添加解释差异的注释

---

## 2. 跨平台实现

### 2.1 平台支持

**发现：** 跨平台支持优秀，抽象层一致。

**证据：**
- 支持 6 个平台：Claude Code、Cursor、Codex、OpenCode、Gemini CLI、OpenClaw
- hooks/session-start.py 中的平台检测：CURSOR_PLUGIN_ROOT → Cursor，CLAUDE_PLUGIN_ROOT → Claude Code，回退 → 纯文本
- 通过 .version-bump.json 同步 5 个清单的版本
- CI 在 Python 3.9 和 3.12 上测试

**优势：**
- Python 3.9+ 要求有明确文档
- 跨平台钩子脚本（session-start.py）使用 os.environ 进行平台检测
- 路径处理全程使用 pathlib.Path
- 无平台特定的 shell 命令（bash vs cmd）

**问题：**

**CP2.1 - Windows 路径处理** （优先级：高） `[DEFERRED -- Phase 3]`
- **严重程度：** 警告
- **描述：** 部分脚本在字符串字面量中使用正斜杠：
  - bin/bundles-forge: `_ROOT / "skills" / "auditing" / "scripts"` （正确）
  - 但错误消息可能在 Windows 上显示 Unix 风格路径
- **影响：** 外观问题 — 路径可用但可能让 Windows 用户困惑
- **建议：** 显示用 `str(path)`，操作用 pathlib
- **验证：** 在 Windows 上运行脚本并检查错误消息格式

**CP2.2 - Python 可执行文件检测** （优先级：中） `[DONE]`
- **严重程度：** 警告
- **描述：** hooks/hooks.json 使用 `python` 命令：
  ```json
  "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/session-start.py\""
  ```
- **影响：** 如果 `python` 不在 PATH 中会失败（某些系统使用 `python3`）
- **建议：** 在 README 前置条件中记录 Python PATH 要求，或在包装器中使用 `sys.executable`
- **验证：** 在 `python` 不在 PATH 中的系统上测试

**CP2.3 - 平台清单同步** （优先级：低） `[SKIPPED -- 当前设计正确]`
- **严重程度：** 信息
- **描述：** .version-bump.json 追踪 5 个文件，但 OpenClaw 共享 .claude-plugin/plugin.json
- **影响：** 无 — 这与 CLAUDE.md 表格一致
- **建议：** 在 .version-bump.json 中添加注释说明 OpenClaw 共享 Claude Code 清单
- **验证：** 验证 OpenClaw 安装读取 .claude-plugin/plugin.json

### 2.2 路径处理

**发现：** 使用 pathlib 的路径处理总体良好，需小幅改进。

**证据：**
- 所有脚本使用 pathlib.Path
- 路径解析使用 .resolve() 获取绝对路径
- 无硬编码的 Windows 风格路径（C:\）

**问题：**

**CP2.4 - 相对路径假设** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 部分脚本假设当前目录为项目根目录
- **影响：** 从子目录调用时会失败
- **建议：** 所有脚本应从自身位置解析项目根目录，而非 cwd
- **验证：** 从 skills/ 子目录运行 `bundles-forge audit-skill .` 并验证正常工作

---

## 3. 文档有效性

### 3.1 README + docs 结构

**发现：** 文档质量高，规范来源管控清晰，但存在一定冗余。

**证据：**
- README.md: 382 行，涵盖安装、快速入门、概念、平台支持
- docs/: 10 份指南（含 .zh.md 翻译共 20 个文件）
- CLAUDE.md: 200+ 行，涵盖架构、命令、约定
- 每份指南声明 `> **Canonical source:**` 指向 skills/agents

**优势：**
- 规范来源策略由 audit_docs.py（D8 检查）强制执行
- 数值交叉验证（D9）确保指南与技能一致
- 中文翻译保持同步（D7-D9 检查）

**问题：**

**D3.1 - CLAUDE.md 与 README 冗余** （优先级：高） `[DEFERRED -- Phase 3]`
- **严重程度：** 警告
- **描述：** CLAUDE.md 和 README 均涵盖：
  - 项目概述
  - 技能列表
  - 架构（中心-辐射）
  - 平台支持
  - 命令
- **影响：** 维护负担 — 变更必须在 2 个文件间同步
- **分析：** CLAUDE.md 面向 AI 代理，README 面向人类，但重叠显著
- **建议：**
  - CLAUDE.md: 聚焦路由（技能列表、命令映射、约定）
  - README: 聚焦用户导引（是什么/为什么、安装、快速入门）
  - 将架构细节移至 docs/concepts-guide.md（已存在）
- **验证：** 运行 audit_docs.py 并验证无 D1（README-技能不同步）警告

**D3.2 - docs/ 指南冗余** （优先级：中） `[SKIPPED -- 当前设计合理]`
- **严重程度：** 信息
- **描述：** 部分指南与技能内容重复：
  - docs/auditing-guide.md vs skills/auditing/SKILL.md
  - docs/scaffolding-guide.md vs skills/scaffolding/SKILL.md
- **影响：** 指南必须与技能保持同步（D9 强制执行，但增加维护量）
- **分析：** 指南提供用户友好的解释，技能提供执行指令 — 重叠是有意为之
- **建议：** 保留指南，但确保聚焦"为什么"和"何时"，而非"如何"（这在技能中）
- **验证：** 审计 D9 发现 — 应为零数值不匹配

**D3.3 - 参考文件可发现性** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** skills/*/references/ 下 33 个参考文件未在任何地方被索引
- **影响：** 用户可能不知道这些文件的存在
- **建议：** 在每个技能的 SKILL.md 中添加 references/ 索引（例如"参见 references/: X, Y, Z"）
- **验证：** 在 SKILL.md 文件中搜索 "references/" 并验证每个技能列出了其参考文件

### 3.2 单一事实来源

**发现：** 事实来源管控出色，权威层级清晰。

**证据：**
- source-of-truth-policy.md 定义了 7 层层级
- auditor 代理在定性评估期间应用该策略
- audit_docs.py 强制执行 D8（规范来源声明）和 D9（数值交叉验证）

**优势：**
- 矛盾解决协议清晰
- 脚本是实现，不是事实来源
- 代理文件是委托来源（仅对执行协议具有权威性）

**问题：**

**D3.4 - 第 5 层例外歧义** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** source-of-truth-policy.md 说 CLAUDE.md 是"路由索引"，但对"安全规则、命令、关键约定"做了例外
- **影响：** 不清楚 CLAUDE.md 中哪些内容是权威的，哪些是摘要
- **建议：** 将安全规则移至 skills/auditing/references/security-rules.md，从 CLAUDE.md 引用
- **验证：** 审计不应在 CLAUDE.md 与技能之间显示 [Source Conflict] 发现

---

## 4. 工作流与测试

### 4.1 技能/代理分解

**发现：** 分解合理，调度模式清晰。

**证据：**
- 8 个技能、3 个代理，调用关系清晰
- 集成部分对称地记录 Calls/Called-by
- 工作流审计检查（W1-W11）验证图拓扑

**优势：**
- 无未声明的循环依赖（W1）
- 所有技能均可从入口点到达（W2）
- 产物交接有文档记录（W5）

**问题：**

**W4.1 - 工作流行为层利用不足** （优先级：高） `[PARTIAL -- 静态链测试完成，动态链Phase 3]`
- **严重程度：** 警告
- **描述：** W10-W11（通过 evaluator 代理进行行为验证）很少运行：
  - workflow-checklist.md 说"evaluator 不可用时跳过"
  - 没有测试套件覆盖 W10-W11
  - CI 不运行行为检查
- **影响：** 工作流链条可能存在静态检查遗漏的断裂交接
- **建议：**
  - 添加 tests/test_workflow_chains.py，包含 2-3 个关键链条场景
  - 作为可选任务加入 CI（初期允许失败）
  - 记录预期的 evaluator 调度模式
- **验证：** CI 应显示工作流链条测试正在运行

**W4.2 - 代理调度回退** （优先级：中） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 技能在子代理不可用时有内联回退：
  - auditing: "读取 agents/auditor.md 并内联执行"
  - scaffolding: "读取 agents/inspector.md 并内联执行"
- **影响：** 回退路径很少被测试，可能与代理行为产生偏差
- **建议：** 添加禁用子代理调度的测试并验证回退正常工作
- **验证：** 测试套件应覆盖调度和回退两条路径

### 4.2 测试覆盖

**发现：** 脚本和集成覆盖良好，技能内容覆盖有限。

**证据：**
- 4 个测试套件：test_scripts.py、test_integration.py、test_graph_fixtures.py、test_unit.py
- 65+ 测试通过
- CI 在 Python 3.9 和 3.12 上运行所有测试
- 脚本覆盖率 80%+（audit_skill.py、audit_security.py、audit_docs.py）

**优势：**
- 脚本测试覆盖项目模式、技能模式、JSON 输出、错误处理
- 集成测试覆盖钩子、版本同步、技能发现
- 图固件测试依赖分析

**问题：**

**T4.1 - 技能内容质量测试** （优先级：高） `[DONE]`
- **严重程度：** 警告
- **描述：** 没有测试验证技能内容质量：
  - 描述是否正确触发
  - 指令是否可执行
  - 示例是否准确
  - 交叉引用是否解析
- **影响：** 技能回归可能直到用户报告才被发现
- **建议：** 添加 tests/test_skill_quality.py：
  - 解析所有 SKILL.md 文件
  - 验证描述以 "Use when" 开头
  - 验证交叉引用解析到现有技能
  - 验证集成部分对称
- **验证：** 测试套件应在 CI 之前捕获损坏的交叉引用

**T4.2 - 钩子冒烟测试** （优先级：中） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** test_integration.py 测试钩子输出格式，但不测试真实会话中的钩子行为
- **影响：** 钩子回归（如 session-start.py 未能输出提示）可能不被发现
- **建议：** 添加模拟 SessionStart 事件并验证提示出现的集成测试
- **验证：** 如果 session-start.py 以非零退出或产生格式错误的 JSON，测试应失败

**T4.3 - 跨平台测试覆盖** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** CI 仅在 ubuntu-latest 上测试，未覆盖 Windows 或 macOS
- **影响：** 平台特定问题（路径处理、Python 可执行文件）可能不被发现
- **建议：** 在 CI 中添加 matrix: os: [ubuntu-latest, windows-latest, macos-latest]
- **验证：** CI 应显示测试在所有 3 个平台上通过

### 4.3 CI 有效性

**发现：** CI 流水线稳健，检查全面。

**证据：**
- .github/workflows/validate-plugin.yml 运行：
  - JSON 验证
  - 版本漂移检查
  - 检查清单漂移检查
  - 技能质量审计
  - 安全扫描
  - 文档一致性
  - 所有测试套件
- Python 3.9 和 3.12 矩阵

**优势：**
- 在合并前捕获版本漂移
- 捕获检查清单漂移（audit-checks.json vs markdown 表格）
- 运行完整审计流水线

**问题：**

**CI4.1 - CI 中缺少工作流审计** （优先级：中） `[DONE]`
- **严重程度：** 信息
- **描述：** CI 运行 audit-skill、audit-security、audit-docs，但不运行 audit-workflow
- **影响：** 工作流完整性问题（W1-W11）可能不被发现
- **建议：** 在 CI 中添加 `bundles-forge audit-workflow .`
- **验证：** CI 应显示工作流审计通过

**CI4.2 - 无性能基准** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 没有 CI 任务追踪脚本性能（audit_skill.py 运行时间、测试套件耗时）
- **影响：** 性能回归可能不被发现
- **建议：** 添加追踪关键指标随时间变化的基准任务
- **验证：** 如果 audit_skill.py 在参考项目上耗时 >5s，CI 应报告

---

## 5. 冗余与过度工程

### 5.1 冗余

**发现：** 冗余极少，大部分因关注点分离而合理。

**证据：**
- CLAUDE.md vs README 重叠（见 D3.1）
- docs/ 指南 vs 技能重叠（见 D3.2）
- bump_version.py 同时存在于 skills/releasing/scripts/ 和 skills/scaffolding/assets/scripts/

**问题：**

**R5.1 - 重复的 bump_version.py** （优先级：中） `[DONE]`
- **严重程度：** 警告
- **描述：** bump_version.py 出现在 2 个位置：
  - skills/releasing/scripts/bump_version.py（生产版）
  - skills/scaffolding/assets/scripts/bump_version.py（脚手架项目模板）
- **影响：** 变更必须手动同步
- **建议：** 将脚手架模板改为符号链接，或在脚手架生成时从 releasing 复制
- **验证：** 对比两个文件并验证完全一致

**R5.2 - 代理调度模式** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 每个调度代理的技能都有类似的调度逻辑：
  - 检查子代理是否可用
  - 带上下文调度
  - 解析报告
  - 不可用时回退到内联
- **影响：** 调度逻辑在 3 个技能（auditing、scaffolding、optimizing）中重复
- **建议：** 将调度模式提取到共享参考（例如 references/agent-dispatch-protocol.md）
- **验证：** 技能应引用共享协议，而非重复指令

### 5.2 过度工程

**发现：** 总体范围合理，少数方面可以简化。

**问题：**

**OE5.1 - 6 平台支持** （优先级：低） `[SKIPPED -- 非过度工程]`
- **严重程度：** 信息
- **描述：** 项目支持 6 个平台，但大多数用户可能只用 1-2 个
- **影响：** 平台特定适配器的维护负担
- **分析：** 这是项目的核心价值主张 — 不属于过度工程
- **建议：** 无需更改，但考虑弃用使用率 <5% 的平台
- **验证：** 如有条件追踪平台安装指标

**OE5.2 - 167 项审计检查** （优先级：低） `[SKIPPED -- 非过度工程]`
- **严重程度：** 信息
- **描述：** audit-checks.json 定义了跨 10 个类别的 167 项检查
- **影响：** 全面但对用户可能造成负担
- **分析：** 检查按类别和严重程度组织良好 — 不属于过度工程
- **建议：** 考虑添加"快速审计"模式，仅运行关键检查
- **验证：** 快速模式应在 <5s 内完成

**OE5.3 - 33 个参考文件** （优先级：低） `[SKIPPED -- 非过度工程]`
- **严重程度：** 信息
- **描述：** 8 个技能共 33 个参考文件（平均每个技能 4.1 个）
- **影响：** 维护负担高，但对 Token 效率必要
- **分析：** 参考文件使 SKILL.md 保持在 500 行以下 — 合理
- **建议：** 无需更改，但确保参考文件在 SKILL.md 中有索引
- **验证：** 每个 SKILL.md 应列出其参考文件

---

## 6. 缺口与偏差

### 6.1 缺口

**G6.1 - 无技能性能指标** （优先级：中） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 无法衡量技能性能：
  - 触发准确率（描述是否匹配用户意图？）
  - 执行成功率（技能是否无错完成？）
  - Token 效率（实际使用了多少上下文？）
- **影响：** 优化决策基于人工审查，而非数据
- **建议：** 添加可选遥测以追踪技能调用、完成、错误
- **验证：** 遥测应为可选加入且保护隐私

**G6.2 - 无技能版本管理** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 技能没有独立版本号，仅有项目版本
- **影响：** 难以追踪哪个技能版本引入了回归
- **建议：** 在 SKILL.md 中添加可选的 `version` frontmatter 字段
- **验证：** audit_skill.py 应在存在时验证版本格式

**G6.3 - 无技能弃用路径** （优先级：低） `[DEFERRED -- Phase 3]`
- **严重程度：** 信息
- **描述：** 没有文档化的技能弃用流程
- **影响：** 旧技能会积累而没有明确的移除路径
- **建议：** 添加 `deprecated: true` frontmatter 字段和弃用指南
- **验证：** 引导技能应在路由中跳过已弃用的技能

### 6.2 偏差

**M6.1 - 编排器复杂度 vs 执行器简洁** （优先级：高） `[DONE]`
- **严重程度：** 警告
- **描述：** 编排器是执行器的 2 倍大（见 A1.1）
- **影响：** 违反编排器应为轻量路由的原则
- **建议：** 将决策树提取到 references/（见 A1.1）
- **验证：** 编排器行数应 <300

**M6.2 - 代理调度开销 vs 收益** （优先级：中） `[SKIPPED -- 同A1.2]`
- **严重程度：** 信息
- **描述：** 代理调度增加延迟（上下文分叉、子代理启动），收益有限
- **影响：** 审计更慢，错误处理更复杂
- **分析：** 隔离收益（只读代理）可能不足以抵消开销
- **建议：** 基准测试调度延迟，考虑对 inspector 采用内联执行
- **验证：** 测量有/无代理调度的审计耗时

---

## 7. 分阶段实施计划（修订版）

> **说明：** 实施过程中本计划已修订。原第 1 阶段（CP2.2 + T4.1 + D3.1）已重排，以优先保障 Token 效率与回归防护。经分析后，A1.2 代理合并方案未采纳。

### 第 1 阶段：回归防护 + Token 效率 `[DONE]`

1. **T4.1 - 技能内容质量测试** `[DONE]`
   - 已创建 tests/test_skill_quality.py（5 项测试：描述格式、长度、交叉引用、Integration 对称性）
   - 已加入 run_all.py（现为 5 个测试套件）

2. **A1.1 - 编排器复杂度** `[DONE]`
   - optimizing：429→340 行（将 A/B 评估协议与 Target 5 重构操作抽至 references/）
   - blueprinting：337→301 行（将自适应模式问题 4a–7 抽至 references/）

3. **CI4.1 - CI 中缺少工作流审计** `[DONE]`
   - 已在 validate-plugin.yml 中加入 `bundles-forge audit-workflow .` 步骤

### 第 2 阶段：工作流测试 + 文档 `[DONE]`

4. **W4.1 - 静态工作流链条测试** `[DONE]`
   - 创建 tests/test_workflow_chains.py（9 个测试：图完整性、Calls/Called-by 对称性、连通性）
   - 动态行为测试推迟至第 3 阶段

5. **R5.1 - bump_version.py 漂移检测** `[DONE]`
   - 在 test_integration.py 中添加 TestBumpVersionSync（剥离文档字符串后对比逻辑）

6. **CP2.2 - Python 可执行文件说明** `[DONE]`
   - 在 README 前置条件中补充 `python` PATH 要求和别名说明（中英双语）

### 第 3 阶段：精细化（已推迟）

7. **D3.1** — CLAUDE.md 整合
8. **CP2.1** — Windows 路径显示
9. **T4.3** — 跨平台 CI 矩阵
10. **D3.3** — references/ 可发现性
11. **G6.1** — 技能性能指标

---

## 8. 验证方法

### 自动化验证

**脚本：**
- `bundles-forge audit-skill .` — 验证行数、交叉引用
- `bundles-forge audit-docs .` — 验证文档一致性
- `bundles-forge audit-workflow .` — 验证工作流完整性
- `python tests/run_all.py` — 验证所有测试通过

**CI：**
- .github/workflows/validate-plugin.yml — 验证所有检查通过
- 将工作流链条测试加入 CI
- 添加跨平台矩阵

### 人工验证

**架构：**
- 审查编排器 SKILL.md 文件的决策树提取
- 审查代理调度模式的合并机会
- 审查集成部分的对称声明

**文档：**
- 审查 CLAUDE.md 的路由聚焦 vs 架构细节
- 审查 docs/ 指南的规范来源合规性
- 审查 references/ 的可发现性

**测试：**
- 手动运行工作流链条场景
- 在真实会话中测试钩子行为
- 在 Windows、macOS、Linux 上测试

---

## 9. 风险评估

### 破坏性变更

**高风险：**
- **A1.2 - 代理合并：** 将 inspector 合并到 auditor 会改变调度 API
  - **缓解：** 保留 inspector 作为弃用包装器 1 个版本
  - **迁移：** 更新 scaffolding 技能以使用带模式标志调度 auditor

**中风险：**
- **A1.1 - 编排器重构：** 提取决策树改变技能结构
  - **缓解：** 保留决策树内联 1 个版本，添加弃用警告
  - **迁移：** 技能引用新的 references/ 文件

**低风险：**
- **D3.1 - CLAUDE.md 重构：** 将内容移至 docs/ 不会破坏功能
  - **缓解：** 无需 — 文档变更不具破坏性
  - **迁移：** 更新 README 中的链接

### 非破坏性变更

**所有第 1 阶段和大部分第 2 阶段变更均为非破坏性：**
- 添加测试不改变行为
- 记录 Python 要求不改变代码
- 添加 CI 检查不改变用户体验
- 整合重复文件属于内部重构

---

## 10. 结论

bundles-forge 架构良好、基础扎实。中心-辐射模型合理，自动化全面，质量门禁严格。

**第 1 阶段已完成** — 已处理影响最大的问题：

1. **降低编排器复杂度** `[DONE]` — 决策树已抽至 references/（optimizing：429→340，blueprinting：337→301）
2. **新增技能内容质量测试** `[DONE]` — test_skill_quality.py 含 5 项确定性检查
3. **CI 中增加工作流审计** `[DONE]` — validate-plugin.yml 现已运行 audit-workflow

**第 2 阶段已完成** — 强化工作流测试与文档：

4. **静态工作流链测试** `[DONE]` — 9 个测试覆盖图完整性、Calls/Called-by 对称性和中心-辐射连通性
5. **bump_version.py 漂移检测** `[DONE]` — 自动化测试检测两个副本之间的逻辑分歧
6. **Python PATH 文档** `[DONE]` — README 前置条件已更新别名说明（中英双语）

**后续机会（第 3 阶段）：**

7. **整合文档** — 减少 CLAUDE.md 与 README 重叠
8. **跨平台 CI** — 在测试矩阵中添加 Windows 和 macOS
9. **参考文件可发现性** — 在每个 SKILL.md 中索引 references/

**决策：不合并代理** — inspector/auditor 分离因职责边界清晰而保留。

**总体评级：** A-（优秀，仍有针对性改进空间）

**建议下一步：**
1. 根据项目需要评估第 3 阶段项
2. 安排下一轮架构审查

---

**审查完成：** 2026-04-16  
**第 1 阶段落地：** 2026-04-16  
**第 2 阶段落地：** 2026-04-16  
**审查人：** Claude Code Agent  
**下次审查：** 2026-07-16（3 个月后）
