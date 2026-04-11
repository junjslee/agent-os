# Python Runtime Policy

<!-- Personalize: set AGENT_OS_CONDA_ROOT if your Conda or module-loaded Python is not at ~/miniconda3. -->

- All Python-backed `agent-os` commands must run in a supported Python environment.
- Default: Conda `base` at `~/miniconda3`. Override: `export AGENT_OS_CONDA_ROOT=/your/path`.
- On HPC/remote systems using environment modules, load a working Python before running agent-os (e.g. `module load <python-module>`). Add this to `~/.bashrc` so it persists across sessions.
- Homebrew Python and system Python are not the supported runtime for `agent-os`.
- Non-Python tooling (Claude Code, Cursor, Git, `jq`) stays outside the managed environment.
