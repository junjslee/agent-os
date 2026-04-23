# Logo candidates — pick one

Three directions for the episteme character mark. All compose with the existing
wordmark (`docs/assets/logo-{light,dark}.svg`) — the mark sits to the left of
the text so the current word identity stays intact.

## Palette (all three)

| Role | Hex | Use |
|---|---|---|
| Dark anchor | `#1A1740` | Hat, staff, dragon outlines, dark accents |
| Mid (body) | `#2E2A6B` | Robes, dragon silhouette fill |
| Light mid  | `#6B5FB8` | Belly / inner coil highlight |
| Pale accent | `#D4CEEF` | Skin, beard, summoned-hand |
| Warm accent | `#F8E7A3` | Eye glow (staff, dragonling, or dragon) — one pixel, used sparingly |
| Wordmark | `#0a0a0a` | Existing type treatment, unchanged |

Current candidates are **light-mode only** (indigo-on-white). The dark variant
will be derived once a direction is picked — same silhouette, color ramp shifted.

## Candidates

### A — Wizard-Sage (`A-wizard-sage.svg`)

Hooded sage, tall pointed hat, pale beard, holding a staff. The staff's orb is
an **eye** (warm accent), not a crystal — signals "reasoning gates action,"
which is the kernel's thesis. Most literal archetype fit. Safest read at
thumbnail among the three character-only options.

### B — Sage + Dragonling (`B-sage-dragonling.svg`)

Same sage base as A, but the staff is replaced by a **small coiled dragon**
summoned at his side. Mixes all three references: wizard (#4) body, Dratini
(#5) pixel-discrete scale, dragon silhouette (#6) coil. Semantically the
richest — the sage *governs* the powerful instinct, which is what episteme
does to the LLM. Also the most detailed, so the 24px favicon test is the
hardest one for this option to pass.

### C — Dragon Sigil (`C-dragon-sigil.svg`)

No wizard. A coiled dragon silhouette with a warm-accent eye, two-tone body
(dark back + lighter belly for coil definition), horn crest. Reads as a
seal / sigil — governance connotation. Best thumbnail survival of the three.
Weakest at signaling "*thinking* discipline" specifically, because dragon is
a crowded motif in dev tooling.

## After you pick

1. Move the chosen SVG to `docs/assets/logo-mark-light.svg` (keeping the
   wordmark-only files as a fallback; composition is already inside each
   candidate SVG).
2. Derive `logo-mark-dark.svg` from the same source — swap dark anchor
   `#1A1740` → pale `#D4CEEF`, pale `#D4CEEF` → dark `#1A1740`, keep
   mid `#2E2A6B` and `#6B5FB8` at similar luminance (they work for both
   modes).
3. Update README.md `<picture>` block to reference the new mark files.
4. Update `web/src/app/` (Next.js) hero / nav logo import to use the same
   SVG.
5. 24×24 favicon test — scale the chosen SVG to 24×24, confirm the silhouette
   still reads as the archetype. If it collapses, fall back to a simplified
   mark (likely a stripped-down C).
6. CLI half-block render test — convert the 24×24 pixel grid to Unicode
   `▀▄` + ANSI truecolor output, check identity at ~14 cells wide in a
   truecolor terminal (iTerm2 / WezTerm / Kitty / Alacritty).

## Archiving the others

Three options for the two non-picked candidates:

- **Delete** — cleanest. `git rm docs/assets/logo-candidates/{B,C}-*.svg` (or
  whichever two). History preserves them via the commit that introduced them.
- **Archive in-repo** — `mv docs/assets/logo-candidates docs/assets/archive/logo-candidates-2026-04`
  and keep the directory README. Good if you want a visible "what else we
  considered" record next to ARCHITECTURE notes.
- **Gitignore** — leave the files on disk locally but `echo "docs/assets/logo-candidates/" >> .gitignore`
  after moving the winner out. Avoid — state that's ignored-but-present drifts
  silently and is the shape of future confusion.

Default recommendation: **delete**. The commit history is the right place for
"considered alternatives"; a floating candidates directory accrues cruft.
