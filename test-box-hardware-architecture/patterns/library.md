# Reusable Pattern / Failure Pattern Library

## 结构模式

| ID / Pattern | 条件与结构 | Trade-off / 反例 | 验证 |
|---|---|---|---|
| PAT-01 Camera Test | 真Camera→可换接收/PoC→capture→Host；模拟Camera另作source路径 | capture、emulation、production不能混成一个用例 | 方向、格式、并发、端到端数据和控制 |
| PAT-02 SerDes Adapter | PHY+connector/cable约束+局部clock/power+vendor driver形成兼容单元 | 换厂商可能改变Core lane/clock/热/带宽包络 | profile与API兼容、冷启动、训练、误码、状态 |
| PAT-03 FPGA Bridge | 速率转换/路由/CDC/buffer由FPGA；管理启动路径独立 | 低带宽直通无需FPGA；“独立”不强制MCU | 自启动、未配置IO、overflow、latency |
| PAT-04 Video Capture | data path和management分离；Host流量背压有定义 | 单一物理Ethernet可共享，需容量/队列保证 | data flood时命令响应和日志完整 |
| PAT-05 Remote Power | 每端口power policy、限流/反向保护、测量+远端线损 | 不是所有端口都需可编程源；PoC耦合网络有协议限制 | short/open、hotplug、DUT off、Core存活 |
| PAT-06 Host Control | 稳定语义API+模块profile，幂等命令/失联状态 | 不为5台debug盒做无需求的远程服务 | Host reboot、重连、重复命令、不兼容profile |
| PAT-07 DUT Adapter | 电气/机械适配、pin map、可选身份；Core保持契约 | 高频连接损耗可能要求合板；插件数越多不一定更好 | 变体矩阵、防误插、装配/固件组合 |

## 失败模式

| ID | 触发/机制 | 正确推理 | 防过拟合与VAL |
|---|---|---|---|
| FAIL-01 Floating Receiver | TX关或RX输出Hi-Z，下游误采样 | 区分line bias、receiver guarantee和downstream valid mask | hysteresis不等于failsafe；测各供电/方向组合 |
| FAIL-02 Improper Bias | 端接/上拉域改变导致差分或共模越界 | 最坏网络/容差与门限区间对照 | 不指定万能阻值；测活动负载与idle |
| FAIL-03 Enable Timing | 两方驱动重叠/接收尚未ready | hardware default、grant/release、turnaround窗口 | 延时改善不等于根因确认；抓OE与实际线 |
| FAIL-04 Back Power | pull-up/输出/下载器对off域注入 | 逐路径和供电组合核Ioff、注入与残压 | Hi-Z/串阻/TVS不自动根治；关DUT测残压电流 |
| FAIL-05 Wrong Ground Model | 屏蔽/仪器/Host形成未考虑回路 | 完整外部拓扑与共模路径 | 不默认全共地/全隔离；按线束测试 |
| FAIL-06 Power Retry Loop | 短路→整机reset→再次上电 | 硬件支路保护、日志生存、重试预算 | 不一律双PSU；测最坏故障 |
| FAIL-07 Incomplete Initialization | ready先于clock/RAM/config有效 | 明确服务ready谓词及因果依赖 | 不靠无限sleep；记录缺失先决条件 |
| FAIL-08 Link Dependency | 远端配置依赖尚未建立的link | 本地最小启动配置与分层状态机 | 不把所有失败都当SI；找首个分叉 |
| FAIL-09 Version Contamination | 旧报告与新BOM/PCB混用 | 设计×装配×固件矩阵和hash | 文件名latest无效；冲突保持UNKNOWN |
| FAIL-10 Physical Label Assumption | PCIe外形被当PCIe电气，HBM被当系统ESD | 物理、协议、测试层级分开 | 查实际pin和测试条件，不按标签判定 |

PAT/FAIL保留匿名历史审查所提示的职责与风险问题，并结合一般系统推理和官方机制；公开索引无法独立复核原件；见 [case studies](../examples/case-studies.md)。无实测根因的模式明确作为风险推理，不声称已验证修复。
