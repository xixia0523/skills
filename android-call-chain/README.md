# Android 源码调用链研究

固定 Android 源码版本，从指定 API 追踪唯一请求主链及返回闭环，并将有源码证据的完整报告写入工作区。

## 从 GitHub 安装

将下面这条消息发给 Codex；其中的检查要求会让 Agent 在下载前检查旧安装：

```text
$skill-installer install https://github.com/xixia0523/skills/tree/main/android-call-chain
安装前先检查本地是否已有 android-call-chain；若有则停止，给出实际路径、手动删除命令和标准安装指令，不要自行删除、覆盖、改名或临时安装。
```

使用 Codex 内置安装器，默认安装到 `~/.codex/skills/android-call-chain`；设置了 `CODEX_HOME` 或显式目标时使用实际路径。已有安装由用户手动删除，再发送同样的安装请求。

标准安装消息也可以单独发送第一行，但内置安装器可能先下载再报告目标冲突，不会在安装前自动执行仓库中的检查规则。完整流程见 [references/install.md](references/install.md)。GitHub 安装使用远端 `main` 内容，本地修改需提交并推送后才会生效。

## 使用

安装后，在下一轮消息中显式调用，并提供准确 API 或调用代码以及 Android 版本，例如：

```text
$android-call-chain 分析 Android 16 中 Context.getSystemService(String) 的请求和返回调用链。
```

Skill 仅在显式调用时开展源码研究。完整报告默认保存到 `docs/call-chains/<api>-<baseline>.md`，具体输入和证据要求见 [SKILL.md](SKILL.md)。
