# 历史行为试运行响应（公开泛化版）

2026-09-14隐私编辑说明：已泛化涉及原项目的标识和具体电源值；其余推理与原有失败边界保留。此公开版不宣称逐字原始记录，也没有用v1.1 sizing结果改写T1/T5/T6。

2026-09-07；执行者为Skill作者，SELF/non-blind。以下是本轮按Skill处理 [raw prompts](prompts.json) 的实际回答，非独立模型成绩，也非实物测试报告。问句是试运行响应内容，不是向当前用户新增提问。

## T1 — 新Camera Test Box

先确定这台盒子是在接收Camera、模拟Camera给域控，还是两者之间转发；这会决定数据方向和模块边界，现在还不能据此选择SerDes。

请先确认三组信息：① DUT是Camera还是域控，测试用于bring-up、功能验证还是生产判定？② 同时测几路、分辨率/帧率/格式、已有接口和线缆？③ DUT谁供电、是否需电源测量/故障注入、Host是控制还是还要收完整图像？未知项可以先保留。

在ASSUMPTION“实验室接收真Camera、Host采图并控制”的条件下，候选Data为Camera→接收Adapter→可选处理/缓存→Host；Control为Host→系统控制→Adapter本地配置→Camera；Management为电源/温度/link/counter→管理→日志。Power分Core与DUT支路，并画仪器/Host/PSU回流。

先建立REQ功能/并发/供电/可观测/复用，再定义Core、接收模块、DUT Adapter和Power职责。器件选择等待速率、电气、clock/reset和off-state契约。当前可交付Context和Requirement Contract草案，关键UNKNOWN为角色、吞吐、供电范围、复用候选。下一步用这些值形成接口预算及启动/掉电状态表。

## T2 — 换SerDes供应商

改动应尽量集中于High-Speed/Adapter及其driver；没有现有契约，暂时不能承诺只改子板。

先取旧/新协议代际、数据格式、lane/吞吐、Core侧PHY/Bank、电压、参考clock/jitter、reset/启动、connector/cable/PoC、功率/热、配置语义与固件版本。对每一项标“保持包络 / 超出 / UNKNOWN”。

| 范围 | 预期处理 |
|---|---|
| 接收Adapter、局部电源/clock、厂商driver | changed；新器件/协议的能力与启动重新定义 |
| Core语义API | 只有命令含义、错误/ready语义兼容才可保持；否则版本化扩展 |
| Core数据通道、全局电源/散热、机械/线缆 | retest；超出包络时必须承认改板或降规格 |
| 管理/Host | 验证status/error/timeouts和失联/recovery语义，不让厂商寄存器泄漏到通用层 |

回归包括冷启动、DUT off、sideband、training、并发吞吐、短路隔离和错误日志。用变更传播表记录为何某模块无需改，不能仅因软件接口名字相同认定兼容。

## T3 — DUT off但Core on

目前不能判安全。GPIO Hi-Z撤掉了一个驱动源，但I2C仍被常供电3.3V上拉，可能向DUT未上电输入钳位注入；RX型号与termination未知，也无法证明下游逻辑确定。

| Item | DUT_OFF | ACTIVE | 风险/下一步 |
|---|---|---|---|
| GPIO/TX | Hi-Z或disabled | 允许驱动 | 检查OE硬件默认及掉电切换窗口 |
| I2C pull-up | Core AON 3.3V | 同一上拉 | 不变但危险；核DUT输入注入/Ioff保证并测残压/电流 |
| Receiver | UNKNOWN | UNKNOWN | 查RX enable、保证阈值/输出状态与下游valid mask |
| Termination/bias | UNKNOWN | UNKNOWN | 核断电等效网络、差分/共模；不能直接加经验拉阻 |
| Protection | UNKNOWN | UNKNOWN | 核所有电源组合及器件适用条件 |

列GPIO、I2C、clock/reset、PoC、下载器、仪器等全部路径。可选对策是满足条件的powered-off isolation、域控制上拉或硬件OE门控；每种都要重查反向供电组合。验证ON/OFF四组合及掉电窗，量测DUT残压、逐路径注入与RX/下游状态，判据取具体器件保证值。相关限值仍UNKNOWN，计划可继续，安全结论不放行。

## T4 — 首次无图、重启正常

先比较冷启动与重启实际保留了哪些供电和状态，不能先归因SI或单凭重启有效判断软件。

固定板/装配/固件、源/线/端口/温度；确认断电时长、DUT是否同时断电、残压、Host缓存与配置保留。同步抓输入rail/PG、clock、reset、FPGA DONE与业务ready、接口OE、配置完成、link状态和首帧时间。

按输入供电→管理alive→按依赖建立rails/clock→reset release→FPGA及接口init→DUT detect/config→训练→data，找第一个cold/warm不同阶段。PG未到即reset释放查时序；寄存器配置缺失查依赖/超时；ready早于服务查门控；请求已解析但回复不全查长度/FIFO/返回监听；训练阶段才分叉再深入PHY/线缆和电气余量。

受控延后ready、只reset某域、互换同规格线缆/端口、对照配置readback作为区分实验。一次改善仅支持假设，要抓缺失先决条件并重复受控A/B。设重试总预算，保留首错，失败锁定或局部恢复，不无限循环整机电源。先交付时间轴、差分表和实验排序，不在无波形时给唯一根因。

## T5 — 五种Camera

Core化稳定的管理、Host语义、配置编排、日志格式和通用电源策略；Adapter化供应商协议/PHY、电气/连接器、局部clock/power、pin mapping与厂商driver。是否把数据处理放Core，要等五种Camera的共同包络明确。

