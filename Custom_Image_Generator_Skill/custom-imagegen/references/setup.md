# Setup and configuration

The skill has no third-party Python dependencies. It requires Python 3 and an OpenAI-compatible provider that implements `POST /v1/images/generations` for a `gpt-image-*` model.

## Configuration location

The default file is:

```text
~/.config/custom-imagegen/.env
```

Set `CUSTOM_IMAGEGEN_CONFIG` to use a different file. The file contains:

```dotenv
OPENAI_API_KEY=<provider API key>
AI_BASE_URL=https://provider.example/v1
```

The CLI adds `/v1` when the configured URL does not already end in `/v1`. Configuration files created by the CLI use permission mode `0600`.

## Recommended setup methods

Interactive setup keeps the key out of shell history:

```bash
python3 <skill-dir>/scripts/image_gen.py configure
```

Import an existing local `.env` without showing its values:

```bash
python3 <skill-dir>/scripts/image_gen.py configure --from-env-file "/path/to/existing/.env"
```

For non-interactive setup, put the key in an environment variable and name that variable. Do not pass the key itself as a command argument:

```bash
python3 <skill-dir>/scripts/image_gen.py configure \
  --base-url "https://provider.example/v1" \
  --api-key-env CUSTOM_IMAGEGEN_API_KEY
```

The CLI can also run without a file when both `CUSTOM_IMAGEGEN_API_KEY` and `CUSTOM_IMAGEGEN_BASE_URL` are present in its environment.

For compatibility with existing setups, the loader also accepts `OPENAI_IMAGE_API_KEY` / `OPENAI_IMAGE_BASE_URL` and `OPENAI_API_KEY` / `OPENAI_BASE_URL`. Skill-specific `CUSTOM_IMAGEGEN_*` environment variables have the highest priority.

## Verification

Check configuration without making an API call:

```bash
python3 <skill-dir>/scripts/image_gen.py check
```

Check a complete request without making an API call:

```bash
python3 <skill-dir>/scripts/image_gen.py generate \
  --prompt "A red ceramic teapot on a wooden table" \
  --out "output/custom-imagegen/config-test.png" \
  --dry-run
```

If `check` succeeds but generation returns `404`, the provider may not implement the Images API or the base URL may be wrong. A `401` or `403` usually indicates an invalid key or insufficient provider permissions. A model error means the provider does not expose the requested `gpt-image-*` model identifier.

## Security boundaries

- Never store `.env` inside the skill directory or a shared archive.
- Never paste an API key into agent chat.
- Never put an API key directly in a shell command.
- Share only the skill package; every recipient supplies their own provider URL and key.
