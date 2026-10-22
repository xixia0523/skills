# Install or update through Codex

The user-facing entry is the single `$skill-installer` message in [README.md](../README.md). Codex performs the work below. Use [permissions.md](permissions.md) for download, installation, or configuration-access restrictions: first request authorization when permitted; provide manual commands only if authorization cannot be obtained.

Codex's built-in Skill installer downloads and copies Skill files, refuses an existing destination, and does not run package installation hooks. This repository cannot change that behavior. The README's install/update request explicitly asks Codex to replace the existing version, reuse configuration, and check it; a bare `$skill-installer <URL>` does not guarantee those extra actions.

## Agent workflow

1. Use the built-in Skill installer's `scripts/install-skill-from-github.py` to download the requested GitHub Skill into a fresh temporary `--dest`, keeping the existing installation available. Request network authorization if the download is blocked. For this repository, the Skill path is `Custom_Image_Generator_Skill/custom-imagegen`. Read the downloaded `SKILL.md` and its permission instructions before replacing the installed version.
2. Locate the existing `custom-imagegen` installation. Otherwise use `$CODEX_HOME/skills/custom-imagegen`, or `~/.codex/skills/custom-imagegen` when `CODEX_HOME` is unset.
3. Run the downloaded package's `scripts/install_skill.py --validate-only` before requesting any required write authorization, then run its `scripts/install_skill.py --dest <actual-skill-directory>`. If the Skill directory or its parent is read-only in the sandbox, request approval for this exact replacement command rather than stopping at “downloaded.” This performs a fresh installation or replaces an existing `custom-imagegen`. The installer stages the new files before replacing the installed directory, removes obsolete package files, and restores the previous installation if replacement fails. If restoration itself fails, its error identifies the preserved backup directory. If authorization is denied or prohibited, retain the new package and supply the manual recovery commands in [permissions.md](permissions.md).
4. Run the installed `scripts/image_gen.py check`, requesting read access if needed. Reuse valid external configuration and environment variables, including API keys, provider URLs, proxies, `CUSTOM_IMAGEGEN_CONFIG`, and `XDG_CONFIG_HOME`. An unreadable configuration is not evidence that it is missing or invalid. Configure only if the existing configuration is missing or invalid; follow [setup.md](setup.md), prefer an existing local configuration file, and never request secrets in chat.
5. Report completion and that the Skill will be available on the next turn. A configuration problem should be reported separately from successful installation.

The built-in helper can stage the package with:

```bash
python3 <skill-installer-dir>/scripts/install-skill-from-github.py \
  --url https://github.com/xixia0523/skills/tree/main/Custom_Image_Generator_Skill/custom-imagegen \
  --dest <temporary-directory>/skills
```

Then Codex runs the downloaded installer and configuration check against the actual destination. These are Agent implementation steps; the user runs commands only as a fallback when required access cannot be authorized.

The destination must identify itself as `custom-imagegen` in its `SKILL.md`. Other directories are rejected. Local credentials, outputs, tests, and caches are excluded from replacement files. Configuration located inside the installation directory must be moved outside it before updating; for a symlinked installation use its actual target as `--dest`.

For Codex's supported GitHub Skill installation entry, see [OpenAI Docs](https://learn.chatgpt.com/docs/build-skills).
