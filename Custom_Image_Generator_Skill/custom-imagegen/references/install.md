# Standard installation and manual reinstallation

Use Codex's built-in `skill-installer` and its GitHub helper. This package has no custom installer or installation hooks. The standard message to send in Codex is:

```text
$skill-installer install https://github.com/xixia0523/skills/tree/main/Custom_Image_Generator_Skill/custom-imagegen
```

## Check before downloading

1. Determine the built-in installer's actual destination: its explicit `--dest` skills root, otherwise `$CODEX_HOME/skills`, defaulting to `~/.codex/skills`. The target folder is `custom-imagegen`. Also inspect any existing local installation of this name reported by the current session. Do not mistake this project's source directory or a downloaded checkout for an installed Skill.
2. Check the local installation paths before making a download or requesting installation write access. An existing directory, file, or symlink at the target blocks installation, including an incomplete installation or a dangling symlink. If access is denied, follow [permissions.md](permissions.md) to request read access; do not treat an unreadable path as absent.
3. If any existing installation is found, stop. Show its verified absolute path, a shell-quoted command for the user to delete that exact Skill entry in their own terminal, and the standard Codex installation message above. Do not run the deletion, request authorization for deletion or replacement, rename the old folder, install under a different name, or download to a temporary destination to bypass the conflict. Wait for the user to delete it and send a new installation request.
4. If no installation exists, use the built-in helper directly against the intended destination, following its own instructions and [permissions.md](permissions.md) for required network or filesystem authorization. Do not stage a second copy or invoke an old version's custom installer. If a destination conflict is reported later, follow step 3; never retry with overwrite logic.
5. After successful installation, report the installed path and that the Skill will be available on the next turn. Keep the existing external configuration and environment. The first use runs the configuration check in `SKILL.md`; missing configuration follows [setup.md](setup.md).

## Existing installation response

For the default destination, the response can say:

> 检测到已安装 custom-imagegen，本次安装已停止。请先在本机终端手动删除旧 Skill，再回到 Codex 重新发送安装指令。

Run in the user's terminal:

```bash
rm -rf -- "$HOME/.codex/skills/custom-imagegen"
```

Then send in Codex:

```text
$skill-installer install https://github.com/xixia0523/skills/tree/main/Custom_Image_Generator_Skill/custom-imagegen
```

In an actual response, replace the example deletion path with the verified absolute installation path, accounting for `CODEX_HOME` or an explicit destination. Keep a final symlink as the entry to remove: do not follow it or add a trailing slash. Never suggest deleting the entire `skills` folder, a repository source folder, or the external configuration. Before offering deletion, check whether the active configuration is inside that Skill directory; if so, first explain how the user can move it outside and update `CUSTOM_IMAGEGEN_CONFIG` without exposing secrets. The default `~/.config/custom-imagegen/.env`, other external configuration paths, API keys, provider URLs, proxies, and environment variables are reused.

## Scope of repository instructions

The built-in installer refuses an existing destination, but it may download the repository before checking that destination. It does not automatically execute this package's instructions before installation. This repository cannot change the built-in installer's preflight order or guarantee that a bare URL request prints the manual removal instructions. For an explicit request to check first, the user can append:

```text
安装前先检查本地是否已有 custom-imagegen；若有则停止，只给出手动删除命令和上面的标准安装指令，不要自行删除、覆盖、改名或临时安装。
```

For the supported repository installation entry, see [OpenAI Docs](https://learn.chatgpt.com/docs/build-skills). For destination-conflict behavior, consult the current host's built-in `skill-installer/SKILL.md` and `scripts/install-skill-from-github.py`.
