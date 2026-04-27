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
  <a href="README.es.md"><b>Español</b></a> &bull;
  <a href="README.zh.md">中文</a>
</p>

<p align="center"><a href="https://epistemekernel.com"><b>epistemekernel.com</b></a></p>

---

## ¿Por qué los agentes de IA se equivocan con tanta confianza?

Son las 11 de la noche. Le pides a tu agente de IA que arregle un bug de migración. La respuesta es fluida, segura, plausible — combina patrones de Stack Overflow con sintaxis de la documentación oficial de Postgres. Lo que no aparece en ninguna parte: la decisión que tu equipo tomó hace tres meses de que esa columna *nunca debe ser nullable*. El agente no la conocía. Tú tampoco lo recordabas a medianoche.

A la mañana siguiente, 400.000 filas en producción tienen `NULL`.

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