建立5行variant表，每行列协议/代际、分辨率/fps/bpp、并发/lane、同步、供电/PoC、connector/cable、控制/地址、散热、机械。现在这些值均UNKNOWN，不能虚构五个具体型号。

从变体差异定义接口版本与能力profile。若其中一种超出Core输出带宽或Bank能力，选择提高Core包络、限制并发、分成两个平台族，或更换相关Core部分，并给成本/进度取舍。模块化以可验证替换为准，不以插件数评分。只有5台低频复用时，可保留同板可选装配，避免无收益的连接器与多控制器。

下一步输出Reuse Matrix与有界变更测试：替换Adapter后Core启动/Host管理保持、相应数据链和power/thermal重新验收；按实际复用次数估算收益。

## T6 — 从框图逐级Review

系统角色初步是接收Camera图像并送PC，PC同时控制；它适合进一步架构review，但图中还不能证明吞吐、部分掉电或故障隔离。

L1先核Camera是DUT还是激励源、PC需原始全量数据还是抽样、24V源/仪器/Host的地，以及USB同时承载数据和控制与否。补Data、Control、Management、Power语义：目前Management缺少明确状态/日志路径。

L2看compute/interface/power划分：单Buck分支可能让Camera短路拖垮MCU，需先核是否已有独立限流/稳压和裕量，不能据图断言必然reset。FPGA做buffer/CDC是否必要取决于输入与USB可用吞吐；缓存不能弥补持续过载。

L3为DES↔FPGA、MCU↔DES、FPGA↔USB、Power↔Camera建立IF契约，明确时钟、reset/OE、供电域、局部恢复、DUT off的pull-up和RX状态。把Camera连接器/电平集中到Adapter候选边界，观察点覆盖link、counter、rail与首帧。

L4/L5需数据表、电气规格和原理图后再核器件/电阻电容。当前优先产物是需求缺口、三Plane+Power图、接口矩阵、带宽预算、生命周期差分、短路/Host reboot/冷启动的VAL。结论为CONDITIONAL，不能据此放行电路。

## A1 — Normal足够

正常运行只覆盖一个状态。需要至少核该设计相关的上电、idle、DUT off、fault/recovery和转换窗口；尤其检查默认OE、RX输出解释和partial power。可裁剪文档深度，但不能用正常出图代替生命周期证据。

## A2 — Hysteresis保证floating

不能这样推断。hysteresis只描述阈值切换行为，floating/terminated/shorted时是否有确定输出取决于具体receiver保证范围、供电与共模条件。先查准确型号和min/max，再分析bias等效网络及下游mask；无数据表则UNKNOWN，不给“加某个阻值就安全”的结论。

## A3 — 一律共地

先把Host、仪器、PSU、车辆/DUT、机壳、shell和shield都纳入拓扑，找DC和高频回流、可能的地电位差与共模电流。共地可能合适，但不能从布线简单得出结论；全隔离也不自动正确。按线束/环境选择连接与保护，验证真实配置。

## A4 — 五台盒子全插件加冗余

先把等级暂定B、数量5台作为CONSTRAINT，比较预计复用次数、停机代价、SI连接损耗、机械/维护成本。建议优先DUT易变接口可换、常用管理同板，基础保护和观察保留；双控制器/冗余源只有独立启动、日志生存或停机需求证明价值时增加，不因“未来”自动加入。

## A5 — FPGA开启自身启动电源

这里存在启动依赖环：FPGA用户逻辑要先配置运行才能开电源，而运行又依赖这路电源。把最小上电和安全默认放到不依赖该逻辑的电路、supervisor或控制器；配置失败记录也需在可存活域。若硬件默认启动与配置状态输出已足够，无需强制再加MCU。画prerequisite图并验证配置失败、无clock与brownout。

## A6 — 相互矛盾版本

无法从Final/draft/mtime给唯一当前树。先确认实物的HW、装配和固件身份，核受控发布/变更记录及每份资料hash；分别保留RAIL-A与RAIL-B的出处和适用范围。可画两个条件性候选树继续依赖分析，但当前有效树标UNKNOWN。最新修改时间的BOM不自动优先于发布记录。

## A7 — 相同端点无争用

两态enable均0只说明端点声明相同，不证明中间没有毛刺、方向反转或reset默认失控。还要检查power/PG、OE延迟、所有权移交及FPGA配置窗。捕获完整转换，比较最坏overlap/gap与器件保证；若两态RX均浮空，不变风险也必须列出。

## A8 — 吞吐翻倍仍只改子板

该约束下无法保证原Core持续接收全部数据。先算逐跳payload、overhead、并发与容量；超出持续服务率时有限buffer只能延迟溢出。需要提高Core/Host通道能力，或明确降低并发、压缩/抽样等允许的功能变更；未经需求接受不能把丢数据当透明兼容。Adapter可封装厂商差异，不能消除物理容量限制。

## A9 — HBM替代系统ESD

器件HBM与系统ESD的对象、波形和运行条件不同。应把项目适用标准、版本、端口、等级、线束、运行模式和判据写入验证计划；现有HBM值不证明整机通过。具体等级未给时保留UNKNOWN，不自行编造系统认证。

## A10 — 延后HPD一次成功即根因

这支持启动/ready竞争的候选解释，但不足以关闭根因。需要记录延前/延后时clock、reset、配置、DPCD/AUX服务ready与HPD的因果关系，控制其它变量并重复冷启动，证伪替代的时序/采样余量解释。修复应落实真实ready guard及异常路径，不能只留下无来源固定延时。
