# 审计指南

[English](auditing-guide.md)

使用 Bundles Forge 审计 bundle-plugin 的完整指南。涵盖全部四种审计范围、配套工具和推荐工作流。

## 概述

Bundles Forge 提供四种审计范围，各自针对不同粒度：

| 范围 | 适用场景 | 检查类别 | 脚本 |
|------|---------|---------|------|
| **完整项目** | 发布前、重大变更后、初次审查 | 10 大类、60+ 项检查 | `audit_project.py` |
| **单个技能** | 审查单个技能、评估第三方技能 | 4 类（结构、质量、交叉引用、安全） | `audit_skill.py` |
| **工作流** | 添加/移除技能后、链路集成检查 | 3 层（静态、语义、行为）、W1-W12 | `audit_workflow.py` |
| **仅安全扫描** | 快速安全检查、安装前检查 | 5 大攻击面 | `scan_security.py` |

所有范围共享相同的评分公式、严重级别和报告规范。Agent 根据目标路径自动检测范围 — 你也可以直接调用脚本。

> **权威来源：** 执行细节（评分公式、报告格式、定性评估标准）定义在 `agents/auditor.md` — 审计协议的唯一事实来源。本指南仅作摘要参考。

---

## 通用概念

### 严重级别

| 级别 | 含义 |
|------|------|
| **Critical** | 技能/项目无法正常工作，或包含活跃的安全威胁 |
| **Warning** | 可以工作但存在质量问题或需要审查的可疑模式 |
| **Info** | 改进机会 |

### 评分公式

每个类别评分 0-10：

```
baseline = max(0, 10 - (critical_count × 3 + warning_count × 1))
```

审计 agent 可在基线上 **±2 分** 微调并附理由。总分 = 各类别加权平均。

### Go/No-Go 判定

| 条件 | 建议 |
|------|------|
| 存在任何 Critical 发现 | **NO-GO** |
| 仅有 Warning | **CONDITIONAL GO** |
| 全部检查通过 | **GO** |

### 报告位置

所有审计报告保存至 `.bundles-forge/`，使用带时间戳的文件名：
- 完整审计：`<project>-v<version>-audit.YYYY-MM-DD[.<lang>].md`
- 技能审计：`<skill-name>-v<version>-skill-audit.YYYY-MM-DD[.<lang>].md`
- 工作流审计：`<project>-v<version>-workflow-audit.YYYY-MM-DD[.<lang>].md`
- 安全扫描：`<project>-v<version>-security-scan.YYYY-MM-DD[.<lang>].md`

### 退出码（所有脚本）

| 代码 | 含义 |
|------|------|
| `0` | 通过 — 无问题 |
| `1` | 发现警告 |
| `2` | 发现严重问题 |

所有脚本支持 `--json` 获取机器可读输出。

---

## 完整项目审计

**适用场景：** 发布前质量关卡、重大变更后审查、安装前评估第三方 bundle-plugin。

### 通过 Agent

```
/bundles-audit
```

Agent 检测项目根目录（包含 `skills/` + `package.json`）并运行全部 10 个类别。如果子代理可用，会派遣 `auditor` agent 进行自动化评估。

### 通过脚本

```bash
python scripts/audit_project.py <project-root>        # markdown 报告
python scripts/audit_project.py --json <project-root>  # JSON 输出
```

`audit_project.py` 编排三个子脚本：
- `lint_skills.py` — 技能质量 lint（Q1-Q17、S9、X1-X3、G1-G5）
- `scan_security.py` — 安全模式扫描（5 大攻击面）
- `audit_workflow.py` — 工作流集成分析（W1-W12）

然后添加自身的结构、清单、版本同步、钩子、测试和文档检查。

### 10 大类别

| # | 类别 | 权重 | 关键检查 |
|---|------|------|---------|
| 1 | 结构 | 高 (3) | `skills/` 存在、目录布局、引导技能 |
| 2 | 平台清单 | 中 (2) | 清单 JSON 合法、路径可解析 |
| 3 | 版本同步 | 高 (3) | `.version-bump.json` 完整性、无漂移 |
| 4 | 技能质量 | 中 (2) | Frontmatter、描述、token 预算（Q1-Q17） |
| 5 | 交叉引用 | 中 (2) | `project:skill` 解析、相对路径（X1-X3） |
| 6 | 工作流 | 高 (3) | 图拓扑、集成对称性、制品（W1-W12） |
| 7 | 钩子 | 中 (2) | 引导注入、平台检测 |
| 8 | 测试 | 中 (2) | 测试目录、提示词、A/B 评估结果 |
| 9 | 文档 | 低 (1) | README、安装文档、CHANGELOG |
| 10 | 安全 | 高 (3) | 5 大攻击面 — 技能内容、钩子、插件、Agent、脚本 |

