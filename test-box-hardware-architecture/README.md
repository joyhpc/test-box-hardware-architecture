# Test Box Hardware Architecture — v1.1.0

用于测试盒、调试盒、接口转换、Camera/SerDes、FPGA/SoC、视频链路、域控配套与工程验证设备的设计、review、变更和bring-up/debug。不是某款板的参考BOM，也不自动控制硬件。

## 入口

调用 `$test-box-hardware-architecture`，或让AI直接读取本目录 [SKILL.md](SKILL.md)。移动/安装时复制整个目录，保留references、patterns、assets、examples、evals和scripts；只复制入口会丢框架。保持默认自动选择资格，实际客户端发现/触发需在相应客户端验证。

## 交付内容

| 内容 | 入口 |
|---|---|
| 方法论/Requirement/分类/ADR | [top-down](references/top-down.md) |
| 并发配置/逐跳容量/资源档位 | [sizing](references/sizing.md) |
| 模块分解/三Plane/参考架构/复用评分 | [modules-planes](references/modules-planes.md) |
| 接口/高速分层/带宽/器件候选 | [interfaces](references/interfaces.md) |
| 生命周期/差分/不变量/转换窗口 | [lifecycle](references/lifecycle.md) |
| 电源/时钟/复位/接地/EMC | [power-clock-reset](references/power-clock-reset.md) |
| Bring-up/Debug/故障树 | [bringup-debug](references/bringup-debug.md) |
| Review/Validation/可靠性/制造维护 | [review-validation](references/review-validation.md) |
| 版本、证据与项目挖掘 | [evidence](references/evidence.md)、[sources](references/sources.md) |
| 可复用模式与反模式 | [library](patterns/library.md) |
| 项目填写模板 | [architecture-workbook](assets/architecture-workbook.md) |
| 匿名证据角色/完整教学推导 | [case-studies](examples/case-studies.md)、[worked example](examples/worked-camera-architecture.md) |
| 工具/行为评测 | [scripts](scripts/README.md)、[evals](evals/README.md) |
| 设计理由/局限 | [rationale](references/design-rationale.md)、[limitations](references/limitations.md) |

工具只检查显式输入的结构/算法。示例中的UNKNOWN与容量不足是故意保留的工程未决项；非零结果不是包安装失败。具体命令见scripts说明。

## 维护方式

改规则时至少关联一个case或新输入与反例，解释适用边界，避免累积万能禁令。更新外部数值必须确认准确文档版本；不要为规避UNKNOWN填典型值。私有原始证据与公开角色索引分别维护；公开清单只保留匿名ID、artifact_role、locator与evidence_scope。发布前审查技术内容、身份、路径和文件指纹，自动检查只是辅助。历史评测的隐私泛化必须披露。
