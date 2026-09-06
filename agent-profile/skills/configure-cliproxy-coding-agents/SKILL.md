---
name: configure-cliproxy-coding-agents
description: Configure or repair Claude Code and Copilot CLI wrappers for a local CLIProxyAPI gateway, preserving native logins and verifying model routing and BYOK limits.
---

# Configure CLIProxy Coding Agents

Use isolated runtime wrappers so gateway configuration does not replace native CLI authentication. Inspect only the clients and configuration relevant to the request.

## Operational constraints

- Read credentials inside a process that emits only structural or redacted results. Keep keys out of command arguments, logs, generated source, and shell tracing.
- Keep the gateway on loopback and preserve native commands, login state, and unrelated settings. Restart or reinstall only when diagnosis requires it; use the user's service context rather than `sudo brew services`.
- Back up affected settings before mutation. Some interactive CLI flags persist settings; restore incidental changes.
- Wrappers should parse credentials at runtime, reject group/other-readable configuration, pass credentials only in the child environment, remove conflicting auth variables, preserve arguments, use absolute executable paths, and have mode `0700`.

## Models and client behavior

Prefer the user's selected model from GPT-5.6 Luna/Sol, GPT-6 Astra, GLM-5.3 Flash, or DeepSeek V4 Flash/Pro when that client and provider support it. Preserve exact configured model IDs and provider routes. Parent, subagent, and configurable fast aliases inherit the chosen model by default; use a different model for a concrete task benefit or explicit preference. Do not infer a downgrade merely from Luna or Flash in the name.

Read relevant sections of [the client matrix](references/client-matrix.md) when changing wrappers or routing. Confirm version-sensitive names against installed CLI help and exact model IDs against the authenticated gateway catalog. Obtain context/output limits from live metadata when available; do not infer limits from a model picker or invent missing values.

Configure only available subagents within scope. For Copilot, merge affected `subagents.agents` entries instead of replacing settings. Provider-level model overrides can defeat per-agent routing; `contextTier` does not replace numeric BYOK limits.

## Verification

Use [the audit script](scripts/audit_setup.rb) when structural checks or an authenticated local catalog probe help. Match checks to the change: syntax and secret checks for wrappers; inference, streaming, and a restricted read-only tool call for transport changes; one child call and redacted wire-model evidence for subagent routing changes. A complete new setup should cover each affected capability.

Keep smoke tests narrow. Check native authentication and the listener when affected. Report evidence and untested capabilities without requiring an unrelated full audit for every edit.
