<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg?v=2">
    <img alt="episteme" src="docs/assets/logo-light.svg?v=2" width="456">
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

周二，晚上 11 点。你让代理为 `orders` 表加一个软删除列——`deleted_at TIMESTAMP NULL`。代理生成 migration。测试通过。你 merge。

40 小时后，凌晨 4 点，值班工程师被叫起。发货服务在每次重试时 panic——一个 Rust deserializer 期望对 `shipping_status` 进行穷尽匹配，而 NULL 不在其中。六个月前一位资深工程师改过 CHECK constraint，PR 描述只有一行，理由埋在没人搜过的 Slack 串里。代理没有理由去走 `orders.*` 下游消费者的 call graph。你也没有理由在晚上 11 点想起它。

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

## 零信任执行

[**OWASP Top 10 for Agentic Applications (2026)**](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — 由 100 多位业界专家同行评议 — 将 prompt injection、goal hijacking、overreach、memory poisoning、unbounded action 列为自主代理的主要风险类别。Knowns / Unknowns / Assumptions / Disconfirmation 结构对每一项都是*结构性*反制：

| OWASP Agentic Risk (2026) | episteme 的反制 |
|---|---|
| 直接目标操纵 / prompt injection | 执行前声明 Core Question；偏差以 Unknowns 形式浮现 |
| 间接指令注入 | Knowns / Disconfirmation 将可信状态与 prompt 内容分离；代理在依据检索到的输入行动之前承诺一个可证伪的结果 |
| Overreach / unbounded action | 在 Frame 中声明约束规则；强制 reversible-first 策略 |
| 流畅幻觉 | Unknowns 字段不可为空；行动前必须命名假设 |
| 内存投毒 | Pillar 2 hash-chained protocols — append-only、tamper-evident；对先前状态的静默重写由 `verify_chain` 检测 |
| 无限规划循环 | Disconfirmation 条件必填；证据触发时循环退出 |

未命名的假设不被信任。未声明前提条件 (Knowns) 与约束规则之前不采取任何行动。kernel 是意图与执行之间的验证层。

### 业界收敛 — 2025–2026

同一时间窗内的主要框架与学术论文，正向 kernel 已交付的相同架构模式收敛：文件系统层的 pre-invocation checkpoint ([Capsule Security ClawGuard](https://www.businesswire.com/news/home/20260415670902/), 2026)、hash-chained 防篡改内存 ([SSGM](https://arxiv.org/abs/2603.11768) — Lam et al., 2026)、基于理由而非规则清单的对齐 ([Anthropic Claude Constitution](https://www.anthropic.com/constitution), 2026-01-22)、带治理层的五阶段认知循环 ([SCL R-CCAM](https://arxiv.org/abs/2511.17673) — Kim, 2025)、五支柱 agent integrity ([Proofpoint Agent Integrity Framework 2026](https://www.proofpoint.com/us/resources/white-papers/agent-integrity-framework))。kernel 早于这些出版物 (CP1 于 2026-04-21 交付；v1.0.0 GA 于 2026-04-28)；这种收敛是独立验证，并非血统。完整 attribution map 见 [`kernel/REFERENCES.md`](./kernel/REFERENCES.md) 中 *Convergent contemporary work* 章节。

---

## Cognitive Arms — v1.1+

上述四个 Blueprint 和三个 Pillar — Cognitive Blueprints · Append-Only Hash Chain · Framework Synthesis & Active Guidance — 是 v1.0 *不变的结构基础*。Pillar 不会移动。v1.1 在其之上加入了 **3 Cognitive Arms**：随着时间推移、不断重构 kernel 自身知识的流动型主动引擎。

- **Arm A · Temporal Integrity** — 协议会衰退。经操作员确认的 retire 会 supersede 一条陈旧规则，而不是静默覆盖它。验证窗口：CP-DECAY-03 之后 30 天。
- **Arm B · Causal Synthesis** — 对 deferred-discovery 流进行零-LLM 实体抽取，产生 framework 可以据此行动的聚类提案。验证窗口：60 天。
- **Arm C · Self-Consistency Convergence** — 协议升级为以结构化方式推导 disconfirmation 的模型。验证窗口：90 天。

这个区分承载结构性意义 — Pillar 是已沉淀的术语，Arm 是系统跨越时间审计和打磨自己输出的方式。状态：**v1.1.0-rc1 于 2026-04-29 切出**，Arm A 基础设施已交付（supersede-with-history 基础设施 + 将 operator profile / policy 编辑自动记录到 chain stream 的 hook）；Arm A 衰退验证机制、Arm B、Arm C 已 scope 到 v1.1.0 GA → v1.2。

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
