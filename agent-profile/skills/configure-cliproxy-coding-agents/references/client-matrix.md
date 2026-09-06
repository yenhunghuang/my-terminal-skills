# Client Integration Matrix

## Contents

- Claude Code
- GitHub Copilot CLI
- Context and model discovery
- Subagent routing
- Verification patterns
- Rollback

## Claude Code

Use runtime-only environment variables in a dedicated wrapper:

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_BASE_URL` | CLIProxyAPI origin, normally loopback without `/v1` |
| `ANTHROPIC_AUTH_TOKEN` | Existing downstream key, read at runtime |
| `ANTHROPIC_MODEL` | Parent/default model |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Map the Opus alias to the selected parent model |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Map the Sonnet alias to the selected parent model |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Map the Haiku/fast alias to the selected parent model unless a different model is explicitly needed |
| `ANTHROPIC_SMALL_FAST_MODEL` | Model for the fast-task slot; prefer the selected parent model |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Default model for spawned subagents |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | Client-side context ceiling when using a custom model |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Client-side output ceiling |

Delete `ANTHROPIC_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN` in the wrapper child environment so they cannot override gateway auth. This does not alter the parent shell or native login.

Use the Claude Agent/Explore tool for a subagent smoke test. Restrict available tools and disable session persistence for the test.

## GitHub Copilot CLI

Confirm current names with `copilot help providers` and `copilot help environment`.

| Variable/argument | Purpose |
| --- | --- |
| `COPILOT_PROVIDER_TYPE=openai` | Select OpenAI-compatible BYOK mode |
| `COPILOT_PROVIDER_BASE_URL` | CLIProxyAPI origin including `/v1` |
| `COPILOT_PROVIDER_API_KEY` | Existing downstream key, read at runtime |
| `COPILOT_PROVIDER_WIRE_API=responses` | Responses wire API; confirm support for the selected model and installed client |
| `COPILOT_MODEL` | Parent/default model |
| `COPILOT_PROVIDER_MAX_PROMPT_TOKENS` | Manual BYOK prompt/context limit |
| `COPILOT_PROVIDER_MAX_OUTPUT_TOKENS` | Manual BYOK output limit |
| `--secret-env-vars=COPILOT_PROVIDER_API_KEY` | Redact the key and strip it from shell/MCP tool environments |

Delete `COPILOT_PROVIDER_BEARER_TOKEN`; it takes precedence over the provider API key.

When subagents use a different model, also delete inherited `COPILOT_PROVIDER_MODEL_ID` and `COPILOT_PROVIDER_WIRE_MODEL`. Setting either globally can make the UI show the child model while the wire request still uses the parent model.

Copilot's general model picker and BYOK provider catalog are separate. If logs contain:

```text
Model "..." is not in the built-in catalog. Using defaults for prompt/output tokens.
```

set both numeric provider limits explicitly from live gateway metadata. A successful inference does not prove that token budgeting is correct.

### Copilot subagents

Inspect `/subagents` in the installed version. Typical built-ins include `explore`, `task`, `general-purpose`, `code-review`, `research`, and `security-review`; names can change. Configure only names actually shown:

```json
{
  "subagents": {
    "agents": {
      "explore": {
        "model": "inherit",
        "contextTier": "default"
      }
    }
  }
}
```

Merge this object into the existing `~/.copilot/settings.json`; never replace unrelated settings. This is a persisted Copilot setting and can affect native Copilot subagents, so report that scope.

Some command-line UI flags persist settings. Snapshot relevant keys before opening `/subagents`, and remove or restore incidental changes afterward.

## Context and model discovery

1. Call `GET /v1/models` with bearer auth to verify exact model IDs.
2. Repeat with `Anthropic-Version: 2023-06-01` to request Claude-format fields:
   - `max_input_tokens`
   - `max_tokens`
3. Compare against the installed gateway model registry or client cache.
4. Use the live gateway values for wrappers connected to that gateway.
5. Record source and timestamp; model limits and client catalogs are version-sensitive.

Never place the bearer value in `curl` arguments. Use the bundled audit script or an in-process HTTP client that reads YAML directly.

## Verification patterns

### Secret-safe structural checks

- Config mode has no group/other bits (`mode & 0077 == 0`).
- Wrapper mode is `0700`.
- Wrapper bytes do not contain the parsed downstream key.
- Shell startup files contain no permanent gateway provider exports unless explicitly requested.

### Restricted tool smoke tests

- Claude: expose only `Read`; read one known harmless line; require an exact marker.
- Copilot: expose only a read-only tool or a precisely allowed shell command; require an exact marker.
- Disable unrelated MCP servers during BYOK transport testing so GitHub auth does not mask provider failures.

### Subagent smoke tests

- Ask the parent to launch exactly one named subagent for a trivial no-file task.
- Restrict the parent to only the subagent/task tool.
- Inspect redacted gateway logs for one parent-model request and one child-model request.
- Do not accept UI labels or final prose as proof of wire routing.

## Rollback

- Delete only the added wrappers.
- Remove only the inserted `subagents.agents` entries, preserving unrelated Copilot settings.
- Do not delete OAuth credentials or the CLIProxyAPI config.
- Recheck native authentication and the loopback listener after rollback.
