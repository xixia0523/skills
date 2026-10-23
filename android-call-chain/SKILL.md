---
name: android-call-chain
description: Reconstruct one evidence-backed request-and-return call chain for a pinned Android source version. Use only when the user explicitly invokes $android-call-chain; do not use for ordinary Android or source-code questions.
---

# Android 源码调用链研究

调用链研究只在用户显式输入 `$android-call-chain` 时开展。若本 Skill 被隐式加载而用户没有显式调用，不要套用调用链研究流程。

目标是基于不可变源码基线还原一条实际主链：从用户指定的上层 API 出发，追到承担该调用语义的责任终点，再反向追踪返回值、回调或状态事件，形成可审计闭环。不要把所有可能实现分支罗列成“完整调用链”。

## 安装与更新

用户要求安装或更新本 Skill 时，先阅读 [references/install.md](references/install.md)。在下载或申请安装写入权限前，检查实际目标路径及当前会话报告的同名安装。发现已有安装时停止，给出已核实的绝对路径、供用户在本机终端手动删除该 Skill 的命令，以及删除后重新发送的标准 GitHub 安装消息；不要自行删除、改名、替换、覆盖或通过临时安装绕过冲突，也不要申请删除或替换权限。确认不存在旧安装后，直接使用 Codex 内置 `skill-installer` 安装。

## 输入门禁

开始前必须获得：

- 准确 API 或调用代码，足以确定类、方法和重载；
- Android 版本。

仅在会改变主链选择或证据结论时补问调用场景。自研框架还需要源码位置和 commit；第三方 SDK 还需要依赖坐标及版本，并在可用时取得源码或二进制路径。

版本处理规则：

- 精确 Android tag 或可映射到源码清单的 build ID 优先；
- 只有 Android 大版本时，默认固定到该版本的基础发布 `android-<major>.0.0_r1`；
- 解析并记录实际使用的不可变 commit。多仓库调用链分别记录各仓库 commit，不用浮动分支替代。

如果缺少必填输入，先询问缺失项，不要开始猜测式分析。如果已有信息足以锁定基线，但设备配置、feature flag、HAL 类型或构建事实会在多个实现之间改变实际主链，先做可用的只读检查；仍无法判定时只追问决定分支所需的最小事实。

## 开始分析

每次任务都先阅读：

- [references/source-routing.md](references/source-routing.md)：确定 AOSP、Kernel、Vendor、自研和第三方源码从哪里取证；
- [references/evidence-policy.md](references/evidence-policy.md)：按逐跳标准证明进程、线程、边界和闭环等级；
- [references/source-walkthrough.md](references/source-walkthrough.md)：组织请求与返回每一步的源码摘录、执行时序和阅读续接。

报告以 [assets/call-chain-report-template.md](assets/call-chain-report-template.md) 为起点，按实际链路增删内容，不保留占位符。

## 工作流

1. 锁定准确重载、调用场景、源码归属和版本基线。把初始化链压缩为前置条件，除非它直接决定当前请求的路由或返回语义。
2. 建立源码基线清单。所有源码链接固定到 commit；tag、build ID、设备 fingerprint 和配置事实另列，不能互相替代。
3. 从生产代码的调用点向下追踪。结合源码配置、运行时 flag 和设备事实选出唯一主链。未选分支只说明排除依据，不并列展开。
4. 为每一跳记录调用双方、参数或数据形态变化、同步性、进程、源执行上下文、切换机制和目标执行上下文。在每个 R/S 步骤中给出对应源码调用片段，按调用下潜或返回恢复顺序展示调用点与必要实现，并解释关键语句和下一步入口。
5. 遇到 Binder、Handler、Executor、JNI、HAL、socket 或 syscall 边界时，必须分别给出边界两端证据。不能只因命名、架构常识或相邻层接口而补出中间箭头。
6. 按 API 语义选择责任终点：纯本地 API 可止于权威本地实现；系统状态止于权威系统服务；硬件操作止于可证明的驱动/固件实现或正式契约；网络调用止于设备侧请求与服务端响应契约。不要为了“完整”强行追到内核。
7. 从责任终点反向追踪结果。明确它是同步返回、Binder reply、callback、Future、广播还是状态事件，并追到调用方可观察结果的位置。
8. 只补充会改变完成语义的异常、权限拒绝、超时、取消、进程死亡、Binder death 和资源清理路径。
9. 审计主链中每一条箭头，核对各步骤源码片段的覆盖、版本、截取上下文和时序，填完证据账本，并按证据策略给出 `SOURCE-CLOSED`、`CONTRACT-CLOSED` 或 `OPEN-GAP`。
10. 有匹配设备时，可用 adb、日志或 Perfetto 验证分支与时序；没有真机也应完成静态分析。动态结果只作旁证，不能替代源码证据。

## 主链纪律

- 正文只呈现与指定基线和前置条件一致的一条主链。
- 若静态源码无法区分 AIDL/HIDL、binderized/passthrough、不同 HAL 或 feature flag，实现分支尚未锁定；不要任意挑选。
- 无法证明的跳转明确标为 gap，不用测试、文档、trace 或反编译结果伪装成生产源码。
- 静态源码不能证明具体线程 ID 时，只写可证明的执行上下文，例如“调用线程”“Binder worker”“主 Looper”或“指定 Executor”。
- 初始化、缓存命中、懒加载和异步排队等前置状态必须与主链假设一致。

## 输出

默认使用中文，源码符号保持原文。将完整报告写入当前工作区：

```text
docs/call-chains/<api>-<baseline>.md
```

`<api>` 使用可辨识的 `Class.method`，文件名中的其他不安全字符替换为 `-`；`<baseline>` 使用解析后的 tag，若只有 commit 则用其短哈希。报告至少包含源码基线、前置条件、唯一主链时序图、请求链、响应链、失败与清理、底层概念简释、证据账本和闭环结论。

请求链和响应链默认采用逐步源码导读：每个步骤配有对应的源码调用、固定版本出处、关键数据说明及后续步骤或返回续接位置。源码不可见的部分明确展示可用契约与缺口，按证据策略定级。具体组织方式见 [source-walkthrough.md](references/source-walkthrough.md)。

对话中只返回主链摘要、闭环等级、关键 gap（如有）和报告路径。不要只在对话中给出分析而省略报告文件。