总权重 = 23。总分 = `sum(score_i × weight_i) / 23`。

### 报告模板

完整项目审计使用 `skills/auditing/references/report-template.md` — 六层结构：决策摘要 → 风险矩阵 → 按类别分组的发现 → 方法论 → 附录。

### 检查清单

- **项目检查清单：** `skills/auditing/references/audit-checklist.md`（类别 1-5、7-10）
- **工作流检查清单：** `skills/auditing/references/workflow-checklist.md`（类别 6：W1-W12）
- **安全检查清单：** `skills/auditing/references/security-checklist.md`（类别 10 详细）

---

## 单个技能审计

**适用场景：** 集成前审查单个技能、评估第三方技能安全性、编写中的技能快速质量检查。

### 通过 Agent

```
/bundles-audit skills/authoring
```

Agent 检测到单个技能目录（包含 `SKILL.md`、无 `skills/` 子目录）并运行 4 个适用类别。

### 通过脚本

```bash
python scripts/audit_skill.py <skill-directory>           # markdown 报告
python scripts/audit_skill.py <skill-directory>/SKILL.md   # 同样有效
python scripts/audit_skill.py --json <skill-directory>     # JSON 输出
```

`audit_skill.py` 编排：
- `lint_skills.lint_skill()` — 质量、结构和交叉引用检查
- `scan_security` — 限定在技能目录的安全扫描

也可以单独运行子脚本：

```bash
python scripts/lint_skills.py <skill-directory>     # 质量 + 交叉引用
python scripts/scan_security.py <skill-directory>   # 安全扫描
```

### 4 大类别

| # | 类别 | 权重 | 关键检查 |
|---|------|------|---------|
| 1 | 结构 | 高 (3) | S2、S3、S9 — 独立目录、SKILL.md 存在、名称匹配 |
| 2 | 技能质量 | 中 (2) | Q1-Q17 — frontmatter、描述、token、各节内容 |
| 3 | 交叉引用 | 中 (2) | X1-X3 — `project:skill` 解析、相对路径 |
| 4 | 安全 | 高 (3) | SEC1、SEC5、SEC8-SEC10 — 敏感文件、覆盖、编码 |

总权重 = 10。技能范围不适用的类别：平台清单、版本同步、钩子、测试、文档。

### 第三方技能扫描

评估外部来源的技能时：

1. **下载但不执行** — 克隆/下载但不运行钩子或脚本
2. **运行技能审计** — `python scripts/audit_skill.py <downloaded-skill-dir>`
3. **与用户审查严重发现** 后再安装
4. **绝不自动安装** 存在未解决严重安全发现的技能

### 报告模板

单个技能审计使用 `skills/auditing/references/skill-report-template.md` — 三层结构：决策摘要 → 按类别分组的发现 → 技能概况。包含两套决策词汇：
- **自检：** PASS / PASS WITH NOTES / FAIL
- **第三方评估：** SAFE TO INSTALL / REVIEW REQUIRED / DO NOT INSTALL

### 检查清单

- **技能检查清单：** `skills/auditing/references/skill-checklist.md`

---

## 工作流审计

**适用场景：** 在工作流链中添加/移除技能后、修改 Integration 部分或 Inputs/Outputs 后、验证第三方技能集成、或完整审计的工作流类别出现警告时。

### 通过 Agent

显式请求：
- "审计工作流"
- "检查工作流集成"
- "以 skill-a 为焦点运行工作流审计"

或者当完整审计的工作流类别出现发现时，Agent 会建议运行。

### 通过脚本

```bash
python scripts/audit_workflow.py <project-root>                          # 完整工作流审计
python scripts/audit_workflow.py --focus-skills skill-a,skill-b <root>   # 聚焦模式
python scripts/audit_workflow.py --json <project-root>                   # JSON 输出
```

### 3 层检查（W1-W12）

| 层 | 权重 | 检查项 | 自动化 |
|----|------|--------|--------|
| 静态结构 | 高 (3) | W1-W5：环路、可达性、Inputs/Outputs 存在性、制品 ID 匹配 | `lint_skills.py` 图分析 |
| 语义接口 | 中 (2) | W6-W10：Integration 完整性、制品清晰度、Calls/Called by 对称性 | `audit_workflow.py` + agent 审查 |
| 行为验证 | 低 (1) | W11-W12：链路 A/B 评估、上下文中的触发/退出 | `evaluator` agent 派遣 |

