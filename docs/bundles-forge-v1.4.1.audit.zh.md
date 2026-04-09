# Bundles Forge v1.4.1 — 综合审计报告

**日期：** 2026-04-09
**范围：** 全项目 — 8 个技能、3 个代理、6 个命令、5 个脚本、5 个平台清单、5 个测试
**方法论：** 10 维度分析 + 逐组件审查

---

## 执行摘要

Bundles Forge 是一个架构良好的项目，技能质量整洁（0 条 lint 发现），版本同步，脚本代码复用率高。但存在一些**结构性问题**值得关注：

| 维度 | 评级 | 关键发现 |
|------|------|----------|
| #1 边界测试 | B | 脚本能优雅处理缺失目录/文件；YAML 解析器脆弱；空 skills 目录返回 exit 0（应发出警告） |
| #2 提示词冲突 | B+ | 无硬性矛盾；"MUST/ALWAYS"用法与 authoring 自身反对该用法的建议之间存在张力 |
| #3 循环依赖 | A | 技能引用无循环；图结构为清晰的 DAG |
| #4 降级路径 | C | 大多数技能无明确的回退指令；钩子失败 = 静默降级 |
| #5 竞态条件 | B+ | 代理报告使用序列号避免冲突；`.bundles-forge/` 是共享可变状态 |
| #6 信息密度 | A- | 所有技能均在预算内；引导注入 112 行（上限 200）；最大主体 302 行（上限 500） |
| #7 重复信息 | C+ | Token 预算在 2 个技能中重复；描述反模式在 3 处重复；"Use when"指导在 3 个技能中重复 |
| #8 时序依赖 | B | 引导→技能→代理流程定义良好；Codex 无引导注入（有意为之但未记录） |
| #9 冷/热启动 | B | 钩子在 `clear|compact` 时重新触发；冷热启动无状态差异；可能浪费 token |
| #10 版本兼容 | A- | 版本同步机制健壮；.version-bump.json 覆盖所有清单；版本升级无备份/回滚机制 |

**总体评分：B+** — 架构合理，需在降级路径、信息去重和测试覆盖率方面加强。

---

## #1 边界条件测试

### 测试结果

| 脚本 | 输入 | 行为 | 退出码 | 判定 |
|------|------|------|--------|------|
| `lint_skills.py` | 不存在的路径 | `error: has no skills/ directory` | 1 | 良好 |
| `lint_skills.py` | 空的 skills/ 目录 | 返回 0 条发现，exit 0 | 0 | **薄弱** — 应发出警告 |
| `lint_skills.py` | 格式错误的 frontmatter | 报告 Q1 严重发现 | 2 | 良好 |
| `lint_skills.py` | 目录中缺少 SKILL.md | 报告 Q1 严重发现 | 2 | 良好 |
| `lint_skills.py` | 描述超过 250 字符 | 报告 Q7 警告 | 1 | 良好 |
| `scan_security.py` | 不存在的路径 | `error: has no skills/ directory` | 1 | 良好 |
| `audit_project.py` | 不存在的路径 | `error: has no skills/ directory` | 1 | 良好 |
| `audit_project.py` | 不完整的项目（无 hooks/） | 报告 S1 严重（缺失目录） | 2 | 良好 |
| `bump_version.py --check` | 从正确目录执行 | 报告同步状态 | 0 | 良好 |
| `bump_version.py --audit` | 从正确目录执行 | 扫描仓库，无未声明版本 | 0 | 良好 |
| `session-start` | 无平台环境变量 | 默认使用 Claude Code 格式 | 0 | 良好 |
| `session-start` | 缺少 SKILL.md | 输出 "Error reading bootstrap skill" | 0 | **薄弱** — 应返回非零退出码 |

### 发现的问题

1. **空 skills 目录返回 exit 0**（`lint_skills.py`）：当 `skills/` 存在但无子目录时，检查器报告"已检查 0 个技能"并正常退出。至少应产生信息级别的警告。

2. **YAML 解析器为自定义实现且脆弱**（`lint_skills.py:parse_frontmatter`）：使用正则 `^---\s*\n(.*?)\n---\s*\n` 替代 YAML 库。局限性：
   - 不支持 YAML 转义序列
   - 多行值仅在续行以 2+ 个空格开头时有效
   - 包含转义内部引号的带引号值解析不正确
   - frontmatter 值不支持数组或对象

