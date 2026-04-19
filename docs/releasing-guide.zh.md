# 发布指南

[English](releasing-guide.md)

使用 Bundles Forge 发布 bundle-plugin 的完整指南。涵盖从预检到发布的全流程，包括文档一致性验证和变更一致性审查。

## 概述

发布流水线是质量关卡 — 不是走过场。它确保每个版本内部一致、文档完善、无已知缺陷。用户应在启动发布流程前完成所有 agent、skill 和工作流（插件）的开发。

> **权威信源：** 完整执行协议（前置条件、预检、版本升级、发布步骤）定义在 `skills/releasing/SKILL.md` 中。本指南帮助你理解*发布流水线*和*每个阶段的预期*——执行由 skill 自身处理。

| 阶段 | 步骤 | 工具 | 阻塞？ |
|------|------|------|--------|
| 前置条件 | 干净 git 状态、分支检查、标签检查 | `git status`、`git tag -l` | 是（脏工作区阻塞） |
| 预检 | 版本漂移、完整审计、文档一致性 | `bundles-forge bump-version`、`bundles-forge audit-plugin`、`bundles-forge audit-docs` | 是（严重发现阻塞） |
| 处理发现 | 审查并修复 critical/warning 问题 | 手动 + `bundles-forge:optimizing` | 是（critical 必须解决） |
| 变更审查与文档同步 | 变更一致性审查、文档更新 | AI 审查 + `bundles-forge audit-docs` | 是（矛盾阻塞） |
| 版本升级 | 更新所有清单 | `bundles-forge bump-version` | — |
| 发布说明 | CHANGELOG、README | 手动 | — |
| 最终验证 | 重新运行所有检查 | `bundles-forge bump-version`、`bundles-forge audit-docs` | 是（必须通过） |
| 发布 | 提交、打标签、推送、平台发布 | `git`、`gh`、平台 CLI | — |

---

## 开始之前

### 开发必须完成

**发布（releasing）** 技能在 hub-and-spoke 架构中是**发布流水线编排器**：它编排诊断、修复、版本升级与发布。它不能替代前期的设计与实现。调用前请确保：

- 所有技能内容已编写并审查（`bundles-forge:authoring`）
- 质量问题正在得到解决。**发布**编排 **`bundles-forge:auditing`** 做诊断，并引导你使用 **`bundles-forge:optimizing`**（及按需的 authoring）做修复 — **审计不会自动跳转到优化**；由发布流水线（或你）决定该顺序。
- 平台适配器已就位（`bundles-forge:scaffolding`）
- 所有更改已提交 — `git status` 显示干净的工作区

### 选择版本号

| 变更类型 | 版本升级 | 示例 |
|---------|---------|------|
| 技能行为或结构的破坏性变更 | **Major**（X.0.0） | 重命名技能、更改工作流链路、移除技能 |
| 新技能、新平台支持、重大改进 | **Minor**（0.X.0） | 添加技能、添加 Gemini 支持、新 agent |
| Bug 修复、描述改进、文档更新 | **Patch**（0.0.X） | 修复描述、更新 README、修正错别字 |
| 稳定前测试大版本 | **Pre-release**（X.Y.Z-beta.N） | `2.0.0-beta.1`、`2.0.0-rc.1` |

Bump 脚本接受任何合法的 semver 字符串 — pre-release 版本与稳定版本在所有清单中的处理方式相同。

---

## 流水线逐步说明

### 步骤 0：前置条件

```bash
# 工作区必须干净
git status

# 验证目标标签不存在
git tag -l v<version>

# 检查当前分支
git branch --show-current
```

| 检查 | 要求 | 失败时 |
|------|------|--------|
| 工作区干净 | 硬性 — 流水线阻塞 | 提交或 stash 所有更改 |
| 目标标签空闲 | 软性 — 警告 | 选择不同的版本号 |
| 在 main 分支 | 软性 — 警告 | 与用户确认后再继续 |

