# Next Steps

Exact next actions, in priority order. Update this file at every handoff.

---

## Immediate (verify before promoting 0.7.0)

1. **Verify marketplace source fix** — run `/plugin marketplace add junjslee/episteme` in a clean Claude Code session. This is the one unverified assumption carried from 0.6.0.

2. **Run push-readiness checklist**
   ```bash
   PYTHONPATH=. pytest -q tests/test_profile_cognition.py
   python3 -m py_compile src/episteme/cli.py
   python3 -m py_compile core/hooks/reasoning_surface_guard.py
   episteme doctor
   ```

3. **Push and tag** — `git push && git tag v0.7.0 && git push --tags`

---

## Carried from 0.6.0

## Immediate (verify before promoting 0.6.0)

1. **Verify marketplace source fix** — run `/plugin marketplace add junjslee/episteme` in a clean Claude Code session and confirm the schema error is resolved. If it persists, inspect the live validator error and adjust the `source` field format. This is the one unverified assumption in 0.6.0.

2. **Run push-readiness checklist**
   ```bash
   PYTHONPATH=. pytest -q tests/test_profile_cognition.py
   python3 -m py_compile src/episteme/cli.py
   episteme doctor
   git status && git rev-list --left-right --count @{u}...HEAD
   ```

3. **Commit 0.6.0** — once marketplace fix is verified, create a single commit covering all changes in this cycle (see `docs/PROGRESS.md` for full file list).

---

## Short-term (next cycle)

- Replace ASCII control-plane diagram in `README.md` with an SVG asset (see TODO comment removed in this cycle; concept is now defined)
- Add `last_elicited` timestamp field to operator profile schema (Gap B in KERNEL_LIMITS.md)
- Implement calibration telemetry stub — `decisions/*.md` append-only log (Gap A)

---

## Medium-term (roadmap)

- Multi-operator mode design (Gap C)
- `tacit-call` decision marker in Reasoning Surface schema (Gap D)
- Cynefin domain classification field in `reasoning-surface.json` schema (companion to KERNEL_LIMITS.md addition)
