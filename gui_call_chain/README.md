# Android Callchain Closure

从 Android Demo 中指定的 API 调用或第三方框架回调出发，追踪 App → Framework → Native/HAL → 内核/驱动边界，生成一份可逐跳核验的中文 Markdown 文档。文档包含唯一总览时序图、源码链接，以及每跳的进程、线程和同步/异步语义；内核层只做有来源的概念讲解。

本目录按 [OpenAI 官方 Skill 格式](https://learn.chatgpt.com/docs/build-skills)组织，可作为 GitHub 仓库中的独立 Skill 目录分发。`SKILL.md` 是入口，`agents/openai.yaml` 是可选的 Codex 界面元数据；无运行脚本或 API Key 依赖。

## 文件

```text
gui_call_chain/
├── README.md
└── android-callchain-closure/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    └── references/
        └── report-template.md
```

- [SKILL.md](android-callchain-closure/SKILL.md)：触发描述、输入门槛、源码规则、A/B/C 编排与验收。
- [报告模板](android-callchain-closure/references/report-template.md)：最终单一 Markdown 文档的 §0–§6 结构。
- [Codex 元数据](android-callchain-closure/agents/openai.yaml)：显示名称与默认调用提示；保留默认自动匹配行为。

## 本地使用

将完整的 `android-callchain-closure` 文件夹复制到目标环境的 Skill 搜索目录，保留目录名和相对路径。Codex 的用户级目录为 `~/.agents/skills/`，项目级目录为 `<项目>/.agents/skills/`。在当前目录执行以下命令可安装到用户级目录；若已有同名 Skill，先检查现有内容。

```bash
mkdir -p ~/.agents/skills
cp -R -n android-callchain-closure ~/.agents/skills/
```

安装后，可在 Codex 中调用：

```text
使用 $android-callchain-closure
DEMO_SOURCE: /你的项目/AndroidDemo
TARGET_CALL: app/src/main/java/com/example/demo/MainActivity.kt 中 onClick 内的 vibrator.vibrate(...) 调用
AOSP_VERSION: android-13.0.0_r1
```

上述 tag 仅展示显式指定版本的格式，执行时仍须验证其存在及入口兼容性。省略 `AOSP_VERSION` 时，Skill 会核实并锁定 Android 13 系列最新稳定发布 tag。也可以提供 Demo 仓库地址或代码内容；第三方框架实现依据优先从 Demo 提取。

## 分析边界

- 缺少 `DEMO_SOURCE` 或 `TARGET_CALL` 时，只索取缺失输入，不开始分析。
- 目标涉及的第三方框架必须有可公开访问且能对应依赖版本的源码；校验失败时终止且不产出分析文档。没有第三方框架时，该检查不适用。
- 分层以真实源码路径为准；不经过 HAL 的调用无需构造 HAL 路径。正式追踪时遇到源码缺口，停止该分支并在报告中标明。
- A/B/C 分别负责 App/第三方框架、Framework/Native/HAL、内核概念及交叉校验。有子 Agent 能力时分工执行；没有时按职责顺序执行并披露。
- 执行分析需要读取 Demo、访问官方源码和可靠技术资料；本 Skill 的创建与结构校验不代表已经完成某个 Android 调用的分析。
