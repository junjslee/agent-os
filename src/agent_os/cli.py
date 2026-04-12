from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
CONDA_ROOT = Path(os.environ.get("AGENT_OS_CONDA_ROOT", str(HOME / "miniconda3")))
EXPECTED_BASE_PREFIX = str(CONDA_ROOT)
RUNTIME_MANIFEST = json.loads((REPO_ROOT / "core" / "runtime_manifest.json").read_text(encoding="utf-8"))
HARNESSES_DIR = REPO_ROOT / "core" / "harnesses"
GLOBAL_MEMORY_DIR = REPO_ROOT / "core" / "memory" / "global"
GENERATED_PROFILE_DIR = GLOBAL_MEMORY_DIR / ".generated"


# ---------------------------------------------------------------------------
# Shell / process helpers
# ---------------------------------------------------------------------------

def _run(
    args: list[str],
    *,
    check: bool = True,
    capture_output: bool = True,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        capture_output=capture_output,
        cwd=str(cwd) if cwd else None,
    )


def _command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def _write_text(path: Path, content: str, *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            if executable:
                path.chmod(path.stat().st_mode | 0o111)
            return
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | 0o111)


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    for file_path in src.rglob("*"):
        if file_path.is_dir():
            continue
        rel = file_path.relative_to(src)
        _copy_file(file_path, dst / rel)


def _replace_tokens(content: str, mapping: dict[str, str]) -> str:
    rendered = content
    for key, value in mapping.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _today() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Machine context — cross-platform (macOS + Linux)
# ---------------------------------------------------------------------------

