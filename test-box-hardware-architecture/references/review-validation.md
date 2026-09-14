# Architecture Review 与验证闭环

## 从系统到电路

L1明确purpose/boundary、data/control/management/power流及外部角色；L2检查power/compute/interfaces/management划分和启动/故障依赖；L3检查模块内聚、责任、IF契约与复用；L4在已知需求内核器件；L5核电路计算/连接/布局。若上层未知，明确条件性评价并继续能完成的分析，不把缺框图当停止review的理由。

每项finding用“版本化证据 → 条件 → 失效机制 → 系统后果 → 方案/取舍 → 验证和判据”写。severity与confidence分开：严重但未证实的风险不能写成已发生故障。

## Review coverage：必须推理，不只打勾

| 领域 | 关键问题 | 所需证据/验证 |
|---|---|---|
| Requirement / Boundary | 功能是否属于盒内，DUT与Host谁供电/控制 | REQ、context、外部契约 |
| Data / Bandwidth | 并发是否过载，overhead是否重复或漏算 | 逐跳预算、drop/latency实测 |
| Control / Firmware | 谁初始化、谁处理bus stuck，升级失败谁恢复 | 依赖图、readback、恢复/兼容矩阵 |
| Power / PI | inrush/短路是否拖垮Core，残压如何消失 | 最坏负载/源阻抗、rail/PG/电流波形 |
| Clock / Reset | 有无自启动依赖环，reset release是否合规 | 源、锁定/稳定定义、异常时序 |
| Interface / SI | 完整电气/物理/状态契约，连接器与线缆是否改变负载 | 数据表min/max、pin/约束、模型和实测 |
| EMC / ESD | 真实回流与测试拓扑，器件等级是否误当整机 | grounding图、受控标准版本、整机报告 |
| Lifecycle / Idle | disabled RX如何被解释，off域是否被注入 | module×state、差分和转换测量 |
| Fault / Recovery | 是否局部隔离，是否无限重试/抹日志 | fault tree、注入、恢复预算 |
| Debug / Observability | 失败前状态能否保留，探头是否改变故障 | 时间戳、触发、负载、首个分叉 |
| Manufacturing / Service | NC/DNP是否一致，治具可接触和替换，校准可追溯 | 装配选项、pin-1、寿命/维修步骤 |
| Upgrade / Reliability | 坏固件/配置、brownout、反复热插拔、风扇/线缆故障 | rollback或恢复入口、热/长时/循环测试 |
| Reuse / Cost | 换型改什么，复杂度是否有收益 | change-impact、评分、复用次数和成本范围 |

## Validation matrix

每个 VAL 必须含 REQ/FUNC/MOD/IF/RISK/INV 关联、版本/配置、precondition、stimulus、method/instrument/point、sample/range、pass criteria、证据路径和结果。PLANNED与PASS分开；未知判据不允许PASS。校准、仪器带宽/采样和测量不确定度影响判断时必须列出。

覆盖 Functional、Signal、Power、Sequence、Link、Error injection、Hot plug、ESD、EMC、Thermal、Stress、Long-run、Recovery。按需求选择，N/A要理由，不能机械全部执行。生产设备另覆盖校准漂移、重复性、节拍、治具寿命、记录追溯。

判据示例：DUT短路试验中 Core rail始终处于[经确认Vmin,Vmax]，无reset计数增加，故障日志完整，DUT支路在Ttrip内关断；数值由源/负载器件与系统要求给定。没有这些数值时可生成测试计划，不能声称已验证。

变更后回归由影响图和契约决定：替换SerDes要重测boot/sideband/link/data/功率/热/EMC相关路径；Core管理API若契约未变可复用证据，但共享供电/clock/固件包仍需评估。图可达是检查提示，不自动判定所有节点都要重设计。

结论等级：BLOCKED（关键证据缺失）/ CHANGES REQUIRED / CONDITIONAL（列条件）/ READY FOR NEXT STAGE。后者不是制造放行或实物合规认证。