3. **session-start 输出错误字符串但退出码为 0**：当 `using-bundles-forge/SKILL.md` 缺失时，钩子以 JSON 包装输出 "Error reading bootstrap skill" 但退出码为 0。代理收到一个无意义的引导注入，且无错误信号。

4. **bump_version.py 无备份/回滚机制**：如果写入一个清单成功但另一个失败（磁盘满、权限问题），没有回滚。已写入的文件保留新版本，而其他文件仍为旧版本 — 恰恰造成了该工具旨在防止的版本漂移。

5. **scan_security.py 误报风暴**：安全扫描器将自身的规则定义标记为严重发现（`scan_security.py` 自身 10 条严重）。`audit-checklist.md` 和 `security-checklist.md` 参考文件也触发 14+ 条严重发现，因为它们记录了攻击模式。这些都是由于上下文无感知的正则匹配导致的误报。

### 改进建议

- **P1：** 在 `scan_security.py` 中为自引用文件添加白名单（或至少将 `scripts/` 和 `references/` 从扫描中排除，因为这些是工具/文档）
- **P2：** 当引导 SKILL.md 缺失时，使 `session-start` 返回非零退出码
- **P2：** 当 `lint_skills.py` 发现零个技能需检查时添加警告
- **P3：** 为 `bump_version.py` 添加原子写入或备份机制

---

## #2 提示词冲突检测

### 方法论

从所有 8 个 SKILL.md 文件中提取所有命令式指令（MUST、NEVER、ALWAYS、REQUIRED），并交叉比较是否存在矛盾。

### 发现

**未发现硬性矛盾。** 所有技能内部一致且交叉引用正确。

**一处元级张力：**

| 文件 | 行号 | 指令 |
|------|------|------|
| `authoring/SKILL.md` | 109 | "如果你发现自己在写全大写的 MUST 或 ALWAYS，这是一个信号，需要重新表述：解释其原因" |
| `authoring/SKILL.md` | 113 | 展示反面示例："You MUST ALWAYS check version drift before releasing. NEVER skip this step." |
| `optimizing/SKILL.md` | 269 | "添加 MUST/ALWAYS/NEVER 而不解释原因"被列为常见错误 |
| `auditing/SKILL.md` | 215 | "**Never** auto-install a skill that has unresolved critical security findings" |
| `auditing/SKILL.md` | 229 | "**Always** run `python scripts/bump_version.py --check`" |
| `releasing/SKILL.md` | 211 | "**Always** run full pipeline" |

**分析：** authoring 和 optimizing 技能明确建议不要使用 MUST/ALWAYS/NEVER 指令，推荐"解释原因"。然而 auditing 和 releasing 技能恰好使用了这些模式。这不是功能性冲突 — auditing/releasing 的规则是具体的安全约束，绝对指令在此场景下是恰当的。但 authoring 指导未区分"基于推理的指令"和"硬性安全边界"，使得项目看起来违反了自身的建议。

**建议：** authoring 应承认绝对指令适用于安全边界（安全扫描、版本检查），同时不鼓励在行为指导中使用它们。

### 代理提示词一致性

| 代理 | 约束 | 是否与技能匹配？ |
|------|------|-------------------|
| `auditor.md` | `disallowedTools: Edit` | 是 — auditing 声明"永不修改文件" |
| `evaluator.md` | `disallowedTools: Edit` | 是 — optimizing 声明代理为只读 |
| `inspector.md` | `disallowedTools: Edit` | 是 — scaffolding 声明仅做验证 |

所有代理约束与其调度技能一致。

### AG4 警告分析

安全扫描器对所有 3 个代理标记了 AG4"过于宽泛的权限声明"。这是一个**误报** — 代理并未声明权限；`disallowedTools` 字段是限制它们的。扫描器的正则可能匹配了关于代理"能"或"将"做什么的措辞。

---

## #3 循环依赖检测

### 依赖图（来自交叉引用）

```
blueprinting ──→ scaffolding ──→ auditing ──→ optimizing
     │                │              │              │
     │                │              └──→ releasing  │
     │                │                      │       │
     │                └──→ authoring         │       │
     │                                       │       │
     └──→ porting ←─────────────────────────┘       │
                                                     │
     optimizing ──→ auditing（单次循环，受门控限制）
     releasing  ──→ auditing
     releasing  ──→ optimizing
```

