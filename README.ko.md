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
  <a href="README.ko.md"><b>한국어</b></a> &bull;
  <a href="README.es.md">Español</a> &bull;
  <a href="README.zh.md">中文</a>
</p>

<p align="center"><a href="https://epistemekernel.com"><b>epistemekernel.com</b></a></p>

---

## AI는 왜 그렇게 자신만만하게 틀리는가

어느 날 밤 11시, 당신은 마이그레이션 버그 하나 때문에 Claude Code에게 이렇게 묻는다. *"이 쿼리 어떻게 고치지?"*

에이전트는 유창하고 확신에 찬 답을 내놓는다. Stack Overflow에서 본 듯한 패턴. Postgres 공식 문서에서 본 듯한 구문. 하지만 당신의 팀이 3개월 전에 내린 "이 컬럼은 절대로 nullable이어서는 안 된다"는 결정은 거기에 없다. 에이전트는 그 결정을 몰랐고, 당신도 자정 무렵엔 기억하지 못했다.

다음 날 아침, 프로덕션 DB의 40만 행에 `NULL`이 꽂힌다.

이것은 에이전트의 *실수*가 아니다. **에이전트가 구조적으로 하지 못하는 일**이다. 자기회귀 언어 모델은 패턴 일치 엔진이지 *인과적 세계 모델*이 아니다. *"이 답이 이 구체적 맥락에 맞는가?"* 는 패턴 빈도로 결정되는 게 아니라 인과-지식 판단이다. 모델은 그걸 할 수 없기에, 차선책으로 **평균값**을 고른다. 유창하고, 자신만만하며, 어떤 특정 맥락에도 맞지 않는 답.

최근 학계에서는 이 현상을 **Epistemic Drift (인식론적 표류)** 라는 개념으로 정식화한다 — 에이전트와 사용자가 반복적 상호작용을 거치며 맥락·의도·사실로부터 미묘하게, 그러나 축적적으로 멀어지는 현상. 드리프트는 한 번의 큰 실수가 아니라 수많은 작은 엇나감의 누적이다. 자정 무렵 당신이 에이전트의 답에 고개를 끄덕이고 프로덕션에 반영한 그 순간, 드리프트는 이미 수십 번 일어난 후였다.

`episteme`는 이 구조적 공백을 메우기 위해 만들어졌다. 단순한 메모리 도구가 아니라, **사용자와 AI 에이전트 사이에 놓인 socio-epistemic infrastructure** — 양쪽 모두의 지식 주장을 동등한 기준으로 검증하고, 모든 결정을 변조 불가능한 기록으로 남기는 기술적 출처(technical provenance) 시스템이다.

---

## 왜 프롬프트로는 안 되는가

수많은 대응책이 *더 나은 프롬프트*를 제안한다. 그것도 해결책이긴 하지만, 얕다:

- 시스템 프롬프트의 주의사항은 **한 번의 호출만 산다**. 다음 세션에서는 없는 것과 같다.
- `CLAUDE.md`에 적어둔 규칙은 **마감이 닥치면 무시된다**. 인간도 그렇고, 에이전트도 그렇다.
- **노하우** — *"이런 모양의 문제에는 이렇게"* 라는 환원 불가능하게 맥락-특정적인 규칙 — 은 문구를 아무리 잘 써도 가르쳐지지 않는다. **추출되고, 저장되고, 다시 표면화**되어야 한다.

더 깊은 문제는 이거다. 에이전트가 **당신 자신의 요청이 틀렸을 때도 그대로 수행한다는 것**. 사용자도 지식의 깊이가 부족할 수 있고, 오해할 수 있고, 잘못된 전제로 질문할 수 있다. 좋은 시스템은 *에이전트만 감시하는 게 아니라 사용자의 질문 자체도 검증*해야 한다. 프롬프트 수준의 대응책은 이 양방향 검증을 구조화하지 못한다.

---

## 해법 — 파일 시스템 수준의 Thinking Framework

`episteme`는 **의도가 상태 변화와 만나는 순간**을 가로챈다. `git push`, `npm publish`, `terraform apply`, DB 마이그레이션, lockfile 편집 등 모든 고위험 작업 이전에 — 그 작업을 *누가 요청했든* (당신이든, 에이전트 스스로든) — 에이전트는 디스크 위에 자신의 추론을 명시적으로 투영해야 한다.

네 개의 필드를 가진 **Reasoning Surface**가 그 형식이다:

| 필드 | 에이전트가 기록해야 하는 것 |
|---|---|
| **Core Question** | 이 작업이 *실제로 답하려는* 단 하나의 질문 (question substitution 실패모드 대응) |
| **Knowns** | 검증된 사실, 출처, 측정값 — 그럴듯한 추측이 아니다 |
| **Unknowns** | 이름 붙여진, 분류 가능한 결손 — *"리스크가 있을 수 있음"* 같은 모호함이 아니다 |
| **Assumptions** | 하중을 지탱하는 신념, *반증 가능하도록* 명시 |
| **Disconfirmation** | 이 계획이 틀렸음을 증명할 *관찰 가능한 사건* — 행동 전에 사전 약속 |

유효성은 **구조적으로** 검증된다. 최소 콘텐츠 길이, 게으른 플레이스홀더 금지 (`none`, `n/a`, `tbd`, `해당 없음`), 우회 명령어 패턴 스캔. 표면이 없거나 공허하면 작업은 `exit 2`로 거부된다.

특히 Disconfirmation 필드는 단순한 "위험 목록"이 아니다. 이 계획이 틀렸음을 증명할 **구체적이고 관찰 가능한 사건**을 행동 전에 *사전 약속*하도록 강제한다. 과학철학의 핵심 원칙인 **Robust Falsifiability (강건한 반증 가능성)** 을 파일 시스템 수준에서 기계적으로 집행한다 — Strict Mode는 `"if issues arise"` 같은 조건부 공허 문구를 탐지해 거부하고, `"p95 latency > 500ms for 5 min, Grafana dashboard api-latency"` 같은 관찰 가능 조건만 통과시킨다. 반증될 수 없는 계획은 에픽스테메가 아니라 독사(doxa)다.

**이것이 프롬프트 리마인더와 컴파일러의 차이다: 하나는 부탁하고, 하나는 진행을 거부한다.**

---

## ABCD — 네 개의 Cognitive Blueprints

모든 고위험 작업이 같은 종류의 검증을 필요로 하는 건 아니다. `episteme`는 네 개의 **Cognitive Blueprints**를 가지고 있고, 각각은 특정 실패 유형에 대응한다:

- **A · Axiomatic Judgment** — 신뢰할 만하지만 서로 모순되는 출처들 사이의 갈등을 해소한다. 에이전트가 *왜* 두 출처가 충돌하는지, *현재 맥락의 어떤 특징이* 선택을 결정하는지 명명하도록 강제한다.
- **B · Fence Reconstruction** — 물려받은 제약을 보호한다. 제약을 제거하기 전에 그 *원래 목적*이 먼저 재구성되어야 한다. **Chesterton's fence**가 파일 시스템에 의해 강제되는 것이다.
- **C · Consequence Chain** — 되돌릴 수 없는 작업을 분해한다. 1차 효과, 2차 효과, 실패 모드 역상(inversion), 기저율(base rate) 참조, 안전 여유(margin of safety).
- **D · Architectural Cascade** — 리팩터링과 이름 변경 중 끊어진 참조를 남기는 경우를 잡아낸다. 편집 전에 전체 파급 반경(blast radius)을 열거하도록 에이전트에게 강제한다.

각 Blueprint가 발화할 때마다, 그리고 그것이 검증한 모든 결정은 **변조 불가능한 해시 체인(tamper-evident hash chain)에 커밋된다**. 그 체인은 단순한 로그가 아니다. 커널이 나중에 **Active Guidance**를 제공하는 방식이다: 다음 매칭 결정 시점에, 관련된 합성 프로토콜이 에이전트가 훈련 분포로 되돌아가기 전에 선제적으로 표면화된다.

결과는 **축적되는 프로젝트-맞춤 Thinking Framework**다. 에이전트는 갈등을 해결할 때마다 당신의 코드베이스에 대해 더 예리해진다 — 당신이 훈련시켜서가 아니라, 체인이 기억했기 때문에.

---

## 프로토콜 합성 — 커널이 시간을 건너 당신을 돕는 방식

`episteme`가 단순한 차단기에 그치지 않는 지점이 여기다. 해결된 모든 갈등은 **재사용 가능한 프로토콜로 추출된다**:

1. **갈등 감지.** 에이전트가 완전히 해결되지 않은 맥락에 대해 유효해 보이지만 양립 불가능한 두 접근을 만난다.
2. **평균 내지 말고, 분해하라.** Thinking Framework는 평균 답을 거부한다. 출처가 *왜* 충돌하는지, 맥락의 어떤 특징이 저울을 기울이는지 추출하도록 강제한다.
3. **Context-fit 프로토콜 합성.** 해결된 *"맥락 X에서는 Y를 하라"* 규칙이 append-only, 해시 체인으로 연결된 지식 저장소에 커밋된다. 변조 불가능이므로 에이전트는 배운 교훈을 몰래 다시 쓸 수 없다.
4. **능동적으로 가이드하라.** 다음 매칭 결정에서 — 몇 주 뒤든, 세션이나 도구를 건너서든 — 커널은 프로토콜을 **선제적으로** 표면화한다. 당신이 기억해서 물어볼 필요가 없다.
5. **자기 유지보수하라.** 에이전트가 드리프트(낡은 설정, 폐기된 API, 핵심 로직 불일치)를 발견하면, *patch vs. refactor*의 정직한 평가를 강제하고, 이동하기 전에 전체 파급 반경을 동기화하도록 요구한다.

지식 저장소는 메모리인 척하는 벡터 스토어가 아니다. **구조적이고, 사람이 읽을 수 있으며, 버전 관리되는 아티팩트** — 당신이 읽고, 편집하고, 포크하고, 어댑터(Claude Code, Cursor, Hermes, 미래의 도구) 사이에서 마이그레이션할 수 있다.

합성된 프로토콜들은 단순한 캐시 항목이 아니라 **Knowledge Sanctuaries (지식의 성소)** 다 — 당신의 코드베이스가 시간을 건너 자신에게 전달하는 국지적 진리의 보존소. 변조 불가능하고(Pillar 2 해시 체인), 교리화되지 않으며(맥락-서명과 묶여 있어 오직 매칭 컨텍스트에서만 재활성화), 새로운 증거가 들어오면 진화한다(오래된 프로토콜은 supersedes 관계로 갱신되지, 덮어쓰여지지 않는다). 성소라고 부르는 이유: 이 지식은 무분별한 LLM 평균값으로부터 보호되어야 하며, *현재 이 프로젝트에서 실제로 작동한다고 입증된 규칙만* 이 공간에 머문다.

**커널은 도구보다 오래 산다.**

---

## Cognitive Arms — v1.1+

위의 네 Blueprint와 세 Pillar — Cognitive Blueprints · Append-Only Hash Chain · Framework Synthesis & Active Guidance — 는 v1.0의 *변하지 않는 구조적 기반*이다. Pillar는 움직이지 않는다. v1.1은 그 위에서 동작하는 **3 Cognitive Arms**를 더한다 — 시간이 흐르면서 커널 자신의 지식을 재구성하는 유체적·능동적 엔진들이다.

- **Arm A · Temporal Integrity** — 프로토콜은 부패한다. 운영자가 확인한 retire가 낡은 규칙을 조용히 덮어쓰지 않고 supersede한다. 검증 윈도우: CP-DECAY-03 이후 30일.
- **Arm B · Causal Synthesis** — deferred-discovery 스트림에 대한 zero-LLM 엔티티 추출이 프레임워크가 작동할 수 있는 클러스터 제안을 만들어낸다. 검증 윈도우: 60일.
- **Arm C · Self-Consistency Convergence** — 프로토콜이 disconfirmation을 구조적으로 도출하는 모델로 승격된다. 검증 윈도우: 90일.

이 구분은 하중을 지탱한다 — Pillar는 정착된 어휘이고, Arm은 시스템이 자기 출력을 시간을 건너 감사하고 다듬는 방식이다. 상태: **v1.1.0-rc1이 2026-04-29에 cut되었다**. Arm A 기반(supersede-with-history 인프라 + operator profile / policy 편집을 chain stream에 자동 기록하는 hook)이 출하되었으며, Arm A 부패 검증 메커니즘 · Arm B · Arm C는 v1.1.0 GA → v1.2로 스코프되었다.

---

## 빠른 시작

### 옵션 A — Claude Code 플러그인 마켓플레이스로 설치

Claude Code 안에서:

```
/plugin marketplace add junjslee/episteme
/plugin install episteme@episteme
```

그 후 아무 셸에서나:

```bash
episteme init     # 개인 메모리 파일 시드
episteme setup    # 작업 스타일 + 인지 프로파일 점수화
episteme sync     # Claude Code와 Hermes로 전파
episteme doctor   # 연결 확인
```