### 步骤 1：预检

在继续之前运行所有自动化检查：

```bash
# 版本漂移检测
bundles-forge bump-version <target-dir> --check

# 文档一致性（9 项检查）
bundles-forge audit-docs <target-dir>
```

**插件验证（仅 Claude Code）：** 在 Claude Code 环境中，运行 `claude plugin validate`（或会话内 `/plugin validate`）以验证 `plugin.json` schema、skill/agent/command frontmatter 和 `hooks.json` 有效性。其他平台通过 inspector agent 覆盖等效的结构检查。

**完整审计：** 调用 `bundles-forge:auditing`（首选 — 通过 auditor 子代理提供 10 类定性评估与评分）。回退：`bundles-forge audit-plugin .`（仅自动化检查，无定性评分）。

**`bundles-forge audit-docs` 检查项（D1–D9）：**

| 检查 | 验证内容 |
|------|---------|
| D1 — 技能列表同步 | `skills/` 目录与 CLAUDE.md、AGENTS.md、README.md、README.zh.md 一致 |
| D2 — 交叉引用有效性 | 所有 `bundles-forge:<name>` 引用指向已存在的 `skills/<name>/` |
| D3 — 平台清单同步 | CLAUDE.md 平台清单表与 `.version-bump.json` 一致 |
| D4 — 脚本准确性 | CLAUDE.md 引用的技能脚本存在于其声明的 `skills/.../scripts/` 路径 |
| D5 — Agent 列表同步 | CLAUDE.md 中的 agent 与 `agents/` 目录一致 |
| D6 — README 数据同步 | README.md 和 README.zh.md 之间的硬数据一致 |
| D7 — Guide 语言同步 | `docs/` 中英文 guide 对的硬数据一致 |
| D8 — 权威信源声明 | 每个 `docs/*.md` guide 必须有 `> **Canonical source:**` 声明指向已存在的 skill 或 agent 文件 |
| D9 — 数字交叉验证 | `docs/*.md` guide 中的关键数字与其权威信源一致（如攻击面数量、类别数量） |

### 步骤 2：处理发现

步骤 1 的所有发现按严重级别分组：

| 严重级别 | 操作 | 示例 |
|---------|------|------|
| **Critical** | 必须在发布前修复 | 断裂的交叉引用、安全漏洞、缺失的技能 |
| **Warning** | 建议修复，用户决定 | 文档漂移、缺失的表格条目 |
| **Info** | 记录待后续处理 | 未文档化的脚本、轻微不一致 |

**安全扫描 confidence 层：** 安全发现分为 `deterministic`（在可执行代码中匹配 — hooks、plugins、scripts）和 `suspicious`（在自然语言内容中匹配 — SKILL.md、references、agent prompts）。Suspicious 发现显示在审计报告的独立 "Needs review" 区域，不计入评分和退出码。仅 deterministic 发现会阻塞发布。

如需质量修复，在本流水线中调用 `bundles-forge:optimizing`。审计只呈现发现，不会自动交给优化 — 由**发布**（或你）编排该步骤。

### 步骤 3：变更审查与文档同步

此步骤结合自动化检查和 AI 判断。

**变更一致性审查：**

审查从上次发布到 HEAD 的差异：

```bash
# 变更文件摘要
git diff $(git describe --tags --abbrev=0)..HEAD --stat

# 完整差异供审查
git diff $(git describe --tags --abbrev=0)..HEAD
```

如果没有历史标签，使用 `git log --oneline` 确定变更范围。

关注：

| 问题 | 示例 | 严重级别 |
|------|------|---------|
| 矛盾 | 一个文件说"支持 5 个平台"，另一个说"支持 4 个平台" | Critical |
| 冗余 | 两个 SKILL.md 中重复的段落 | Warning |
| 过度工程 | 对简单功能的复杂抽象 | Warning |
| 遗漏注册 | 新技能未添加到引导路由、README、AGENTS.md | Critical |
| 过期引用 | 重命名后仍使用旧技能名称 | Critical |

