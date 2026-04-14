# Bundles Forge 文档

[English](index.md)

> **Canonical source:** 本索引为所有指南提供导航。每个指南的规范来源为其对应的技能定义（`skills/*/SKILL.md`）。

本目录包含使用 Bundles Forge 进行 bundle-plugin 开发各方面的指南。每个指南都有中英文双版本。

## 从哪里开始

| 如果你想... | 从这里开始 |
|------------|-----------|
| 理解核心概念 | [概念指南](concepts-guide.zh.md) |
| 从零构建新 bundle-plugin | [蓝图规划指南](blueprinting-guide.zh.md) |
| 审计现有项目 | [审计指南](auditing-guide.zh.md) |
| 改进项目 | [优化指南](optimizing-guide.zh.md) |
| 准备发布 | [发布指南](releasing-guide.zh.md) |

## 完整指南索引

| 指南 | 阶段 | 涵盖内容 |
|------|------|---------|
| [概念指南](concepts-guide.zh.md) | 基础 | 核心术语、架构图、设计决策 |
| [蓝图规划指南](blueprinting-guide.zh.md) | 设计 | 访谈技巧、设计文档格式、拆分模式 |
| [脚手架指南](scaffolding-guide.zh.md) | 生成 | 项目结构、平台适配器、模板系统 |
| [编写指南](authoring-guide.zh.md) | 编写 | SKILL.md 编写模式、渐进式加载、Agent 编写 |
| [审计指南](auditing-guide.zh.md) | 验证 | 10 大类检查清单、报告模板、CI 集成 |
| [优化指南](optimizing-guide.zh.md) | 改进 | 描述调优、token 压缩、工作流重构 |
| [发布指南](releasing-guide.zh.md) | 发布 | 版本管理、CHANGELOG 格式、发布流程 |

## 生命周期流程

```
概念 → 蓝图规划 → 脚手架 → 编写 → 审计 → 优化 → 发布
```

每个指南都是独立的 — 你可以直接跳到所需的阶段。[概念指南](concepts-guide.zh.md)提供其他所有指南共享的基础术语。

## 信源说明

这些指南源自对应的技能定义（`skills/*/SKILL.md`）和代理文件（`agents/*.md`）。当存在冲突时，技能文件是唯一信源 — 详见 `skills/auditing/references/source-of-truth-policy.md`。
