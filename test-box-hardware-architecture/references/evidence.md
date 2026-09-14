# 证据、版本与项目挖掘

## 资料登记

在项目授权的**私有证据库**登记 source_id、原始文件身份、设计/装配/固件版本、受控日期、定位、指纹、status、supersedes 和可信范围。公开包只留匿名 ID、artifact_role、locator、evidence_scope；不复制项目名称、本地路径、原文件名、hash、mtime或非公开设计细节。技术内容也须泛化，改名不足以完成审查。status 可为 released/draft/historical/superseded/conflicting/unknown。设计/装配/固件是不同维度，不能按一个数字排序。

选择基线先看用户明确指定的实物/发布记录，再核变更记录和同一套设计/BOM/PCB/固件对应关系。mtime仅帮助定位；Final/latest不证明有效性。后续草稿不自动替代已发布版；新发布包存在也不证明旧报告中的风险已修复。

同一claim若冲突，保留双方值、定位与适用版本；可证明版本变更则分开叙述，无法判定则UNKNOWN。使用“最近可核验的本地快照”，不要写“公司当前最新版”除非有证据。

## 类型纪律

- FACT：原始资料直接支持的有限陈述；如“报告X第Y节写了Z”仅证明报告内容。
- ASSUMPTION：为继续分析采用的临时参数，有owner、影响与失效条件。
- INFERENCE：证据到结论的推理，列出替代解释和证伪途径。
- CONSTRAINT：用户/规范/既有接口限制，保留来源与适用条件。
- DECISION：方案选择，链接ADR与回看触发条件。
- RISK：条件满足时的可能失效，不自动等于缺陷事实。
- OPEN QUESTION：需回答的具体问题及责任人/验证手段。
- UNKNOWN：没有足够证据；不能静默替换为典型值或N/A。

数字采样可支持协议事件，不能证明模拟幅度、共模、眼图；原理图相同不能证明layout/批次/RTL相同。项目报告、AI生成规格书、提取JSON/CSV要与原始图纸/测量做可获得的交叉核验。不得从“报告建议改”推出“当前实物已改”。

## 挖掘与泛化

1. 只读当前授权相关资料，先项目/文件清单，再按问题取内容，排除软件测试fixture和无关文件。
2. 建版本关系，选择scope；找需求模式、重复模块、实际观察与失败假设。
3. 每个case记录 source → observation → pattern → scope → rule → counterexample → validation/eval。
4. 找另一授权项目或官方机制支撑；只有单例时标 single-case heuristic。项目名、位号和具体技术值只留在私有证据库；公开 case 留一般机制、适用范围和验证方法。
5. 避免“加了延时就证明根因”“floating需全加pull-up”“所有接口做插件”等过拟合结论。

公开案例边界见 [case-studies](../examples/case-studies.md)，匿名角色清单见 [source-manifest](../examples/source-manifest.json)。此清单不含可复核原件，不能作为独立物证。公开发布检查与私有证据完整性是两道不同检查；前者不能替代后者。
