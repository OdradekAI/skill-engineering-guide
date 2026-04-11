# 发布指南

[English](releasing-guide.md)

使用 Bundles Forge 发布 bundle-plugin 的完整指南。涵盖从预检到发布的全流程，包括文档一致性验证和变更一致性审查。

## 概述

发布流水线是质量关卡 — 不是走过场。它确保每个版本内部一致、文档完善、无已知缺陷。用户应在启动发布流程前完成所有 agent、skill 和工作流（插件）的开发。

| 阶段 | 步骤 | 工具 | 阻塞？ |
|------|------|------|--------|
| 前置条件 | 干净 git 状态、分支检查、标签检查 | `git status`、`git tag -l` | 是（脏工作区阻塞） |
| 预检 | 版本漂移、完整审计、文档一致性 | `bump_version.py`、`audit_project.py`、`check_docs.py` | 是（严重发现阻塞） |
| 处理发现 | 审查并修复 critical/warning 问题 | 手动 + `bundles-forge:optimizing` | 是（critical 必须解决） |
| 文档同步 | 变更一致性审查、文档更新 | AI 审查 + `check_docs.py` | 是（矛盾阻塞） |
| 版本升级 | 更新所有清单 | `bump_version.py` | — |
| 文档更新 | CHANGELOG、README | 手动 | — |
| 最终验证 | 重新运行所有检查 | `bump_version.py`、`check_docs.py` | 是（必须通过） |
| 发布 | 提交、打标签、推送、平台发布 | `git`、`gh`、平台 CLI | — |

---

## 开始之前

### 开发必须完成

发布技能是开发生命周期的**最后一步**。调用前请确保：

- 所有技能内容已编写并审查（`bundles-forge:authoring`）
- 质量问题已解决（`bundles-forge:auditing` → `bundles-forge:optimizing`）
- 平台适配器已就位（`bundles-forge:porting`）
- 所有更改已提交 — `git status` 显示干净的工作区

### 选择版本号

| 变更类型 | 版本升级 | 示例 |
|---------|---------|------|
| 技能行为或结构的破坏性变更 | **Major**（X.0.0） | 重命名技能、更改工作流链路、移除技能 |
| 新技能、新平台支持、重大改进 | **Minor**（0.X.0） | 添加技能、添加 Gemini 支持、新 agent |
| Bug 修复、描述改进、文档更新 | **Patch**（0.0.X） | 修复描述、更新 README、修正错别字 |

---

## 流水线逐步说明

### 步骤 0：前置条件

```bash
# 工作区必须干净
git status

# 验证目标标签不存在
git tag -l v1.6.0

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
python scripts/bump_version.py --check

# 完整质量 + 安全审计
python scripts/audit_project.py .

# 文档一致性（7 项检查）
python scripts/check_docs.py .
```

**`check_docs.py` 检查项（D1–D7）：**

| 检查 | 验证内容 |
|------|---------|
| D1 — 技能列表同步 | `skills/` 目录与 CLAUDE.md、AGENTS.md、README.md、README.zh.md 一致 |
| D2 — 交叉引用有效性 | 所有 `bundles-forge:<name>` 引用指向已存在的 `skills/<name>/` |
| D3 — 平台清单同步 | CLAUDE.md 平台清单表与 `.version-bump.json` 一致 |
| D4 — 脚本准确性 | CLAUDE.md 引用的脚本存在于 `scripts/` |
| D5 — Agent 列表同步 | CLAUDE.md 中的 agent 与 `agents/` 目录一致 |
| D6 — README 数据同步 | README.md 和 README.zh.md 之间的硬数据一致 |
| D7 — Guide 语言同步 | `docs/` 中英文 guide 对的硬数据一致 |

### 步骤 2：处理发现

步骤 1 的所有发现按严重级别分组：

| 严重级别 | 操作 | 示例 |
|---------|------|------|
| **Critical** | 必须在发布前修复 | 断裂的交叉引用、安全漏洞、缺失的技能 |
| **Warning** | 建议修复，用户决定 | 文档漂移、缺失的表格条目 |
| **Info** | 记录待后续处理 | 未文档化的脚本、轻微不一致 |

如需质量修复，调用 `bundles-forge:optimizing`。

### 步骤 3：文档同步

此步骤结合自动化检查和 AI 判断。

**3a. 变更一致性审查**

审查从上次发布到 HEAD 的差异：

```bash
# 变更文件摘要
git diff $(git describe --tags --abbrev=0)..HEAD --stat

# 完整差异供审查
git diff $(git describe --tags --abbrev=0)..HEAD
```

关注：

