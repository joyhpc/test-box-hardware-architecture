# 离线工具

Python 3.11+标准库，无网络、硬件控制、API key和第三方依赖。在Skill目录运行下列命令。所有输入都是项目人员声明的数据，不解析原始EDA文件，不自动确定电气安全。

```powershell
python scripts/arch_tools.py diff examples/lifecycle-demo.json --before DUT_OFF --after ACTIVE
python scripts/arch_tools.py dependency examples/dependency-demo.json --changed SERDES
python scripts/arch_tools.py budget examples/budget-demo.json
python scripts/arch_tools.py budget examples/traffic-camera-proposed.json
python scripts/arch_tools.py budget examples/traffic-camera-sized.json
python scripts/arch_tools.py resource examples/resource-camera.json --traffic examples/traffic-camera-sized.json
python scripts/arch_tools.py trace examples/trace-demo.json
```

输出JSON；可加 `--output <new-report.json>` 保存，不覆盖已有文件或输入。exit 0表示该结构/计算检查无问题；1表示缺项、依赖环、带宽或资源候选不足；2表示无效输入。resource的ARITHMETIC_FEASIBLE仅代表声明参数算术满足，所有内存映射仍UNVERIFIED。exit 0不是电气/行为PASS。初始traffic示例预期exit1，调整后budget/resource预期exit0。

## Schema与解释

- diff：`states`是state→module→field对象；必需字段为power, clock, reset, enable, gpio, receiver, transmitter, termination, bias, pulls, ownership, firmware, communication, protection, back_power_risk, evidence。字段可字符串或结构化对象；UNKNOWN/TBD标记（含句中）、null/空值/裸N/A均显示缺口。N/A写理由。结果使用固定before_value/after_value，不以state名作为字段。跨两态新增/消失模块不静默丢弃。只显示变化或未知项，**不变风险仍需人工逐状态审查**，转换顺序不在此算法内。
- dependency：`nodes:[{id:...}]`、`edges:[{from:...,to:...}]`，方向为prerequisite→dependent，不是任意信号箭头。输出拓扑顺序、实际cycle节点及其blocked descendants；`--changed`输出潜在传播范围。不同电源/状态条件使用分开的图，不能合并互斥条件后声称有真实环。
- budget legacy：streams为同构数量时保持原schema与输出；分辨率正整数、fps/bpp正数、packet_factor≥1、coding_efficiency在(0,1]、reserve_fraction在[0,1)、stall_seconds≥0。该模式只有单跳，不应用于异构端到端结论。
- trace：节点kind依次requirement/function/module/interface/implementation/validation，边只能相邻级。每个节点必须有相应上下游，每阶段存在；validation有method/pass_criteria/status，PASS或FAIL需evidence。检查闭环结构，不验证文本是否合理或证据真实。

JSON重复key、NaN/Infinity、非法数值、重复node或悬空edge会拒绝。用 [tests](../evals/README.md) 中的回归命令验证工具；这些测试与模型行为评测分开。

## budget v2：端口profile + scenario + route

[完整输入](../examples/traffic-camera-proposed.json) 是可复制schema，无省略字段。`streams`为非空对象列表触发v2：

| 集合 | 必需字段 | 语义 |
|---|---|---|
| streams | id, port, profile, width, height, fps, bits_per_pixel, path | 一个物理端口的一个格式候选；path为有序hop ID列表 |
| scenarios | id, active_streams, required_sink, rationale | 真正允许同时运行的组合；终点与需求一致，理由必须声明golden/互斥/调度条件 |
| hops | id, from, to, capacity_bps, packet_factor, coding_efficiency, reserve_fraction, stall_seconds, buffer_owner, capacity_basis | 每跳相对于payload的开销、持续capacity依据、零服务停顿及存储责任域 |

ID必须唯一，引用存在，路径连续、无环且到required_sink。一个场景不接受同一物理端口两个profile同时激活；多VC应先显式聚合模型，当前工具不推测复用调度。未使用stream或hop拒绝，以暴露漏建配置。异构流可走不同路径；不同跳分别找最坏场景。并发组合及容量依据由工程人员提供，工具不能证明其完整或真实。

结果含每场景各跳payload/wire、headroom、保留后利用率、最低capacity、分流停服buffer、失败hop和瓶颈；`worst_by_hop`保留其scenario。所有hop capacity均用bit/s，Host磁盘MB/s先乘8×10^6；buffer输出byte。因子对canonical payload定义，不自动累乘前跳编码；数据变换和multicast尚不支持。

## resource：由流量到容量包络

`--traffic`必须是v2输入，资源端口集合必须与其物理端口并集一致。参考 [完整资源输入](../examples/resource-camera.json)：

| 字段 | 定义 |
|---|---|
| evidence_scope | 必需，说明数据来源、假设与使用范围 |
| ports | id, resource_type, lanes；非负整数lane；按物理接线计GT/DPHY_IO等独立类别 |
| additional_channels | 可选列表：resource_type, count, reason；Host/回环/物理预留显式计入 |
| io_groups | id, vccio_v, bank_class, pins, pins_per_bank, reserve_fraction；每组专用Bank下界，不解实际pin placement |
| maximum_utilization | (0,1]；当前简化为memory/logic共用上限；GT预留用额外channel表示 |
| functions | id, instances, lut/ff/dsp各[low,high]整数区间, evidence_type（ASSUMPTION/MEASURED/VENDOR_ESTIMATE）, basis |
| buffer | hop, owner, burst_bytes_per_port, metadata_factor≥1；从该hop各端口跨场景最大停服量分配独立队列，owner必须一致 |
| memory_options | id, nominal_block_bits, usable_block_bits, packing_efficiency, fixed_blocks, available_blocks, mapping_limitations；逐队列取整。可选auxiliary_pools用于另一类固定资源池 |
| auxiliary_pools | 列表：id, allocated_blocks, available_blocks；例如URAM方案依赖的BRAM固定IP，按利用率复核，不能只看URAM |
| external_memory | 可选：capacity_bytes, bus_capacity_bps, traffic_passes≥2, efficiency, reserve_fraction；可附auxiliary_pools。含读写但没有controller资源自动估算 |
| production | 可选：target_duts_per_hour, cycle_seconds, availability, ports_per_station, shared_golden_ports；每工位每周期一DUT，取整工位后核端口数；不解共享资源调度 |
| power | 可选：loads（id, output_w, instances, efficiency, fraction_heat_outside），reserve_fraction, input_voltage_v, fpga_dissipation_w, ambient_c, target_junction_c, effective_theta_c_per_w |

同类额外IP容量要并入functions/fixed_blocks；memory_options是备选而非并加。任一完整备选及其附属池算术满足，可解除容量不足，但mapping_status仍UNVERIFIED。DDR的容量、带宽与附属池必须同时满足。外置负载功率从机内热扣除，转换损耗保留在机内。

未决项用文档UNKNOWN，数值字段不能填字符串来跳过预算；先拿到有依据的区间或声明有条件假设再运行。resource不自动选择型号、speed grade、GT tile/PLL、Bank电压兼容、存储端口配置，不综合RTL、不操作硬件。时延与复用收益的示范计算见 [worked example](../examples/worked-camera-architecture.md)。
