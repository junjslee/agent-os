# Open Source Your Profile

Your personal episteme files — `cognitive_profile.md`, `operator_profile.md`, `workflow_policy.md`, `overview.md`, `python_runtime_policy.md` — are the deepest expression of what episteme is meant to do.

The `*.example.md` files in `core/memory/global/` are minimal templates. They show the shape. Your personal files show the depth: the actual reasoning philosophy, the real workflow constraints, the genuine cognitive posture that shapes every session you run.

Sharing your personal files (with appropriate redactions) is the most valuable thing you can contribute to the episteme community.

## Why opening your profile matters

Other users can read the README and understand what episteme does architecturally. But most people don't understand what a fully realized episteme profile actually looks like until they see one.

A real profile shows:
- How someone actually encodes their reasoning philosophy (not just placeholder text)
- What a mature `workflow_policy.md` looks like after real-world iteration
- How cognitive posture and execution policy interact in practice
- The depth of the `build_story.md` when it's genuinely authored, not filled-in template

Without reference implementations, new users are left guessing. Your profile fills that gap.

## What to redact before sharing

Before adding your personal files to git as reference implementations, remove or anonymize:

1. **Machine-specific paths** — anything like `/Users/yourname/`, `~/projects/your-project/`, or HPC-specific paths.
   Replace with generic placeholders: `~/projects/<project-name>/` or `{{CONDA_ROOT}}`.

2. **Private API keys, tokens, or credentials** — these should never be in these files anyway, but double-check.

3. **Private project names or client names** — replace with generic descriptors like `<project-a>` or `<client-project>`.

4. **Personal identifying information** — name, employer, specific institutional affiliations if you prefer not to share.

5. **Internal tool names or infrastructure** — if your profile references internal tooling, either redact or generalize.

Keep:
- Your reasoning philosophy — this is the valuable part
- Your workflow policy rules — these generalize well
- Your cognitive posture settings — unique to you, useful to others
- Your build story arc — shows how the system is actually used

## The reference implementation pattern

The pattern: copy your personal files to `core/memory/global/*.reference.md` and add those to git.
Your personal `*.md` files remain gitignored. Your reference files become public examples.

```bash
# Create reference versions of your personal files
cp core/memory/global/cognitive_profile.md core/memory/global/cognitive_profile.reference.md
cp core/memory/global/operator_profile.md core/memory/global/operator_profile.reference.md
cp core/memory/global/workflow_policy.md core/memory/global/workflow_policy.reference.md
cp core/memory/global/overview.md core/memory/global/overview.reference.md
cp core/memory/global/build_story.md core/memory/global/build_story.reference.md

# Edit each *.reference.md to redact private details
# Then add them to git
git add core/memory/global/*.reference.md
git commit -m "docs: add personal profile reference implementations"
```

The `.gitignore` already allows `*.reference.md` files — only bare `*.md` personal files are excluded.

## Example.md vs reference.md

| File pattern | Purpose | Depth |
|---|---|---|
| `*.example.md` | Minimal template — shows structure | Low — blank fields, generic text |
| `*.reference.md` | Real implementation — shows what's possible | High — actual philosophy, real choices |

The `*.example.md` files are already public. They're the starter kit.
`*.reference.md` files show what a mature, personally authored episteme profile looks like.

## A note on vulnerability

Sharing your cognitive profile is somewhat personal. It encodes your reasoning defaults, your noise sources, your operating doctrine. That's fine — it's also what makes it valuable.

You're not sharing secrets. You're sharing craft.

The episteme community benefits most from people who've done the work of actually encoding their philosophy, not just filling in templates. If you've gotten that far, consider sharing it.