| 问题 | 示例 | 严重级别 |
|------|------|---------|
| 矛盾 | 一个文件说"支持 5 个平台"，另一个说"支持 4 个平台" | Critical |
| 冗余 | 两个 SKILL.md 中重复的段落 | Warning |
| 过度工程 | 对简单功能的复杂抽象 | Warning |
| 遗漏注册 | 新技能未添加到引导路由、README、AGENTS.md | Critical |
| 过期引用 | 重命名后仍使用旧技能名称 | Critical |

**3b. 文档更新**

解决一致性问题后，同步所有项目文档：

1. **`docs/`** — 修复技能、脚本、架构的过时引用
2. **`CLAUDE.md`** — 更新技能数量、生命周期流程、命令、agent、清单
3. **`AGENTS.md`** — 更新可用技能表
4. **`README.md` + `README.zh.md`** — 更新技能表、Agent 表、命令表、代码块

更改后重新运行 `check_docs.py` 确认一致性。

### 步骤 4：版本升级

```bash
python scripts/bump_version.py <new-version>
```

这会更新 `.version-bump.json` 中声明的所有文件，并运行升级后审计以捕获遗漏。

### 步骤 5：文档更新

**CHANGELOG.md** — 使用 [Keep a Changelog](https://keepachangelog.com/) 格式：

```markdown
## [1.6.0] - 2026-04-11

### Added
- New documentation consistency checker (`check_docs.py`)
- Enhanced releasing pipeline with 8-step verification

### Changed
- Releasing skill now requires clean git status before starting

### Fixed
- Cross-reference validation now excludes CHANGELOG.md historical entries
```

**验证清单：**
- [ ] 格式遵循 `## [version] - YYYY-MM-DD`
- [ ] 版本号与升级后的版本一致
- [ ] 日期为今天
- [ ] 无重复版本条目
- [ ] 类别有效（Added、Changed、Deprecated、Removed、Fixed、Security）

### 步骤 6：最终验证

```bash
python scripts/bump_version.py --check   # 无版本漂移
python scripts/bump_version.py --audit   # 无游离版本字符串
python scripts/check_docs.py .           # 文档一致
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

## 热修复发布

对于计划发布之间的紧急修复：

1. 在 `main` 上修复问题（或使用专用热修复分支）
2. 运行精简流水线：
   - `bump_version.py --check`（版本漂移）
   - `scan_security.py .`（仅安全）
   - `check_docs.py .`（文档一致性）
3. 升级补丁版本
4. 更新 CHANGELOG，仅包含 `### Fixed` 部分
5. 发布

热修复跳过完整审计和变更一致性审查 — 速度优先。在下次常规发布时运行完整审计。

---

## 版本基础设施搭建

对于尚未建立版本管理的新项目：

1. 创建 `.version-bump.json`，包含所有版本承载清单的条目
2. 添加 `scripts/bump_version.py`（从脚手架模板或 bundles-forge 复制）
3. 验证：`python scripts/bump_version.py --check`
4. 审计：`python scripts/bump_version.py --audit`

完整项目搭建（含版本基础设施）请参见 `bundles-forge:scaffolding`。

---

## 故障排除

| 问题 | 原因 | 修复 |
|------|------|------|
| `bump_version.py --check` 发现漂移 | 手动编辑或遗漏文件 | 运行 `bump_version.py <correct-version>` 重新同步 |
| `check_docs.py` 报告断裂的交叉引用 | 重命名技能但未更新引用 | 在所有 `.md` 文件中查找替换旧名称 |
| `check_docs.py` 报告技能列表不匹配 | 添加新技能但未更新文档 | 将技能添加到 AGENTS.md 表、README 表、CLAUDE.md |
| 标签已存在 | 之前的发布尝试或版本冲突 | 选择不同版本或 `git tag -d` 删除标签 |
| `gh release create` 失败 | `gh` CLI 未安装或未认证 | 通过 `gh auth login` 安装或在 GitHub 网页 UI 手动创建 |
| CHANGELOG 格式错误 | 缺少日期、版本错误、类别无效 | 严格遵循 Keep a Changelog 格式 |
| 从错误分支发布 | 功能分支而非 main | 先合并到 main，或与用户确认分支发布是有意的 |

---

## 快速参考

### 命令

```bash
python scripts/bump_version.py --check     # 检测版本漂移
python scripts/bump_version.py --audit     # 查找未声明的版本字符串
python scripts/bump_version.py <version>   # 升级所有清单
python scripts/check_docs.py .             # 文档一致性检查
python scripts/audit_project.py .          # 完整质量 + 安全审计
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