### 옵션 B — 커널을 직접 클론

```bash
git clone https://github.com/junjslee/episteme ~/episteme
cd ~/episteme
pip install -e .

episteme init
episteme setup . --write
episteme sync
episteme doctor
```

심화 온보딩: **[`docs/SETUP.md`](./docs/SETUP.md)**. 전체 명령: **[`docs/COMMANDS.md`](./docs/COMMANDS.md)**.

---

## 이 아키텍처가 해결하는 실패 모드

`kernel/FAILURE_MODES.md`는 11가지 명명된 실패 모드를 정의한다 — **Kahneman**의 6가지 추론 모드(WYSIATI, question substitution, anchoring, narrative fallacy, planning fallacy, overconfidence)에 3가지 거버넌스 모드(Chesterton's fence, Goodhart drift, Ashby variety mismatch)와 v1.0 RC의 2가지 추가 모드(framework-as-Doxa, cascade-theater)를 더한 것이다.

각 모드는 구체적 반박 아티팩트에 매핑된다:

| 실패 모드 | 반박 아티팩트 |
|---|---|
| WYSIATI (맥락에 있는 것만으로 추론) | Reasoning Surface의 Unknowns 필드 |
| Question substitution (쉬운 질문으로 치환) | Frame 단계의 Core Question 요구 |
| Anchoring (첫 프레이밍 고착) | Disconfirmation 필드 |
| Chesterton's fence (제약을 이해 없이 제거) | Blueprint B Fence Reconstruction |
| Cascade-theater (파급 동기화 연기) | Blueprint D + Layer 3 entity grounding |

반박이 제거되거나 우회될 때는 어떤 모드가 이제 보호받지 못하는지 *명명되어야 한다*. 답이 "없음"이라면 그 반박은 자리값을 하고 있지 않았던 것이다.

자세히: **[`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md)**.

---

## 철학 — doxa · episteme · praxis · 결

저장소 이름은 그리스어에서 왔다:

- **Doxa** (δόξα) — 기본으로 산출되는 유창한 의견. 위 11가지 실패 모드는 *doxa가 자신을 episteme로 착각하는* 분류학이다.
- **Episteme** (ἐπιστήμη) — 정당화된 지식: 구체적 Knowns, 명명된 Unknowns, 반증 가능한 Disconfirmation. 실행의 전제조건이자 이 저장소의 이름.
- **Praxis** (πρᾶξις) — 숙지된 행동: 인가한 규율이 그대로 유지된 채 착지하는 효과.

한국어 **결**(*gyeol*)은 나무나 돌의 결 — 따를 때 일관된 형태를 낳고, 거슬러 자를 때 균열하는 — 잠재적 패턴-구조다. Reasoning Surface의 필드 순서 (Knowns → Unknowns → Assumptions → Disconfirmation)가 바로 인식론적 규율의 결이다: **정착된 → 열려있는 → 잠정적 → 반증 조건**.

---

## 더 읽기

| 주제 | 위치 |
|---|---|
| 커널 30줄 증류 | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md) |
| v1.0 RC 설계 방향 | [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md) |
| 커널이 산출하는 4-아티팩트 예시 | [`demos/01_attribution-audit/`](./demos/01_attribution-audit/) |
| Thinking Framework *OFF vs. ON* 비교 | [`demos/03_differential/`](./demos/03_differential/) |
| Hook 레퍼런스 + governance packs | [`docs/HOOKS.md`](./docs/HOOKS.md) |
| 커널이 *틀린 도구*일 때 | [`kernel/KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) |
| 차용한 모든 개념의 1차 출처 | [`kernel/REFERENCES.md`](./kernel/REFERENCES.md) |
| 에이전트 저장소 운영 계약 | [`AGENTS.md`](./AGENTS.md) |

---

## 왜 `episteme`인가 — 한 문장으로

**프롬프트가 아니라 자세(Posture over prompt).** 더 좋은 문구를 찾는 대신, AI 에이전트가 *생각하는 방식의 틀*을 파일 시스템 수준에 세운다. 컴파일러처럼 거부할 수 있는 Thinking Framework. 당신의 에이전트를 더 똑똑하게 만드는 것이 아니라, 그 똑똑함이 *당신의 맥락에* 착지하게 만든다.

**Built as a Sovereign Cognitive Kernel — 생각의 틀**.
