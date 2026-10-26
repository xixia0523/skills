# 源码路由

先判断每一段实现归属，再选择取证位置。目标是得到与指定版本、产品和配置一致的生产源码，而不是找到名称相似的最新代码。

## 基线解析

1. 精确 tag：先在平台 manifest 或对应官方仓库中核实 tag 存在，再解析实际取证仓库的清单 revision/tag 对应的 commit；报告同时记录 tag 与 commit。
2. Build ID：从官方 build/tag 对照或该产品的 manifest 固定到源码清单；无法唯一映射时明确缺口并索取完整 build fingerprint、manifest 或厂商版本信息。
3. Android 大版本：从官方[版本、标签与 Build ID 表](https://source.android.com/docs/setup/reference/build-numbers)确认该版本的基础源码发布，再在官方仓库核实 tag 并解析各取证仓库的清单 revision/tag 与 commit。不能按多数版本的命名规律直接拼接 `android-<major>.0.0_r1`，例如 Android 4 的基础发布标签是 `android-4.0.1_r1`。用户给出的次版本或季度版本属于基线约束，不能退回该大版本的另一个基础发布。无法确认标签或解析 revision 时说明未锁定的部分，不擅自切换到最新版本或其他仓库的相似标签。
4. 产品构建：以该构建的 manifest、repo revision、内核 commit、Vendor 配置和 overlay 为准。AOSP 基础 tag 不能替代产品实际 revision。

禁止把 `main`、`master`、`android-latest-release` 或网页当前版本作为固定基线。引用 tag 便于阅读，但证据 URL 应固定到不可变 commit。

## AOSP 平台

- 优先使用 `android.googlesource.com` 的生产仓库和 Gitiles commit 固定链接；Android Code Search 可用于定位符号，但最终核对指定基线。
- 先从调用点所在模块查找实际依赖，再跨仓库追踪；不要假设同名类属于相同进程或版本。
- 用 build 文件、manifest、资源 overlay、service 注册和 feature flag 确认被编译与被选择的实现。
- AIDL 的生成代码可依据接口和生成规则解释，不需要粘贴整份生成物；主链所经过的 client proxy、server stub/实现及约定的返回/通知均需定位。若本次范围只到投递确认，不能据此推定服务端已执行。

## Kernel 与驱动

- GKI/common kernel 使用与产品基线匹配的官方 kernel tag 或 commit。
- 设备内核、模块和 Vendor driver 以产品实际源码/commit 为准；不能用 common kernel 的相似实现代替。
- 从 native wrapper 或 syscall 继续追踪时，证明 syscall/ioctl/netlink/file operation 的用户态发起点与内核入口/回调两端。
- 若固件或内核实现闭源，以正式 UAPI、头文件、协议或厂商接口契约封口；没有契约则保留 `OPEN-GAP`。

## HAL 与 Vendor

- 先确定实际传输与版本：AIDL 或 HIDL、binderized 或 passthrough、接口版本、实例名和选中实现。
- 使用 VINTF manifest、compatibility matrix、service 注册、构建配置、属性和设备事实锁定实现。
- AOSP 默认实现只能证明使用它的产品；不能自动代表 Vendor 实现。
- Vendor 闭源时可用稳定 AIDL/HIDL、正式头文件或 SDK 契约封口，但结论最多为 `CONTRACT-CLOSED`。
- 无法判断实际 HAL 类型或实例时，索取产品 manifest、`lshal`/service 信息、构建配置或匹配设备输出，不并列编造一条主链。

## 自研框架

- 要求源码根目录或仓库地址以及 commit；多仓库项目记录 manifest/lockfile 和每个相关仓库 revision。
- 从真实调用方使用的依赖和构建变体入手，核对生成代码、开关和产品 overlay。
- 没有固定 revision 时不把本地工作树快照描述为可复现基线；应记录工作树状态或请求 commit。

## 第三方 SDK

按以下优先级取证：

1. 与依赖坐标和版本完全匹配的发布源码或 source JAR；
2. 厂商提供、带版本标识的正式接口文档和 SDK 契约；
3. 对实际 AAR/JAR/SO 的反编译、符号和反汇编分析；
4. 测试、示例、日志或运行 trace。

必须记录依赖坐标、版本、artifact 校验值或来源。反编译结果标为 `BINARY`，不能声称等同于生产源码；混淆、优化或 native 动态分发造成的不可见段必须保留 gap。闭源 SDK 只有在正式接口契约覆盖终点和返回路径时才能达到 `CONTRACT-CLOSED`。

## 在线与本地取证

- 本地已有匹配源码时优先使用，并记录 commit 与工作树状态。
- 在线获取默认选择官方仓库、发布清单和供应商一手资料。下载前遵守当前环境的网络与写入权限。
- 行号必须对应报告中的 commit。若网页行号不稳定，同时记录文件路径、完整符号和 commit，保证可复查。
- 远端服务器、ECU 固件和闭源 Vendor 内部实现默认不展开；以完整正式契约封口，否则明确 gap。
