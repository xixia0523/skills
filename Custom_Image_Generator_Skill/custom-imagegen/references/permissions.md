# Permissions and manual recovery

Use this procedure when a required operation exceeds the current filesystem or network permissions. It applies to downloading a Skill, replacing an installation, reading or writing configuration, querying models, generating or downloading an image, and saving output. The agent requests authorization; the Python CLI does not grant itself permissions.

## Request authorization before stopping

1. Inspect the host's current sandbox and approval rules. Reuse existing authorization and do not ask for permissions that the operation already has. Prepare the exact command, paths, and network destination before asking. Complete permitted preparation first, such as validating the downloaded package before requesting permission to replace an installation.
2. Recognize access failures: a host denial, `PermissionError`, `EACCES`, `EPERM`, `Permission denied`, `Operation not permitted`, or a read-only filesystem. Network or DNS failures in a network-restricted sandbox may also require approval. A provider's HTTP `401`/`403`, an invalid response, or an empty model list is not itself a local sandbox permission failure.
3. When the host permits approval requests, use its native approval mechanism to ask the user for the specific blocked operation. With an execution tool that supports it, request `sandbox_permissions="require_escalated"` and a concise `justification` question explaining the required access and purpose. Request filesystem access only for the actual affected paths, or network access for the actual service. Do not request blanket access. Do not stop at saying permission is needed: submit the approval request and continue after approval.
4. If the host provides no native approval prompt but permits another authorization flow, ask through its user-input tool or chat and wait for an explicit answer. Explain how the user must grant the access in that environment. A chat answer alone does not change filesystem, network, or managed policy. Resume only when the host actually permits the operation.
5. After approval, retry the blocked operation and finish the original workflow. `models` is safe to rerun; display its returned IDs and wait for the user's model selection. Approval to access the network does not select a model. For `generate`, retry only if the denial is known to have happened before submission. If submission or completion is uncertain, explain the possible existing generation and obtain the user's decision before submitting another paid request. If only saving failed, recover the existing result when available.
6. If the user declines, approval is rejected, escalation is unavailable, or policy explicitly forbids requesting it, stop the blocked action and use the manual fallback below. Do not repeatedly request the same denied permission or retry through another tool to bypass it. Never modify global sandbox settings, directory permissions, or proxy configuration to evade a denial. If the host explicitly forbids escalation (for example, a `never` approval policy), do not submit a prohibited escalation request or imply that chat consent can override it.

Examples of authorization questions, substituting the actual paths or host:

- Installation: “需要写入 `<actual-skill-directory>` 及其父目录来覆盖旧版，外部配置会保留。是否授权本次安装？”
- Model discovery: “当前沙箱阻止访问 `<provider-host>`，需要联网读取可用生图模型。是否授权执行这次模型查询？”
- Configuration: “需要读取 `<actual-config-file>` 来检查现有配置，检查输出不会显示 API key。是否授权？”

The host may route native approval requests to automatic review instead of the user. The Skill cannot choose that reviewer or override its decision. If automatic review rejects an action, explicitly identify the rejected action and summarize the stated reason in a separate short paragraph. Do not describe it as a user refusal. If the user wants human prompts in a later session, point to the host's permission controls; do not silently edit them.

For a local Codex CLI where the user controls the approval settings, they can start an interactive session with:

```bash
codex --sandbox workspace-write --ask-for-approval on-request -c approvals_reviewer=user
```

This keeps the workspace sandbox and routes required approvals to the user. Managed host or organization restrictions can still prohibit an operation. Offer this as an optional user-run setup change; never restart their session or change settings automatically.

## Manual fallback

State what completed, what remains incomplete, which access was blocked, and whether the user declined, host policy forbids escalation, or automatic review rejected the action. Preserve the old installation, downloaded package, external configuration, and any recoverable generated result. Verify their state before claiming they were preserved. Report a preserved backup path if rollback failed.

Give commands for the user's own local terminal, outside the restricted agent sandbox. Resolve every placeholder below to a verified actual path and shell-quote paths and the prompt safely. Preserve the current environment and configuration overrides. If the terminal does not inherit session-only variables, tell the user which variable names are required without displaying their values. Never include API keys in commands, ask for them in chat, or recommend `sudo`, broad `chmod`, or disabling all sandbox protections as a default solution.

### Installation or update

Keep the validated new package at a persistent, accessible path; do not delete staging files while manual recovery is pending. Supply the new package's installer command, then the configuration check to run only after installation succeeds:

```bash
python3 "<downloaded-skill-dir>/scripts/install_skill.py" --dest "<actual-skill-directory>"
```

```bash
python3 "<actual-skill-directory>/scripts/image_gen.py" check
```

Use the downloaded version's installer, since an old installation may not include it. If downloading was also blocked, supply a concrete staging command using the built-in helper from [install.md](install.md), followed by the two commands above with matching resolved paths. Do not report an update as complete merely because downloading or a check of the old installation succeeded.

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
