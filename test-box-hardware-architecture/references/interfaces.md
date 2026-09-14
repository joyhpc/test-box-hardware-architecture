# Interface Contract 与预算

容量先读 [sizing](sizing.md)：Requirement Contract的并发配置矩阵定义输入，逐跳到需求终点（含Host持续存储），再形成端口/GT/Bank/存储/逻辑包络。

每条跨模块边（包括电源/机械/管理）有 IF ID 和版本。逻辑规范和物理连接可多对多，不能只写 SPI 或阻抗值。

| 字段 | 必答内容 |
|---|---|
| Producer / Consumer / Owner | 谁驱动、接收、配置、处理故障；半双工逐阶段唯一主动驱动 owner |
| Protocol | 版本/角色、format、lane、速率、地址/alias、timeout/retry、错误码 |
| Electrical / Voltage | 电气标准、VDDIO域、电平、差分阈值、共模、absolute max、injection/Ioff 条件 |
| Direction / Bandwidth | 单向/双向/半双工、并发、平均/峰值/payload/wire |
| Clock | source、频率/容差/jitter来源、同步、CDC、reset时是否存在 |
| Reset / Enable | 极性、默认拉阻所属域、硬件控制、释放条件、故障切断时间 |
| Idle / Power-off | 两端电源组合、TX/RX、termination/bias、GPIO、pulls、反灌路径 |
| Ownership transfer | grant/release、break-before-make、overlap/gap、bus idle判据、异常退出 |
| Fault behavior | stuck-low/短路/断线/掉电/坏配置/无时钟；检测、限流、隔离、恢复 |
| Debug point | 位置、探头/仪器、允许负载、方向有效标志、时间戳、寄存器清除语义 |
| Physical | connector/pin map、pin-1/view、shell/shield、cable/长度/锁扣、额定值、热插拔顺序 |
| SI / PI / Isolation | 阻抗/端接位置、coupling、损耗、return path、common mode、是否隔离及原因 |
| Compatibility | HW/assembly/firmware/API/profile版本、允许组合、安全拒绝、VAL ID |

高速分析依次覆盖 Protocol → PHY → Connector → Cable → Termination → Bias → AC/DC coupling → Clock → Reset → Sideband。GMSL/FPD-Link 核具体系列/代际；MIPI 区分 D-PHY/C-PHY 和协议；LVDS/M-LVDS 不互相代称；DP/eDP、PCIe、Ethernet、USB、HDMI 核版本、PHY和外部要求。标称速率不能证明吞吐。

## 非正常状态

列 TX关闭、RX使能/禁用、两端供电、断线、短线、线缆存在组合，再查具体 receiver 的 guaranteed thresholds、common-mode 和 powered-off 条款。M-LVDS Type-1/Type-2 的 failsafe 有差异，不能把 hysteresis 当所有输入状态的保证。[TI LVDS manual §4.6](https://www.ti.com/lit/ug/snla187/snla187.pdf)

Bias 用实际等效网络（双端termination、上拉源、断电路径）计算最坏容差的差分/共模区间，证明落在保证区，并评估活动驱动负载/功耗。无数据表/网络则 UNKNOWN，不推荐经验电阻。

Hi-Z 若仍接 AON pull-up、探头、下载器或其它驱动端，仍可能注入。Ioff/隔离必须覆盖具体引脚和供电组合，不能从“有 level shifter”推断保护。[TI powered-off protection](https://www.ti.com/document-viewer/lit/html/SSZT432/GUID-663B212B-D217-43C9-88A4-B7A51ABDEB40)

## 带宽、buffer、latency

区分 bit/s 与 byte/s。未压缩 active payload = width×height×fps×bits_per_pixel×simultaneous_streams，不自动含 blanking/metadata/封装。是否传 blanking 需协议证据。

packet factor = 总协议数据/payload，coding efficiency = 有效bit/wire bit，则 required wire rate = payload×packet factor/efficiency；逐跳算，不能重复计 overhead。可用容量还受lane数、共享竞争和协议效率限制。

教学 ASSUMPTION：4×1920×1080×60×12 = 5.971968 Gbit/s payload；packet factor 1.05，coding efficiency 0.8 → 7.838208 Gbit/s wire。按1-required/capacity计算，8 Gbit/s链路剩余2.0224%，不满足10%容量保留目标。这不是具体Camera/SerDes规格。

最低buffer是任意区间累计到达与可服务字节的最大正差。完全暂停服务 T 时至少 arrival_rate×T/8，再计burst/margin；长期 arrival>service，有限buffer无法保证无损。延迟包含frame accumulation、serialization、bridge/CDC、queue、DMA、Host；区分 typical/max/jitter。

器件候选对照功能、接口、生命周期、clock/reset、保护、功率/热、诊断、供应/成本。数据表、仿真、实测分别记录。PCB/线缆未读不能宣布 SI 合规。
