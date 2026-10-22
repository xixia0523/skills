# Installation and updates

Use the bundled installer for both a new installation and replacement of an existing `custom-imagegen`. It validates and stages the new files before replacing the installed directory. Replacement failures restore the previous installation; if restoration itself fails, the error identifies the preserved backup directory.

The installer replaces only this Skill. Existing external configuration files and environment variables are reused, including `CUSTOM_IMAGEGEN_CONFIG`, `XDG_CONFIG_HOME`, provider URLs, API keys, and proxy settings. Do not run `configure` during an update unless the existing configuration is missing or invalid.

## Install or update from GitHub

Download the repository to a temporary directory, then run the installer from the downloaded version:

```bash
custom_imagegen_checkout="$(mktemp -d)"
git clone --depth 1 --branch main https://github.com/xixia0523/skills.git "$custom_imagegen_checkout/skills"
python3 "$custom_imagegen_checkout/skills/Custom_Image_Generator_Skill/custom-imagegen/scripts/install_skill.py"
```

The default destination is `$CODEX_HOME/skills/custom-imagegen`, or `~/.codex/skills/custom-imagegen` when `CODEX_HOME` is unset. The destination is the complete Skill directory; `--dest` can select an existing installation in another location:

```bash
python3 <downloaded-skill-dir>/scripts/install_skill.py --dest "/path/to/skills/custom-imagegen"
```

If an Agent uses Codex's built-in GitHub Skill installer to download the source, use a temporary `--dest` for that download, then run the downloaded `scripts/install_skill.py` against the actual installation. The built-in installer refuses an existing destination; a direct `$skill-installer <URL>` invocation does not provide this package's replacement behavior.

The existing installed directory must identify itself as `custom-imagegen` in its `SKILL.md`. Other directories are rejected. The package file list excludes local credentials, generated images, tests, and caches. Configuration inside the installation directory must be moved outside it before updating. For a symlinked installation, pass the actual target directory with `--dest`.

## Reuse and verify configuration

After installation, run the installed CLI's local configuration check:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/custom-imagegen/scripts/image_gen.py" check
```

For a custom destination, use that directory's `scripts/image_gen.py` instead. `check` does not make a network request or display the API key. When it succeeds, proceed with the existing configuration. When it reports missing or invalid configuration, follow [setup.md](setup.md); never request secrets in chat.

Codex detects Skill changes automatically; if the update does not appear, restart Codex. See [OpenAI Docs](https://learn.chatgpt.com/docs/build-skills).
