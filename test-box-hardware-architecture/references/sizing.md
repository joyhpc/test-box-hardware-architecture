# Sizing / Capacity Derivation

器件档位必须由需求包络推导。先确定应用与可同时运行的配置，再求端口、逐跳容量、通道/IO/存储/逻辑、电源热与时延；最后筛档位、封装和 speed grade。型号不固定，数量不能空缺。输入不足时给有来源的区间和敏感性，标 ASSUMPTION，不能伪造实测。

## 1. 从场景得到物理端口与并发

Requirement Contract 增加配置组合矩阵：每行是一个允许同时发生的运行组合，列至少为 scenario ID、工位/DUT 数、每个物理端口的角色/格式/帧率、并发关系、golden/loopback、分时约束、终点与验收目标。格式种类数不等于连接器数。多个虚拟通道共用物理端口时须显式聚合，不能重复计算连接器。

产线可先用 `stations = ceil(target_DUT_per_hour × cycle_seconds / (3600 × availability))`，再算 `DUT_ports = stations × ports_per_station`，加 golden、观测、回环和物理预留。该式假定每工位每周期完成一个 DUT；批量测试、上下料重叠、共享仪器需另建调度模型。availability 不能再次把已计入 cycle 的停顿扣一遍。

物理端口按接线并集；运行并发按每行激活集合。分时复用必须证明测试窗口互斥、切换/稳定/重新训练时间可接受、golden 对照语义仍成立、部分供电和所有权转换安全。仅因“不会总跑满”不能少配资源。

对**每一跳、每一资源类别**寻找最坏行，不强迫所有量采用同一行。固定独立队列可能要按每端口跨场景最大值分配；共享动态池才可用同时峰值，且须证明调度和公平性。

## 2. 完整数据链与停服域

原始有效图像速率 `R_i = width × height × fps × bits_per_pixel`。按格式另计 blanking、包头、时间戳、对齐、重传及压缩的最坏情况；不能默认压缩收益。Mbps/MBps 用十进制，KiB/MiB 与 Kibit 用二进制，始终明确 bit/byte。

每个 scenario、每条经过的 hop：

```
payload_h = Σ active routed R_i
wire_h = payload_h × packet_factor_h / coding_efficiency_h
usable_h = capacity_h × (1 - reserve_h)
headroom_h = 1 - wire_h / capacity_h
minimum_capacity_h = wire_h / (1 - reserve_h)
```

hop 的 packet factor 相对于**该跳的 canonical payload**，不是盲目继承并再乘上一跳的编码。若跨跳封装仍保留，须在下跳 factor 明确包含；格式变换/复制/压缩用不同阶段模型，当前工具不模拟变换或 multicast。

链条必须达到需求终点：Sensor/Adapter → Core → Host link → DMA/RAM → 文件系统/持续存储。物理标称速率、协议可用速率、驱动可持续速率和磁盘持续写速率分别列依据。不得从“某接口名字”或短时缓存峰值推持续吞吐。`bottleneck` 按 `wire_h/usable_h` 最大值找；每跳都过才是算术容量满足，仍需系统验证。

完全停服的 payload 缓存下界 `ceil(R × stall_seconds / 8)`；部分服务为到达与服务曲线最大积压，不能直接套零服务公式。另加 burst、metadata、粒度和裕量。明确停服域、背压传播、存储 owner、排空速率与下一次停顿间隔。持续超载不能靠扩大缓存修复；平均排空有余量也不自动证明任意突发可容纳。Host 存盘停顿若由 Host RAM 吸收，不应全部误记成 FPGA BRAM；若 RAM 满后背压传回，必须重算 FPGA 停服窗口。

## 3. 器件资源包络：按以下顺序

