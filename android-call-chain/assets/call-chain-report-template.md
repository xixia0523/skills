# `<API>` 调用链（`<baseline>`）

> 结论：`<SOURCE-CLOSED | CONTRACT-CLOSED | OPEN-GAP>`  
> 分析对象：`<准确类、方法签名或调用代码>`  
> 生成日期：`<YYYY-MM-DD>`

## 1. 范围与源码基线

### 调用场景

`<调用位置、关键参数、用户/设备状态，以及不在范围内的初始化链或远端内部实现>`

### 基线清单

| 组件/仓库 | Tag / Build ID | Commit | 产品配置或来源 | 用途 |
|---|---|---|---|---|
| `<repo>` | `<tag>` | `<full commit>` | `<manifest/fingerprint/artifact>` | `<本链覆盖范围>` |

### 前置条件

- `<权限、feature flag、service/HAL 实例、初始化或缓存状态>`

## 2. 唯一主链

```mermaid
sequenceDiagram
    participant A as `<调用方进程 / 线程>`
    participant B as `<服务进程 / Binder worker>`
    A->>B: R1 `<请求>`
    B-->>A: S1 `<结果或 callback>`
```

`<用一段话说明为何该基线与前置条件只选择这条实现；必要时简述其他分支的排除依据。>`

## 3. 请求链

### R1. `<caller>` -> `<callee>`

- 位置：`<repo@commit:path:line, symbol>`
- 执行：`<源进程/上下文>` -> `<切换机制>` -> `<目标进程/上下文>`；`<同步性>`
- 数据：`<参数及关键变化>`
- 说明：`<这一跳如何把请求推进到下一责任层>`

`<按 R2、R3... 继续，直至语义责任终点。>`

## 4. 响应链

### S1. `<result source>` -> `<observer>`

- 位置：`<repo@commit:path:line, symbol>`
- 执行：`<源进程/上下文>` -> `<reply/callback/Handler/Executor/...>` -> `<目标进程/上下文>`
- 数据：`<返回值、错误或状态如何转换>`
- 说明：`<调用方在何处观察到完成>`

`<按 S2、S3... 继续，直至原调用方的可观察结果。>`

## 5. 失败、取消与清理

| 情形 | 触发点 | 传播/完成语义 | 清理或恢复 | 证据步骤 |
|---|---|---|---|---|
| `<权限拒绝/超时/取消/死亡/...>` | `<symbol>` | `<exception/error/callback/state>` | `<unlink/release/remove/...>` | `<E1>` |

## 6. 底层概念简释

- **`<概念>`**：`<只解释理解本链必需的 Binder/JNI/HAL/驱动等概念，并对应具体步骤。>`

## 7. 证据账本

| ID | 方向 | Caller -> Callee | 源进程 | 源线程/上下文 | 切换机制 | 目标进程 | 目标线程/上下文 | 同步性 | 数据变化 | 源码 URL | Commit | 文件 | 符号 | 行号 | 证据类型 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `R1` | 请求 | `<caller -> callee>` | `<process>` | `<context>` | `<direct/Binder/Handler/JNI/...>` | `<process>` | `<context>` | `<sync/async/oneway>` | `<input -> output>` | `<commit-pinned URL>` | `<commit>` | `<path>` | `<symbol>` | `<line>` | `<SOURCE/CONTRACT/BINARY/RUNTIME/CORROBORATION>` |
| `S1` | 响应 | `<caller -> observer>` | `<process>` | `<context>` | `<reply/callback/...>` | `<process>` | `<context>` | `<sync/async>` | `<result transformation>` | `<commit-pinned URL>` | `<commit>` | `<path>` | `<symbol>` | `<line>` | `<type>` |

## 8. 旁证与限制

### 动态旁证

- `<设备 fingerprint、命令/trace、观察结果；没有匹配设备时写“未使用，不影响静态证据审计”。>`

### 已知缺口

- `<缺失实现/契约、受影响步骤和仍可确认的范围；无缺口时写“无”。>`

## 9. 闭环结论

**等级：`<SOURCE-CLOSED | CONTRACT-CLOSED | OPEN-GAP>`**

`<说明请求如何到达责任终点、结果如何回到调用方，以及决定该等级的最弱关键证据。>`
