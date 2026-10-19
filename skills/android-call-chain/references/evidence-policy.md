# 证据与闭环策略

报告的基本单位不是“找到一个同名符号”，而是一条有方向的调用箭头。每条主链箭头都必须能回答：谁在何处以什么数据调用谁，是否跨边界，在哪个执行上下文继续，结果如何回来。

## 证据等级

从强到弱使用以下类型，并在账本中明确标注：

- `SOURCE`：固定 commit 的生产源码、生成接口源码或构建配置；用于证明实际调用与实现。
- `CONTRACT`：固定版本的 AIDL/HIDL、UAPI/正式头文件、稳定 SDK 或协议契约；用于封闭不可见实现边界。
- `BINARY`：与目标版本匹配的 AAR/JAR/SO 反编译、符号或反汇编；只能作降级证据。
- `RUNTIME`：adb、日志、Perfetto、binder trace 或设备状态；用于确认选路和时序。
- `CORROBORATION`：测试、示例和说明文档；只作旁证。

架构常识、命名相似和非目标版本源码不构成该箭头的证据。`RUNTIME`、`CORROBORATION` 不能替代缺失的 `SOURCE` 或 `CONTRACT`。

## 逐跳证明

普通函数调用至少记录调用方的 call site，以及被调用方的声明或实现；若动态分派决定主链，还要证明实际接收者。参数重命名可简写，但跨序列化、单位换算、坐标变换、ID 映射、缓存或聚合时必须写明数据变化。

每条证据记录：

- 步骤 ID 与方向（请求/响应）；
- caller 与 callee 的完整符号；
- 源进程和目标进程；
- 源执行上下文、切换机制、目标执行上下文；
- 同步、异步、oneway 或阻塞等待语义；
- 输入/输出及关键数据变化；
- 固定源码 URL、仓库 commit、文件、符号、行号和证据类型。

一条箭头涉及多个源码点时，可在同一账本行列出多条证据，也可拆成连续步骤，但不能把未证明的中间层压成一个箭头。

## 边界证明

### Binder

同时证明 client call/proxy、AIDL/HIDL transaction 或接口定义、server stub/实现，以及 reply/callback 的反向入口。同步 Binder 调用通常由 client 调用线程阻塞等待、server Binder worker 执行；`oneway`、线程池配置或实现再次投递会改变语义，必须以目标版本代码为准。callback 到 client stub 后若再投递 Handler/Executor，分开记录两次切换。

### Handler、Looper 与 Executor

给出 `post`/`sendMessage`/`execute`/调度点和实际 handler、looper、executor 或调度器的来源。无法静态确定具体线程时，只写“主 Looper”“指定 Executor”“Binder worker”“调用线程”等可证明上下文，不猜线程名或线程 ID。

### JNI

同时证明 Java/Kotlin native 声明、静态/动态注册映射和 native 实现。动态注册需定位注册表与加载路径；只有同名 native 符号不足以证明映射。

### HAL

证明 framework/native client 选择的接口版本与实例、transport 边界和实际 service/implementation。若只能看到稳定 AIDL/HIDL 契约而实现闭源，在请求与返回方法均被契约覆盖时以 `CONTRACT` 封口。

### Syscall、socket 与驱动

同时证明用户态发起点和内核入口、驱动 file operation、协议端点或正式 UAPI。一次 `ioctl` 或 socket write 不是天然终点；终点取决于 API 承诺的语义。若内核、固件或远端只可通过契约观察，按契约覆盖范围决定是否闭环。

## 进程与线程判断

进程归属应来自 manifest `android:process`、service 发布/查找、启动代码、进程入口、设备 service 列表或等价生产配置。包名、目录名和类名本身不能证明进程。

线程沿调用栈保持不变，直到出现有证据的调度或 IPC 边界。静态证据通常只能证明执行上下文类别，不能证明某次运行的线程 ID。Binder、Looper 和 Executor 的默认行为也必须与该版本实现及配置一致。

## 责任终点与返回闭环

责任终点由 API 对调用方承诺的可观察语义决定：

- 纯计算、本地缓存或进程内状态：产生权威结果的本地实现；
- 系统管理 API：拥有权威状态或执行动作的系统服务；
- 硬件 API：被选中的 HAL/驱动/固件实现，或覆盖该语义的正式接口契约；
- 网络/远端 API：设备侧发出的最终请求以及把远端响应交回本地的正式协议/SDK 契约。

到达终点后必须反向证明调用方实际观察到的完成信号。同步返回追踪 return/reply；异步调用追踪 callback、Future completion、广播或状态事件。仅证明请求已发送不算闭环。

## 闭环等级

- `SOURCE-CLOSED`：选定主链的请求与返回全部由固定版本生产源码证明，边界两端没有实质缺口。
- `CONTRACT-CLOSED`：请求与返回链完整，但至少一个闭源边界只能由匹配版本的正式接口契约封口。
- `OPEN-GAP`：责任终点、实际分支、任一关键箭头或返回路径既无足够源码，也无完整正式契约。

`BINARY` 可以缩小 gap，不能单独提升为 `SOURCE-CLOSED`；仅有运行 trace、测试或文档时仍为 `OPEN-GAP`。结论按整条链最弱的关键证据定级，并逐项列出 gap 对可确认结论的影响。

## 完成前审计

- 时序图每条主链箭头都有证据账本步骤 ID。
- 请求链到达语义责任终点，响应链回到调用方可观察点。
- 每次跨进程、跨线程、托管/原生、用户态/内核态边界都有两端证据。
- 进程、线程、同步性和数据变化没有超出证据。
- 选定基线中的配置与 flag 足以排除其他实现；否则已补问或标记 gap。
- 异常、超时、取消、死亡和清理只覆盖会改变完成语义的路径。
- 所有源码引用都含仓库、commit、文件、符号和对应行号；动态证据与静态证据分栏说明。
