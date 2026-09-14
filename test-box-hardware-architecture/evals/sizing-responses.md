# v1.1 Sizing actual author responses

2026-09-14；响应作者及评者：Codex（GPT-6），SELF。输入为 [S1–S4](sizing-prompts.json) 和仓库SYNTHETIC JSON。以下是维护时实际形成的作者回答，已知实现和测试，**不是盲测、独立代理运行或实物数据**。计算实际执行，原始CLI输出留在仓库release verification记录；完整工程展开见 [worked example](../examples/worked-camera-architecture.md)。

## S1

单工位27 DUT/h，ceil(45/27)=2工位；每工位一个端口，加一路同时共享golden，所以3物理端口。该共享假设依赖两个DUT能用同一golden采集配置；若对照设置互斥需重新建表。NORMAL/STRESS/LOW的三路payload分别3.566592/6.718464/3.345408 Gbit/s。初始STRESS在CORE_AGG与HOST_STORE失败，瓶颈为CORE_AGG，不能只汇报Adapter一跳。

保留10%容量时Core需≥9.79776 Gbit/s，落盘需≥951.7824 MB/s持续写入；选择Core10 Gbit/s、存储1000 MB/s作为下一轮验证目标，三个场景算术满足。Host10 Gbit/s在当前1.06/(64/66)开销下需要7.34412096 Gbit/s，不能无依据宣称不够。上述容量是输入假设，实际验证需持续负载、驱动/CPU/文件系统压力和序号/CRC检查。

## S2

三端口×4 lane，加Host1、回环1、预留2，给出16 GT候选包络；这些是Adapter适配后的内部串行接口，不能把原生DPHY直接计成GT。IO假设分1.8/3.3 V域，72/24脚、每Bank40脚且保留20%，得3+1 Bank下界；实际family/封装/VREF/时钟脚尚未验证。

FPGA2 ms零服务加每队列64 KiB突发，共1,876,224 B。按declared usable bits/packing逐队列取整，BRAM-only需822块；512块候选不足。URAM数据队列需93块，另固定IP需92 BRAM，96 URAM+128 BRAM仅算术满足，CDC/端口/时延映射未知。外部DDR候选128 MiB、32 Gbit/s总线满足容量≥2,345,280 B及读写带宽≥25.840246 Gbit/s，仍须controller资源和效率验证。不能仅因一个BRAM候选不足宣布DDR必需。

功能区间全为教学ASSUMPTION，合计17,800–36,000 LUT、23,500–48,200 FF；70%上限对应至少51,429 LUT、68,858 FF，无像素算术DSP的当前假设为0。模型没有综合，因此不确定型号或speed grade。先用实际同配置IP报告替换区间，再做pin plan、综合/布局时序与PVT功热验证。

## S3

不能给总吞吐或LUT档位。五profile只描述可选格式集合，不定义同时有几路。先给配置矩阵框架，收集DUT工位、golden共享、分时切换与每个profile格式/帧率；在缺数时可给公式与敏感性，不把未知填成经验事实。若JSON同一场景把同一物理端口的两个profile同时激活，工具拒绝；真实硬件若是多虚拟通道，应声明聚合流或扩展明确的物理端口/虚拟通道模型后重算。

## S4

加buffer不能修复持续Core超载或写盘保留不足。先提高容量或在需求允许时降低并发/格式；本例保留原始数据并提升两跳验收目标。磁盘250 ms需Host RAM至少209,952,000 B payload，还要记录开销、突发和余量；FPGA2 ms buffer的前提是Host RAM持续接收且背压不超过2 ms。Host RAM满、重复停顿或恢复排空太慢会使该假设失效。须为每个停服域分配owner并测试恢复服务和最大积压，不能只看缓存总字节。

## 反例与当前结论

单元回归实际覆盖：缺场景、重复物理端口profile、不连续或未到终点的路径、分支各自最坏场景、负数/非有限数、每队列取整、URAM附属BRAM不足、DDR容量足而带宽不足、buffer owner错配、外置负载热与结温超限。首轮32项通过；不等于行为通过。Sizing SELF暂评3/4，缺真实IP/硬件证据和未见输入的独立前向验证。