### 循环分析

**存在一处互相引用：** `auditing ↔ optimizing`
- auditing 说："有警告？建议 `bundles-forge:optimizing`"
- optimizing 说："修改后，调用 `bundles-forge:auditing` 进行变更后验证"

**这不是真正的循环**，因为 optimizing 明确声明："仅一次审计循环（无循环）"（`optimizing/SKILL.md:260`）。门控防止了无限递归。

**同理：** `releasing → auditing → optimizing → auditing` 受同一单次循环门控约束。

**判定：无无界循环。** 图结构为 DAG，附带一条受门控的双向边。

### 缺失引用

所有 `bundles-forge:xxx` 交叉引用均解析到实际技能目录。未发现断裂链接（由 lint_skills.py X1 检查确认：0 条发现）。

---

## #4 降级路径验证

### 故障场景

| 场景 | 预期行为 | 实际行为 | 判定 |
|------|----------|----------|------|
| 引导 SKILL.md 缺失 | 钩子应以明确错误失败 | 以 JSON 输出 "Error reading bootstrap skill"，exit 0 | **不佳** — 静默降级 |
| 钩子脚本失败 | 会话应警告用户 | 取决于平台；Claude Code 可能静默跳过 | **未知** — 无明确处理 |
| 子代理不可用 | 技能应回退到内联执行 | README 中提及（"主代理内联执行相同工作"）但技能指令中未提及 | **缺口** — 技能缺少回退指导 |
| 脚本错误（Python 未找到） | 测试应报告失败 | `run-all.sh` 警告 "Python not found — skipping" | **可接受** |
| `.version-bump.json` 缺失 | 应阻止发布操作 | `bump_version.py` 以明确错误退出码 1 退出 | **良好** |
| Windows 上 Git 不可用 | 钩子应优雅降级 | `run-hook.cmd` 静默退出码 0 | **可接受**但应记录日志 |

### 关键缺口

1. **技能中无子代理回退指令：** README 记录了代理可以回退到内联执行，但实际的技能文件（auditing、optimizing、scaffolding）从未指导代理在子代理调度失败时应做什么。一个严格按照技能执行的代理会尝试调度、失败，且无指导可循。

2. **引导失败不可见：** 如果 `session-start` 钩子失败或产生错误输出，代理在没有 bundles-forge 技能路由表的情况下继续执行。没有机制让代理检测到"我应该拥有 bundles-forge 技能但它们未加载"。

3. **缺失脚本无优雅降级：** 技能引用了 `python scripts/audit_project.py`、`python scripts/lint_skills.py` 等，但从未指定 Python 不可用或脚本缺失时应怎么做。

### 改进建议

- **P1：** 在 auditing、optimizing 和 scaffolding 中添加明确的回退指令："如果子代理调度不可用，内联执行相同的检查。"
- **P1：** 使 session-start 在引导读取失败时返回非零退出码
- **P2：** 在引用脚本的技能中添加"如果 Python/脚本不可用，使用 Read 和 Grep 手动执行检查"指导

---

## #5 竞态条件分析

### 并行执行场景

| 场景 | 共享状态 | 风险 | 缓解措施 |
|------|----------|------|----------|
| 两个评估器（A/B 测试） | `.bundles-forge/` 目录 | 文件名冲突 | 序列号追加（已记录） |
| 检查器 + 审计器同项目 | `.bundles-forge/` 目录 | 不同文件名 | 低风险 — 不同的命名模式 |
| 两次并发审计 | `.bundles-forge/` + 脚本 | 报告冲突 | 序列号追加 |
| 并发版本升级 | `.version-bump.json` + 清单文件 | 部分写入损坏 | **无缓解措施** |

### 分析

1. **代理报告文件名**使用 `<project>-<version>-<type>.YYYY-MM-DD.md` 格式并带有序列号冲突避免机制。这对常见场景设计良好。

2. **并发版本升级**是最危险的场景。`bump_version.py` 读取所有清单，顺序写入，无文件锁。如果两个进程同时升级版本，清单可能出现混合版本。但在实践中这种场景不太可能（单代理工作流）。

3. **`.bundles-forge/` 目录**无锁机制。如果两个代理同时写入同一报告文件（可能性低但存在），可能发生数据损坏。"永不修改现有文件"的指令缓解了这一问题。

