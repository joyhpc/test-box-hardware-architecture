# Bring-up 与可证伪 Debug

## Bring-up gate

使用真实依赖图裁剪以下阶段。每阶段定义 entry、action、observation、pass criteria、timeout、failure exit、证据文件；未知阈值阻止该阶段放行。

| 阶段 | 观察与推进依据 | 失败定位 |
|---|---|---|
| 输入/待机 | 输入范围/限流、AON rail、保护状态、无异常电流 | 源、极性、短路、inrush、接地 |
| Controller alive | ROM/固件ID、reset原因、watchdog、最小Host或本地日志 | boot/flash、clock、POR、下载路径 |
| 时钟/主rails | 根据依赖先后测PG、斜率、频率、残压 | EN owner、反馈、PG链、缺源rail |
| Reset release / FPGA配置 | reset与电源时钟时间关系、DONE及用户逻辑ready | 配置模式、供电、flash、约束；DONE不等于业务ready |
| 接口器件 | ID/revision、本地寄存器读写、strap与地址 | bus/电平、reset、地址别名、clock |
| DUT power / detect | 支路电压/电流、连接检测、DUT身份/兼容 | 限流、线损、PoC、反灌、接头 |
| Configuration | 按角色依赖配置、本地/远端readback | reverse channel尚未ready、顺序/超时、错误profile |
| Link training | 能力、lock、错误计数、训练状态、retry原因 | AUX/sideband、协议配置、PHY margin |
| Data ready | valid frame、序号、CRC、时间戳、端到端格式/速率 | routing、VC/DT、buffer/overflow、Host |

设备不支持readback或寄存器有read-to-clear时用替代证据，不能把一次读成功当整个初始化完成。

## 首次上电无图，重启正常

先定义cold boot/warm reset的真实差异：断电时长、rail残压、DUT是否持续供电、Host缓存、配置保留、温度、线缆、固件版本。复用同一配置与测点、从输入上电前开始同步记录 power/PG/clock/reset/OE/ready/link/first-frame。

对齐相同因果事件而不是随意平移全部波形；找第一处不同，而不是最后“无图”。建表：Observed failure → possible stage → dependency → observation point → isolation test。同时保留初始化、时序、状态机、协议互操作和模拟余量假设，不能因重启有效直接判固件，也不能只查SI。

| 假设 | 最小区分实验 | 结果解释 |
|---|---|---|
| ready早于服务 | 记录ready与内部配置完成，受控延后ready | 改善仅支持竞争假设，不能单独证明根因；需捕获缺失的先决条件 |
| 未清理旧状态 | 比较真实断电、局部reset、完整reinit | 故障跟随特定状态保留范围，缩小责任域 |
| PHY/采样余量 | 同源同线跨端口并测实际接收点差分/共模与数字状态 | 数字解码正常不能排除模拟门限/边沿问题 |
| 事务状态机/FIFO | 正常/失败输入对照内部长度、count、state、return-to-listen | 分离收到请求、解释请求、生成回复和移交方向 |

重试策略写次数/时间总预算、冷却或backoff、局部reset范围、日志保留与锁定退出。不得无限power cycling掩盖首次错误。复位/上电测试要记录实际配置，不能跨固件版本拼出A/B结论。

## Design for Debug

每模块至少一种无侵入status与必要的电气测点；关键处加入错误counter、trigger、UART/事件log、current monitor或loopback，数量按风险与成本。规定测量点所属域、探头带宽/负载、LA采样限制和trigger。协议流、IO方向、模拟电气三个证据层分开。

Fault tree用条件分支表达，例如无图←无有效输入 / 未ready / 训练失败 / data route错误 / buffer溢出 / Host丢弃。不要把候选原因按名单穷举而无优先级；按信息增益、低侵入与风险排序，并说明排除条件。

已有逻辑捕获需精确解码时可使用环境中可用的 logic-trace-analyzer；本Skill不内置特定格式解码器，也不要求该依赖存在。
