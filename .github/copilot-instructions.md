```markdown
# GitHub Copilot Instructions

## Tech Stack & Architecture

This project is a terminal-based developer environment setup for Claude Code and GitHub Copilot customizations.  
It primarily uses Bash scripts for installation, update, and uninstall operations.  
Key components include Claude Skills (file-organizer, changelog-generator, document-skills, ui-ux-pro-max) and Copilot customizations (conventional-commit, git-flow-branch-creator, github-actions-expert, ci-cd-best-practices).

## Key Directories & Files

- `scripts/` — Contains install.sh, update.sh, uninstall.sh for managing setup.
- `claude-skills/` — Claude Code skills (file-organizer, changelog-generator, document-skills, ui-ux-pro-max).
- `copilot-customizations/` — GitHub Copilot CLI customizations and prompts.
- `docs/` — Documentation (e.g., USAGE.md).
- `README.md` — Main project overview and usage.
- `QUICKSTART.md` — Step-by-step setup guide.

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/my-terminal-skills.git
   cd my-terminal-skills
   ```
2. Run the installer:
   ```bash
   chmod +x scripts/install.sh
   ./scripts/install.sh
   ```
3. (Optional) Update:
   ```bash
   ./scripts/update.sh
   ```
4. (Optional) Uninstall:
   ```bash
   ./scripts/uninstall.sh
   ```

## Usage

- Claude Code: Run `claude` in terminal to access installed skills.
- GitHub Copilot CLI: Use custom prompts in VS Code (e.g., `/conventional-commit`).

## Conventions

- All install/update/uninstall actions are managed via scripts in the `scripts/` directory.
- Skills and customizations are copied to user config directories (`~/.config/claude-code/skills`, `~/.github/copilot`).
- Follow the guides in `README.md` and `QUICKSTART.md` for first-time setup and troubleshooting.

## Testing

- After installation, verify Claude skills with `claude` and Copilot customizations in VS Code.
- No automated test suite; manual verification recommended.

## Contribution

- Add new skills/customizations in their respective directories.
- Update documentation as needed.
```