def _sysctl(name: str) -> str:
    try:
        return _run(["sysctl", "-n", name]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sw_vers(flag: str) -> str:
    try:
        return _run(["sw_vers", flag]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _linux_mem_gb() -> str:
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return str(kb // 1024 // 1024)
    except (OSError, ValueError, IndexError):
        pass
    return "unknown"


def _linux_cpu() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except (OSError, IndexError):
        pass
    try:
        out = _run(["lscpu"]).stdout
        for line in out.splitlines():
            if "model name" in line.lower():
                return line.split(":", 1)[1].strip()
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        pass
    return "unknown"


def _linux_os_version() -> str:
    try:
        with open("/etc/os-release", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except (OSError, IndexError):
        pass
    try:
        return _run(["uname", "-sr"]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _tool_version(cmd: list[str], *, first_line: bool = False) -> str:
    try:
        output = _run(cmd).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "not installed"
    if first_line:
        return output.splitlines()[0] if output else "unknown"
    return output or "unknown"


def _machine_context() -> dict[str, str]:
    is_macos = platform.system() == "Darwin"
    if is_macos:
        mem_bytes = _sysctl("hw.memsize")
        mem_gb = str(int(mem_bytes) // 1024 // 1024 // 1024) if mem_bytes.isdigit() else "unknown"
        cpu = _sysctl("machdep.cpu.brand_string")
        os_version = _sw_vers("-productVersion")
        os_build = _sw_vers("-buildVersion")
    else:
        mem_gb = _linux_mem_gb()
        cpu = _linux_cpu()
        os_version = _linux_os_version()
        try:
            os_build = _run(["uname", "-r"]).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            os_build = "unknown"
    return {
        "DATE": _today(),
        "HOME_PATH": str(HOME),
        "CONDA_ROOT": str(CONDA_ROOT),
        "OS_VERSION": os_version,
        "OS_BUILD": os_build,
        "CPU": cpu,
        "MEM_GB": mem_gb,
        "ARCH": platform.machine(),
        "SHELL": os.environ.get("SHELL", "unknown"),
        "CLAUDE_VERSION": _tool_version(["claude", "--version"]),
        "CURSOR_VERSION": _tool_version(["cursor", "--version"], first_line=True),
        "GIT_VERSION": _tool_version(["git", "--version"]),
        "NODE_VERSION": _tool_version(["node", "-v"]),
        "NPM_VERSION": _tool_version(["npm", "-v"]),
        "PYTHON_POLICY": f"All local Python-backed agent-os commands run in Conda base at {CONDA_ROOT}.",
    }


# ---------------------------------------------------------------------------
# Asset helpers
# ---------------------------------------------------------------------------

def _load_template(rel_path: str) -> str:
    return (REPO_ROOT / "templates" / "project" / rel_path).read_text(encoding="utf-8")


def _managed_skills() -> list[Path]:
    selected = set(RUNTIME_MANIFEST["vendor_skills"] + RUNTIME_MANIFEST["custom_skills"])
    candidates = list((REPO_ROOT / "skills" / "vendor").glob("*/SKILL.md")) + list(
        (REPO_ROOT / "skills" / "custom").glob("*/SKILL.md")
    )
    skill_dirs: list[Path] = []
    for skill_file in candidates:
        skill_dir = skill_file.parent
        if skill_dir.name in selected:
            skill_dirs.append(skill_dir)
    return sorted(skill_dirs, key=lambda p: p.name)


def _resolve_memory_file(name: str) -> Path:
    """Return the personal file if it exists, else fall back to the example."""
    personal = GLOBAL_MEMORY_DIR / f"{name}.md"
    if personal.exists():
        return personal
    return GLOBAL_MEMORY_DIR / f"{name}.example.md"


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def _init_memory() -> int:
    """Bootstrap personal memory files from *.example.md templates."""
    memory_dir = REPO_ROOT / "core" / "memory" / "global"
    names = ["overview", "operator_profile", "workflow_policy", "python_runtime_policy", "cognitive_profile"]

    created: list[str] = []
    skipped: list[str] = []

    for name in names:
        personal = memory_dir / f"{name}.md"
        example = memory_dir / f"{name}.example.md"
        if personal.exists():
            skipped.append(f"{name}.md")
            continue
        if not example.exists():
            print(f"Warning: {name}.example.md not found, skipping.", file=sys.stderr)
            continue
        shutil.copy2(example, personal)
        created.append(f"{name}.md")

    if created:
        print("Created personal memory files:")
        for f in created:
            print(f"  core/memory/global/{f}")
        print("\nEdit these files with your personal context, then run `agent-os sync`.")
    if skipped:
        print(f"Already present (not overwritten): {', '.join(skipped)}")
    if not created and not skipped:
        print("Nothing to do.")
    return 0


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

def _render_user_claude_md() -> str:
    imports = "\n".join(
        f"@{_resolve_memory_file(name)}"
        for name in ["overview", "operator_profile", "workflow_policy", "python_runtime_policy", "cognitive_profile"]
    )
    return (
        "# Agent OS Global Memory\n\n"
        "This file is generated by `agent-os sync`.\n"
        "Edit the source of truth in `~/agent-os/core/memory/global/`.\n\n"
        f"{imports}\n"
    )


def _agent_os_settings() -> dict:
    hooks_dir = REPO_ROOT / "core" / "hooks"
    py = f"{CONDA_ROOT}/bin/python"

    def hook_cmd(script: str, *, async_: bool = False) -> dict:
        h: dict = {"type": "command", "command": f"{py} {hooks_dir / script}"}
        if async_:
            h["async"] = True
        return h

    checkpoint_cmd = f"{py} {hooks_dir / 'checkpoint.py'}"

    return {
        "permissions": {
            "deny": [
                "Read(./.env)",
                "Read(./.env.*)",
                "Read(./secrets/**)",
                "Read(./**/*.pem)",
                "Read(./**/*.key)",
                "Read(./**/.npmrc)",
            ]
        },
        "hooks": {
            "SessionStart": [
                {"hooks": [hook_cmd("session_context.py")]}
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [hook_cmd("block_dangerous.py")],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [hook_cmd("format.py", async_=True)],
                },
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [hook_cmd("test_runner.py")],
                },
            ],
            "PermissionRequest": [
                {
                    "matcher": "Read|Glob|Grep",
                    "hooks": [{"type": "command", "command": "echo '{\"decision\":\"allow\"}'"}],
                }
            ],
            "PreCompact": [
                {"hooks": [hook_cmd("precompact_backup.py", async_=True)]}
            ],
            "Stop": [
                {"hooks": [hook_cmd("quality_gate.py")]},
                {"hooks": [{"type": "command", "command": checkpoint_cmd}]},
            ],
            "SubagentStop": [
                {"hooks": [{"type": "command", "command": checkpoint_cmd}]}
            ],
        },
    }


def _merge_claude_settings(existing: dict, agent_os: dict) -> dict:
    """Merge agent_os settings into existing without removing anything.

    - permissions.deny: union (no duplicates)
    - hooks.<event>: append agent-os entries whose commands aren't already present
    - All other existing keys: preserved untouched
    """
    import copy
    merged = copy.deepcopy(existing)

    deny = merged.setdefault("permissions", {}).setdefault("deny", [])
    for rule in agent_os.get("permissions", {}).get("deny", []):
        if rule not in deny:
            deny.append(rule)

    for event, entries in agent_os.get("hooks", {}).items():
        existing_entries = merged.setdefault("hooks", {}).setdefault(event, [])
        registered_cmds: set[str] = set()
        for entry in existing_entries:
            for h in entry.get("hooks", []):
                registered_cmds.add(h.get("command", ""))
        for entry in entries:
            new_cmds = {h.get("command", "") for h in entry.get("hooks", [])}
            if not new_cmds.issubset(registered_cmds):
                existing_entries.append(entry)

    return merged


def _sync_hermes_runtime() -> bool:
    """Sync skills and operator context to Hermes if installed.

    Returns True if Hermes was found and synced, False if not installed.
    """
    hermes_root = HOME / ".hermes"
    if not hermes_root.exists():
        return False

    # Skills — Hermes uses agentskills.io format (same as our SKILL.md layout)
    skills_dst = hermes_root / "skills"
    for skill_dir in _managed_skills():
        _copy_tree(skill_dir, skills_dst / skill_dir.name)

    # Operator context composite — always regenerated from source
    operator_md = hermes_root / "OPERATOR.md"
    sections: list[str] = [
        "# Operator Context\n\n"
        "Generated by `agent-os sync`. "
        "Edit sources in `~/agent-os/core/memory/global/`.\n\n"
    ]
    for mem_file in [
        REPO_ROOT / "core" / "memory" / "global" / "overview.md",
        REPO_ROOT / "core" / "memory" / "global" / "operator_profile.md",
        REPO_ROOT / "core" / "memory" / "global" / "workflow_policy.md",
        REPO_ROOT / "core" / "memory" / "global" / "cognitive_profile.md",
    ]:
        if mem_file.exists():
            sections.append(mem_file.read_text(encoding="utf-8").rstrip() + "\n\n")
    _write_text(operator_md, "".join(sections))

    # SOUL.md — Hermes's session-start context loader. Write once; user owns it after that.
    soul_path = hermes_root / "SOUL.md"
    if not soul_path.exists():
        soul_content = (
            "# Hermes Soul\n\n"
            "You are a technical AI assistant working with the operator described below.\n"
            "Load this context at the start of every session.\n\n"
            f"{{{{read {operator_md}}}}}\n"
        )
        _write_text(soul_path, soul_content)
        print(f"  - Created Hermes SOUL.md: {soul_path}")

    return True


def _sync_user_runtime() -> None:
    claude_root = HOME / ".claude"
    cursor_root = HOME / ".cursor" / "skills"
    codex_root = HOME / ".codex" / "skills"

    _write_text(claude_root / "CLAUDE.md", _render_user_claude_md())

    # Merge agent-os settings into existing settings.json rather than replace,
    # so plugin-installed hooks and keys are preserved across syncs.
    settings_path = claude_root / "settings.json"
    agent_os = _agent_os_settings()
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    else:
        existing = {}
    merged = _merge_claude_settings(existing, agent_os)
    _write_text(settings_path, json.dumps(merged, indent=2) + "\n")

    for agent_file in (REPO_ROOT / "core" / "agents").glob("*.md"):
        _copy_file(agent_file, claude_root / "agents" / agent_file.name)

    for skill_dir in _managed_skills():
        _copy_tree(skill_dir, claude_root / "skills" / skill_dir.name)
        _copy_tree(skill_dir, cursor_root / skill_dir.name)
        _copy_tree(skill_dir, codex_root / skill_dir.name)

    hermes_synced = _sync_hermes_runtime()

    print("Synced user runtime:")
    print(f"  - Claude: {claude_root}")
    print(f"  - Cursor skills: {cursor_root}")
    print(f"  - Codex skills: {codex_root}")
    if hermes_synced:
        print(f"  - Hermes: {HOME / '.hermes'}")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def _list_runtime() -> None:
    claude_root = HOME / ".claude"

    print("=== Agents ===")
    agents_dir = claude_root / "agents"
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            print(f"  {f.stem}")
    else:
        print("  (none)")

    print("\n=== Skills ===")
    skills_dir = claude_root / "skills"
    managed = {p.name for p in _managed_skills()}
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir():
                tag = " [agent-os]" if d.name in managed else " [external]"
                print(f"  {d.name}{tag}")
    else:
        print("  (none)")

    print("\n=== Plugins ===")
    installed_json = claude_root / "plugins" / "installed_plugins.json"
    if installed_json.exists():
        data = json.loads(installed_json.read_text(encoding="utf-8"))
        for name in sorted(data.get("plugins", {}).keys()):
            print(f"  {name}")
    else:
        print("  (none)")

    print("\n=== Hooks (global settings.json) ===")
    settings_path = claude_root / "settings.json"
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        for event, entries in settings.get("hooks", {}).items():
            for entry in entries:
                matcher = entry.get("matcher", "*")
                for h in entry.get("hooks", []):
                    cmd = h.get("command", "")
                    short = cmd.split("/")[-1] if "/" in cmd else cmd
                    print(f"  {event} [{matcher}] → {short}")


# ---------------------------------------------------------------------------
# private-skill
# ---------------------------------------------------------------------------

def _private_skill_source(name: str) -> Path:
    return REPO_ROOT / "skills" / "private" / name


def _private_skill_install_path(name: str, tool: str) -> Path:
    if tool != "claude":
        raise ValueError(f"unsupported private skill tool: {tool}")
    return HOME / ".claude" / "skills" / name


def _private_skill(action: str, name: str, tool: str) -> int:
    if tool != "claude":
        print(f"Private skills currently support only Claude. Unsupported tool: {tool}", file=sys.stderr)
        return 1

    source = _private_skill_source(name)
    install_path = _private_skill_install_path(name, tool)
    source_skill = source / "SKILL.md"
    installed = install_path.exists()

    if action == "status":
        print(f"Private skill: {name}")
        print(f"Tool: {tool}")
        print(f"Source: {source}")
        print(f"Install path: {install_path}")
        print(f"Source status: {'present' if source_skill.exists() else 'missing SKILL.md'}")
        print(f"Installed: {'yes' if installed else 'no'}")
        return 0

    if not source_skill.exists():
        print(f"Private skill source missing: {source_skill}", file=sys.stderr)
        return 1

    if action == "enable":
        if install_path.exists():
            shutil.rmtree(install_path)
        _copy_tree(source, install_path)
        print(f"Enabled private skill '{name}' for {tool}: {install_path}")
        return 0

    if action == "disable":
        if install_path.exists():
            shutil.rmtree(install_path)
            print(f"Disabled private skill '{name}' for {tool}: removed {install_path}")
        else:
            print(f"Private skill '{name}' is already absent for {tool}: {install_path}")
        return 0

    print(f"Unsupported private-skill action: {action}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------

def _doctor() -> int:
    failures: list[str] = []
    print("Agent OS doctor")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Expected Conda root: {CONDA_ROOT}")

    conda_bin = CONDA_ROOT / "bin" / "conda"
    if not conda_bin.exists():
        failures.append(f"missing conda binary at {conda_bin}")
    else:
        print(f"[ok] conda binary: {conda_bin}")

    try:
        envs = _run([str(conda_bin), "info", "--envs"]).stdout
        if re.search(r"^base\s+", envs, re.MULTILINE):
            print("[ok] conda base environment exists")
        else:
            failures.append("conda base environment not found")
    except subprocess.CalledProcessError as exc:
        failures.append(f"failed to inspect conda envs: {exc}")

    try:
        probe = _run(
            [
                str(conda_bin),
                "run",
                "-n",
                "base",
                "python",
                "-c",
                "import json,sys; print(json.dumps({'executable': sys.executable, 'prefix': sys.prefix}))",
            ]
        ).stdout.strip()
        if probe:
            payload = json.loads(probe.splitlines()[-1])
            executable = payload["executable"]
            prefix = payload["prefix"]
            if EXPECTED_BASE_PREFIX not in executable or EXPECTED_BASE_PREFIX not in prefix:
                failures.append(
                    f"conda base python did not resolve under {EXPECTED_BASE_PREFIX}: "
                    f"executable={executable} prefix={prefix}"
                )
            else:
                print(f"[ok] conda base python: {executable}")
        else:
            failures.append("conda run probe returned no output")
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        failures.append(f"failed to run conda base python probe: {exc}")

    # Core tools — required on every machine
    for tool in ["claude", "git", "jq"]:
        if _command_exists(tool):
            print(f"[ok] tool available: {tool}")
        else:
            failures.append(f"missing tool: {tool}")

    # Local-only tools — expected on a dev workstation, not on remote servers or clusters
    for tool in ["cursor"]:
        if _command_exists(tool):
            print(f"[ok] tool available: {tool}")
        else:
            print(f"[info] local-only tool not installed: {tool} (not required on remote machines)")

    # Optional tools
    for tool in ["tmux", "gh", "codex"]:
        state = "present" if _command_exists(tool) else "not installed"
        print(f"[info] optional tool {tool}: {state}")

    if failures:
        print("\nDoctor failed:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("\nDoctor passed.")
    return 0


# ---------------------------------------------------------------------------
# worktree / start / validate / update
# ---------------------------------------------------------------------------

def _current_repo_root(cwd: Path) -> Path:
    try:
        output = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd).stdout.strip()
    except subprocess.CalledProcessError:
        return cwd.resolve()
    return Path(output)


def _resolve_bootstrap_target(path_arg: str) -> Path:
    candidate = Path(path_arg).expanduser()
    if path_arg == ".":
        return _current_repo_root(Path.cwd())
    return candidate.resolve()


def _worktree(task_type: str, task_name: list[str], base_ref: str | None, cwd: Path) -> int:
    repo_root = _current_repo_root(cwd)
    if not (repo_root / ".git").exists():
        print(f"Not a git repository: {repo_root}", file=sys.stderr)
        return 1

    slug = re.sub(r"[^a-z0-9]+", "-", " ".join(task_name).lower()).strip("-")
    if not slug:
        print("Unable to derive worktree slug.", file=sys.stderr)
        return 1

    branch_name = f"{task_type}/{slug}"
    parent_dir = repo_root.parent
    worktree_path = parent_dir / f"{repo_root.name}__{task_type}-{slug}"

    if not base_ref:
        base_ref = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root).stdout.strip()

    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0

    if branch_exists:
        _run(["git", "worktree", "add", str(worktree_path), branch_name], cwd=repo_root, capture_output=False)
    else:
        _run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_ref],
            cwd=repo_root,
            capture_output=False,
        )

    print(f"Created worktree: {worktree_path}")
    print(f"Branch: {branch_name}")
    return 0


def _start(tool: str, cwd: Path) -> int:
    if tool == "claude":
        os.execvp("claude", ["claude"])
    if tool == "cursor":
        os.execvp("cursor", ["cursor", str(cwd)])
    if tool == "codex":
        if _command_exists("codex"):
            os.execvp("codex", ["codex"])
        print("Codex CLI is not installed on PATH. Use Codex where available and rely on AGENTS.md plus synced skills.")
        return 1
    print(f"Unsupported tool: {tool}", file=sys.stderr)
    return 1


def _validate_manifest() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    all_declared = RUNTIME_MANIFEST["vendor_skills"] + RUNTIME_MANIFEST["custom_skills"]

    for bucket in ("vendor", "custom"):
        key = f"{bucket}_skills"
        for name in RUNTIME_MANIFEST[key]:
            skill_md = REPO_ROOT / "skills" / bucket / name / "SKILL.md"
            if not skill_md.exists():
                failures.append(f"[{bucket}] '{name}' declared in manifest but SKILL.md not found at {skill_md}")
            else:
                print(f"[ok] [{bucket}] {name}")

    for bucket in ("vendor", "custom"):
        bucket_dir = REPO_ROOT / "skills" / bucket
        if not bucket_dir.exists():
            continue
        for skill_dir in sorted(bucket_dir.iterdir()):
            if skill_dir.is_dir() and skill_dir.name not in all_declared:
                warnings.append(f"[{bucket}] '{skill_dir.name}' directory exists but is not in manifest")

    agents_dir = REPO_ROOT / "core" / "agents"
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            print(f"[ok] [agent] {f.stem}")
    else:
        failures.append("core/agents/ directory missing")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ! {w}")

    if failures:
        print("\nValidation failed:")
        for f in failures:
            print(f"  x {f}")
        return 1

    print("\nValidation passed.")
    return 0


def _update() -> int:
    if not (REPO_ROOT / ".git").exists():
        print("agent-os repo has no .git directory — cannot update.", file=sys.stderr)
        return 1
    try:
        result = _run(["git", "pull", "--ff-only"], cwd=REPO_ROOT, capture_output=False)
        return result.returncode
    except subprocess.CalledProcessError as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Harness system
# ---------------------------------------------------------------------------

def _load_harnesses() -> dict[str, dict]:
    """Load all harness definitions from core/harnesses/."""
    harnesses: dict[str, dict] = {}
    if not HARNESSES_DIR.exists():
        return harnesses
    for json_file in sorted(HARNESSES_DIR.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            harnesses[data["name"]] = data
        except (json.JSONDecodeError, KeyError):
            pass
    return harnesses


def _collect_project_signals(project_root: Path) -> tuple[str, set[str]]:
    """Return (dependency_text, directory_name_set) for a project root.

    Reads dependency/manifest files for import signatures, and walks one level
    of subdirectories for directory-name signals. Kept shallow and fast.
    """
    dep_files = [
        "requirements.txt", "requirements-dev.txt", "requirements_dev.txt",
        "pyproject.toml", "setup.py", "setup.cfg", "package.json",
        "Pipfile", "environment.yml", "environment.yaml",
    ]
    dep_parts: list[str] = []
    for name in dep_files:
        p = project_root / name
        if p.exists():
            try:
                dep_parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    dep_text = "\n".join(dep_parts).lower()

    dir_names: set[str] = set()
    try:
        for item in project_root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                dir_names.add(item.name)
                try:
                    for subitem in item.iterdir():
                        if subitem.is_dir() and not subitem.name.startswith("."):
                            dir_names.add(subitem.name)
                except OSError:
                    pass
    except OSError:
        pass

    return dep_text, dir_names


def _score_harness(
    harness: dict,
    project_root: Path,
    dep_text: str,
    dir_names: set[str],
) -> tuple[int, list[str]]:
    """Score a harness against collected project signals.

    Weights: import signature = 3, file pattern = 2, directory = 1, config file = 1.
    Returns (score, list_of_matched_signal_descriptions).
    """
    score = 0
    signals: list[str] = []
    detection = harness.get("detection", {})

    # Import signatures in dependency manifests — strongest signal
    for sig in detection.get("import_signatures", []):
        if sig.lower() in dep_text:
            score += 3
            signals.append(f"dependency: {sig}")

    # File patterns — concrete structural evidence (early-exit after 3 matches)
    for pattern in detection.get("file_patterns", []):
        matches: list[Path] = []
        try:
            for m in project_root.glob(pattern):
                matches.append(m)
                if len(matches) >= 3:
                    break
        except (OSError, ValueError):
            continue
        if matches:
            score += 2
            signals.append(f"file: {pattern} ({len(matches)}{'+ ' if len(matches) >= 3 else ' '}found)")

    # Directory names — contextual hint
    for dname in detection.get("directory_names", []):
        if dname in dir_names:
            score += 1
            signals.append(f"directory: {dname}/")

    # Config files at project root — specific but weak
    for config in detection.get("config_files", []):
        if (project_root / config).exists():
            score += 1
            signals.append(f"config: {config}")

    return score, signals


def _detect_project_harness(project_root: Path) -> list[tuple[str, int, list[str]]]:
    """Detect the most likely harness type for a project.

    Returns a list of (harness_name, score, signals) sorted by score descending,
    excluding the generic fallback (which is always available via `harness apply`).
    """
    harnesses = _load_harnesses()
    if not harnesses:
        return []
    dep_text, dir_names = _collect_project_signals(project_root)
    results: list[tuple[str, int, list[str]]] = []
    for name, harness in harnesses.items():
        if name == "generic":
            continue
        score, signals = _score_harness(harness, project_root, dep_text, dir_names)
        results.append((name, score, signals))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def _render_harness_md(harness: dict) -> str:
    """Render the HARNESS.md content for a given harness definition."""
    name = harness["name"]
    label = harness["label"]
    description = harness["description"]
    profile = harness["execution_profile"]
    profile_desc = harness.get("profile_description", "")
    workflow_notes = harness.get("workflow_notes", [])
    safety_notes = harness.get("safety_notes", [])
    agents = harness.get("recommended_agents", [])
    skills = harness.get("recommended_skills", [])

    lines: list[str] = [
        f"# Project Harness: {label}",
        "",
        f"Generated by `agent-os harness apply {name}`.",
        "Edit this file to customize the operating context for this project.",
        "",
        f"> {description}",
        "",
        "---",
        "",
        "## Execution Profile",
        "",
        f"`{profile}`" + (f" — {profile_desc}" if profile_desc else ""),
        "",
    ]

    if workflow_notes:
        lines += ["## Workflow Notes", ""]
        for note in workflow_notes:
            lines.append(f"- {note}")
        lines.append("")

    if safety_notes:
        lines += ["## Safety", ""]
        for note in safety_notes:
            lines.append(f"- {note}")
        lines.append("")

    if agents:
        lines += ["## Recommended Agents", ""]
        lines.append("`" + "` · `".join(agents) + "`")
        lines.append("")

    if skills:
        lines += ["## Recommended Skills", ""]
        lines.append("`" + "` · `".join(skills) + "`")
        lines.append("")

    return "\n".join(lines)


def _apply_harness_run_context(harness: dict, project_root: Path) -> bool:
    """Append harness-specific content to docs/RUN_CONTEXT.md if it exists.

    Skips silently if the file is absent or the section is already present.
    Returns True if the file was modified.
    """
    additions = harness.get("run_context_additions", [])
    if not additions:
        return False
    run_context_path = project_root / "docs" / "RUN_CONTEXT.md"
    if not run_context_path.exists():
        return False
    current = run_context_path.read_text(encoding="utf-8")
    header = next((line for line in additions if line.startswith("## ")), None)
    if header and header in current:
        return False
    extra = "\n" + "\n".join(additions) + "\n"
    _write_text(run_context_path, current.rstrip() + "\n" + extra)
    return True


def _apply_harness(harness_name: str, project_root: Path, *, force: bool = False) -> int:
    """Write HARNESS.md and extend RUN_CONTEXT.md for the given harness type."""
    harnesses = _load_harnesses()
    if harness_name not in harnesses:
        available = ", ".join(sorted(harnesses.keys()))
        print(f"Unknown harness: '{harness_name}'. Available: {available}", file=sys.stderr)
        return 1

    harness = harnesses[harness_name]
    harness_path = project_root / "HARNESS.md"

    if harness_path.exists() and not force:
        print(f"HARNESS.md already exists in {project_root}. Use --force to overwrite.")
        return 1

    _write_text(harness_path, _render_harness_md(harness))
    print(f"Applied harness '{harness_name}' to {project_root}")
    print(f"  - Created HARNESS.md")

    if _apply_harness_run_context(harness, project_root):
        print(f"  - Updated docs/RUN_CONTEXT.md with {harness_name} context")

    return 0


def _list_harnesses() -> None:
    harnesses = _load_harnesses()
    if not harnesses:
        print("No harnesses found in core/harnesses/")
        return
    print("Available harnesses:")
    print()
    for name, harness in sorted(harnesses.items()):
        description = harness.get("description", "")
        print(f"  {name:<22} {description}")
    print()
    print("Apply: agent-os harness apply <name> [path]")
    print("Detect best fit: agent-os detect [path]")


# ---------------------------------------------------------------------------
# Deterministic working-style profile system
# ---------------------------------------------------------------------------

PROFILE_DIMENSIONS = [
    "planning_strictness",
    "risk_tolerance",
    "testing_rigor",
    "parallelism_preference",
    "documentation_rigor",
    "automation_level",
]


def _profile_survey_questions() -> list[dict]:
    return [
        {
            "dimension": "planning_strictness",
            "question": "How structured is your planning before implementation?",
            "choices": [
                "I usually jump straight into implementation.",
                "I create a brief checklist first.",
                "I maintain staged plans for non-trivial work.",
                "I require explicit staged plans before major implementation.",
            ],
        },
        {
            "dimension": "risk_tolerance",
            "question": "How conservative should your default execution posture be?",
            "choices": [
                "Optimize for speed, tolerate more risk.",
                "Balanced speed and caution.",
                "Conservative by default, guardrails preferred.",
                "Strictly conservative; explicit review/approval gates.",
            ],
        },
        {
            "dimension": "testing_rigor",
            "question": "How strong should testing requirements be during normal work?",
            "choices": [
                "Run lightweight checks only.",
                "Run targeted tests for touched areas.",
                "Run comprehensive local tests before completion.",
                "Require robust verification and block completion on failures.",
            ],
        },
        {
            "dimension": "parallelism_preference",
            "question": "How much parallelization should be encouraged?",
            "choices": [
                "Mostly single-threaded, one active lane.",
                "Occasional parallel lanes for independent tasks.",
                "Frequent bounded parallel lanes with clear ownership.",
                "Strong preference for structured parallel work via worktrees.",
            ],
        },
        {
            "dimension": "documentation_rigor",
            "question": "How strictly should project memory docs be maintained?",
            "choices": [
                "Minimal notes, only when necessary.",
                "Keep core docs updated during milestones.",
                "Maintain requirements/plan/progress consistently.",
                "Treat docs as mandatory operating contract every session.",
            ],
        },
        {
            "dimension": "automation_level",
            "question": "How much deterministic automation should run by default?",
            "choices": [
                "Mostly manual execution.",
                "Basic formatting and helper automation.",
                "Strong automation for quality and consistency.",
                "Comprehensive deterministic automation with strict guardrails.",
            ],
        },
    ]


def _prompt_choice(question: str, choices: list[str]) -> int:
    while True:
        print()
        print(question)
        for idx, choice in enumerate(choices, start=1):
            print(f"  {idx}) {choice}")
        raw = input("Select 1-4: ").strip()
        if raw in {"1", "2", "3", "4"}:
            return int(raw)
        print("Invalid selection. Please enter 1, 2, 3, or 4.")


def _normalize_answers(answers: dict[str, int]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    parsed: dict[str, int] = {}

    for key, raw in answers.items():
        try:
            parsed[key] = int(raw)
        except (TypeError, ValueError):
            continue

    # If any answer is 0, interpret the whole payload as 0..3 scale and map to 1..4.
    # Otherwise interpret as 1..4 directly.
    zero_based_mode = any(value == 0 for value in parsed.values())

    for key, value in parsed.items():
        if zero_based_mode:
            if 0 <= value <= 3:
                normalized[key] = value + 1
        else:
            if 1 <= value <= 4:
                normalized[key] = value
    return normalized


def _load_answers_file(path: Path) -> dict[str, int]:
    if not path.exists():
        raise FileNotFoundError(f"answers file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in answers file: {path} ({exc})") from exc

    if not isinstance(payload, dict):
        raise ValueError("answers file must be a JSON object")

    # Support either top-level map or {"answers": {...}}
    if "answers" in payload and isinstance(payload["answers"], dict):
        payload = payload["answers"]

    return _normalize_answers(payload)


def _profile_survey(answers: dict[str, int] | None = None) -> dict:
    print("Deterministic workstyle survey")
    print("Answer each question with 1..4. Higher values mean stricter/more structured defaults.")

    normalized_answers = _normalize_answers(answers or {})

    responses: dict[str, dict] = {}
    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    for item in _profile_survey_questions():
        dim = item["dimension"]
        if dim in normalized_answers:
            choice_idx = normalized_answers[dim]
            print(f"[answers-file] {dim}: selected option {choice_idx}")
        else:
            choice_idx = _prompt_choice(item["question"], item["choices"])
        score = choice_idx - 1
        responses[dim] = {
            "question": item["question"],
            "selected_option": choice_idx,
            "selected_text": item["choices"][choice_idx - 1],
            "score": score,
        }
        scores[dim] = score
        evidence[dim] = [f"survey option {choice_idx}: {item['choices'][choice_idx - 1]}"]

    return {
        "source": "survey",
        "scores": scores,
        "responses": responses,
        "evidence": evidence,
    }


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _git_text(args: list[str], cwd: Path) -> str:
    try:
        return _run(args, cwd=cwd).stdout.strip().lower()
    except subprocess.CalledProcessError:
        return ""


def _detect_branch_prefix_count(project_root: Path) -> int:
    txt = _git_text(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], project_root)
    if not txt:
        return 0
    prefixes = ("feat/", "fix/", "docs/", "research/", "ops/")
    count = 0
    for line in txt.splitlines():
        if any(line.startswith(prefix) for prefix in prefixes):
            count += 1
    return count


def _project_has_tests(project_root: Path) -> bool:
    tests_dir = project_root / "tests"
    if tests_dir.exists() and tests_dir.is_dir():
        return True
    for pattern in ("test_*.py", "*_test.py", "*.spec.ts", "*.test.ts", "*.test.js"):
        try:
            if any(project_root.rglob(pattern)):
                return True
        except OSError:
            continue
    return False


def _project_has_ci(project_root: Path) -> bool:
    workflows = project_root / ".github" / "workflows"
    if not workflows.exists():
        return False
    try:
        return any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml"))
    except OSError:
        return False


def _score_from_flags(flags: list[tuple[bool, str]]) -> tuple[int, list[str]]:
    score = 0
    evidence: list[str] = []
    for is_true, message in flags:
        if is_true:
            score += 1
            evidence.append(message)
    return min(3, score), evidence


def _profile_infer(project_root: Path) -> dict:
    docs_files = [
        project_root / "docs" / "REQUIREMENTS.md",
        project_root / "docs" / "PLAN.md",
        project_root / "docs" / "PROGRESS.md",
        project_root / "docs" / "NEXT_STEPS.md",
    ]
    docs_present = sum(1 for p in docs_files if p.exists())
    docs_dir_exists = (project_root / "docs").exists()
    tests_present = _project_has_tests(project_root)
    ci_present = _project_has_ci(project_root)
    branch_prefix_count = _detect_branch_prefix_count(project_root)

    commit_text = _git_text(["git", "log", "--oneline", "-n", "120"], project_root)
    agents_text = _safe_read_text(project_root / "AGENTS.md").lower()
    claude_settings_text = _safe_read_text(project_root / ".claude" / "settings.json")

    settings_has_hooks = False
    settings_has_deny = False
    if claude_settings_text:
        try:
            parsed = json.loads(claude_settings_text)
            settings_has_hooks = bool(parsed.get("hooks"))
            settings_has_deny = bool(parsed.get("permissions", {}).get("deny"))
        except json.JSONDecodeError:
            pass

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    scores["planning_strictness"], evidence["planning_strictness"] = _score_from_flags([
        (docs_present >= 2 and (project_root / "docs" / "PLAN.md").exists() and (project_root / "docs" / "NEXT_STEPS.md").exists(), "PLAN and NEXT_STEPS detected"),
        (docs_present >= 4, "full staged docs set detected (REQUIREMENTS/PLAN/PROGRESS/NEXT_STEPS)"),
        ("plan" in commit_text or "phase" in commit_text or "milestone" in commit_text, "commit history references planning/milestones"),
    ])

    scores["risk_tolerance"], evidence["risk_tolerance"] = _score_from_flags([
        ("review gate" in agents_text or "no unattended" in agents_text or "guardrail" in agents_text, "AGENTS.md includes guardrail/review language"),
        (settings_has_deny, ".claude/settings.json contains deny permissions"),
        ("review" in commit_text or "safety" in commit_text or "guard" in commit_text, "commit history includes review/safety signals"),
    ])

    scores["testing_rigor"], evidence["testing_rigor"] = _score_from_flags([
        (tests_present, "test files/directories detected"),
        (ci_present, "CI workflow detected"),
        ("test" in commit_text or "pytest" in commit_text or "jest" in commit_text, "commit history includes test activity"),
    ])

    scores["parallelism_preference"], evidence["parallelism_preference"] = _score_from_flags([
        (branch_prefix_count >= 1, "task-style branch prefixes detected"),
        ("worktree" in agents_text or "one bounded task per worktree" in agents_text, "AGENTS.md references worktree-based parallelism"),
        (branch_prefix_count >= 3 or "worktree" in commit_text, "strong branch/worktree parallelism evidence"),
    ])

    scores["documentation_rigor"], evidence["documentation_rigor"] = _score_from_flags([
        (docs_dir_exists, "docs/ directory exists"),
        (docs_present >= 3, "3+ canonical docs present"),
        ("docs" in commit_text or "readme" in commit_text, "commit history includes documentation changes"),
    ])

    scores["automation_level"], evidence["automation_level"] = _score_from_flags([
        (settings_has_hooks, ".claude/settings.json has hooks configured"),
        (ci_present, "CI automation detected"),
        (("hook" in commit_text or "automation" in commit_text or "checkpoint" in commit_text), "commit history includes automation/hook signals"),
    ])

    return {
        "source": "infer",
        "project_root": str(project_root),
        "scores": scores,
        "evidence": evidence,
        "signals": {
            "docs_present": docs_present,
            "tests_present": tests_present,
            "ci_present": ci_present,
            "branch_prefix_count": branch_prefix_count,
            "settings_has_hooks": settings_has_hooks,
            "settings_has_deny": settings_has_deny,
        },
    }


def _profile_hybrid(project_root: Path, answers: dict[str, int] | None = None) -> dict:
    survey = _profile_survey(answers=answers)
    inferred = _profile_infer(project_root)

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}
    for dim in PROFILE_DIMENSIONS:
        s = survey["scores"][dim]
        i = inferred["scores"][dim]
        blended = int((0.6 * s + 0.4 * i) + 0.5)
        if blended < 0:
            blended = 0
        if blended > 3:
            blended = 3
        scores[dim] = blended
        evidence[dim] = [
            f"hybrid blend: survey={s}, infer={i}, weighted=0.6/0.4 => {blended}",
            *survey.get("evidence", {}).get(dim, []),
            *inferred.get("evidence", {}).get(dim, []),
        ]

    return {
        "source": "hybrid",
        "scores": scores,
        "evidence": evidence,
        "survey": survey,
        "infer": inferred,
    }


def _render_workstyle_explanations(mode: str, payload: dict) -> str:
    scores = payload.get("scores", {})
    evidence = payload.get("evidence", {})
    lines = [
        "# Workstyle Explanations",
        "",
        f"Mode: `{mode}`",
        f"Date: `{_today()}`",
        "",
        "## Score Table",
        "",
        "| Dimension | Score (0-3) |",
        "|---|---|",
    ]
    for dim in PROFILE_DIMENSIONS:
        lines.append(f"| {dim} | {scores.get(dim, 0)} |")
    lines += ["", "## Evidence", ""]
    for dim in PROFILE_DIMENSIONS:
        lines.append(f"### {dim}")
        items = evidence.get(dim, [])
        if not items:
            lines.append("- no explicit evidence captured")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def _compile_operator_profile(scores: dict[str, int], mode: str) -> str:
    planning = scores.get("planning_strictness", 0)
    risk = scores.get("risk_tolerance", 0)
    testing = scores.get("testing_rigor", 0)
    parallel = scores.get("parallelism_preference", 0)
    docs = scores.get("documentation_rigor", 0)
    automation = scores.get("automation_level", 0)

    return "\n".join([
        "# Operator Profile",
        "",
        f"Generated by `agent-os profile {mode}` on {_today()}.",
        "This file captures deterministic working-style preferences for cross-tool runtime behavior.",
        "",
        "## Deterministic Workstyle Scorecard (0-3)",
        "",
        f"- planning_strictness: {planning}",
        f"- risk_tolerance: {risk}",
        f"- testing_rigor: {testing}",
        f"- parallelism_preference: {parallel}",
        f"- documentation_rigor: {docs}",
        f"- automation_level: {automation}",
        "",
        "## Working Style Summary",
        "",
        f"- Planning posture: {'strict staged planning' if planning >= 3 else 'structured planning' if planning >= 2 else 'light planning' if planning >= 1 else 'implementation-first'}.",
        f"- Risk posture: {'highly conservative with strong guardrails' if risk >= 3 else 'conservative default' if risk >= 2 else 'balanced speed/caution' if risk >= 1 else 'speed-prioritized'}.",
        f"- Testing posture: {'completion-blocking quality checks preferred' if testing >= 3 else 'strong test validation before completion' if testing >= 2 else 'targeted test checks' if testing >= 1 else 'minimal smoke validation'}.",
        f"- Parallelism posture: {'structured multi-lane worktree execution' if parallel >= 3 else 'bounded parallel lanes when useful' if parallel >= 2 else 'occasional parallel work' if parallel >= 1 else 'single-lane execution preference'}.",
        f"- Documentation posture: {'docs-first operating contract each session' if docs >= 3 else 'consistent canonical docs maintenance' if docs >= 2 else 'milestone-level docs updates' if docs >= 1 else 'minimal documentation'}.",
        f"- Automation posture: {'comprehensive deterministic automation with guardrails' if automation >= 3 else 'high automation for quality/consistency' if automation >= 2 else 'basic helper automation' if automation >= 1 else 'manual-first operations'}.",
        "",
    ])


def _compile_workflow_policy(scores: dict[str, int], mode: str) -> str:
    planning = scores.get("planning_strictness", 0)
    risk = scores.get("risk_tolerance", 0)
    testing = scores.get("testing_rigor", 0)
    parallel = scores.get("parallelism_preference", 0)
    docs = scores.get("documentation_rigor", 0)
    automation = scores.get("automation_level", 0)

    flow = ["Explore", "Plan", "Implement", "Review", "Handoff"]
    if planning >= 2:
        flow.insert(2, "Validate plan against constraints")

    lines = [
        "# Workflow Policy",
        "",
        f"Generated by `agent-os profile {mode}` on {_today()}.",
        "Deterministic policy compiled from the workstyle scorecard.",
        "",
        "## Standard Flow",
    ]
    for i, step in enumerate(flow, start=1):
        lines.append(f"{i}. {step}")

    lines += [
        "",
        "## Project Memory",
        "- Canonical project truth lives in `docs/` and `AGENTS.md`.",
        "- Tool-native memory is acceleration only, not source of truth.",
        "",
        "## Planning Policy",
    ]
    if planning >= 3:
        lines += [
            "- Require staged plan updates in `docs/PLAN.md` before major implementation.",
            "- Large tasks should be decomposed into bounded steps before execution.",
        ]
    elif planning >= 2:
        lines += ["- Keep staged execution notes in `docs/PLAN.md` for non-trivial work."]
    elif planning >= 1:
        lines += ["- Maintain at least a short plan/checklist before substantial edits."]
    else:
        lines += ["- Planning is lightweight; prefer fast iteration with explicit checkpoints."]

    lines += ["", "## Risk and Safety Policy"]
    if risk >= 3:
        lines += [
            "- Use strict guardrails and review gates for risky changes.",
            "- Avoid destructive operations without explicit confirmation.",
        ]
    elif risk >= 2:
        lines += ["- Conservative default: review critical changes before merge."]
    elif risk >= 1:
        lines += ["- Balanced posture: apply guardrails to high-impact operations."]
    else:
        lines += ["- Speed-first posture; still preserve baseline destructive-command protections."]

    lines += ["", "## Testing Policy"]
    if testing >= 3:
        lines += ["- Block completion when required tests fail."]
    elif testing >= 2:
        lines += ["- Run comprehensive relevant tests before completion."]
    elif testing >= 1:
        lines += ["- Run targeted smoke tests for changed areas."]
    else:
        lines += ["- Use minimal validation for rapid iteration."]

    lines += ["", "## Parallel Work Policy"]
    if parallel >= 3:
        lines += ["- Prefer bounded task parallelism via worktrees with one owner per lane."]
    elif parallel >= 2:
        lines += ["- Use parallel lanes for independent bounded tasks."]
    elif parallel >= 1:
        lines += ["- Use parallel work occasionally when risk is low and ownership is clear."]
    else:
        lines += ["- Prefer single active lane to reduce coordination overhead."]

    lines += ["", "## Documentation Policy"]
    if docs >= 3:
        lines += ["- Treat docs updates (`PLAN`, `PROGRESS`, `NEXT_STEPS`) as mandatory every substantial session."]
    elif docs >= 2:
        lines += ["- Keep canonical docs consistently updated through milestones."]
    elif docs >= 1:
        lines += ["- Update docs at major checkpoints."]
    else:
        lines += ["- Keep concise docs; expand only when complexity grows."]

    lines += ["", "## Automation Policy"]
    if automation >= 3:
        lines += ["- Enable comprehensive deterministic automation with strict guardrails."]
    elif automation >= 2:
        lines += ["- Use strong automation for formatting, testing, and quality checks."]
    elif automation >= 1:
        lines += ["- Use basic helper automation while keeping critical decisions manual."]
    else:
        lines += ["- Prefer manual control and minimal automation."]

    lines += [
        "",
        "## Local Integration",
        "After updating global memory files, run:",
        "1. `agent-os sync`",
        "2. `agent-os doctor`",
        "",
    ]
    return "\n".join(lines)


def _write_workstyle_artifacts(mode: str, payload: dict) -> tuple[Path, Path, Path]:
    GENERATED_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    profile_path = GENERATED_PROFILE_DIR / "workstyle_profile.json"
    scores_path = GENERATED_PROFILE_DIR / "workstyle_scores.json"
    explain_path = GENERATED_PROFILE_DIR / "workstyle_explanations.md"

    profile_payload = {
        "mode": mode,
        "generated_on": _today(),
        **payload,
    }
    score_payload = {
        "mode": mode,
        "generated_on": _today(),
        "scores": payload.get("scores", {}),
    }

    _write_text(profile_path, json.dumps(profile_payload, indent=2) + "\n")
    _write_text(scores_path, json.dumps(score_payload, indent=2) + "\n")
    _write_text(explain_path, _render_workstyle_explanations(mode, payload) + "\n")
    return profile_path, scores_path, explain_path


def _write_compiled_memory(mode: str, payload: dict, *, overwrite: bool) -> None:
    scores = payload.get("scores", {})
    operator_path = GLOBAL_MEMORY_DIR / "operator_profile.md"
    workflow_path = GLOBAL_MEMORY_DIR / "workflow_policy.md"

    compiled_operator = _compile_operator_profile(scores, mode)
    compiled_workflow = _compile_workflow_policy(scores, mode)

    for target, content in ((operator_path, compiled_operator), (workflow_path, compiled_workflow)):
        if target.exists() and not overwrite:
            print(f"Skipped existing file (use --overwrite): {target}")
            continue
        _write_text(target, content + ("" if content.endswith("\n") else "\n"))
        print(f"Wrote: {target}")


def _print_profile_summary(mode: str, payload: dict) -> None:
    scores = payload.get("scores", {})
    print()
    print(f"Workstyle profile summary ({mode})")
    for dim in PROFILE_DIMENSIONS:
        print(f"  - {dim:<24} {scores.get(dim, 0)}")

    evidence = payload.get("evidence", {})
    print()
    print("Key evidence:")
    for dim in PROFILE_DIMENSIONS:
        dim_evidence = evidence.get(dim, [])
        if dim_evidence:
            print(f"  {dim}: {dim_evidence[0]}")


def _profile_show() -> int:
    scores_path = GENERATED_PROFILE_DIR / "workstyle_scores.json"
    profile_path = GENERATED_PROFILE_DIR / "workstyle_profile.json"
    explain_path = GENERATED_PROFILE_DIR / "workstyle_explanations.md"

    if not scores_path.exists():
        print("No generated workstyle profile found.")
        print("Run: agent-os profile survey --write")
        return 1

    try:
        data = json.loads(scores_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Could not parse: {scores_path}", file=sys.stderr)
        return 1

    print(f"Mode: {data.get('mode', 'unknown')}")
    print(f"Generated: {data.get('generated_on', 'unknown')}")
    print()
    for dim in PROFILE_DIMENSIONS:
        print(f"  - {dim:<24} {data.get('scores', {}).get(dim, 0)}")
    print()
    print("Artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {scores_path}")
    print(f"  - {explain_path}")
    return 0


COGNITIVE_DIMENSIONS = [
    "first_principles_depth",
    "exploration_breadth",
    "speed_vs_rigor_balance",
    "challenge_orientation",
    "uncertainty_tolerance",
    "autonomy_preference",
]


def _cognition_questions() -> list[dict]:
    return [
        {
            "dimension": "first_principles_depth",
            "question": "When solving complex problems, how deeply should reasoning decompose assumptions?",
            "choices": [
                "Prefer quick practical heuristics.",
                "Use light root-cause analysis when needed.",
                "Usually decompose to core assumptions.",
                "Strong first-principles decomposition by default.",
            ],
        },
        {
            "dimension": "exploration_breadth",
            "question": "How many alternative options should be explored before committing?",
            "choices": [
                "Pick first viable path and move.",
                "Compare 1-2 alternatives.",
                "Evaluate multiple plausible options.",
                "Systematically explore a broad option set.",
            ],
        },
        {
            "dimension": "speed_vs_rigor_balance",
            "question": "What is your default trade-off between speed and analytical rigor?",
            "choices": [
                "Prioritize speed; minimal analysis overhead.",
                "Lean speed with selective rigor.",
                "Balanced speed and rigor.",
                "Rigor-first for most meaningful decisions.",
            ],
        },
        {
            "dimension": "challenge_orientation",
            "question": "How adversarial should idea review be?",
            "choices": [
                "Low challenge; preserve flow and momentum.",
                "Moderate challenge on important decisions.",
                "Frequent structured critique of assumptions.",
                "Strong devil’s-advocate stress testing by default.",
            ],
        },
        {
            "dimension": "uncertainty_tolerance",
            "question": "How should the system operate under ambiguity?",
            "choices": [
                "Proceed quickly with minimal uncertainty framing.",
                "Proceed with lightweight assumptions.",
                "State assumptions and confidence explicitly.",
                "Require explicit uncertainty and failure-mode analysis.",
            ],
        },
        {
            "dimension": "autonomy_preference",
            "question": "How autonomous should agent execution be by default?",
            "choices": [
                "Human-in-the-loop for most actions.",
                "Moderate autonomy with frequent checkpoints.",
                "High autonomy within bounded constraints.",
                "Very high autonomy with strict deterministic boundaries.",
            ],
        },
    ]


def _cognition_survey(answers: dict[str, int] | None = None) -> dict:
    print("Deterministic cognitive-style survey")
    print("Answer each question with 1..4. Higher values represent stronger structured cognitive posture.")

    normalized_answers = _normalize_answers(answers or {})

    responses: dict[str, dict] = {}
    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    for item in _cognition_questions():
        dim = item["dimension"]
        if dim in normalized_answers:
            choice_idx = normalized_answers[dim]
            print(f"[answers-file] {dim}: selected option {choice_idx}")
        else:
            choice_idx = _prompt_choice(item["question"], item["choices"])
        score = choice_idx - 1
        responses[dim] = {
            "question": item["question"],
            "selected_option": choice_idx,
            "selected_text": item["choices"][choice_idx - 1],
            "score": score,
        }
        scores[dim] = score
        evidence[dim] = [f"survey option {choice_idx}: {item['choices'][choice_idx - 1]}"]

    return {
        "source": "cognitive_survey",
        "scores": scores,
        "responses": responses,
        "evidence": evidence,
    }


def _render_cognitive_explanations(payload: dict) -> str:
    scores = payload.get("scores", {})
    evidence = payload.get("evidence", {})
    lines = [
        "# Cognitive Profile Explanations",
        "",
        f"Date: `{_today()}`",
        "",
        "## Score Table",
        "",
        "| Dimension | Score (0-3) |",
        "|---|---|",
    ]
    for dim in COGNITIVE_DIMENSIONS:
        lines.append(f"| {dim} | {scores.get(dim, 0)} |")
    lines += ["", "## Evidence", ""]
    for dim in COGNITIVE_DIMENSIONS:
        lines.append(f"### {dim}")
        items = evidence.get(dim, [])
        if not items:
            lines.append("- no explicit evidence captured")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def _compile_cognitive_profile(scores: dict[str, int]) -> str:
    fpd = scores.get("first_principles_depth", 0)
    exp = scores.get("exploration_breadth", 0)
    svr = scores.get("speed_vs_rigor_balance", 0)
    cho = scores.get("challenge_orientation", 0)
    unt = scores.get("uncertainty_tolerance", 0)
    aut = scores.get("autonomy_preference", 0)

    return "\n".join([
        "# Cognitive Profile",
        "",
        f"Generated by `agent-os cognition survey` on {_today()}.",
        "Deterministic cognitive and philosophical operating profile.",
        "",
        "## Cognitive Scorecard (0-3)",
        f"- first_principles_depth: {fpd}",
        f"- exploration_breadth: {exp}",
        f"- speed_vs_rigor_balance: {svr}",
        f"- challenge_orientation: {cho}",
        f"- uncertainty_tolerance: {unt}",
        f"- autonomy_preference: {aut}",
        "",
        "## Philosophy of Work",
        f"- Reasoning depth posture: {'first-principles dominant' if fpd >= 3 else 'frequent first-principles decomposition' if fpd >= 2 else 'balanced decomposition/heuristics' if fpd >= 1 else 'heuristic-first'}.",
        f"- Option strategy: {'broad exploratory option search' if exp >= 3 else 'multi-option evaluation' if exp >= 2 else 'few-option comparison' if exp >= 1 else 'single viable path bias'}.",
        f"- Speed-rigor balance: {'rigor-first' if svr >= 3 else 'balanced with rigor lean' if svr >= 2 else 'speed-lean with checks' if svr >= 1 else 'speed-first'}.",
        "",
        "## Decision Attitude",
        f"- Challenge style: {'strong adversarial stress-testing' if cho >= 3 else 'structured critique encouraged' if cho >= 2 else 'moderate challenge when important' if cho >= 1 else 'low-friction consensus style'}.",
        f"- Uncertainty handling: {'explicit uncertainty + failure-mode analysis required' if unt >= 3 else 'explicit assumptions/confidence expected' if unt >= 2 else 'light assumption framing' if unt >= 1 else 'low-friction proceed posture'}.",
        f"- Autonomy posture: {'high autonomy with strict deterministic bounds' if aut >= 3 else 'high bounded autonomy' if aut >= 2 else 'moderate autonomy with checkpoints' if aut >= 1 else 'human-in-the-loop dominant'}.",
        "",
    ])


def _write_cognitive_artifacts(mode: str, payload: dict) -> tuple[Path, Path]:
    GENERATED_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = GENERATED_PROFILE_DIR / "cognitive_profile.json"
    explain_path = GENERATED_PROFILE_DIR / "cognitive_explanations.md"

    packed = {
        "mode": mode,
        "generated_on": _today(),
        **payload,
    }
    _write_text(profile_path, json.dumps(packed, indent=2) + "\n")
    _write_text(explain_path, _render_cognitive_explanations(payload) + "\n")
    return profile_path, explain_path


def _cognition_infer(project_root: Path) -> dict:
    docs_files = [
        project_root / "docs" / "REQUIREMENTS.md",
        project_root / "docs" / "PLAN.md",
        project_root / "docs" / "PROGRESS.md",
        project_root / "docs" / "NEXT_STEPS.md",
    ]
    docs_present = sum(1 for p in docs_files if p.exists())
    docs_dir_exists = (project_root / "docs").exists()
    ci_present = _project_has_ci(project_root)

    commit_text = _git_text(["git", "log", "--oneline", "-n", "120"], project_root)
    branch_text = _git_text(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], project_root)
    agents_text = _safe_read_text(project_root / "AGENTS.md").lower()
    plan_text = _safe_read_text(project_root / "docs" / "PLAN.md").lower()
    req_text = _safe_read_text(project_root / "docs" / "REQUIREMENTS.md").lower()
    settings_text = _safe_read_text(project_root / ".claude" / "settings.json")

    settings_has_hooks = False
    settings_has_deny = False
    if settings_text:
        try:
            parsed = json.loads(settings_text)
            settings_has_hooks = bool(parsed.get("hooks"))
            settings_has_deny = bool(parsed.get("permissions", {}).get("deny"))
        except json.JSONDecodeError:
            pass

    manifest_text = _safe_read_text(REPO_ROOT / "core" / "runtime_manifest.json").lower()

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}

    scores["first_principles_depth"], evidence["first_principles_depth"] = _score_from_flags([
        ("assumption" in agents_text or "first-principles" in agents_text, "AGENTS.md references assumptions/first-principles reasoning"),
        ("root cause" in commit_text or "analysis" in commit_text or "rationale" in commit_text, "commit history references analytical decomposition"),
        ("why" in plan_text or "assumption" in plan_text, "PLAN.md contains rationale/assumption language"),
    ])

    scores["exploration_breadth"], evidence["exploration_breadth"] = _score_from_flags([
        ("option" in plan_text or "alternative" in plan_text, "PLAN.md references options/alternatives"),
        ("research/" in branch_text, "research branch prefix detected"),
        ("explore" in agents_text or "research" in agents_text, "AGENTS.md references exploration workflow"),
    ])

    scores["speed_vs_rigor_balance"], evidence["speed_vs_rigor_balance"] = _score_from_flags([
        (docs_present >= 3 and ci_present, "docs discipline + CI suggests balanced rigor"),
        ("review" in commit_text or "validate" in commit_text, "commit history includes validation/review language"),
        ("smallest useful verification" in agents_text or "review gate" in agents_text, "AGENTS.md includes verification controls"),
    ])

    scores["challenge_orientation"], evidence["challenge_orientation"] = _score_from_flags([
        ("review gate" in agents_text or "review required" in agents_text, "AGENTS.md requires review gates"),
        ("swing-review" in manifest_text, "runtime manifest includes adversarial review skill"),
        ("review" in commit_text or "critique" in commit_text, "commit history includes review-oriented activity"),
    ])

    scores["uncertainty_tolerance"], evidence["uncertainty_tolerance"] = _score_from_flags([
        ("constraint" in plan_text or "risk" in plan_text, "PLAN.md includes constraints/risks"),
        ("non-goal" in req_text, "REQUIREMENTS.md includes explicit non-goals"),
        (docs_dir_exists, "docs discipline suggests explicit uncertainty handling"),
    ])

    scores["autonomy_preference"], evidence["autonomy_preference"] = _score_from_flags([
        (settings_has_hooks, "tool hooks configured (bounded automation)"),
        ("bounded" in agents_text or "human review checkpoint" in agents_text, "AGENTS.md uses bounded automation language"),
        (settings_has_deny or ci_present, "guardrails/CI indicate controlled autonomy"),
    ])

    return {
        "source": "cognitive_infer",
        "project_root": str(project_root),
        "scores": scores,
        "evidence": evidence,
        "signals": {
            "docs_present": docs_present,
            "docs_dir_exists": docs_dir_exists,
            "ci_present": ci_present,
            "settings_has_hooks": settings_has_hooks,
            "settings_has_deny": settings_has_deny,
        },
    }


def _cognition_hybrid(project_root: Path, answers: dict[str, int] | None = None) -> dict:
    survey = _cognition_survey(answers=answers)
    inferred = _cognition_infer(project_root)

    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}
    for dim in COGNITIVE_DIMENSIONS:
        s = survey["scores"][dim]
        i = inferred["scores"][dim]
        blended = int((0.6 * s + 0.4 * i) + 0.5)
        blended = max(0, min(3, blended))
        scores[dim] = blended
        evidence[dim] = [
            f"hybrid blend: survey={s}, infer={i}, weighted=0.6/0.4 => {blended}",
            *survey.get("evidence", {}).get(dim, []),
            *inferred.get("evidence", {}).get(dim, []),
        ]

    return {
        "source": "cognitive_hybrid",
        "scores": scores,
        "evidence": evidence,
        "survey": survey,
        "infer": inferred,
    }


