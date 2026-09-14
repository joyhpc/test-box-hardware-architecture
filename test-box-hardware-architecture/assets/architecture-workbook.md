# Test Box Architecture Workbook

复制后按项目填写。UNKNOWN是显式未决值，不是完成标志；N/A必须有理由。只输出本次任务需要的表，完整项目保留其它表的链接。

## 0. Baseline / Evidence / Assumptions

私有受控证据库可保留原始文件身份和指纹；下表是可公开的角色索引，不能直接复制私有台账。公开前还须审查内容本身，匿名名称不代表技术细节可公开。

| Source ID | artifact_role | 公开 locator | HW / Assembly / FW别名 | evidence_scope | 状态/取代关系 | 可证明范围 |
|---|---|---|---|---|---|---|
| SRC-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| Claim ID | FACT/ASSUMPTION/INFERENCE/CONSTRAINT/DECISION/RISK/OPEN QUESTION/UNKNOWN | 内容 | 来源 | 影响/owner | 关闭条件 |
|---|---|---|---|---|---|
| ASM-001 | ASSUMPTION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 1. Requirement Contract / Context

一句话目的：UNKNOWN。等级A/B/C/D：UNKNOWN，裁剪理由：UNKNOWN。
系统内：UNKNOWN。系统外：DUT / Host / PSU / Instruments / Camera-Display-Sensor-Load / Network / Debug tools逐项确认。

| REQ ID | DUT角色/用途/接口/供电/控制/环境/观察/注入/复用/成本 | 条件下应完成的功能 | 定量/可判定要求 | 来源/优先级/owner | VAL |
|---|---|---|---|---|---|
| REQ-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

### 1.1 Configuration Combination Matrix

先从节拍、工位、golden 与分时约束确定物理端口并集，再列每种允许同时运行的组合。每跳/每类资源分别找最坏行；五种 profile 不等于五个连接器。多虚拟通道共用一个端口时先给显式聚合模型。

| Scenario / REQ | 工位与DUT数 | Port 1：角色/格式/fps/active | Port 2：角色/格式/fps/active | Golden/loopback/其它端口 | 并发/互斥依据 | 切换与稳定时间 | 数据终点/验收 |
|---|---|---|---|---|---|---|---|
| SC-001 / REQ-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

### 1.2 Sizing Parameter Sheet

数值与区间都标单位、来源/版本及证据类型。推导先后与方法见 [sizing](../references/sizing.md)。所有最坏条件必须可追溯到 scenario。

| Parameter ID / REQ / Scenario | 参数/单位/范围 | FACT/ASSUMPTION等 + 来源/版本 | 推导式/依赖ID | 数值结果与余量 | 最坏条件/失效触发 | Owner / 关闭测试 |
|---|---|---|---|---|---|---|
| SZ-PORT | takt/availability/stations/golden/物理端口并集 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-HOP | 每跳payload/编码/持续capacity/reserve，直到Host落盘 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-GT | 每端口lane/GT类型/速率/Host/回环/预留 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-IO | pin map/VCCIO/Bank class/可用引脚 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-MEM | stall/owner/队列bytes/burst/BRAM或URAM宽深/固定IP/DDR读写 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-LOGIC | 功能×实例×LUT/FF/DSP区间/利用率 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-PVT | datapath clock/speed grade/布局与PVT门控 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-POWER | rail/PoC/转换损耗/输入额定/机内热/结温 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-LATENCY | 起止事件/关键路径/排队与尾延迟 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| SZ-REUSE | 变体数/独立开发/Core+Adapter/维护/回本点 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

候选档位比较：GT拓扑/Bank下界、逻辑容量区间、存储备选、功热包络、speed grade与封装未决项。未形成并发矩阵不发吞吐结论；容量链未闭合不发器件档位。

## 2. Function / Module / Reuse

| FUNC | REQ | 功能 | Subsystem / Plane | MOD | 为什么此模块存在 |
|---|---|---|---|---|---|
| FUNC-001 | REQ-001 | UNKNOWN | UNKNOWN | MOD-001 | UNKNOWN |

| MOD | 职责/owner | Core/Adapter/合板及理由 | 输入/输出 IF | 启动依赖/故障域 | 独立测试 | 替换条件 |
|---|---|---|---|---|---|---|
| MOD-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| 变体/更改 | 保持的契约 | changed模块 | retest模块 | 证明无需改的模块 | HW/FW/机械成本 | 超出包络处理 |
|---|---|---|---|---|---|---|
| VAR-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 3. Interface Contract（每条IF复制）

