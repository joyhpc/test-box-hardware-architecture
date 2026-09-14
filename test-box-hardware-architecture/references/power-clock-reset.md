# Power、Clock、Reset 与 Ground

## Power architecture

从每个源到每个负载画功率与回流路径：外部输入 → 反接/浪涌/热插拔 → 中间rail → POL → 内部负载；独立DUT支路 → cable/PoC → DUT。并列 Controller/AON、monitor、风扇供电。24V只是可能的名义电压，不能代替输入工作范围与瞬态包络。

每条rail记录：ID、源、min/nom/max、稳态/启动/瞬态电流、源阻抗、线损、效率、bulk/inrush、PG、EN owner、discharge、reverse current、短路响应、测试点。Pinput≈ΣPout/η，电缆压降按最坏回路电阻与峰值电流；估计值标假设，不能拿芯片额定电流当真实热设计能力。

Fault containment需证明 DUT短路 → 支路限流/切断，Core电压仍在工作区且日志可存。可选择fuse/eFuse/hot-swap/独立稳压/hold-up/独立源；选哪种由能量、响应时间、故障持续、成本决定。共用输入仍有共同故障；软件检测通常不能替代快速硬件限流。限流、反向阻断、隔离、保险丝各自作用分开。

反灌检查覆盖 power outputs、GPIO、I2C pull-up、reset/clock、USB VBUS、PoC、下载器、传感器输入、仪器地线。两端ON/OFF四组合及断电瞬间都查。串阻只限制电流，不自动使幽灵供电消失；把上拉移到对端也要检查反向组合。具体Ioff条件见 [interfaces](interfaces.md)。

## 依赖图代替固定上电表

基础因果为 Power Good → Clock Stable → Reset Release → Device Init → Ready；器件实际要求决定分支和例外。有的时钟源本身依赖主rail，不机械执行“先clock后全部rails”。FPGA负责开启自己的启动电源、或远端bus负责开启承载该bus的link，是需要引入独立默认路径/本地控制的依赖环。

Clock表包含 source/frequency/tolerance/jitter profile/distribution/owner、reset时存在性、CDC、clock失效检测与恢复；不能用单一RMS jitter无条件替代规定积分范围/模板。

Reset区分 POR、global、device、software、watchdog、reconfiguration。记录assert来源/极性、最小pulse、release条件、同步域、IO默认与传播范围。研究异步assert/同步deassert是否适用于该器件与无时钟阶段，不能泛化。PG去抖、brownout与reset反复振荡必须有可观察结果。

Shutdown同样需要序列：停止事务→撤销ready→停止驱动/隔离→关DUT/域→确认放电→保留或关闭管理域；掉输入电源的非受控路径另画，不能假设固件还能执行。

器件可能有专用电源排序约束，应在架构阶段纳入。[ADI AN-932](https://www.analog.com/en/resources/app-notes/an-932.html)

## Ground / EMC / ESD architecture

画节点：保护接地PE（如有）、chassis、connector shell、cable shield、signal/power return、DUT/Host/PSU/仪器地。每一连接写DC阻抗、HF回流意图、共模路径与是否可拆。单点/多点/隔离必须由真实车辆/实验室/暗室拓扑判断，不默认全隔离或全共地。隔离数据而共用非隔离电源/屏蔽可能没有形成目标隔离边界。

按环境和客户要求确定ESD、EFT、surge、BCI、辐射/传导发射及抗扰度的适用标准、版本、等级、端口、线束和运行模式；未取得受控规范不编造等级。考虑TVS能量/钳位与被保护器件裕量、入口短回路、屏蔽端接、共模电流、风扇/线缆耦合。架构决定保护域与测试拓扑，PCB再落实位置/回流。

器件制造阶段HBM/CDM与整机ESD测试用途不同，不能互相替代。[TI SLVAFR3](https://www.ti.com/document-viewer/lit/html/SLVAFR3/GUID-7F89B48F-6B8F-45D0-A2F4-22806A8048AB)
