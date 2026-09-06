# Repository guidance

This repository distributes a portable personal CLI agent profile. Shared user instructions live in `agent-profile/AGENTS.md`; this file is for maintaining the installer.

- Run `uv run --locked python -m unittest discover -s tests -v` for installer or launcher changes.
- Test installation and restoration in a temporary `--home`, not the developer's real home. A user-requested bootstrap on their computer may use their actual home.
- Keep credentials, private endpoints, session data, and workstation-specific executable paths out of tracked files. Put machine-specific inputs in the local `machine.json`; secrets stay in process environment or the private local secret store.
- Preserve unrelated native settings and authentication. A model catalog response does not establish inference, tool, streaming, or child-routing support.
- Keep Windows native behavior separate from WSL. Do not require privileged symlinks on Windows or run npm command shims through an interpolated command shell.
