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
  <a href="README.es.md"><b>Español</b></a> &bull;
  <a href="README.zh.md">中文</a>
</p>

<p align="center"><a href="https://epistemekernel.com"><b>epistemekernel.com</b></a></p>

---

## ¿Por qué los agentes de IA se equivocan con tanta confianza?

Martes, 11 de la noche. Le pides al agente que añada una columna soft-delete a la tabla `orders` — `deleted_at TIMESTAMP NULL`. Genera la migración. Las pruebas pasan. Mergeas.

Cuarenta horas después, 4 de la mañana, llaman al ingeniero de guardia. El servicio de envíos hace panic en cada reintento — un deserializador en Rust espera un match exhaustivo sobre `shipping_status` que *no incluye NULL*. El CHECK constraint que lo aplicaba fue modificado hace seis meses por un senior con una descripción de PR de una sola línea; el razonamiento vive en un hilo de Slack que nadie buscó. El agente no tenía razón para recorrer el call-graph de los consumidores downstream de `orders.*`. Tú no tenías razón para mencionarlo a las 11 PM.

Esto no es un *error* del agente. Es algo que el agente **estructuralmente no puede hacer**. Un modelo de lenguaje auto-regresivo es un motor de coincidencia de patrones, no un *modelo causal del mundo*. La pregunta *"¿esta respuesta encaja con este contexto específico?"* es un juicio causal, no una coincidencia de frecuencia de tokens. Como el modelo no puede hacerlo, recurre al siguiente mejor: **el promedio estadístico**. Fluido, seguro, y que no encaja con ningún contexto específico.

`episteme` existe para cerrar ese vacío estructural.

---

## Por qué los prompts no resuelven esto

- Un recordatorio en el system prompt **vive solo una llamada**.
- Una nota en `CLAUDE.md` **se ignora cuando llega el deadline** — tanto los humanos como los agentes lo hacen.
- **El know-how** — la regla irreduciblemente específica al contexto de *"en esta forma de problema, haz esto"* — no se enseña con mejor redacción. Tiene que ser **extraído, almacenado y re-emergido**.

Y lo más profundo: el agente **ejecuta incluso cuando la solicitud del usuario es incorrecta**. Los usuarios también pueden carecer de profundidad, malinterpretar o partir de premisas erróneas. Un buen sistema *no solo vigila al agente, también valida la pregunta misma del usuario*. Los parches a nivel de prompt no estructuran esta validación bidireccional.

---

## La solución — un Thinking Framework a nivel del sistema de archivos

`episteme` intercepta **el momento en que la intención se encuentra con el cambio de estado**. Antes de cualquier operación de alto impacto (`git push`, `npm publish`, `terraform apply`, migraciones de DB, edición de lockfiles) — sin importar *quién* la solicitó (el usuario o el propio agente) — el agente debe proyectar su razonamiento explícitamente en una **Reasoning Surface** de cuatro campos en el disco:

| Campo | Qué debe declarar el agente |
|---|---|
| **Core Question** | La única pregunta que esta acción realmente intenta responder (contra la question substitution) |
| **Knowns** | Hechos verificados, citas, mediciones — no suposiciones que suenan bien |
| **Unknowns** | Vacíos nombrados y clasificables — no un vago *"puede haber riesgos"* |
| **Assumptions** | Creencias que soportan la carga, marcadas para que puedan ser falsificadas |
| **Disconfirmation** | El evento observable que *probaría que este plan está mal* — comprometido antes de actuar |

La validación es **estructural**: longitud mínima, prohibición de placeholders perezosos (`none`, `n/a`, `tbd`, `해당 없음`), escaneo normalizado de comandos. Si la surface falta o es vacía, la operación se rechaza con `exit 2`.

**Esta es la diferencia entre un recordatorio de prompt y un compilador: uno pide por favor, el otro se niega a continuar.**

---

## ABCD — cuatro Cognitive Blueprints

Cada operación de alto impacto dispara uno de cuatro Blueprints, cada uno contrarrestando una clase específica de falla:

