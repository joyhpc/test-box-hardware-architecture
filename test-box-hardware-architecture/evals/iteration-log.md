# Research → Implement → Test → Refactor → Retest

## Research / 架构草案

历史研究读取了授权材料与TI/ADI官方机制资料。原项目身份和特定设计值于2026-09-14从公开版移除，仅保留方法演进：版本模型采用HW×Assembly×FW，状态模型区分系统/模块/协议。此段为披露过的隐私概括，不宣称逐字原件。

## 首轮实现与检查

完成小入口、9份reference、pattern、模板、真实case和4种离线工具。第一批15项unittest实际运行全部通过；以T1–T6执行并保存响应。没有把这个结果视为结束。

## 反例发现与修订

1. 状态字段写“DUT asserted; pin injection UNKNOWN”时，初版unknown检查只看字符串开头，漏掉未决条件。加入真实回归测试，结果FAIL；修复为识别独立UNKNOWN/TBD token，裸N/A也列缺口。
2. 自定义state名为module/field时，初版动态输出key覆盖row元数据。加入回归测试，结果FAIL（module变成OFF）；修复为固定before_value/after_value字段。
3. 完整推导演示复核带宽margin：区分 `(capacity-required)/required` 的约2.06%与脚本采用 `(capacity-required)/capacity` 的2.0224%。统一容量保留口径，需求10%对应capacity≥8.70912Gbit/s。
4. A7反例再次检查：不变值与转换窗不能被diff工具代替；在说明和响应中保留逐状态人工推理。A8再次检查：超吞吐可触发Core修改，不能让Stable Core原则覆盖真实物理限制。A10再次检查：延时一次成功不闭合根因。
5. 最终安装检查发现Windows默认编码使初始化器写出的openai.yaml为GBK。实际UTF-8读取失败后转换为UTF-8，并将所有文本资源编码检查纳入check_package，避免只验证SKILL.md而漏掉UI元数据。

## 重测

17项unittest全部通过，包括两个先失败后修复的测试；四种CLI示例实际执行，预期输出INCOMPLETE或容量不足也正确返回非零。T3/A7与T2/A8、T4/A10按修订契约重查，实际响应与assessment保留。

局限：行为测试SELF、非盲测；没有独立代理或新模型会话运行，没有实物上电/故障注入，没有客户端自动触发验证。后续真实项目应固定Skill版本和输入，保留新响应并追加迭代，不覆盖这轮证据。

## v1.1：公开内容与Sizing修订，2026-09-14

用户审查证实早期校验通过并不代表数量推导充分，也发现公开材料边界失守。公开case改为匿名证据角色，删除原文件身份与具体非公开技术结论；原始历史仅保留在私有归档。历史SELF记录做了已披露的隐私泛化，不假装为逐字原件。

新增配置矩阵、Sizing Parameter Sheet、逐跳budget v2与resource，旧同构schema回归保留。重写示例从45 DUT/h推到3端口、Host落盘、GT/Bank/存储/逻辑、功热和延迟；初始两跳容量失败与调整后的候选均保留JSON。首次17旧+15新=32项回归实际通过。

第二轮用畸形资源对象追加第33项测试，实际发现`power: []`绕过数值检查，在`sizing.resource`读取`p.get('loads')`时报`AttributeError: 'list' object has no attribute 'get'`，测试输出`FAILED (errors=1)`。修复为对buffer/production/power/external_memory先校验对象类型，返回可解释的INPUT_ERROR。该失败是工具错误处理缺口，不能改写为从未失败；修复后重测结果见release verification。

行为S1–S4为作者在已知实现下形成的实际回答，SELF/非盲测。旧评分保留并追加回溯更正，不把新脚本测试或新示例计成独立行为成功。没有硬件/RTL综合/客户端触发验证。
