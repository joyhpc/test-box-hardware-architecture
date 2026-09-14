# 从需求到实现

## Requirement Contract

用途还必须推出量：从产线节拍/工位/golden/复用约束形成配置组合矩阵，确定物理端口并集和逐场景并发；然后沿需求终点做逐跳预算与资源容量推导。模板保留 Sizing Parameter Sheet；见 [sizing](sizing.md)。在组合未定义时不发吞吐结论，在容量链未闭合时不发器件档位。

先写操作人、系统目的和 DUT 在真实系统中的角色。Camera Test Box 可能接收真 Camera、模拟 Camera 给域控、桥接、录制回放或做产线判定，这些用例不可混写。

每项 REQ 用“条件 X 下，系统应执行 Y，达到 Z，采用 V 验证”表达。记录来源、优先级、适用配置、负责人和验收值来源。未知值写 UNKNOWN；估计值有 ASSUMPTION ID、影响和获取办法。

| 需求域 | 契约内容 |
|---|---|
| DUT / 目的 | DUT角色；Functional/Bring-up/Production/EMC/Reliability/Debug/Demo/Software/Regression/Automation；谁决定合格 |
| 信号 | 源/汇/模拟/透明转发，协议版本、格式、分辨率、帧率、lane、并发、峰值、线缆/连接器 |
| 供电 | 各端点源/负载角色，电压范围，稳态/启动/瞬态，测量精度与带宽，保护、掉电/热插拔 |
| 操作 | Host OS、自动化/API/GUI/按钮、控制权限、离线运行、Host 断联、数据保存 |
| 环境 | 实验室/产线/客户/暗室/车辆，温湿度、接地、线长、ESD/EMC 条件及适用标准版本 |
| 观察 / 注入 | 必须看到的状态、日志保留；允许注入的故障、能量和恢复范围 |
| 工程约束 | 台数、进度、预算、维护、校准、寿命、采购、升级与复用频率 |
| 复用 | 具体下一种 DUT 和候选差异，不能只写“未来扩展” |

## 等级是裁剪工具

| 等级 | 目标 | 基础投入 | 有条件增加 |
|---|---|---|---|
| A Simple Fixture | 被动适配/低复杂度 | pin map、防误插、额定值、基础测试点 | 保护按风险；无需强制 MCU |
| B Engineering Debug Box | 少量实验室调试 | 可恢复控制、可测电源、debug、标识 | 日志/自动化按工作量 |
| C Reusable Validation Platform | 多 DUT / 回归 | 稳定契约、适配身份、版本兼容、故障隔离、可复现实验 | 时间同步、校准、远程管理按需求 |
| D Production Test Equipment | 节拍/可追溯判定 | 治具寿命、校准不确定度、适用的量测 GR&R、审计记录与维修 | 冗余由停机成本决定，D 不自动等于双 PSU |

电气与安全边界不因等级低而删除；文档、软件、冗余和自动化深度可裁剪。

## 推导与门控

1. Context：列系统内外、供电/接地/屏蔽关系，标 Host 控制与数据是否共享介质。
2. Function：分解采集、生成、转换、路由、缓冲、配置、供电、测量、记录、恢复。每项 FUNC 引用 REQ。
3. Subsystem：按 Plane 和物理空间组织功能，一个模块可承担多 Plane，但所有权清楚。
4. Module：按变化频率、启动依赖、故障边界、电压域、高速损耗、制造服务成本划界；写存在理由、职责与边界。
5. Interface：先形成物理/电气/时序/协议/状态/机械/软件兼容包络再选芯片。冻结意为有版本和变更管理，不是永不改变。
6. Implementation：候选能力映射契约，核 min/max、温度、供电、封装、时序、errata；计算与布局约束绑定来源。
7. Validation：从 REQ 和风险推回条件、测量位置、定量或可判定准则；只有“做测试”不算闭环。

追踪链：REQ → FUNC → MOD → IF → IMP → VAL；额外链接 RISK、ADR、STATE。重大模块不能仅因旧版已有而保留。

ADR：Context → Options → Decision → Rationale → Trade-offs → Risks → Validation → Revisit trigger。例如 MCU 是否必要取决于 FPGA 配置前是否需维护供电/日志/Host；简单 supervisor 足够时无需第二处理器。
