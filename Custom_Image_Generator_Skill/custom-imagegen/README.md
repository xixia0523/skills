# Custom Image Generator

使用自己的 OpenAI 兼容服务生成图片。每次生图先读取服务端模型列表，再由用户手动选择模型。

## 一条消息安装或更新

将下面这一条消息发给 Codex：

```text
$skill-installer https://github.com/xixia0523/skills/tree/main/Custom_Image_Generator_Skill/custom-imagegen 安装或覆盖更新，沿用现有环境配置并检查；权限不足时先请求授权，无法授权则停止、说明原因并给出手动操作命令。
```

Codex 负责下载、安装或覆盖更新，以及检查现有配置。正常情况下无需手动克隆仓库或运行安装脚本。已有 API key、服务地址、代理及外部配置继续沿用；配置有效时直接使用，首次缺少配置时只需按提示在本地录入自己的服务地址和 API key。

安装写入、配置读取或生图联网受限时，Codex 会先通过宿主的审批机制请求本次操作所需权限，获准后继续。用户拒绝、自动审批拒绝或宿主策略禁止提权时，停止受阻操作，说明具体原因并给出带实际路径的手动命令。宿主决定审批是交给用户还是自动审核；Skill 无法覆盖宿主策略。详见 [references/permissions.md](references/permissions.md)。

内置 `$skill-installer` 会在目标目录已存在时退出，也不会自动运行仓库里的安装或配置脚本。因此，上面消息中的“覆盖、沿用配置、检查配置”是交给 Codex 的明确任务；只提供 Skill 名称和 URL，无法保证完成这些额外步骤。

Agent 安装流程见 [references/install.md](references/install.md)。

## 使用

安装完成后，在下一轮消息中发送：

```text
$custom-imagegen 生成一张夏日中国乡村儿童在田野和溪流边玩耍的图片。
```

Skill 查询当前服务端的 `gpt-image-*` 模型，展示列表并等待用户选择，再使用选定模型生成图片。即使只有一个模型也需要选择。沙箱权限导致查询受阻时先请求授权；无法授权、服务端查询失败或没有支持的模型时，提示原因并停止。

## 环境与配置

需要 Python 3，无第三方 Python 依赖。服务端需提供 `GET /v1/models` 和 `POST /v1/images/generations`，并支持 `gpt-image-*` 模型。

默认配置保存在 `~/.config/custom-imagegen/.env`，CLI 写入权限为 `0600`，支持自定义配置路径和环境变量。详细说明见 [references/setup.md](references/setup.md)。API key 通过本地交互或已有配置文件提供，不在聊天中发送。

Skill 包使用 [Agent Skills 标准结构](https://agentskills.io/specification)，入口为 [SKILL.md](SKILL.md)。
