# Custom Image Generator

使用自己的 OpenAI 兼容服务生成图片。每次生图先读取服务端模型列表，再由用户手动选择模型。

## 标准安装

将下面这一条消息发给 Codex：

```text
$skill-installer install https://github.com/xixia0523/skills/tree/main/Custom_Image_Generator_Skill/custom-imagegen
```

使用 Codex 内置安装器下载和安装，本项目不提供覆盖安装脚本。已有同名 Skill 时停止，由用户手动删除旧 Skill 后重新发送上述标准安装指令。

内置安装器会拒绝已存在的目标目录，但可能先下载再检查，也不会在安装前自动读取仓库中的 Skill 规则。本项目无法改变它的执行顺序。若要求**下载前检查，并在已安装时给出手动删除命令**，请在同一条安装消息中补充：

```text
安装前先检查本地是否已有 custom-imagegen；若有则停止，只给出手动删除命令和标准安装指令，不要自行删除、覆盖、改名或临时安装。
```

Agent 安装流程见 [references/install.md](references/install.md)。

## 已有旧版时手动重装

在本机终端删除旧 Skill。下面适用于默认路径；设置过 `CODEX_HOME` 或自定义安装目录时，应使用 Codex 检查后给出的实际路径：

```bash
rm -rf -- "$HOME/.codex/skills/custom-imagegen"
```

再回到 Codex，重新发送“标准安装”中的 `$skill-installer install ...` 指令。Codex 不执行删除或自动覆盖。

仅删除旧 Skill 目录，保留 `~/.config/custom-imagegen/.env` 等外部配置。已有 API key、服务地址、代理及环境变量继续沿用。若旧配置放在 Skill 内部，删除前应先迁移到外部配置路径。

## 使用

安装完成后，在下一轮消息中发送：

```text
$custom-imagegen 生成一张夏日中国乡村儿童在田野和溪流边玩耍的图片。
```

Skill 查询当前服务端的 `gpt-image-*` 模型，展示列表并等待用户选择，再使用选定模型生成图片。即使只有一个模型也需要选择。沙箱权限导致查询受阻时先请求授权；无法授权、服务端查询失败或没有支持的模型时，提示原因并停止。

首次安装写入、配置读取或生图联网受限时，先通过宿主的审批机制请求所需权限，获准后继续；用户拒绝、自动审批拒绝或策略禁止提权时，停止、说明原因并给出手动操作办法。已有安装始终按上面的手动重装流程处理。详见 [references/permissions.md](references/permissions.md)。

## 环境与配置

需要 Python 3，无第三方 Python 依赖。服务端需提供 `GET /v1/models` 和 `POST /v1/images/generations`，并支持 `gpt-image-*` 模型。

默认配置保存在 `~/.config/custom-imagegen/.env`，CLI 写入权限为 `0600`，支持自定义配置路径和环境变量。详细说明见 [references/setup.md](references/setup.md)。API key 通过本地交互或已有配置文件提供，不在聊天中发送。

Skill 包使用 [Agent Skills 标准结构](https://agentskills.io/specification)，入口为 [SKILL.md](SKILL.md)。