| 字段 | 定义 / 来源 |
|---|---|
| IF ID / version / Plane | UNKNOWN |
| Producer / Consumer / Owner | UNKNOWN |
| Protocol / role / version / format | UNKNOWN |
| Electrical standard / Voltage domains / thresholds / common mode | UNKNOWN |
| Direction / Bandwidth / lane / peak / average | UNKNOWN |
| Clock / frequency / jitter / CDC | UNKNOWN |
| Reset / release dependency / Enable / hardware default | UNKNOWN |
| Idle State / Power-off State / partial power combinations | UNKNOWN |
| Termination / Bias / AC-DC coupling / pulls | UNKNOWN |
| Ownership / transfer / timeout / retry | UNKNOWN |
| Fault Behavior / Protection / Ioff / injection | UNKNOWN |
| Debug Point / probe loading / timestamps | UNKNOWN |
| Connector / pin view / cable / shell / shield | UNKNOWN |
| SI Constraint / PI / Return / Isolation and rationale | UNKNOWN |
| HW-Assembly-FW compatibility / VAL | UNKNOWN |

## 4. Plane / Budget / Dependency

分别画Data、Control、Management、Power、Clock、Reset和Ground图；每条跨模块边标IF ID。可复用总图但不得丢边的语义。

| Scenario / Data edge /终点 | payload | packet overhead | coding efficiency | lanes/持续capacity及依据 | margin目标与结果 | stall/buffer owner/latency | error/观察 |
|---|---|---|---|---|---|---|---|
| IF-D01 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| Control edge | initializer/owner | prerequisite | command/readback | timeout/retry budget | failure detection / recovery |
|---|---|---|---|---|---|
| IF-C01 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| Rail | source/min-nom-max | steady/inrush/transient | loss/efficiency/thermal | EN/PG/reset关联 | reverse/discharge/fault | TP/VAL |
|---|---|---|---|---|---|---|
| PWR-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| Prerequisite node | Dependent node | 类型/理由 | ready谓词 | clock/reset时存在性 | timeout/failure route | 证据 |
|---|---|---|---|---|---|---|
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 5. Lifecycle Matrix

每个模块逐OFF/STANDBY/POWER_APPLIED/INITIALIZATION/CONFIGURATION/LINK_TRAINING/IDLE/ACTIVE/FAULT/RECOVERY/SHUTDOWN填写；可按列拆表，字段不得丢失。

| MOD / state / power-domain组合 | power | clock | reset | enable | GPIO | receiver | transmitter | termination | bias | pull-up/down | ownership | firmware | communication | protection | back-power risk | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MOD-001 / OFF | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| From→To | trigger/guard | actions/硬件默认 | owner | max时间/timeout | 争用/反灌/invalid窗口 | observation / VAL |
|---|---|---|---|---|---|---|
| OFF→STANDBY | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 6. State Differential / Invariants

| Item | State A | State B | Difference（含不变风险） | Risk/mechanism | Evidence | VAL |
|---|---|---|---|---|---|---|
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| INV | 条件与不变量 | 适用范围/例外 | hardware机制 | software责任 | 转换窗口 | VAL |
|---|---|---|---|---|---|---|
| INV-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 7. Risk / ADR / Review

| RISK | 版本化证据 | 触发条件/机制 | 系统后果 | severity / confidence | 候选措施与代价 | owner / VAL /状态 |
|---|---|---|---|---|---|---|
| RISK-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

ADR-001：Context / Options / Decision / Rationale / Trade-offs / Risks / Validation / Revisit trigger逐项填写。

Review结论：UNKNOWN；L1 System → L2 Subsystem → L3 Module → L4 Device → L5 Circuit；覆盖Requirement、Boundary、Data、Control、Power、Clock、Reset、Interface、Bandwidth、SI、PI、EMC、ESD、Lifecycle、Idle、Fault、Recovery、Debug、Observability、Manufacturing、Service、Firmware、Upgrade、Reuse、Cost；每个结论链接推理与证据。

## 8. Traceability / Validation / Bring-up

| REQ | FUNC | MOD | IF | IMP | RISK/INV | VAL | 判据状态 |
|---|---|---|---|---|---|---|---|
| REQ-001 | FUNC-001 | MOD-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

| VAL | 类型/覆盖ID | HW/Assembly/FW/环境 | precondition / stimulus | method/instrument/point/uncertainty | samples/range | pass criteria及来源 | PLANNED/PASS/FAIL/UNKNOWN + evidence |
|---|---|---|---|---|---|---|---|
| VAL-001 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | PLANNED |

| Bring-up gate | entry/action | observation/pass | timeout | failure exit | evidence |
|---|---|---|---|---|---|
| Input power | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

Debug树：Observed failure → possible stage → dependency → observation point → isolation test → outcome/next step。最终保留未关闭项与下一阶段进入条件。