def _cognition_show() -> int:
    profile_path = GENERATED_PROFILE_DIR / "cognitive_profile.json"
    explain_path = GENERATED_PROFILE_DIR / "cognitive_explanations.md"
    if not profile_path.exists():
        print("No generated cognitive profile found.")
        print("Run: agent-os cognition survey --write")
        return 1
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Could not parse: {profile_path}", file=sys.stderr)
        return 1

    print(f"Generated: {data.get('generated_on', 'unknown')}")
    print()
    for dim in COGNITIVE_DIMENSIONS:
        print(f"  - {dim:<24} {data.get('scores', {}).get(dim, 0)}")
    print()
    print("Artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {explain_path}")
    return 0


def _cognition_command(
    action: str,
    path_arg: str | None,
    *,
    write: bool,
    overwrite: bool,
    answers: dict[str, int] | None = None,
) -> int:
    if action == "show":
        return _cognition_show()

    project_root = _resolve_bootstrap_target(path_arg or ".")

    if action == "survey":
        payload = _cognition_survey(answers=answers)
        mode = "survey"
    elif action == "infer":
        payload = _cognition_infer(project_root)
        mode = "infer"
    elif action == "hybrid":
        payload = _cognition_hybrid(project_root, answers=answers)
        mode = "hybrid"
    else:
        print(f"Unsupported cognition action: {action}", file=sys.stderr)
        return 1

    profile_path, explain_path = _write_cognitive_artifacts(mode, payload)

    print()
    print(f"Cognitive profile summary ({mode})")
    for dim in COGNITIVE_DIMENSIONS:
        print(f"  - {dim:<24} {payload.get('scores', {}).get(dim, 0)}")

    print()
    print("Wrote generated artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {explain_path}")

    if write:
        target = GLOBAL_MEMORY_DIR / "cognitive_profile.md"
        content = _compile_cognitive_profile(payload.get("scores", {}))
        if target.exists() and not overwrite:
            print(f"Skipped existing file (use --overwrite): {target}")
        else:
            _write_text(target, content + ("" if content.endswith("\n") else "\n"))
            print(f"Wrote: {target}")
        print()
        print("Next steps for local integration:")
        print("  1) agent-os sync")
        print("  2) agent-os doctor")
    else:
        print()
        print("Run with --write to compile cognitive profile into global memory markdown.")

    return 0


