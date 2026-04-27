<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <img alt="episteme" src="docs/assets/logo-light.svg" width="456">
  </picture>
</h1>

<p align="center">
  <a href="https://github.com/junjslee/episteme/releases"><img alt="Latest Release" src="https://img.shields.io/github/v/release/junjslee/episteme?include_prereleases&label=release&logo=github"></a>
  <a href="https://github.com/junjslee/episteme/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/junjslee/episteme?color=informational"></a>
  <a href="https://github.com/junjslee/episteme"><img alt="Unique Clones" src="https://img.shields.io/badge/dynamic/json?color=success&label=Unique%20Clones&query=uniques&url=https://gist.githubusercontent.com/junjslee/0a171c9a54b11948bbd1562f4f040465/raw/clone.json&logo=github"></a>
</p>

<p align="center">
  <a href="README.md">English</a> &bull;
  <a href="README.ko.md">한국어</a> &bull;
  <a href="README.es.md">Español</a> &bull;
  <a href="README.zh.md"><b>中文</b></a>
</p>

<p align="center"><a href="https://epistemekernel.com"><b>epistemekernel.com</b></a></p>

---

## AI 为什么会如此自信地犯错？

晚上 11 点。你让 AI 编码代理帮你修一个迁移 bug。它给出一个流畅、自信、看似合理的答案——拼接了 Stack Overflow 上的模式和 Postgres 官方文档的语法。**唯一没出现在答案里的**：三个月前你的团队做出的那个决定——"这一列永远不能是 nullable"。代理不知道这件事。你在午夜也没想起来。

第二天早上，生产数据库里 40 万行数据带着 `NULL`。

这不是代理的**失误**。这是代理**在结构上做不到的事**。自回归语言模型是**模式匹配引擎，不是因果世界模型**。*"这个答案是否契合这个具体的上下文？"* 是一个因果推理判断，不是 token 频率匹配。模型做不到，于是退而求其次：选择**统计平均值**——流畅、自信、不契合任何具体上下文的答案。

`episteme` 的存在就是为了填补这个结构性空缺。

---

## 为什么 prompt 解决不了

- 系统提示里的提醒**只活一次调用**。下一次会话里它就不存在了。
- `CLAUDE.md` 里写的规则**一到 deadline 就会被忽视**——人类如此，代理也如此。
- **Know-how**——*"在这种形状的问题里，这样做"* 这种不可还原地依赖上下文的规则——无法靠更好的措辞来教。它必须被**提取、存储、再次显现**。

更深的问题是：代理**即便在用户自己的请求是错的时候，也照样执行**。用户也可能缺乏深度、产生误解、从错误的前提出发。好的系统*不止监督代理，还要验证用户的提问本身*。Prompt 层的补丁无法结构化这种双向验证。

---

## 解法——在文件系统层的 Thinking Framework

`episteme` 拦截**意图遇见状态变更的那一刻**。在任何高影响操作（`git push`、`npm publish`、`terraform apply`、DB 迁移、lockfile 编辑）之前——无论这个请求是*谁*发出的（用户本人，还是代理自己）——代理都必须把自己的推理明确地投射到磁盘上的一个四字段 **Reasoning Surface** 里：

| 字段 | 代理必须声明的内容 |
|---|---|
| **Core Question** | 这个动作**真正在回答**的那一个问题（对抗 question substitution）|
| **Knowns** | 已核实的事实、引用、测量值——不是听起来合理的猜测 |
| **Unknowns** | 已命名、可分类的缺口——不是含糊的 *"可能有风险"* |
| **Assumptions** | 承重的信念，标注出来以便被证伪 |
| **Disconfirmation** | 能*证明此计划错了*的可观测事件——在行动前预先承诺 |

有效性**结构化**校验：最小内容长度、禁止懒惰占位符（`none`、`n/a`、`tbd`、`해당 없음`）、规范化命令扫描。如果 surface 缺失或空洞，操作以 `exit 2` 被拒绝。

**这就是 prompt 提醒和编译器的区别：一个在请求，一个在拒绝推进。**

---

## ABCD——四个 Cognitive Blueprints

每个高影响操作会触发四个 Blueprint 之一，每一个都对应一类特定的失败模式：

