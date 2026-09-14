# Behavioral Evaluation Rubric

评对象是实际响应及产物，不是SKILL.md中有没有关键词。每维0–4：0缺失/错误；1仅列名词；2有合理推理但关键链未闭合；3推理正确、有证据边界和可执行动作；4在任务范围内闭环、主动验证反例且无重大缺口。不适用项写N/A和理由，不能机械给4分。

| 维度 | 3–4分必须看到的行为 |
|---|---|
| Top-down thinking | 从用途/边界/需求到模块契约；已有芯片作为约束 |
| Sizing / capacity derivation | 应用/节拍→配置组合矩阵→物理端口/并发→逐跳到需求终点→GT/IO/存储/逻辑/功热包络；数值有单位、来源/假设、余量与关闭测试 |
| Architecture correctness | 角色与数据方向正确，Plane/clock/reset依赖不混淆 |
| Modularity | 稳定Core、可变Adapter且有物理包络与替换代价 |
| Coupling | 能列出供电/时钟/固件/机械隐性传播，不承诺无条件零影响 |
| Lifecycle completeness | OFF/部分供电/BOOT/IDLE/FAULT/RECOVERY和转换窗口有针对性覆盖 |
| Interface correctness | 保证门限、IO域、termination、bias、owner与有效性相互一致 |
| Fault awareness | 触发→机制→后果→隔离/退出，不无限重启 |
| Debug usefulness | 可观察首个分叉，实验能区分候选原因，说明不同结果下一步 |
| Evidence discipline | 版本、事实/推断/未知分开；不把数字波形当模拟证明 |
| Over-design | 与台数/环境/复用/成本匹配，能拒绝无收益复杂度 |
| Clarity | 按Level渐进给信息，图和表的语义可理解 |
| Actionability | 能执行的契约/测点/判据/owner或明确获取办法 |

建议阈值：适用维度均≥2，平均≥3；不得有hard fail。此阈值是Skill维护标准，不是硬件认证。

Hard fail：未有需求/接口便凭芯片倒推系统；**未定义最坏并发组合就给吞吐结论**；**给出器件档位或资源规模却没有可追溯容量推导**；以hysteresis/Hi-Z直接宣布安全；忽略带电接口的partial power；将冲突版本混成事实；虚构器件保证值/标准等级/实测/根因；超出带宽仍承诺Core不改；把结构检查称电气PASS；擅自控制硬件或注入故障。

Sizing可写N/A的情形：仅做既有状态差分且范围内没有新增吞吐或器件规模结论；必须解释裁剪理由。输入缺数时应写条件区间与获取办法，不能为获得评分伪造参数。工具输出存在不等于工程推导完整，须核输入与需求的追踪。

每项打分必须链接response中的实际证据，记录shortcoming与retest。作者自评分标SELF，不冒充独立盲测或统计性能。独立评测若被明确授权，评者只收skill+raw prompt+必要原始资料，不提供预期答案。
