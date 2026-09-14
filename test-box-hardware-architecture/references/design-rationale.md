# Design Rationale

## 为什么小入口+分层资料

SKILL.md只保留任务路由、推理顺序和不能丢失的约束。新设计、换型、partial power、debug、review和项目挖掘分别读取对应reference；避免每次架构问题都加载全部协议/器件细节。模板是可生成的交付契约，case是有限证据，eval是行为反例，职责分开。

## 架构选择

1. 采用Stable Core+Replaceable Adapter作为优先候选，而非规定物理板数。“同一连接器”远不足以稳定接口，需电气/状态/固件/机械包络。高速损耗或成本不支持拆板时允许合板。
2. Data、Control、Management在语义上独立，Power与Clock/Reset独立分析；共享Ethernet/USB允许，但必须说明容量与失联依赖。监控职责可分布，不增加重复控制owner。
3. Lifecycle从线性阶段词汇升级为分层、有并行电源域的状态图。AUX资料中的init、transaction、training、source policy不能混为单状态机；OFF也不保证外部线无电。
4. State Differential同时考虑不变风险和转换窗口。接收器输出高阻不必强行变成0，可靠的下游valid mask也可以满足系统解释不变量，但需验证mask/unmask窗口。
5. 证据采用类型标签+配置版本+原始来源范围。不能只按mtime或latest选版本；私有原始证据与公开匿名索引分离。
6. 实现脚本只做可确定的差分、图依赖/传播、异构逐跳容量、资源下界和追踪检查；不做泛化“电气安全评分”。schema显式保留UNKNOWN，CLI没有硬件控制入口。
7. 行为评测保留原prompt、实际响应、SELF身份、评分与反例重测。工具15→17项的实际失败/修复证明迭代发生，但不是硬件或模型质量的充分证明。

## 未采纳的设计

不内置固定SerDes/FPGA型号与电阻值：具体器件应是接口推导结果，版本和供应也会变化。不把所有ground隔离、所有功能做插件、所有控制放FPGA；这些都需需求、依赖和成本支持。不将existing logic-trace-analyzer复制成第二份解码器，只在确有捕获解码需求且可用时引用能力。

## 进入下一个真实项目

以Requirement Contract和受控baseline开始。先跑接口/电源/生命周期模型，再做候选器件和电路；关闭关键UNKNOWN后执行实际VAL。新案例必须给反例和适用范围，不能把一次项目修复直接升成通用规则。