- **A · Axiomatic Judgment** — 解决可信但相互矛盾的信息源之间的冲突。强制代理说出*为什么*它们有冲突，以及*当前上下文的哪个特征*做出选择。
- **B · Fence Reconstruction** — 保护继承下来的约束。在移除某个约束之前，必须先重建它的*原始目的*。**Chesterton's fence** 被文件系统强制执行。
- **C · Consequence Chain** — 分解不可逆操作（一阶效应、二阶效应、failure-mode 反转、基准率、margin of safety）。
- **D · Architectural Cascade** — 捕捉那些会留下陈旧引用的重构和重命名。在编辑之前，强制代理枚举完整的 blast radius。

每一次 Blueprint 触发、以及它所验证的每一个决定，都会被提交到一条**防篡改的哈希链（tamper-evident hash chain）**。这条链不是日志——它是 kernel 之后提供 **Active Guidance** 的方式：在下一次匹配的决策点，相关的合成 protocol 会在代理退回到训练分布之前，**主动**浮现出来。

结果是**随你的项目不断累积的 Thinking Framework**。每次代理解决一次冲突，它对你的代码库都变得更敏锐——不是因为你训练它，而是因为链替你记住了。

---

## 快速开始

### 方式 A — Claude Code 插件市场

在 Claude Code 里：

```
/plugin marketplace add junjslee/episteme
/plugin install episteme@episteme
```

然后在任意 shell：

```bash
episteme init     # 从模板种子化个人记忆文件
episteme setup    # 对工作风格 + 认知风格进行打分
episteme sync     # 传播到 Claude Code 和 Hermes
episteme doctor   # 验证连接
```

### 方式 B — 直接克隆 kernel

```bash
git clone https://github.com/junjslee/episteme ~/episteme
cd ~/episteme
pip install -e .

episteme init
episteme setup . --write
episteme sync
episteme doctor
```

更深入的 onboarding：**[`docs/SETUP.md`](./docs/SETUP.md)**。完整命令参考：**[`docs/COMMANDS.md`](./docs/COMMANDS.md)**。

---

## 哲学——doxa · episteme · praxis · 결

仓库名来自希腊语：

- **Doxa** (δόξα) — 默认产出的流畅意见。[`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md) 里的 11 个 failure mode 是一个*把 doxa 误认为 episteme* 的分类学。
- **Episteme** (ἐπιστήμη) — 可辩护的知识：具体的 Knowns、被命名的 Unknowns、可证伪的 Disconfirmation。执行的前置条件。
- **Praxis** (πρᾶξις) — 带着授权纪律的行动：效果落地时纪律完好无损。

韩语 **결**（*gyeol*）命名木材或石头的纹理——潜在的模式结构，顺着它切会形成连贯的形态，逆着它切则会断裂。Reasoning Surface 的字段顺序正是认识论纪律的 *gyeol*：**已确立 → 开放 → 暂定 → 证伪条件**。

---

## 下一步阅读

| 主题 | 位置 |
|---|---|
| Kernel 30 行蒸馏 | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md) |
| v1.0 RC 设计方向 | [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md) |
| 11 个 failure mode 及其反制 artifact | [`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md) |
| 同一个 prompt，Thinking Framework *关 vs. 开* | [`demos/03_differential/`](./demos/03_differential/) |
| 何时 kernel 是错的工具 | [`kernel/KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) |
| 每一个借用概念的出处 | [`kernel/REFERENCES.md`](./kernel/REFERENCES.md) |
| 仓库对代理的运营契约 | [`AGENTS.md`](./AGENTS.md) |

---

## 为什么是 `episteme`——一句话

**姿态高于 prompt（Posture over prompt）**。不是寻找更好的措辞，而是在文件系统层面建立 *AI 代理思考的框架*。一个可以像编译器那样*拒绝继续推进*的 Thinking Framework。它不是让你的代理更聪明——而是让这份聪明*落地到你的上下文里*。

**Built as a Sovereign Cognitive Kernel — 생각의 틀**.

---

> **Note on translation.** This README is a focused-scope Chinese adaptation maintained alongside the canonical English [`README.md`](./README.md). For deepest documentation, demo walkthroughs, and architectural diagrams, refer to the English docs tree. Technical terms (Thinking Framework, Reasoning Surface, Blueprint, Core Question, Chesterton's fence, Pillar 3, flaw_classification, etc.) are kept in English because they are load-bearing kernel vocabulary.
