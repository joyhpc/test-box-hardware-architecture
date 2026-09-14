# 自动工具回归 + 半自动行为评测

本包提供两条独立验证线。工具测试检查算法/错误处理；行为评测执行真实输入，留存完整回答，再按rubric评判。不能用关键词匹配或测试数量替代架构正确性。

```powershell
python -X utf8 -m unittest discover -s evals -p 'test_*.py' -v
```

在Skill文件夹运行。仓库级检查在仓库根目录：`python -X utf8 tools/check_package.py`。初始化格式校验可用skill-creator自带quick_validate，不是本Skill运行依赖。

行为输入：[prompts.json](prompts.json)。实际作者执行响应：[responses.md](responses.md)。评分：[assessment.md](assessment.md)。迭代：[iteration-log.md](iteration-log.md)。这轮是SELF、非盲测；未启动独立评测代理，也未测试客户端自动触发。

后续半自动流程：冻结Skill版本/hash→逐项输入prompts→保存未改写响应与产物→按[rubric](rubric.md)人工逐维判分→保存证据定位与hard-fail判断→修复→对受影响场景重跑，并保留前一轮。真实项目用版本固定的raw artifacts替换模拟输入，结果仍区分文档推理和实物验证。

v1.1增加 [S1–S4输入](sizing-prompts.json) 与 [实际作者响应](sizing-responses.md)，补测数量推导及其反例。历史记录的隐私泛化已披露，不再宣称公开版是逐字原件。

基本验收T1–T6不可删；A1–A10是反例。至少再做一次正常场景和反例，不在首次全部通过后结束。
