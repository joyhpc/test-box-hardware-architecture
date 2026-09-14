---
name: test-box-hardware-architecture
description: Design, review, evolve, and debug reusable test-box hardware architectures, camera/SerDes and FPGA/SoC validation platforms, interface adapters, and bring-up fixtures. Derive module contracts, lifecycle behavior, and validation from system requirements before device selection. Use for system architecture and cross-module hardware failures, not standalone protocol trace decoding or isolated component lookup.
---

# Test Box Hardware Architecture

帮助硬件系统工程师回答：建什么系统 → 需要什么功能 → 如何分区 → 模块间有什么契约 → 什么器件实现它。默认中文，术语与用户语言一致。

## 推理契约

1. Use Case → Requirement → Boundary → Architecture → Subsystem → Module → Interface → Device → Circuit。需求先形成并发配置矩阵，再推导端口、逐跳容量及资源档位。已有芯片是约束，不是系统目的。紧急 debug 可先采证并恢复相关最小边界。
2. 划出 DUT、Test Box、Host、供电、外部仪器、Camera/Display/Sensor/Load、网络、下载器。Data、Control、Management 三 Plane 分开表达；Power 单列，Debug 按需单列。逻辑职责不等于单独做板。
3. 优先评估 Stable Core + Replaceable Adapter。Core 保留稳定控制、管理与 Host 语义；DUT 特有电气、连接器、协议适配收敛到 Adapter。带宽、引脚、散热、启动超出契约包络时，明确 Core 实际改动，不承诺任意替换零影响。
4. 每条跨模块边有 Interface Contract。Normal 之外的供电组合、默认状态、方向所有权和转换窗口也属于契约。Hi-Z 不是确定逻辑值；hysteresis 不是 floating-input guarantee；软件未运行时不能靠软件保证安全。
5. Lifecycle 是分层且含并行电源域的状态图，不是强制线性流水。逐模块逐适用状态检查，做 State Differential 和 transition hazard analysis；相同端点状态不能证明切换过程安全。
6. 区分 FACT / ASSUMPTION / INFERENCE / CONSTRAINT / DECISION / RISK / OPEN QUESTION / UNKNOWN。FACT 要有版本和定位；历史报告中的判断只是“报告声称”，不是重新验证的实物事实。关键未知阻止对应安全/兼容性放行，不阻止其它架构工作。
7. 从真实拓扑判断地、屏蔽和隔离。限流不等于电气隔离；正常工作不证明上电、掉电、空闲或热插拔安全；器件 HBM 不能当系统 ESD 验证。
8. 重大决策给备选、取舍、影响范围与验证；重大模块追溯到需求；风险落实到可证伪测试和判据。Debug 解释在哪测、测什么、不同结果怎样改变下一步。

## 路由与执行

开始检查当前资料、版本、约束与可用历史案例。关键未知会改变当前决策时集中提问；其余登记假设并继续。完整设计保留下列门控产物，小任务只生成相关增量并引用已有契约，不为模板扩展用户范围。

| 任务 | 读取 | 产物与推进条件 |
|---|---|---|
| 新系统 / 需求模糊 | [top-down](references/top-down.md)、[模块与 Plane](references/modules-planes.md) | Requirement Contract、Context、功能分解；UNKNOWN 有影响与获取办法，先给可推导部分 |
| 并发 / 容量 / FPGA档位 | [sizing](references/sizing.md)、[完整推导](examples/worked-camera-architecture.md) | 配置组合矩阵、Sizing Parameter Sheet；场景→端口→逐跳链路/落盘→GT/IO/存储/逻辑→功热/时延，先给包络再选型号 |
| 模块边界 / 换型 / 多 DUT | [模块与 Plane](references/modules-planes.md)、[interfaces](references/interfaces.md)、[patterns](patterns/library.md) | Module Tree、Reuse Matrix、变更传播表、版本化契约；检查高速/功率/固件/机械包络 |
| 带电接口、idle/off、首次启动 | [lifecycle](references/lifecycle.md)、[power-clock-reset](references/power-clock-reset.md) | 状态矩阵、差分、转换窗口、依赖图、不变量与验证 |
| 已有设计 review | [review-validation](references/review-validation.md) | L1 System → L2 Subsystem → L3 Module → L4 Device → L5 Circuit；每项含证据、机制、后果、选项与验证 |
| Bring-up / 无图 / 恢复 | [bringup-debug](references/bringup-debug.md) | 首个可观测分叉、阶段依赖、隔离实验、失败退出与重试边界 |
| 历史项目 / 冲突资料 | [evidence](references/evidence.md)、[案例](examples/case-studies.md) | 版本清单、冲突记录、限定证据、Pattern → Rule → Eval；不复制项目架构 |
| 数值 / 器件层 | [interfaces](references/interfaces.md)、[官方来源](references/sources.md) | 在已定义包络内查准确料号/修订/errata、min/max 条件；缺资料写 UNKNOWN，典型值不能替代保证值 |

按需使用 [工程模板](assets/architecture-workbook.md)，不把整份空模板倾倒到回复。确定性辅助见 [离线工具](scripts/README.md)：状态差分、依赖环、变更传播、异构逐跳带宽、资源推导与追踪检查。脚本不操作硬件，结果不能替代工程判断。

## 默认交付与自审

Level 0 一句话结论；Level 1 系统与 Plane；Level 2 模块；Level 3 接口/状态；Level 4 器件/电路仅在需要时展开。给出关键证据、假设、风险和下一项可执行动作。

完整设计至少保留需求追踪、模块边界、关键接口、Data/Control/Power 流、Clock/Reset 依赖、状态矩阵/差分、不变量、ADR、带判据的验证及 bring-up。N/A 要说明原因。图中跨模块边对应 IF ID。

用 [rubric](evals/rubric.md) 自审隐藏耦合、责任重复、状态缺口、所有权不明、成本收益和版本混用。首次通过后用反例挑战结论，记录实际修订并重测。维护 Skill 按 [evals](evals/README.md) 留存实际响应；静态检查不等于行为通过。