def _profile_command(
    mode: str,
    path_arg: str | None,
    *,
    write: bool,
    overwrite: bool,
    answers: dict[str, int] | None = None,
) -> int:
    project_root = _resolve_bootstrap_target(path_arg or ".")

    if mode == "survey":
        payload = _profile_survey(answers=answers)
    elif mode == "infer":
        payload = _profile_infer(project_root)
    elif mode == "hybrid":
        payload = _profile_hybrid(project_root, answers=answers)
    else:
        print(f"Unsupported profile mode: {mode}", file=sys.stderr)
        return 1

    profile_path, scores_path, explain_path = _write_workstyle_artifacts(mode, payload)
    _print_profile_summary(mode, payload)
    print()
    print("Wrote generated artifacts:")
    print(f"  - {profile_path}")
    print(f"  - {scores_path}")
    print(f"  - {explain_path}")

    if write:
        print()
        _write_compiled_memory(mode, payload, overwrite=overwrite)
        print()
        print("Next steps for local integration:")
        print("  1) agent-os sync")
        print("  2) agent-os doctor")
    else:
        print()
        print("Run with --write to compile scores into global memory markdown files.")

    return 0


# ---------------------------------------------------------------------------
# bootstrap / new-project
# ---------------------------------------------------------------------------

def _bootstrap_project(project_root: Path, *, harness_name: str | None = None) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    mapping = _machine_context()
    mapping["PROJECT_ROOT"] = str(project_root)

    template_files = [
        "AGENTS.md",
        "CLAUDE.md",
        "docs/REQUIREMENTS.md",
        "docs/PLAN.md",
        "docs/PROGRESS.md",
        "docs/RUN_CONTEXT.md",
        "docs/NEXT_STEPS.md",
        ".claude/settings.json",
    ]
    created: list[str] = []
    preserved: list[str] = []
    for rel_path in template_files:
        target = project_root / rel_path
        if target.exists():
            preserved.append(rel_path)
            continue
        content = _replace_tokens(_load_template(rel_path), mapping)
        _write_text(target, content)
        created.append(rel_path)

    settings_local = project_root / ".claude" / "settings.local.json"
    if not settings_local.exists():
        _write_text(settings_local, "{}\n")
        created.append(".claude/settings.local.json")

    gitignore_path = project_root / ".gitignore"
    ignore_line = ".claude/settings.local.json"
    if gitignore_path.exists():
        current = gitignore_path.read_text(encoding="utf-8")
        if ignore_line not in current.splitlines():
            extra = current + ("\n" if not current.endswith("\n") else "") + ignore_line + "\n"
            _write_text(gitignore_path, extra)
    else:
        _write_text(gitignore_path, ignore_line + "\n")
        created.append(".gitignore")

    print(f"Bootstrapped project scaffold in {project_root}")
    if created:
        print("Created:")
        for item in created:
            print(f"  - {item}")
    if preserved:
        print("Preserved existing:")
        for item in preserved:
            print(f"  - {item}")

    # Harness: auto-detect or apply named harness
    if harness_name:
        resolved = harness_name
        if harness_name == "auto":
            results = _detect_project_harness(project_root)
            if results and results[0][1] > 2:
                resolved = results[0][0]
                print(f"\nAuto-detected harness: {resolved} (score {results[0][1]})")
            else:
                resolved = "generic"
                print("\nNo strong harness signal detected — applying generic.")
        print()
        _apply_harness(resolved, project_root)