**判定：** 实际风险低。代理工作流的顺序性使得并发访问不太可能。序列号机制是合理的防护措施。

---

## #6 信息密度评估

### Token 预算合规性

| 技能 | 行数 | 预算 | 预估 Token | 状态 |
|------|------|------|-----------|------|
| `using-bundles-forge`（引导） | 112 | 200 | ~1,412 | 合规 |
| `blueprinting` | 302 | 500 | ~3,528 | 合规 |
| `optimizing` | 283 | 500 | ~3,250 | 合规 |
| `authoring` | 220 | 500 | ~2,692 | 合规 |
| `auditing` | 245 | 500 | ~2,477 | 合规 |
| `releasing` | 228 | 500 | ~2,218 | 合规 |
| `scaffolding` | 158 | 500 | ~1,905 | 合规 |
| `porting` | 100 | 500 | ~960 | 合规 |

所有技能均在其声明的预算内。纪律良好。

### 引导注入成本

session-start 钩子在每次会话启动、清除或压缩事件时注入约 **6,204 字节**（~1,550 token）。这是安装 bundles-forge 的固定成本。

### 参考文件大小

| 文件 | 行数 | 用途 |
|------|------|------|
| `scaffolding/references/project-anatomy.md` | 447 | bundle-plugin 完整文件参考 |
| `auditing/references/audit-checklist.md` | 233 | 9 类质量检查清单 |
| `auditing/references/security-checklist.md` | 216 | 50+ 安全模式检查 |
| `porting/references/platform-adapters.md` | 145 | 平台特定文档 |
| `scaffolding/references/scaffold-templates.md` | 60 | 模板文件索引 |
| `using-bundles-forge/references/codex-tools.md` | 15 | 工具映射 |
| `using-bundles-forge/references/gemini-tools.md` | 15 | 工具映射 |

`project-anatomy.md` 以 447 行为最大参考文件。提取方式恰当 — 每次运行 scaffolding 时都加载它会显著膨胀上下文。

### 密度评估

- **高密度（良好）：** `porting`（100 行，覆盖 5 个平台）、`scaffolding`（158 行，两种模式）、`using-bundles-forge`（112 行，完整路由表）
- **中等密度：** `auditing`（245 行用于 9 个类别）、`releasing`（228 行用于 6 步流水线）
- **较低密度：** `blueprinting`（302 行，包含 3 个场景及访谈问题 — 难以压缩）、`optimizing`（283 行，包含 6 个目标 + 反馈迭代 — 同样难以压缩）

**判定：** 无冗余。blueprinting 和 optimizing 是真正复杂的技能，确实需要其行数。

---

## #7 重复信息检测

### 重复概念

| 概念 | 位置 | 是否逐字重复？ | 是否需要去重？ |
|------|------|---------------|---------------|
| Token 预算（200/500/250） | `authoring`（l.138-140）、`optimizing`（l.109-110, 126） | 近乎逐字 | **是** — 提取到共享参考 |
| "描述以 Use when 开头" | `authoring`（l.47）、`optimizing`（l.64）、`blueprinting`（l.83） | 改写表述 | 否 — 各自在上下文中使用 |
| 描述反模式（代理快捷方式） | `authoring`（l.48）、`optimizing`（l.69）、`auditing`（l.230） | 其中 2 处近乎逐字 | **是** — authoring 和 optimizing 重复了相同发现 |
| Kebab-case 命名 | `blueprinting`、`scaffolding`、`using-bundles-forge` | 简短提及 | 否 — 上下文相关 |
| "存在未解决的严重安全发现时不得自动安装" | `auditing`（l.215）、`auditing/references/audit-checklist.md` | 相同规则 | 否 — 参考文件做了展开 |
| 平台检测（CURSOR_PLUGIN_ROOT） | `porting`（l.67）、`porting/references/platform-adapters.md` | 相同信息 | 否 — 参考文件为权威来源 |
| 安全扫描 5 个攻击面 | `auditing/SKILL.md`、`auditing/references/security-checklist.md`、`README.md` | SKILL.md 中为摘要 | 否 — 适当的渐进式披露 |

### 高影响去重机会

1. **Token 预算：** 创建 `references/token-budgets.md`（5 行），由 authoring 和 optimizing 引用。目前相同的三个数字出现在两个技能中。

