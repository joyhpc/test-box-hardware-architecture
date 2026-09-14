# 能力矩阵

按工程问题定位方法、产物和证据。这里列能力与边界，不依赖未随仓库发布的需求编号。

| 工程问题 | 方法与产物 | 验证 / 局限 |
|---|---|---|
| 系统该做什么、边界在哪 | [top-down](../test-box-hardware-architecture/references/top-down.md)，Requirement Contract | T1/T6历史SELF；不能从芯片清单倒推用途 |
| 要几个端口、多大FPGA | [sizing](../test-box-hardware-architecture/references/sizing.md)，配置矩阵与参数表 | [完整数字案例](../test-box-hardware-architecture/examples/worked-camera-architecture.md)，scenario budget/resource回归；参数是假设，非综合结果 |
| 异构流在哪一跳过载 | [工具](../test-box-hardware-architecture/scripts/README.md)，每跳余量/瓶颈/停服buffer owner | 到Host落盘；不自动模拟封装变换/重传/共享总线调度 |
| 如何复用Core、替换Adapter | [modules-planes](../test-box-hardware-architecture/references/modules-planes.md)，模块/复用/传播矩阵 | T2/T5/A8；超过包络可要求Core改变 |
| 接口在掉电、空闲、恢复时怎样工作 | [interfaces](../test-box-hardware-architecture/references/interfaces.md)、[lifecycle](../test-box-hardware-architecture/references/lifecycle.md) | T3/A1/A2/A7；diff不替代模拟验证或转换窗分析 |
| 谁先上电、谁控制谁 | [power-clock-reset](../test-box-hardware-architecture/references/power-clock-reset.md)，依赖与默认态 | dependency cycle/传播回归；边的工程语义须人工确认 |
| 不出图或冷启动失败如何定位 | [bringup-debug](../test-box-hardware-architecture/references/bringup-debug.md)，首个分叉与隔离实验 | T4/A10；尚无本包实物验证 |
| 审查结果如何闭环 | [review-validation](../test-box-hardware-architecture/references/review-validation.md)，需求到验证追踪 | trace回归只检查结构；证据真实性与判据质量靠工程审查 |
| 历史材料能证明什么 | [evidence](../test-box-hardware-architecture/references/evidence.md)，私有证据库与公开匿名角色分离 | 公开清单不提供原始物证；不能冒充独立case复核 |

行为证据与工具测试分开记录，见 [evals](../test-box-hardware-architecture/evals/README.md)。早期Top-down评分遗漏sizing深度，已保留原评分并追加更正，未把新文档冒称为旧响应的表现。