总权重 = 6。跳过行为层时评分为 10（满分）；报告中会注明跳过。

### 聚焦模式（增量审计）

指定 `--focus-skills skill-a,skill-b` 时：

1. **所有检查在完整图上运行** — 不跳过任何分析
2. **发现按区域划分** 为焦点区域（涉及指定技能）和上下文（其他全部）
3. **报告突出** 焦点技能，同时保留完整图的可见性

这使得添加新技能后可以进行增量验证，而不遗漏级联影响。

**添加第三方技能的典型工作流：**

```
1. 运行 blueprinting 场景 D（集成规划）
2. 将技能添加到项目
3. 运行：python scripts/audit_workflow.py --focus-skills new-skill-a,new-skill-b .
4. 修复焦点区域发现
5. 审查上下文发现以排除意外影响
```

### 报告模板

工作流审计使用 `skills/auditing/references/workflow-report-template.md` — 三层结构：决策摘要 → 按层分组的发现 → 技能集成图。

### 检查清单

- **工作流检查清单：** `skills/auditing/references/workflow-checklist.md`

---

## 仅安全扫描

**适用场景：** 安装第三方 bundle-plugin 前的快速安全检查、提交前验证、或只关心安全风险时。

### 通过 Agent

```
/bundles-scan
```

映射到 `bundles-forge:auditing` 技能的安全专用模式 — 仅运行类别 10（安全），覆盖全部 5 大攻击面。

### 通过脚本

```bash
python scripts/scan_security.py <project-root>           # 项目级扫描
python scripts/scan_security.py <skill-directory>         # 单技能扫描
python scripts/scan_security.py --json <project-root>     # JSON 输出
```

### 5 大攻击面

| 攻击面 | 风险等级 | 示例 |
|--------|---------|------|
| SKILL.md 内容 | 高 | 敏感文件访问、破坏性命令、安全覆盖、编码欺骗 |
| Hook 脚本 | 高 | 网络调用、环境变量泄露、系统配置修改 |
| OpenCode 插件 | 高 | 动态代码执行、网络访问、消息操纵 |
| Agent 提示词 | 中 | 权限提升、范围扩展、安全覆盖 |
| 打包脚本 | 中 | 网络调用、系统修改、未消毒的输入 |

### 检查清单

- **安全检查清单：** `skills/auditing/references/security-checklist.md` — 全部 5 个攻击面的完整模式列表

---

## 审计之后

| 报告来源 | 发现级别 | 操作 |
|---------|---------|------|
| 完整项目（`audit-report`） | Critical/Warning | `bundles-forge:optimizing` — 项目优化（全部 6 项目标） |
| 单个技能（`skill-report`） | Critical/Warning | `bundles-forge:optimizing` — 技能优化（4 项目标 + 反馈） |
| 工作流（`workflow-report`） | W1-W12 发现 | `bundles-forge:optimizing` 目标 4（工作流链路完整性） |
| 任意范围 | Info | 记录待后续考虑 |
| 任意范围 | 全部通过 | `bundles-forge:releasing` 进入发布前流水线 |

**重审规则：** 修复 critical/warning 问题后，运行一次重审验证。不要循环超过一次 — 如果重审仍有问题，交给用户手动决定。

---

## CI 集成

### 脚本组合

```bash
# 完整流水线：lint → 安全 → 完整审计
python scripts/lint_skills.py --json . > lint.json
python scripts/scan_security.py --json . > security.json
python scripts/audit_project.py --json . > audit.json

# CI 中的单技能审计
python scripts/audit_skill.py --json skills/my-skill > skill-audit.json

# PR 修改技能后的工作流检查
python scripts/audit_workflow.py --json --focus-skills changed-skill . > workflow.json
```

### 退出码用法

```bash
python scripts/audit_project.py . || echo "Audit found issues (exit $?)"

# 仅在 critical 时使 CI 失败
python scripts/audit_project.py . ; [ $? -ne 2 ] || exit 1
```

### JSON 输出

所有脚本支持 `--json`。JSON 输出包含：
- `status` — PASS / WARN / FAIL
- `overall_score` — 加权平均（0-10）
- `summary` — `{critical: N, warning: N}`
- `categories` / `layers` — 各类别/层的分解，含发现和评分
