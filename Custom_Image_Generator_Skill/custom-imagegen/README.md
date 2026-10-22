# Custom Image Generator

符合 [Agent Skills 规范](https://agentskills.io/specification) 的独立生图 Skill 包。完整保留本目录，入口为 [SKILL.md](SKILL.md)，配置说明为 [references/setup.md](references/setup.md)。

## 安装

将本目录交给 Agent，并告诉它：

```text
使用包内 scripts/install_skill.py 安装或更新 custom-imagegen Skill；已安装时覆盖旧版并沿用已有外部配置和环境变量。
安装后运行 image_gen.py check，配置有效时直接使用。
不要让我在聊天中粘贴 API key。以后生成新图片时使用 $custom-imagegen。
```

通过 GitHub 链接交给 Agent 安装或更新：

```text
从 https://github.com/xixia0523/skills/tree/main/Custom_Image_Generator_Skill/custom-imagegen 下载最新 Skill 到临时目录，
运行新版 scripts/install_skill.py；若已安装则覆盖旧版，保留已有 API key、服务地址及相关环境配置。
安装后检查配置，有效时直接沿用，不重新配置，不要让我在聊天中粘贴 API key。
```

也可以在终端执行：

```bash
custom_imagegen_checkout="$(mktemp -d)"
git clone --depth 1 --branch main https://github.com/xixia0523/skills.git "$custom_imagegen_checkout/skills"
python3 "$custom_imagegen_checkout/skills/Custom_Image_Generator_Skill/custom-imagegen/scripts/install_skill.py"
```

默认安装到 `$CODEX_HOME/skills/custom-imagegen`，未设置 `CODEX_HOME` 时为 `~/.codex/skills/custom-imagegen`。同一命令兼顾首次安装和覆盖更新；先校验新版，替换失败时恢复旧版。完整流程见 [安装与更新说明](references/install.md)。

## 配置

需要 Python 3，无第三方 Python 依赖。服务端必须提供 `GET /v1/models` 和 `POST /v1/images/generations`，并支持 `gpt-image-*` 模型。

首次使用时先检查配置；安装后也可将脚本路径替换为安装位置：

```bash
python3 scripts/image_gen.py check
python3 scripts/image_gen.py models
```

检查通过时直接沿用原配置。只有配置缺失或无效时，才运行 `python3 scripts/image_gen.py configure`。

`configure` 通过本地交互读取 API key；默认配置保存在 `~/.config/custom-imagegen/.env`，CLI 写入权限为 `0600`。导入已有配置、环境变量和错误处理见 [配置说明](references/setup.md)。每位使用者提供自己的配置，配置文件不放在本目录。

## 使用

```text
$custom-imagegen 生成一张夏日中国乡村儿童在田野和溪流边玩耍的图片。
```

Skill 每次先读取服务端支持的 `gpt-image-*` 模型，展示列表并等待用户选择，再使用选定模型生图。即使只有一个模型也需要选择；查询失败或没有支持的模型时提示并停止。