**文档更新：**

解决一致性问题后，同步所有项目文档：

1. **`docs/`** — 修复技能、脚本、架构的过时引用
2. **`CLAUDE.md`** — 更新技能数量、生命周期流程、命令、agent、清单
3. **`AGENTS.md`** — 更新可用技能表
4. **`README.md` + `README.zh.md`** — 更新技能表、Agent 表、命令表、代码块

更改后重新运行 `bundles-forge audit-docs` 确认一致性。

### 步骤 4：版本升级

```bash
bundles-forge bump-version <target-dir> <new-version>
```

这会更新 `.version-bump.json` 中声明的所有文件，并运行升级后审计以捕获遗漏。

### 步骤 5：发布说明

**CHANGELOG.md** — 使用 [Keep a Changelog](https://keepachangelog.com/) 格式：

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New skill: `bundles-forge:authoring` for skill authoring guidance

### Changed
- Improved descriptions for better triggering accuracy

### Fixed
- Version drift in Cursor manifest
```

**验证清单：**
- [ ] 格式遵循 `## [version] - YYYY-MM-DD`
- [ ] 版本号与升级后的版本一致
- [ ] 日期为今天
- [ ] 无重复版本条目
- [ ] 类别有效（Added、Changed、Deprecated、Removed、Fixed、Security）

### 步骤 6：最终验证

```bash
bundles-forge bump-version <target-dir> --check   # 无版本漂移
bundles-forge bump-version <target-dir> --audit   # 无游离版本字符串
bundles-forge audit-docs <target-dir>             # 文档一致
```

三者必须全部以退出码 0（干净）退出后才能发布。

### 步骤 7：发布

**Git + GitHub Release：**

```bash
git add -A
git commit -m "release: v<version>"
git tag v<version>
git push origin main --tags
```

**GitHub Release（推荐）：**

```bash
gh release create v<version> --title "v<version>" --notes-file CHANGELOG-EXCERPT.md
```

从 CHANGELOG.md 中提取当前版本的内容生成 `CHANGELOG-EXCERPT.md`。发布创建后删除该文件。

**平台特定：**

| 平台 | 发布方式 |
|------|---------|
| Claude Code | `claude plugin publish` |
| Cursor | 通过 Cursor 插件市场提交 |
| Codex | GitHub Release（用户从 git 拉取） |
| OpenCode | GitHub Release（用户从 git 拉取） |
| Gemini CLI | GitHub Release（用户从 git URL 安装） |

---

## 分发策略

根据目标受众选择用户安装插件的方式：

| 策略 | 适用场景 | 方式 |
|------|---------|------|
| Marketplace（Claude Code） | 公开分发，覆盖面最广 | `claude plugin publish` — 用户通过 `claude plugin install` 安装 |
| Project scope | 通过 git 共享的团队工具 | 使用 `--scope project` 安装 — 配置提交到 `.claude/settings.json` |
| Local scope | 个人项目专用插件 | 使用 `--scope local` 安装 — 被 gitignore，仅限开发者本地 |
| Git-based（Codex、OpenCode、Gemini） | 无 marketplace 的平台 | 用户 clone 仓库并按平台文档安装 |
| Development mode | 发布前迭代 | `claude --plugin-dir .` — 加载当前目录，无缓存 |

Marketplace 分发需确保 `.claude-plugin/marketplace.json` 存在且包含插件元数据（包括在 `.version-bump.json` 中跟踪的 `plugins.0.version` 条目）。开发迭代时使用 `--plugin-dir .` 绕过缓存 — 更改立即生效，无需升级版本号。

---

## 热修复发布

对于计划发布之间的紧急修复：

1. 在 `main` 上修复问题（或使用专用热修复分支）
2. 运行精简流水线：
   - `bundles-forge bump-version --check`（版本漂移）
   - `bundles-forge audit-security .`（仅安全）
   - `bundles-forge audit-docs .`（文档一致性）
3. 升级补丁版本
4. 更新 CHANGELOG，仅包含 `### Fixed` 部分
5. 发布

热修复跳过完整审计和变更一致性审查 — 速度优先。在下次常规发布时运行完整审计。

---

## 版本基础设施搭建

对于尚未建立版本管理的新项目：

1. 创建 `.version-bump.json`，包含所有版本承载清单的条目
2. 验证：`bundles-forge bump-version --check`
3. 审计：`bundles-forge bump-version --audit`

完整项目搭建（含版本基础设施）请参见 `bundles-forge:scaffolding`。

---

## 故障排除

| 问题 | 原因 | 修复 |
|------|------|------|
| `bundles-forge bump-version --check` 发现漂移 | 手动编辑或遗漏文件 | 运行 `bundles-forge bump-version [target-dir] <correct-version>` 重新同步 |
| `bundles-forge audit-docs` 报告断裂的交叉引用 | 重命名技能但未更新引用 | 在所有 `.md` 文件中查找替换旧名称 |
| `bundles-forge audit-docs` 报告技能列表不匹配 | 添加新技能但未更新文档 | 将技能添加到 AGENTS.md 表、README 表、CLAUDE.md |
| 标签已存在 | 之前的发布尝试或版本冲突 | 选择不同版本或 `git tag -d` 删除标签 |
| `gh release create` 失败 | `gh` CLI 未安装或未认证 | 通过 `gh auth login` 安装或在 GitHub 网页 UI 手动创建 |
| CHANGELOG 格式错误 | 缺少日期、版本错误、类别无效 | 严格遵循 Keep a Changelog 格式 |
| 从错误分支发布 | 功能分支而非 main | 先合并到 main，或与用户确认分支发布是有意的 |
| 未运行审计就发布 | 跳过流水线步骤 — "只是个小改动" | 始终运行完整流水线；漂移往往发生在小改动中 |
| 推送了标签但未创建 GitHub Release | 只执行了 `git push --tags` | 使用 `gh release create` — 标签出现在 `/tags` 但不出现在 `/releases` |
| 修复问题前就升级版本 | 流水线顺序错误 | 先修复再升级 — 避免发布已知有问题的版本 |
| CHANGELOG 未更新 | 跳过了步骤 5 | 用户需要知道发生了什么变更，尤其是破坏性变更 |
| 修复后出现新漂移 | 修复引入了新的不一致 | 在步骤 6 发布前重新运行所有检查 |
| `marketplace.json` 版本过期 | 未在 `.version-bump.json` 中跟踪 | 添加 `plugins.0.version` 字段路径的条目 |
| 手动编辑清单中的版本号 | 直接编辑 JSON 而未使用 CLI | 始终使用 `bundles-forge bump-version` — 它会运行升级后审计 |
| 意外从非 main 分支发布 | 误选了功能分支 | 先合并到 main，或确认分支发布是有意的 |

---

## 快速参考

### 命令

```bash
bundles-forge bump-version [target-dir] --check     # 检测版本漂移
bundles-forge bump-version [target-dir] --audit     # 查找未声明的版本字符串
bundles-forge bump-version [target-dir] <version>   # 升级所有清单
bundles-forge audit-docs <target-dir>               # 文档一致性检查
bundles-forge audit-plugin <target-dir>             # 完整质量 + 安全审计
```

### 退出码

| 代码 | 含义 |
|------|------|
| 0 | 干净 — 未发现问题 |
| 1 | 警告 — 建议审查 |
| 2 | 严重 — 必须在发布前解决 |

### 严重级别

| 级别 | 发布影响 |
|------|---------|
| Critical | **阻塞发布** — 必须修复 |
| Warning | **审查** — 建议修复，用户决定 |
| Info | **记录** — 发布不需要操作 |