1. **Serial/GT channel**：物理端口 × lane，加 Host、loopback 和预留。分清 FPGA GT、DPHY IO、普通 LVDS 与专用硬核，sideband 通常计入 GPIO。端口物理并集不等于同时吞吐最大集合。检查 lane 速率、direction、quad/tile 分组、PLL/refclk、协议硬核和封装可达性；总数够不等于能布进去。
2. **IO / VCCIO / Bank**：Adapter pin map 分解单端/差分/clock/控制/专用脚，每差分对按两个物理脚计。按兼容电压、IO 标准和 bank class 分组。`ceil(pins / usable_pins_per_bank)` 仅是下界；保留专用脚、clock、VREF、差分对及跨 Bank 限制，落到候选封装 pin plan 才关闭。
3. **BRAM / URAM**：先得到每个队列字节数，再按实际宽深和端口模式分块：`blocks_queue = ceil(bytes_queue × 8 / (usable_bits_per_block × packing_efficiency))`。独立队列逐个取整，加 IP 固定块数，再除利用率上限向上取整。nominal bits 不能当所有配置的 payload bits；parity/ECC、FIFO 对齐、端口数、CDC staging、延迟与路由会改变可用量。
4. **外部内存是否需要**：在候选器件片内可用池不足时比较更大 BRAM 档、适用的 URAM 档、外部 DDR 或需求裁剪。计算读写双向次数、有效总线效率、刷新/ECC、争用、带宽保留和停服容量。容量够而读写服务不足仍失败。不能把“超过一个候选片内容量”写成“必上 DDR”。
5. **LUT / FF / DSP**：按功能块 per-instance 区间 × 实例数累加，包括接收/解包、CDC/FIFO 控制、路由、打包、Host IP、管理及真正的像素计算。每个区间记录来自实际同配置综合、vendor estimate 还是 ASSUMPTION。器件 family 的 LUT/ALM 不能直接等价互换。没有估算依据时可演示计算，但不可把教学区间当 IP 经验数据。
6. **利用率 / speed grade / PVT**：例如 70% 仅是本项目规划上限，非通用保证。分别设逻辑/内存/GT 余量并解释原因；本工具用统一 memory/logic 上限作简化，GT 采用显式预留通道。以目标 datapath clock、IO 速率、跨域、布局拥塞和 PVT 筛 speed grade；综合和布局后报告、功耗工具与结温关闭决定最终档位。

AMD 的 [memory technology](https://www.amd.com/en/products/adaptive-socs-and-fpgas/technologies/memory.html) 列出 36 Kibit BRAM 与 288 Kibit UltraRAM；[UG573 UltraRAM Summary](https://docs.amd.com/r/en-US/ug573-ultrascale-memory-resources/UltraRAM-Summary) 描述单时钟同步结构。此处仅引用块几何和结构，不能外推所有系列均含该资源；示例的 32/256 Kibit usable 与 packing=0.9 是另行声明的教学假设（2026-09-14核验）。

输出为可比较的**器件档位包络**：GT 类型/数量与速率、兼容 Bank 下界、LUT/FF/DSP 区间及最小容量、各存储备选块数、DDR 需求、时钟目标、speed grade 待验证条件、封装/功耗/温度与余量。一个数字不代表推荐型号。

## 4. 功率、热、时延、节拍和复用收益

- 功率 ledger：各 rail 输出功率 × 实例数 / 效率，再加 PoC、风扇和其它负载；用 min input 与浪涌/瞬态约束选额定电流。盒内热 = 输入功率 − 盒外负载带走的功率，外置 DUT 的负载热不要全部算进机壳，但其供电损耗须计入。
- 结温粗算 `Tj = Tambient + Pchip × effective_theta`；effective_theta 要对应实际风道/散热器，不拿数据表单个热阻机械替代。最大允许热阻 `(Tj_target - Tambient)/Pchip`，再做 PVT、风扇失效、降额与实测。
- 延迟按“触发到首字节/末字节/Host可见/落盘确认”定义终点。串行依赖项求和，重叠项取关键路径；分别列最小、典型、最坏和排队条件，尾延迟不能用平均值替代。
- 复用收益 = 变体独立开发/回归工时 − Core+Adapters 工时 − 平台维护/额外硬件成本；写数量和回本点。低台数也可能有软件/验证收益，不能只数板件。

## 5. 门控与复核

未定义最坏并发组合，不发布总吞吐结论；没有可追溯容量推导，不发布器件档位。UNKNOWN 阻止对应选型/签核，但可以发布有条件的包络和下一步测量。算术可行仍需 IP 配置估算 → 综合 → 布局/时序 → 持续端到端数据 → 故障/温度压力验证。

完整输入及数字见 [worked example](../examples/worked-camera-architecture.md)，可填写表见 [workbook](../assets/architecture-workbook.md)，可执行 schema 见 [tools](../scripts/README.md)。