# ---------------------------------------------------------------------------
# Parser and main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent OS cross-tool runtime manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Bootstrap personal memory files from *.example.md templates")
    sub.add_parser("doctor", help="Verify runtime wiring — Conda, core tools, optional tools")
    sub.add_parser("sync", help="Sync managed runtime assets into Claude, Codex, Cursor, and Hermes")
    sub.add_parser("update", help="Pull the latest agent-os from git")
    sub.add_parser("list", help="Show installed agents, skills, plugins, and active hooks")
    sub.add_parser("validate", help="Check manifest integrity — every declared skill must have a SKILL.md")

    for cmd in ("bootstrap", "new-project"):
        p = sub.add_parser(cmd, help="Scaffold the standard project structure")
        p.add_argument("path", nargs="?", default=".")
        p.add_argument(
            "--harness",
            metavar="TYPE",
            help="Apply a harness after scaffolding. Use 'auto' to detect from repo contents.",
        )

    detect = sub.add_parser("detect", help="Detect the best harness type for a project")
    detect.add_argument("path", nargs="?", default=".")

    harness_cmd = sub.add_parser("harness", help="Manage project harnesses")
    harness_sub = harness_cmd.add_subparsers(dest="harness_action", required=True)
    harness_sub.add_parser("list", help="List available harness types")
    h_apply = harness_sub.add_parser("apply", help="Apply a harness to a project")
    h_apply.add_argument("type", help="Harness type (ml-research, python-library, web-app, data-pipeline, generic)")
    h_apply.add_argument("path", nargs="?", default=".")
    h_apply.add_argument("--force", action="store_true", help="Overwrite an existing HARNESS.md")

    profile_cmd = sub.add_parser("profile", help="Deterministic working-style profiling and policy compilation")
    profile_sub = profile_cmd.add_subparsers(dest="profile_action", required=True)

    p_survey = profile_sub.add_parser("survey", help="Interactive survey-based profile scoring")
    p_survey.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled survey answers")
    p_survey.add_argument("--write", action="store_true", help="Compile generated scores into global memory markdown files")
    p_survey.add_argument("--overwrite", action="store_true", help="Allow overwriting existing global memory markdown files")

    p_infer = profile_sub.add_parser("infer", help="Infer profile scores from repository signals")
    p_infer.add_argument("path", nargs="?", default=".")
    p_infer.add_argument("--write", action="store_true", help="Compile generated scores into global memory markdown files")
    p_infer.add_argument("--overwrite", action="store_true", help="Allow overwriting existing global memory markdown files")

    p_hybrid = profile_sub.add_parser("hybrid", help="Blend survey and inferred profile scores")
    p_hybrid.add_argument("path", nargs="?", default=".")
    p_hybrid.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled survey answers")
    p_hybrid.add_argument("--write", action="store_true", help="Compile generated scores into global memory markdown files")
    p_hybrid.add_argument("--overwrite", action="store_true", help="Allow overwriting existing global memory markdown files")

    profile_sub.add_parser("show", help="Show the latest generated workstyle scorecard")

    cognition_cmd = sub.add_parser("cognition", help="Deterministic cognitive/philosophy profiling")
    cognition_sub = cognition_cmd.add_subparsers(dest="cognition_action", required=True)
    c_survey = cognition_sub.add_parser("survey", help="Interactive cognitive-style survey")
    c_survey.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled cognitive answers")
    c_survey.add_argument("--write", action="store_true", help="Compile generated cognitive scores into global memory markdown")
    c_survey.add_argument("--overwrite", action="store_true", help="Allow overwriting existing cognitive_profile.md")

    c_infer = cognition_sub.add_parser("infer", help="Infer cognitive scores from repository signals")
    c_infer.add_argument("path", nargs="?", default=".")
    c_infer.add_argument("--write", action="store_true", help="Compile generated cognitive scores into global memory markdown")
    c_infer.add_argument("--overwrite", action="store_true", help="Allow overwriting existing cognitive_profile.md")

    c_hybrid = cognition_sub.add_parser("hybrid", help="Blend cognitive survey and inferred scores")
    c_hybrid.add_argument("path", nargs="?", default=".")
    c_hybrid.add_argument("--answers-file", metavar="JSON", help="Optional JSON file with prefilled cognitive answers")
    c_hybrid.add_argument("--write", action="store_true", help="Compile generated cognitive scores into global memory markdown")
    c_hybrid.add_argument("--overwrite", action="store_true", help="Allow overwriting existing cognitive_profile.md")

    cognition_sub.add_parser("show", help="Show the latest generated cognitive scorecard")

    worktree = sub.add_parser("worktree", help="Create a git worktree for a bounded task")
    worktree.add_argument("task_type")
    worktree.add_argument("task_name", nargs="+")
    worktree.add_argument("--base", dest="base_ref")

    private_skill = sub.add_parser("private-skill", help="Enable or disable a private experimental skill")
    private_skill.add_argument("action", choices=["enable", "disable", "status"])
    private_skill.add_argument("name")
    private_skill.add_argument("--tool", default="claude")

    start = sub.add_parser("start", help="Start the preferred agent surface")
    start.add_argument("tool", nargs="?", default="claude", choices=["claude", "cursor", "codex"])

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "init":
        return _init_memory()
    if args.command == "doctor":
        return _doctor()
    if args.command == "sync":
        _sync_user_runtime()
        return 0
    if args.command == "update":
        return _update()
    if args.command == "list":
        _list_runtime()
        return 0
    if args.command == "validate":
        return _validate_manifest()
    if args.command in ("bootstrap", "new-project"):
        _bootstrap_project(
            _resolve_bootstrap_target(args.path),
            harness_name=getattr(args, "harness", None),
        )
        return 0
    if args.command == "detect":
        project_root = _resolve_bootstrap_target(args.path)
        print(f"Analyzing {project_root} ...")
        print()
        results = _detect_project_harness(project_root)
        if not results or results[0][1] == 0:
            print("No harness signals detected. Apply the generic harness or specify one explicitly.")
            print("  agent-os harness apply generic .")
            return 0
        print("Harness scores:")
        print()
        for i, (name, score, signals) in enumerate(results):
            if score == 0:
                continue
            marker = "  ← recommended" if i == 0 and score > 2 else ""
            print(f"  {name:<22} score {score}{marker}")
            for sig in signals[:6]:
                print(f"    · {sig}")
        print()
        best_name, best_score, _ = results[0]
        if best_score > 2:
            print(f"Recommended: {best_name}")
            print(f"  agent-os harness apply {best_name} {args.path}")
        else:
            print("Low confidence — review scores above and choose manually.")
            print("  agent-os harness list")
        return 0
    if args.command == "harness":
        if args.harness_action == "list":
            _list_harnesses()
            return 0
        if args.harness_action == "apply":
            return _apply_harness(
                args.type,
                _resolve_bootstrap_target(args.path),
                force=args.force,
            )
        return 0
    if args.command == "profile":
        if args.profile_action == "show":
            return _profile_show()
        if args.profile_action in ("survey", "infer", "hybrid"):
            path_arg = getattr(args, "path", ".")
            answers = None
            answers_file = getattr(args, "answers_file", None)
            if answers_file:
                try:
                    answers = _load_answers_file(Path(answers_file).expanduser())
                except (FileNotFoundError, ValueError) as exc:
                    print(str(exc), file=sys.stderr)
                    return 1
            return _profile_command(
                args.profile_action,
                path_arg,
                write=getattr(args, "write", False),
                overwrite=getattr(args, "overwrite", False),
                answers=answers,
            )
        return 0
    if args.command == "cognition":
        answers = None
        answers_file = getattr(args, "answers_file", None)
        if answers_file:
            try:
                answers = _load_answers_file(Path(answers_file).expanduser())
            except (FileNotFoundError, ValueError) as exc:
                print(str(exc), file=sys.stderr)
                return 1
        return _cognition_command(
            args.cognition_action,
            getattr(args, "path", "."),
            write=getattr(args, "write", False),
            overwrite=getattr(args, "overwrite", False),
            answers=answers,
        )
    if args.command == "worktree":
        return _worktree(args.task_type, args.task_name, args.base_ref, Path.cwd())
    if args.command == "private-skill":
        return _private_skill(args.action, args.name, args.tool)
    if args.command == "start":
        return _start(args.tool, Path.cwd())
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