2. **描述反模式段落：** authoring/SKILL.md:48 和 optimizing/SKILL.md:69 包含关于描述快捷方式的相同关键发现。提取到 `authoring/references/description-conventions.md` 并从 optimizing 交叉引用。

### 低影响（保持原样）

- "Use when"指导在每个技能中具有恰当的上下文性
- Kebab-case 提及简短且服务于不同目的
- 安全面描述属于恰当的渐进式披露（SKILL.md 中为摘要，参考文件中为详情）

---

## #8 时序依赖分析

### 各平台加载 DAG

```
┌─────────────────────────────────────────────────────────┐
│                      会话启动                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Claude Code:                                           │
│    SessionStart 事件                                    │
│    → hooks.json（匹配器：startup|clear|compact）         │
│    → run-hook.cmd session-start                         │
│    → session-start（bash）                              │
│    → 读取 using-bundles-forge/SKILL.md                  │
│    → 输出 hookSpecificOutput JSON                       │
│    → 代理获得路由表                                      │
│                                                         │
│  Cursor:                                                │
│    sessionStart 事件                                    │
│    → hooks-cursor.json                                  │
│    → ./hooks/session-start                              │
│    → 读取 using-bundles-forge/SKILL.md                  │
│    → 输出 additional_context JSON                       │
│    → 代理获得路由表                                      │
│                                                         │
│  Gemini CLI:                                            │
│    扩展加载                                              │
│    → gemini-extension.json                              │
│    → contextFileName: GEMINI.md                         │
│    → @./skills/using-bundles-forge/SKILL.md             │
│    → @./skills/using-bundles-forge/references/gemini..  │
│    → 代理获得路由表 + 工具映射                            │
│                                                         │
│  OpenCode:                                              │
│    插件加载                                              │
│    → .opencode/plugins/bundles-forge.js                 │
│    → 注册技能路径                                        │
│    → 消息转换（首条消息）                                 │
│    → 前置引导内容                                        │
│    → 代理获得路由表 + 工具映射                            │
│                                                         │
│  Codex:                                                 │
│    技能发现                                              │
│    → ~/.agents/skills/bundles-forge（符号链接）           │
│    → 读取 AGENTS.md（指向 CLAUDE.md）                    │
│    → 无引导注入                                          │
│    → 代理有指南但无路由表                                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                      技能调用                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  用户意图 / 斜杠命令 / 交叉引用                          │
│    → Skill 工具（CC/Cursor）/ activate_skill（Gemini）   │
│    → SKILL.md 加载到上下文                               │
│    → references/ 按需加载                                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                      代理调度                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  技能指令 → 调度子代理                                    │
│    → agents/<role>.md 加载                               │
│    → 代理读取参考文件（audit-checklist 等）               │
│    → 代理将报告写入 .bundles-forge/                      │
│    → 控制权返回父技能                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 时序假设

1. **引导必须在任何技能调用之前完成。** 如果钩子静默失败，代理没有路由表，技能匹配退化为仅基于描述的匹配。

2. **Codex 无引导注入。** AGENTS.md 指向 CLAUDE.md 获取指南，但两个文件均不包含完整路由表。Codex 用户完全依赖描述匹配进行技能发现 — 这是一个设计选择但未记录为有意为之。

3. **OpenCode 引导注入延迟** — 通过消息转换在首条用户消息时注入，而非在会话启动时。这意味着首条消息有引导上下文，但如果代理在转换触发前开始处理，存在一个短暂的无引导窗口期。

### 改进建议

- **P2：** 在 porting/references/platform-adapters.md 中记录 Codex 无引导设计为有意为之
- **P3：** 考虑在 AGENTS.md 中为 Codex 用户添加轻量级路由表

---

## #9 冷/热启动比较

### 钩子触发分析

`hooks.json` 匹配器：`startup|clear|compact`

| 触发条件 | 上下文 | 行为 |
|----------|--------|------|
| `startup` | 新会话 | 完整引导注入（冷启动） |
| `clear` | 用户执行 /clear | 完整引导重新注入（热启动） |
| `compact` | 上下文压缩 | 完整引导重新注入（热启动） |

### 冷启动与热启动差异

**没有差异。** session-start 钩子始终执行相同操作：读取 SKILL.md，JSON 转义，输出 JSON。无缓存状态，无增量检测。

### Token 浪费分析

每次 `clear` 或 `compact` 事件都会重新注入完整的 ~1,550 token 引导内容。对于压缩 5 次的会话，仅引导就消耗 ~7,750 token。对于这个规模的工具包，这是可接受的开销。

### 状态持久化

会话事件之间没有状态持久化。代理每次都重新学习路由表。这是**正确的**行为 — 引导内容在两次调用之间可能已变化（例如，添加/修改了技能后）。

### Cursor 与 Claude Code 对比

Cursor 的 `hooks-cursor.json` **无匹配器** — `sessionStart` 在每次会话启动时触发。没有等同于 `clear|compact` 触发器的机制。这意味着 Cursor 每个会话只注入一次，而 Claude Code 在 clear/compact 时重新注入。

**影响：** 如果 Cursor 用户在会话中途清除上下文，引导不会重新注入。代理会丢失路由表直到新会话启动。

---

## #10 版本兼容性

### 版本同步覆盖范围

`.version-bump.json` 声明了 5 个文件：

| 文件 | 字段路径 | 是否存在 | 是否同步 |
|------|----------|----------|----------|
| `package.json` | `version` | 是 | 1.4.1 |
| `.claude-plugin/plugin.json` | `version` | 是 | 1.4.1 |
| `.claude-plugin/marketplace.json` | `plugins.0.version` | 是 | 1.4.1 |
| `.cursor-plugin/plugin.json` | `version` | 是 | 1.4.1 |
| `gemini-extension.json` | `version` | 是 | 1.4.1 |

**状态：全部同步。** `--audit` 扫描未发现未声明的版本字符串。

### 未纳入版本同步的文件

| 文件 | 是否有版本？ | 是否跟踪？ | 风险 |
|------|------------|-----------|------|
| `.opencode/plugins/bundles-forge.js` | 无明确版本 | 不适用 | 低 — 运行时从 package.json 读取 |
| `.codex/INSTALL.md` | 无版本字符串 | 不适用 | 低 — 指令与版本无关 |
| `CHANGELOG.md` | 包含版本字符串 | 被审计配置排除 | 排除正确 |

### 健壮性分析

1. **点路径遍历**（`plugins.0.version`）：对 `marketplace.json` 工作正确。但如果数组索引不存在，`_resolve_field_path` 静默返回 None — 无错误，无警告。向 marketplace 数组添加新插件可能导致此字段解析错误。

2. **SemVer 验证**：仅通过正则检查 `X.Y.Z` 格式。预发布标签（如 `1.4.1-beta.1`）被拒绝。这是有意为之但对使用预发布版本的项目有限制。

3. **无预演模式**：`bump_version.py <version>` 立即写入。没有 `--dry-run` 来预览哪些文件会被修改。

---

## 逐组件审查

### 技能

| 技能 | 合理？ | 重复？ | 完整？ | 过度设计？ |
|------|--------|--------|--------|-----------|
| `using-bundles-forge` | 是 — 必要的引导 | 否 | 是 | 否 — 112 行，精简 |
| `blueprinting` | 是 — 防止返工 | 否 | 是 — 3 个场景 | 略微 — Q0"最小化 vs 智能"增加复杂度；可默认为智能 |
| `scaffolding` | 是 — 一致的生成 | 否 | 是 — 2 种模式 | 否 — 模式对应真实需求 |
| `authoring` | 是 — 质量指导 | 部分 — token 预算与 optimizing 重叠 | 是 | 否 — 指导与示例的良好平衡 |
| `auditing` | 是 — 必要的质量关卡 | 否 | 是 — 9 个类别 + 安全 | 略微 — 第 9 类安全扫描与 `scan_security.py` 脚本高度重叠；技能仅增加了"运行脚本"之外的少量价值 |
| `optimizing` | 是 — 反馈循环 | 部分 — 描述指导与 authoring 重叠 | 是 — 6 个目标 | 略微 — 用子代理做 A/B 评估对于可以目测验证的描述变更来说是重型机制 |
| `porting` | 是 — 多平台是核心 | 否 | **缺失**平台移除/弃用 | 否 — 100 行，精简 |
| `releasing` | 是 — 防止漂移 | 否 | 是 | 否 |

### 代理

| 代理 | 合理？ | 重复？ | 完整？ | 过度设计？ |
|------|--------|--------|--------|-----------|
| `inspector` | 是 — 脚手架后验证 | 部分 — 与 auditor 在结构、清单、版本同步方面重叠 | **缺失**功能测试（技能是否能实际加载？） | 否 |
| `auditor` | 是 — 全面评估 | 否 | 是 — 9 个类别含检查清单 | 否 |
| `evaluator` | 是 — A/B 测试 | 否 | **缺失**比较逻辑 — 仅运行一侧；人工必须比较 | 否 |

**Inspector 与 Auditor 重叠：** 两者都验证结构、清单和版本同步。Inspector 在脚手架后运行（快速检查），Auditor 作为全面评估运行（评分）。重叠是有意为之 — Inspector 是快速健全检查，Auditor 是全面审计。但 Inspector 可以将结构/清单/版本检查委托给 Auditor，以避免维护两套验证实现。

### 命令

| 命令 | 合理？ | 重复？ |
|------|--------|--------|
| `bundles-forge` | 是 — 引导入口点 | 否 |
| `bundles-blueprint` | 是 — 清晰的入口点 | 否 |
| `bundles-audit` | 是 | **是** — 功能上与 `bundles-scan` 相同 |
| `bundles-optimize` | 是 | 否 |
| `bundles-release` | 是 | 否 |
| `bundles-scan` | **存疑** | **是** — 调用与 `bundles-audit` 相同的技能 |

**`bundles-scan` 是冗余的。** 它调用 `bundles-forge:auditing` 并在描述中附带"安全聚焦"提示，但 auditing 技能始终包含安全扫描（第 9 类）。scan 命令未提供额外功能。它的存在是为了"语义清晰"但增加了维护负担。

### 脚本

| 脚本 | 合理？ | 重复？ | 完整？ | 过度设计？ |
|------|--------|--------|--------|-----------|
| `_cli.py` | 是 — 出色的复用 | 否 | 是 | 否 |
| `bump_version.py` | 是 — 防止漂移 | 否 | **缺失**预演、备份/回滚 | 否 |
| `lint_skills.py` | 是 — 自动化质量检查 | 否 | **缺失**基本字段之外的 frontmatter 模式验证 | 否 |
| `scan_security.py` | 是 — 自动化扫描 | 否 | **有缺陷** — 对自引用文件大量误报 | 略微 — 54 条无上下文感知的正则规则 |
| `audit_project.py` | 是 — 全面审计 | 部分 — 编排其他脚本但添加了自己的结构检查 | 是 | 否 |

### 测试

| 测试 | 合理？ | 完整？ |
|------|--------|--------|
| `test-bootstrap-injection.sh` | 是 | **失败** — 1 项失败（Claude Code 平台检测） |
| `test-skill-discovery.sh` | 是 | 在其范围内完整 |
| `test-version-sync.sh` | 是 | **失败** — jq 路径解析在 Windows 上异常 |
| `test_scripts.py` | 是 | **主要缺口** — 无错误用例、无边界测试、无单条规则测试、无退出码测试 |
| `run-all.sh` | 是 | **4 套中 3 套失败** |

---

## 测试基础设施问题

当前测试结果：**4 套测试中 3 套失败**

1. `test-bootstrap-injection.sh`：在"Claude Code 平台检测"上失败 — 测试在默认（无环境变量）模式下检查 `hookSpecificOutput`，但条件可能因平台而异。

2. `test-version-sync.sh`：失败原因是基于 jq 的文件存在性检查无法正确解析路径。在 Windows/Git Bash 上，jq 输出的路径可能有编码问题。脚本使用 `jq -r '.files[].path'` 然后检查文件是否存在 — 这在 Unix 上有效但在 Windows 上失效。

3. `test_scripts.py`：通过（Python 测试运行成功）。

4. 缺失的测试覆盖：
   - 无错误用例测试（损坏的 JSON、缺失文件、错误的 YAML）
   - 无单条 lint 规则测试
   - 无单条安全规则测试
   - 无退出码测试
   - 无跨平台测试
   - 无否定测试（"应检测到 X 问题"）

---

## 优先级改进建议

### 优先级 1 — 立即修复（功能性问题）

| # | 问题 | 建议 | 文件 |
|---|------|------|------|
| 1 | 安全扫描器对自身文件误报 | 添加自排除：跳过 `scripts/` 和 `skills/*/references/` 下的 bundled_script 和 skill_content 扫描，或为扫描上下文中的已知安全模式添加白名单 | `scripts/scan_security.py` |
| 2 | 4 套测试中 3 套失败 | 修复 `test-bootstrap-injection.sh` 平台检测检查；修复 `test-version-sync.sh` 的 jq 路径解析以支持 Windows | `tests/test-bootstrap-injection.sh`、`tests/test-version-sync.sh` |
| 3 | 技能指令中无子代理回退 | 在 auditing、optimizing、scaffolding 中添加"如果子代理调度不可用，内联执行相同的检查" | `skills/auditing/SKILL.md`、`skills/optimizing/SKILL.md`、`skills/scaffolding/SKILL.md` |

### 优先级 2 — 应当修复（质量问题）

| # | 问题 | 建议 | 文件 |
|---|------|------|------|
| 4 | session-start 在引导读取失败时退出码为 0 | 在 cat 命令后添加 `\|\| exit 1` | `hooks/session-start` |
| 5 | Token 预算重复 | 提取到共享参考文件，从 authoring 和 optimizing 交叉引用 | 新增：`skills/authoring/references/token-budgets.md` |
| 6 | 描述反模式重复 | 合并到 authoring 中，从 optimizing 交叉引用 | `skills/authoring/SKILL.md`、`skills/optimizing/SKILL.md` |
| 7 | Porting 技能缺失平台移除 | 添加场景 B：平台弃用/移除指导 | `skills/porting/SKILL.md` |
| 8 | `bundles-scan` 命令冗余 | 考虑移除 — `bundles-audit` 已包含安全扫描 | `commands/bundles-scan.md` |
| 9 | Codex 无引导设计未记录 | 在 platform-adapters.md 中记录 Codex 有意不使用路由表 | `skills/porting/references/platform-adapters.md` |

### 优先级 3 — 锦上添花（打磨）

| # | 问题 | 建议 | 文件 |
|---|------|------|------|
| 10 | bump_version.py 缺少预演和回滚 | 添加 `--dry-run` 标志和写入前备份 | `scripts/bump_version.py` |
| 11 | 空 skills 目录返回 exit 0 | 添加信息级别警告 | `scripts/lint_skills.py` |
| 12 | Inspector/Auditor 结构验证重叠 | 考虑让 Inspector 委托给 Auditor 或共享验证模块 | `agents/inspector.md`、`agents/auditor.md` |
| 13 | MUST/ALWAYS 用法与 authoring 指导的张力 | 在 authoring 中添加注释，说明绝对指令适用于安全边界 | `skills/authoring/SKILL.md` |
| 14 | test_scripts.py 缺少边界/错误测试 | 添加否定测试：格式错误的 YAML、断裂交叉引用、漂移场景 | `tests/test_scripts.py` |
| 15 | Cursor 不会在上下文清除时重新注入 | 记录此限制或探索替代的引导持久化方案 | `skills/porting/references/platform-adapters.md` |

---

## 附录：文件清单

### 技能（共 8 个，SKILL.md 1,648 行 + 参考文件 1,131 行）

| 技能 | SKILL.md 行数 | 参考文件行数 | 合计 |
|------|--------------|-------------|------|
| blueprinting | 302 | 0 | 302 |
| optimizing | 283 | 0 | 283 |
| auditing | 245 | 449 | 694 |
| releasing | 228 | 0 | 228 |
| authoring | 220 | 0 | 220 |
| scaffolding | 158 | 507 | 665 |
| using-bundles-forge | 112 | 30 | 142 |
| porting | 100 | 145 | 245 |

### 脚本（共 5 个，1,216 行）

| 脚本 | 行数 |
|------|------|
| audit_project.py | 335 |
| scan_security.py | 322 |
| bump_version.py | 265 |
| lint_skills.py | 264 |
| _cli.py | 30 |

### 测试（共 5 个）

| 测试 | 类型 | 状态 |
|------|------|------|
| test-bootstrap-injection.sh | Shell | 1 项失败 |
| test-skill-discovery.sh | Shell | 通过 |
| test-version-sync.sh | Shell | 失败（Windows） |
| test_scripts.py | Python | 通过 |
| run-all.sh | 编排器 | 3/4 失败 |
