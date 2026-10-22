# Permissions and manual recovery

Use this procedure when a required operation exceeds the current filesystem or network permissions. It applies to installing into an absent destination with the built-in installer, reading or writing configuration, querying models, generating or downloading an image, and saving output. The agent requests authorization; the Python CLI does not grant itself permissions. An existing Skill follows [install.md](install.md): stop and give manual deletion and standard reinstallation instructions, without requesting authorization to delete or replace it.

## Request authorization before stopping

1. Inspect the host's current sandbox and approval rules. Reuse existing authorization and do not ask for permissions that the operation already has. Prepare the exact command, paths, and network destination before asking. Complete permitted preparation first, including checking for an existing Skill before requesting download or fresh installation access.
2. Recognize access failures: a host denial, `PermissionError`, `EACCES`, `EPERM`, `Permission denied`, `Operation not permitted`, or a read-only filesystem. Network or DNS failures in a network-restricted sandbox may also require approval. A provider's HTTP `401`/`403`, an invalid response, or an empty model list is not itself a local sandbox permission failure.
3. When the host permits approval requests, use its native approval mechanism to ask the user for the specific blocked operation. With an execution tool that supports it, request `sandbox_permissions="require_escalated"` and a concise `justification` question explaining the required access and purpose. Request filesystem access only for the actual affected paths, or network access for the actual service. Do not request blanket access. Do not stop at saying permission is needed: submit the approval request and continue after approval.
4. If the host provides no native approval prompt but permits another authorization flow, ask through its user-input tool or chat and wait for an explicit answer. Explain how the user must grant the access in that environment. A chat answer alone does not change filesystem, network, or managed policy. Resume only when the host actually permits the operation.
5. After approval, retry the blocked operation and finish the original workflow. `models` is safe to rerun; display its returned IDs and wait for the user's model selection. Approval to access the network does not select a model. For `generate`, retry only if the denial is known to have happened before submission. If submission or completion is uncertain, explain the possible existing generation and obtain the user's decision before submitting another paid request. If only saving failed, recover the existing result when available.
6. If the user declines, approval is rejected, escalation is unavailable, or policy explicitly forbids requesting it, stop the blocked action and use the manual fallback below. Do not repeatedly request the same denied permission or retry through another tool to bypass it. Never modify global sandbox settings, directory permissions, or proxy configuration to evade a denial. If the host explicitly forbids escalation (for example, a `never` approval policy), do not submit a prohibited escalation request or imply that chat consent can override it.

Examples of authorization questions, substituting the actual paths or host:

- Fresh installation: “已检查 `<actual-skill-directory>` 尚不存在，需要联网下载并写入该目录。是否授权本次标准安装？”
- Model discovery: “当前沙箱阻止访问 `<provider-host>`，需要联网读取可用生图模型。是否授权执行这次模型查询？”
- Configuration: “需要读取 `<actual-config-file>` 来检查现有配置，检查输出不会显示 API key。是否授权？”

The host may route native approval requests to automatic review instead of the user. The Skill cannot choose that reviewer or override its decision. If automatic review rejects an action, explicitly identify the rejected action and summarize the stated reason in a separate short paragraph. Do not describe it as a user refusal. If the user wants human prompts in a later session, point to the host's permission controls; do not silently edit them.

For a local Codex CLI where the user controls the approval settings, they can start an interactive session with:

```bash
codex --sandbox workspace-write --ask-for-approval on-request -c approvals_reviewer=user
```

This keeps the workspace sandbox and routes required approvals to the user. Managed host or organization restrictions can still prohibit an operation. Offer this as an optional user-run setup change; never restart their session or change settings automatically.

## Manual fallback

State what completed, what remains incomplete, which access was blocked, and whether the user declined, host policy forbids escalation, or automatic review rejected the action. Preserve any existing installation, external configuration, and recoverable generated result. Verify their state before claiming they were preserved.

Give commands for the user's own local terminal, outside the restricted agent sandbox. Resolve every placeholder below to a verified actual path and shell-quote paths and the prompt safely. Preserve the current environment and configuration overrides. If the terminal does not inherit session-only variables, tell the user which variable names are required without displaying their values. Never include API keys in commands, ask for them in chat, or recommend `sudo`, broad `chmod`, or disabling all sandbox protections as a default solution.

### Fresh installation

If the destination already exists, follow [install.md](install.md) and stop with the manual deletion command and standard Codex reinstallation message. Permission approval does not authorize automatic replacement.

If the destination is absent but download or installation cannot be authorized, supply the current host's built-in helper command for the user to run in their own terminal:

```bash
python3 "<skill-installer-dir>/scripts/install-skill-from-github.py" \
  --url https://github.com/xixia0523/skills/tree/main/Custom_Image_Generator_Skill/custom-imagegen \
  --dest "<actual-skills-root>"
```

The helper's `--dest` is the containing skills root, not the final `custom-imagegen` directory. Resolve the helper and destination to actual paths and follow the host's current installer options. Never supply an overwrite script. Do not report installation as complete merely because downloading succeeded. After the user completes installation, the next use checks configuration normally.

### Configuration check or model discovery

For a blocked configuration read, supply the installed CLI's `check` command. For blocked model discovery, supply:

```bash
python3 "<actual-skill-directory>/scripts/image_gen.py" models
```

Ask the user to return only the model IDs or sanitized error and select a returned model. Do not supply a generation command with a guessed model or treat a previously cached list as a successful current query.

### Generation or saving output

Only after a successful query and the user's explicit model selection, supply the exact generation command with the chosen model, original final prompt, size, quality, and an absolute output path. For example:

```bash
python3 "<actual-skill-directory>/scripts/image_gen.py" generate \
  --prompt "<final-prompt>" \
  --model "<user-selected-model-id>" \
  --size 1024x1024 --quality medium \
  --out "<absolute-output-file>"
```

If a previous request may have been submitted, explain that this manual command creates another generation and may incur another charge. If a result already exists, prefer instructions to save that result. State that generation or saving remains incomplete until the actual file has been verified.

For host approval policies and manual versus automatic review, see [Codex sandboxing](https://learn.chatgpt.com/docs/sandboxing) and [Agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security).
