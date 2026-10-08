
# Custom Image Generator Skill

这是一个可移植的 Codex/AI agent 生图 skill。它通过用户自己的 OpenAI 兼容 Images API 生成图片，并在触发后避开系统 `imagegen` skill。

## 交给 AI agent 的安装要求

将完整的 `custom-imagegen` 文件夹或分享压缩包交给 agent，并告诉它：

```text
安装这个 custom-imagegen skill，按其中的 SKILL.md 和 references/setup.md 完成配置检查。以后生成新图片时使用 $custom-imagegen，不使用系统 imagegen。不要让我在聊天中粘贴 API key。
```

Agent 应将整个目录安装到它的 skills 目录，例如：

```text
~/.codex/skills/custom-imagegen
```

安装后可能需要开启新会话，让 agent 重新发现 skill。

## 接收者需要准备

- Python 3，无需安装第三方 Python 包。
- 一个实现了 `POST /v1/images/generations` 的 OpenAI 兼容服务。
- 该服务的 base URL、API key，以及可用的 `gpt-image-*` 模型。

推荐运行交互式配置，API key 不会出现在命令历史中：

```bash
python3 ~/.codex/skills/custom-imagegen/scripts/image_gen.py configure
```

默认配置文件为 `~/.config/custom-imagegen/.env`，权限为 `0600`。也可以让 agent 从已有配置导入，只需提供文件路径，不要在聊天中发送文件内容：

```bash
python3 ~/.codex/skills/custom-imagegen/scripts/image_gen.py configure \
  --from-env-file "/path/to/existing/.env"
```

配置文件格式：

```dotenv
OPENAI_API_KEY=<接收者自己的 key>
AI_BASE_URL=https://provider.example/v1
```

配置不能放进 skill 文件夹，也不能打进分享包。每位接收者必须使用自己的 key。

验证配置：

```bash
python3 ~/.codex/skills/custom-imagegen/scripts/image_gen.py check
```

验证完成后可在新会话中使用：

```text
$custom-imagegen 生成一张春节厨房做饭图片
```

完整配置方式和错误处理见 `references/setup.md`。
