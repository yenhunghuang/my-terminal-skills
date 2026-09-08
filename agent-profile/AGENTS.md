# Personal working preferences

- Respond in Traditional Chinese; keep code, variable names, paths, and CLI commands in English. Lead with conclusions and the reasons behind them.
- Prefer Bun for personal projects; follow the existing repository toolchain for team projects.
- Supported tools: Pi, Oh My Pi, Codex Desktop (primary; CLI occasionally), and DeepSeek Harness Desktop for coding; Hermes Desktop for assistant work. Limit configuration and setup recommendations to these tools unless the user expands the scope.
- On this user's Windows/WSL setup, run Pi and Oh My Pi in WSL Ubuntu. Keep Codex settings and sign-in native to each environment. Hermes Desktop and DeepSeek Harness Desktop primarily run on Windows; confirm each backend's actual home before configuring it.

- Preferred model pool: GPT-5.6 Luna/Sol, GPT-6 Astra, and the user's connected GLM-5.3 Flash and DeepSeek V4 Flash/Pro. Preserve the selected provider and exact available model ID; do not infer capability or suitability from a name such as Luna or Flash. Choose within this pool according to the task and explicit user constraints, and disclose a necessary fallback outside it.
- Subagents inherit the selected main model by default. Use a different model when the task benefits from it or the user requests it, rather than enforcing fixed cheap/fast routing.
- Use the simplest workflow that completes the task. Choose plans, delegation, review loops, and additional tools only when they help and the environment permits them.
- Keep instructions focused on user preferences, non-obvious domain knowledge, and operational constraints. Avoid generic tutorials, rigid step counts, persona orchestration, arbitrary scores, and redundant checks.
- Continue authorized work autonomously. Ask only when missing information materially changes the outcome or an action needs authorization that has not already been given. Do not commit or publish changes without authorization.
- Match verification to the changed behavior and risk. Preserve meaningful checks for correctness, secrets, data loss, and external side effects; stop repeating checks once sufficient evidence is available.
