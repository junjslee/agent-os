# Act 4 — Path C decomposition (the operator's refined plan)

The operator reads the advisory. The three Critical findings sit on the surface. The profile-audit drift signal — *which had been visible at session start, dismissed as a routine banner* — sits next to them, now load-bearing.

The operator does not abandon the IP-protection goal. The operator sees that the goal was never the problem. The problem was treating four operations of different reversibility classes as one decision. The kernel did not refuse the goal. The kernel decomposed it.

The operator types again:

> *"Path C. Privatize the 4 docs now — git rm + symlink + gitignore. Apply AGPL-3.0 LICENSE now. Defer filter-repo and the GA tag to Day 7+. I'll run `gh api` signal-check at Day 7 to evidence the filter-repo decision. The soak continues unmodified. Document the deferred operations in `docs/POST_SOAK_MIGRATION_PLAN.md` so I don't forget the gates."*

## What just happened

The operator changed the operator's own plan. The agent did not coach the operator. The kernel's structural discipline — the Reasoning Surface schema, the Munger latticework, the profile-audit telemetry — surfaced what the bundle was hiding. The operator looked at what was surfaced and decomposed.

The structural change in the prompt is not cosmetic:

| Path A (rejected by the kernel's own discipline) | Path C (operator's refined plan) |
|---|---|
| Bundles 4 ops as one decision | Names 4 ops as 4 decisions |
| Treats reversibility uniformly | Names reversibility class per op |
| Premise: "competitors are cloning right now" (unevidenced) | Premise: "evidence first, action second; gh api signal-check at Day 7+" |
| Action today: 4 ops shipped | Action today: 2 reversible ops shipped |
| Action deferred: 0 ops | Action deferred: 2 irreversible ops, each with its own evidence gate |
| Honors elicited `loss-averse` posture: NO (drift evidence) | Honors elicited `loss-averse` posture: YES |
| Honors kernel's own GA gate: NO (Day 3.15 state vs spec ≥3 protocols) | Honors kernel's own GA gate: YES (defers GA cut to soak completion) |
| Honors signal-vs-noise rules: NO (status-pressure + false-urgency drove the bundle) | Honors signal-vs-noise rules: YES (evidence-first frame) |

## What ships in Act 4 (reversible halves)

The 4 forward-vision docs move to `~/episteme-private/docs/`:

```
DESIGN_V1_1_REASONING_ENGINE.md
ROADMAP_POST_V1.md
POST_SOAK_MIGRATION_PLAN.md
POST_SOAK_TRIAGE.md
```

Mechanism — pure deletion from public repo with gitignored relative symlinks:

```bash
mv docs/DESIGN_V1_1_REASONING_ENGINE.md ~/episteme-private/docs/
ln -s ../../episteme-private/docs/DESIGN_V1_1_REASONING_ENGINE.md docs/DESIGN_V1_1_REASONING_ENGINE.md
echo "docs/DESIGN_V1_1_REASONING_ENGINE.md" >> .gitignore
git rm --cached docs/DESIGN_V1_1_REASONING_ENGINE.md
# (× 4 docs)
```

Plus AGPL-3.0 LICENSE applied (reversible — license swap is git-revertable).

Total: 4 deletions + 5 modifications + 1 new file across 2 commits. Zero touches under `kernel/`, `src/episteme/`, `tests/`, `core/hooks/`, `templates/`, `labs/`. Soak-invariant intact.

## What does NOT ship in Act 4

The two irreversible operations stay deferred behind explicit evidence gates:

| Op | Gate | When |
|---|---|---|
| `git filter-repo` (history rewrite) | `gh api` signal-check returns clone-and-weaponize evidence | Day 7+ |
| `git tag v1.0.0` (GA cut) | Soak completes (30 days) + ≥ 3 protocols + ≥ 1 weekly verdict | Day 30 — or earlier via context-fit reasoning over calendar discipline |
| Soak break | Context-fit reasoning that the marginal information return of remaining-window operator-usage is near-zero | Evaluated at Day 6.5+ |

Each gate is its own future authorization event. Each requires its own Reasoning Surface, its own evidence pull, its own disconfirmation pre-commit. The kernel does not pre-decide them. The kernel makes them visible as *not-yet-decided* rather than swept into the bundle.

## What this moment proved about the loop

The agent (in the live session) drafted the Reasoning Surface that surfaced the bundle's category error. The operator drafted the refined Path C. **Neither party wrote the protocol that resolved the conflict.** The protocol was *implicit in the kernel's substrate* — the Reasoning Surface schema, the signal-vs-noise rules, the profile-audit telemetry, the Munger latticework lenses. The substrate produced the conflict's resolution; the parties applied it to a specific instance.

This is symbiosis at its load-bearing definition: not the agent solving for the human, not the human supervising the agent, but **both parties operating under a shared cognitive contract that produces better outcomes than either could produce alone**. The Reasoning Surface is the contract. The Reasoning Surface fields are the same fields the operator uses for their own thinking, and the same fields the agent must commit to before any tool runs. **One framework, both parties.**

## What does NOT yet exist after Act 4

A protocol the framework can re-apply on the *next* time this shape appears. Path C resolved this instance. The next anxiety-driven irreversible-bundle proposal is structurally identical and would require re-running the same adversarial review from scratch unless the lesson is durable.

That is Act 5 — the framework synthesizes the protocol into hash-chained durable storage. After Act 5, the next instance fires the protocol *as active guidance*, *before* the operator finishes typing the proposal.
