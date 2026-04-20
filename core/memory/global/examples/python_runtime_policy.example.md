# Python Runtime Policy

<!-- Personalize: set EPISTEME_CONDA_ROOT if your Conda or module-loaded Python is not at ~/miniconda3. -->

- All Python-backed `episteme` commands must run in a supported Python environment.
- Default: Conda `base` at `~/miniconda3`. Override: `export EPISTEME_CONDA_ROOT=/your/path`.
- On HPC/remote systems using environment modules, load a working Python before running episteme (e.g. `module load <python-module>`). Add this to `~/.bashrc` so it persists across sessions.
- Homebrew Python and system Python are not supported runtimes for `episteme`.
- Non-Python tooling (Claude Code, Cursor, Git, `jq`) stays outside the managed environment.
