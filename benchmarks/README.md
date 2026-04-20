# Benchmarks

A kernel that claims to prevent fluent-but-wrong decisions must be *falsifiable*. This directory holds versioned benchmarks whose purpose is to expose the kernel — not decorate it.

## Philosophy

Every benchmark here ships with:

1. **A hypothesis.** "The kernel reduces X failure mode by Y."
2. **A dataset.** Enough cases to separate signal from noise.
3. **A rubric.** How each case is scored, structurally (not semantically), so the scorer is deterministic and doesn't depend on an LLM judge.
4. **A disconfirmation target.** The *exact* result that would prove the hypothesis wrong. Published *before* the score, not after.
5. **A published result.** `RESULTS.md` holds the latest run, dated, reproducible with a single command.

Per episteme's own principles: claims without disconfirmation conditions are creed, not engineering.

## Current benchmarks

- **[`kernel_v1/`](./kernel_v1/)** — tests whether the Reasoning Surface + Failure Modes catalog would have surfaced at least one structural flaw in 20 curated *confident-wrong* decision prompts.

## How to reproduce

```bash
python3 benchmarks/kernel_v1/run.py
cat benchmarks/kernel_v1/RESULTS.md
```

No network. No LLM calls. No API keys. The scorer is a pure-Python rubric application against a static dataset — anyone can verify the result by reading the code.