- **A · Axiomatic Judgment** — resuelve conflictos entre fuentes creíbles pero incompatibles. Obliga al agente a nombrar *por qué* difieren y *qué característica del contexto actual* decide.
- **B · Fence Reconstruction** — protege restricciones heredadas. Antes de remover una restricción, su *propósito original* debe ser reconstruido. **La cerca de Chesterton (Chesterton's fence)** aplicada por el sistema de archivos.
- **C · Consequence Chain** — descompone operaciones irreversibles (efecto de primer orden, de segundo orden, inversión de failure-mode, tasa base, margin of safety).
- **D · Architectural Cascade** — atrapa refactorizaciones y renombres que dejarían referencias obsoletas. Obliga al agente a enumerar el blast radius completo antes de editar.

Cada activación de un Blueprint y cada decisión que valida se registra en una **cadena hash a prueba de manipulación (tamper-evident hash chain)**. Esa cadena no es un simple log — es cómo el kernel ofrece **Active Guidance** más tarde: en la siguiente decisión coincidente, el protocolo sintetizado relevante se expone proactivamente, antes de que el agente retroceda a su distribución de entrenamiento.

El resultado: **un Thinking Framework específico de tu proyecto que se acumula**. El agente se afina con tu codebase cada vez que resuelve un conflicto — no porque lo hayas entrenado, sino porque la cadena recordó por ti.

---

## Ejecución zero-trust

El [**OWASP Top 10 for Agentic Applications (2026)**](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — revisado por más de 100 expertos de la industria — identifica prompt injection, goal hijacking, overreach, memory poisoning y unbounded action como las principales clases de riesgo para agentes autónomos. La estructura Knowns / Unknowns / Assumptions / Disconfirmation es un contador *estructural* a cada uno:

| OWASP Agentic Risk (2026) | contador de episteme |
|---|---|
| Manipulación directa de objetivos / prompt injection | Core Question declarada antes de la ejecución; las desviaciones afloran como Unknowns |
| Inyección indirecta de instrucciones | Knowns / Disconfirmation separan el estado confiable del contenido del prompt; el agente se compromete a un resultado falsable antes de actuar sobre la entrada recuperada |
| Overreach / acción no limitada | Régimen de restricciones declarado en Frame; política reversible-first aplicada |
| Alucinación fluida | El campo Unknowns no puede quedar vacío; las suposiciones deben nombrarse antes de actuar sobre ellas |
| Envenenamiento de memoria | Protocolos Pillar 2 hash-chained — append-only, tamper-evident; reescrituras silenciosas de estado previo son detectadas por `verify_chain` |
| Bucles de planificación infinita | Condición de Disconfirmation requerida; el bucle sale cuando la evidencia se dispara |

Ninguna suposición se confía hasta ser nombrada. Ninguna acción se toma sin la precondición (Knowns) y el régimen de restricciones declarados. El kernel es la capa de verificación entre intención y ejecución.

### Convergencia industrial — 2025–2026

Frameworks y artículos académicos importantes en la misma ventana convergen sobre los mismos patrones arquitectónicos que el kernel envía: checkpoints pre-invocación a nivel del sistema de archivos ([Capsule Security ClawGuard](https://www.businesswire.com/news/home/20260415670902/), 2026), memoria hash-chained tamper-evident ([SSGM](https://arxiv.org/abs/2603.11768) — Lam et al., 2026), alineación basada en razones en lugar de listas de reglas ([Anthropic's Claude Constitution](https://www.anthropic.com/constitution), 2026-01-22), bucle cognitivo de cinco fases con capa de gobernanza ([SCL R-CCAM](https://arxiv.org/abs/2511.17673) — Kim, 2025), e integridad de agente de cinco pilares ([Proofpoint Agent Integrity Framework 2026](https://www.proofpoint.com/us/resources/white-papers/agent-integrity-framework)). El kernel precede a estas publicaciones (CP1 enviado 2026-04-21; v1.0.0 GA 2026-04-28); la convergencia es validación independiente, no linaje. Mapa completo de atribución en [`kernel/REFERENCES.md`](./kernel/REFERENCES.md) bajo *Convergent contemporary work*.

---

## Cognitive Arms — v1.1+

Los cuatro Blueprints (arriba) y los tres Pillars — Cognitive Blueprints · Append-Only Hash Chain · Framework Synthesis & Active Guidance — son la *base estructural inmóvil* de v1.0. Los Pillars no se mueven. v1.1 añade **3 Cognitive Arms** que operan encima: motores activos y fluidos que refactorizan el propio conocimiento del kernel a lo largo del tiempo.

- **Arm A · Temporal Integrity** — los protocolos decaen. El retiro confirmado por el operador supersede una regla obsoleta en lugar de sobrescribirla silenciosamente. Ventana de verificación: 30 días después de CP-DECAY-03.
- **Arm B · Causal Synthesis** — extracción de entidades sin LLM sobre el stream de deferred-discovery produce propuestas de clúster sobre las que el framework puede actuar. Ventana de verificación: 60 días.
- **Arm C · Self-Consistency Convergence** — los protocolos se promueven a modelos que derivan disconfirmaciones estructuralmente. Ventana de verificación: 90 días.

La distinción es estructural — los Pillars son vocabulario asentado; los Arms son cómo el sistema audita y refina sus propias salidas a lo largo del tiempo. Estado: **v1.1.0-rc1 cortado el 2026-04-29** con el sustrato de Arm A enviado (infraestructura supersede-with-history + hooks de auto-instrumentación que registran ediciones de perfil de operador y de policy a streams de cadena). El mecanismo de verificación de decaimiento de Arm A, Arm B y Arm C están scopeados para v1.1.0 GA → v1.2.

---

## Inicio rápido

### Opción A — Plugin de Claude Code

Dentro de Claude Code:

```
/plugin marketplace add junjslee/episteme
/plugin install episteme@episteme
```

Luego en cualquier shell:

```bash
episteme init     # sembrar archivos de memoria personal
episteme setup    # puntuar estilo de trabajo + perfil cognitivo
episteme sync     # propagar a Claude Code y Hermes
episteme doctor   # verificar conexiones
```

### Opción B — Clonar el kernel directamente

```bash
git clone https://github.com/junjslee/episteme ~/episteme
cd ~/episteme
pip install -e .

episteme init
episteme setup . --write
episteme sync
episteme doctor
```

Onboarding detallado: **[`docs/SETUP.md`](./docs/SETUP.md)**. Referencia completa de comandos: **[`docs/COMMANDS.md`](./docs/COMMANDS.md)**.

---

## Filosofía — doxa · episteme · praxis · 결

El nombre del repositorio viene del griego:

- **Doxa** (δόξα) — opinión común, la salida fluida producida por defecto. Los 11 failure modes en [`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md) son una taxonomía de *doxa confundiéndose con episteme*.
- **Episteme** (ἐπιστήμη) — conocimiento justificado: Knowns concretos, Unknowns nombrados, Disconfirmation falsificable. El precondición para ejecución.
- **Praxis** (πρᾶξις) — acción informada: efectos que aterrizan con su disciplina autorizante intacta.

La palabra coreana **결** (*gyeol*) nombra el grano de la madera o piedra — el patrón latente que, seguido, produce forma coherente, y cortado en contra, se fractura. El orden de los campos de la Reasoning Surface es el *gyeol* de la disciplina epistémica: **establecido → abierto → provisional → condición de falsificación**.

---

## Lee a continuación

| Tema | Ubicación |
|---|---|
| Destilación del kernel en 30 líneas | [`kernel/SUMMARY.md`](./kernel/SUMMARY.md) |
| Dirección de diseño v1.0 RC | [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md) |
| Los 11 failure modes con sus contraartefactos | [`kernel/FAILURE_MODES.md`](./kernel/FAILURE_MODES.md) |
| Thinking Framework *OFF vs. ON* sobre el mismo prompt | [`demos/03_differential/`](./demos/03_differential/) |
| Cuándo el kernel es la herramienta equivocada | [`kernel/KERNEL_LIMITS.md`](./kernel/KERNEL_LIMITS.md) |
| Atribución de cada concepto prestado | [`kernel/REFERENCES.md`](./kernel/REFERENCES.md) |
| Contrato operativo del repositorio para agentes | [`AGENTS.md`](./AGENTS.md) |

---

## Por qué `episteme` — en una frase

**Postura antes que prompt (Posture over prompt).** En lugar de buscar mejor redacción, establece el *marco en el que un agente de IA piensa* a nivel del sistema de archivos. Un Thinking Framework que — como un compilador — puede negarse a continuar. No hace tu agente más inteligente; hace que esa inteligencia *aterrice en tu contexto*.

**Built as a Sovereign Cognitive Kernel — 생각의 틀**.

---

> **Note on translation.** This README is a focused-scope Spanish adaptation maintained alongside the canonical English [`README.md`](./README.md). For deepest documentation, demo walkthroughs, and architectural diagrams, refer to the English docs tree. Technical terms (Thinking Framework, Reasoning Surface, Blueprint, Core Question, Chesterton's fence, Pillar 3, flaw_classification, etc.) are kept in English because they are load-bearing kernel vocabulary.
