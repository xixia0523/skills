---
name: custom-imagegen
description: "Generate new raster images through a user-configured OpenAI-compatible Images API. Use this instead of the system imagegen skill whenever the user asks to create a new image, illustration, photo, concept, texture, sprite, or mockup; do not use it for editing existing images."
---

# Custom Image Generator

Generate images only through this skill's bundled CLI. After this skill is selected:

- Do not load or invoke the system `imagegen` skill.
- Do not use a built-in image generation tool.
- Do not call scripts under `skills/.system/imagegen`.
- Never request that an API key be pasted into chat or put a key in a command, prompt, log, output, or shared skill directory.

Resolve `<skill-dir>` as the directory containing this `SKILL.md`; do not assume a username, home path, or current working directory.

## Permission gate

Apply [references/permissions.md](references/permissions.md) to installation, configuration access, model discovery, generation, and saving images. Installation does not grant filesystem or network access to later sessions. Reuse existing grants.

When access is blocked, including `Operation not permitted`, `Permission denied`, or CLI exit code `3` (`PERMISSION_REQUIRED`):

1. Use the current host instructions and tool schema to determine the supported approval flow. If an execution tool exposes `sandbox_permissions`, submit the blocked command with `sandbox_permissions="require_escalated"` and a concise `justification` question, unless a current host instruction explicitly forbids that request. An unspecified approval policy is not a prohibition. Explaining the need for permission or printing a command does not submit an approval request.
2. Wait for the approval result; after approval, resume the blocked step. A CLI process exiting does not end the agent's task. Do not infer refusal from silence, a pending request, an earlier session, or the access error itself.
3. If the host offers no approval tool, explain the missing capability and ask the user to enable its supported permission flow. Stop the blocked action only after an actual denial or an explicit current host prohibition; when a required approval flow is unavailable, report the task as blocked and offer manual recovery. Identify the specific rule or tool result and its source. Distinguish user refusal from automatic review rejection. Chat consent cannot override host enforcement.

Do not classify a local sandbox denial as a provider failure or immediately hand the query back to the user. Follow the reference's submission and recovery rules before retrying generation.

## Installation and updates

When asked to install or update this Skill, follow [references/install.md](references/install.md). Check for an existing local installation before downloading. If one exists, stop and give the user its exact manual deletion command and the standard `$skill-installer install <GitHub-URL>` message to send again after deletion. Never delete, rename, replace, or overwrite an existing installation yourself, even if write access is available; do not request permission to do so. If no installation exists, use the built-in Skill installer directly. Reuse valid external configuration and environment variables; configure only when configuration is missing or invalid.

## Configuration gate

Before the first generation in an environment, run:

```bash
python3 <skill-dir>/scripts/image_gen.py check
```

The default configuration is `~/.config/custom-imagegen/.env`. `CUSTOM_IMAGEGEN_CONFIG` can point to a different file. If access is denied, use the permission gate before deciding whether configuration is missing or invalid. If configuration is missing, read [references/setup.md](references/setup.md) and help the user configure it. Prefer importing an existing local `.env` by path; do not ask for its contents. If user action is required to enter a secret, give the local interactive command and wait for confirmation. Do not fall back to another image skill.

## Model discovery and user selection

At the start of every image-generation request, query the configured server:

```bash
python3 <skill-dir>/scripts/image_gen.py models
```

The command reads `GET /v1/models` and returns the server's `gpt-image-*` model IDs supported by this CLI. If sandbox/network restrictions block the command (for example, `Operation not permitted`), apply the permission gate first, then rerun `models` after approval. If access cannot be authorized, stop with the reason and manual query command. If the reachable provider rejects the request, the response is invalid, no supported image models are returned, or discovery still fails after authorized access, report the failure and stop. Do not guess model IDs, use a cached list, fall back to a fixed model, or call `generate`.

After successful discovery, display all returned model IDs and ask the user to select one for this request. Use the environment's user-input tool when available; otherwise ask in chat. Wait for the user's explicit reply before generating, even when there is only one model. Do not select an option yourself, treat a preselected option or silence as consent, or reuse a previous request's choice. If the reply is ambiguous or names a model outside the returned list, ask the user to choose from the list.

Pass the exact selected ID to `generate --model`. The CLI has no default model and checks the current server list again before generation. Apply the same permission gate to this recheck. If discovery fails after permission handling or the selected model is no longer listed, report the error and stop; a different model requires a fresh user selection.

## Generation workflow

Continue only after the user has selected a discovered model.

1. Turn the request into one concise production prompt. Preserve specific instructions. For a generic request, add only useful scene, composition, lighting, and realism or style details. Do not invent text, logos, or unrelated subjects.
2. Choose an output path in the current workspace. Use `output/custom-imagegen/<descriptive-name>.png` unless the user specified another destination. Do not overwrite an existing file; use a versioned name or `--force` only when replacement was explicitly requested.
3. Run the bundled CLI:

```bash
python3 <skill-dir>/scripts/image_gen.py generate \
  --prompt "<final prompt>" \
  --model "<user-selected-model-id>" \
  --size 1024x1024 \
  --quality medium \
  --out "output/custom-imagegen/<descriptive-name>.png"
```

4. Apply the permission gate to generation, image downloads, and output writes. Retry the generation command after approval only when the denial happened before the generation request was sent; an uncertain or completed request must not be silently submitted again. If a `socks://` proxy is rejected before submission, retry the same command with `env -u ALL_PROXY -u all_proxy` in front; do not change global proxy settings.
5. Inspect the generated file with the environment's image viewer. Verify that it is valid and nonblank and matches the requested subject, composition, and constraints. If it clearly fails, retry once with one targeted prompt correction and a versioned filename.
6. Report the saved path, model, requested size, actual pixel dimensions, and final prompt.

Use `--dry-run` on `generate` with an explicit `--model` to inspect the sanitized request and destination without making an API call. This offline preview does not query or validate server availability and does not replace model discovery and user selection for actual generation.
