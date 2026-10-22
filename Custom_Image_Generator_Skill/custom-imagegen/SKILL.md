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

## Configuration gate

Before the first generation in an environment, run:

```bash
python3 <skill-dir>/scripts/image_gen.py check
```

The default configuration is `~/.config/custom-imagegen/.env`. `CUSTOM_IMAGEGEN_CONFIG` can point to a different file. If configuration is missing, read [references/setup.md](references/setup.md) and help the user configure it. Prefer importing an existing local `.env` by path; do not ask for its contents. If user action is required to enter a secret, give the local interactive command and wait for confirmation. Do not fall back to another image skill.

## Generation workflow

1. Turn the request into one concise production prompt. Preserve specific instructions. For a generic request, add only useful scene, composition, lighting, and realism or style details. Do not invent text, logos, or unrelated subjects.
2. Choose an output path in the current workspace. Use `output/custom-imagegen/<descriptive-name>.png` unless the user specified another destination. Do not overwrite an existing file; use a versioned name or `--force` only when replacement was explicitly requested.
3. Run the bundled CLI:

```bash
python3 <skill-dir>/scripts/image_gen.py generate \
  --prompt "<final prompt>" \
  --model gpt-image-2 \
  --size 1024x1024 \
  --quality medium \
  --out "output/custom-imagegen/<descriptive-name>.png"
```

4. If network access requires approval, request it for this exact generation command. If a `socks://` proxy is rejected, retry the same command with `env -u ALL_PROXY -u all_proxy` in front; do not change global proxy settings.
5. Inspect the generated file with the environment's image viewer. Verify that it is valid and nonblank and matches the requested subject, composition, and constraints. If it clearly fails, retry once with one targeted prompt correction and a versioned filename.
6. Report the saved path, model, requested size, actual pixel dimensions, and final prompt.

Use `--dry-run` on `generate` to inspect the sanitized request and destination without making an API call.
