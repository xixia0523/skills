# Setup and configuration

The skill has no third-party Python dependencies. It requires Python 3 and an OpenAI-compatible provider that implements both `GET /v1/models` and `POST /v1/images/generations` for a `gpt-image-*` model.

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

When reinstalling, use [install.md](install.md): an existing Skill requires the user to delete its installation directory manually and send the standard installation request again. Keep external configuration files and environment variables intact. Run `check` on first use and reuse valid configuration; configure again only if it is missing or invalid.

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

Query the server's current image models:

```bash
python3 <skill-dir>/scripts/image_gen.py models
```

This uses the authenticated [List models endpoint in OpenAI Docs](https://developers.openai.com/api/reference/resources/models/methods/list), expecting a JSON object with a `data` array whose entries have an `id`. The CLI lists only `gpt-image-*` models because its generation parameters support that family. It does not infer image-generation support for other model IDs. Listing a model does not test generation permissions or quota.

Model discovery makes one request, with a default timeout of 30 seconds (`models --timeout SECONDS` to change it). If filesystem or sandbox network permissions block configuration access or the query, first follow [permissions.md](permissions.md): request the required authorization when permitted and retry after approval. If authorization is declined or prohibited, explain why and provide the actual manual command. Provider HTTP errors, invalid responses, an empty supported model list, or failures remaining after authorized access stop the workflow and must be reported. There is no fixed-model fallback.

For every generation request, show the discovered model IDs and wait for the user to choose one, including when only one is returned. `generate` requires `--model` and checks the server list again before calling the generation endpoint. If the selected model disappears, stop and ask for a new selection after fresh discovery.

After the user selects a returned model, check a complete request without making another API call (replace the model placeholder with that exact ID):

```bash
python3 <skill-dir>/scripts/image_gen.py generate \
  --prompt "A red ceramic teapot on a wooden table" \
  --model "<user-selected-model-id>" \
  --out "output/custom-imagegen/config-test.png" \
  --dry-run
```

`--dry-run` remains an offline preview; it does not prove that the selected model is currently listed or usable.

If `check` succeeds but `models` returns `404`, the provider may not implement the Models API or the base URL may be wrong. Generation cannot proceed until model discovery works. If `models` succeeds but generation returns `404`, the provider may not implement the Images API. A `401` or `403` usually indicates an invalid key or insufficient provider permissions. A generation model error can indicate that the provider lists a model that the key cannot actually use.

## Security boundaries

- Never store `.env` inside the skill directory or a shared archive.
- Never paste an API key into agent chat.
- Never put an API key directly in a shell command.
- Share only the skill package; every recipient supplies their own provider URL and key.
