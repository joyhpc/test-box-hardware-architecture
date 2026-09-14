# Test Box Hardware Architecture Design Skill

面向硬件系统工程师的可复用架构方法：从应用场景推导并发端口、逐跳容量和器件资源，再形成模块契约、生命周期与验证计划。支持测试盒、Camera/SerDes、FPGA/SoC验证平台、接口适配及bring-up；不内置固定BOM，不控制硬件。

从 [Skill入口](test-box-hardware-architecture/SKILL.md) 开始，或直接阅读 [完整定量示例](test-box-hardware-architecture/examples/worked-camera-architecture.md)：45 DUT/h → 2工位+golden → 3端口 → 异构逐跳容量 → GT/Bank/BRAM/URAM/DDR/逻辑档位。所有示例数值均有假设边界，不代表已验证硬件。

```text
使用 $test-box-hardware-architecture。
为支持五种Camera格式的平台，从工位节拍和golden需求建立配置组合矩阵，
推导端口、逐跳带宽、FPGA资源包络，再给模块契约和验证计划。
```

复制或安装时保留整个 `test-box-hardware-architecture/` 目录。维护源与已安装副本分开；打包工具默认只生成ZIP，指定安装目录时拒绝覆盖已有内容。客户端发现与自动选择尚未验证。

- [能力矩阵](docs/capabilities.md) · [资料目录](test-box-hardware-architecture/README.md)
- [工程工作簿](test-box-hardware-architecture/assets/architecture-workbook.md) · [Sizing方法](test-box-hardware-architecture/references/sizing.md)
- [离线工具与schema](test-box-hardware-architecture/scripts/README.md)
- [评测、实际响应与局限](test-box-hardware-architecture/evals/README.md) · [修订后的SELF评估](test-box-hardware-architecture/evals/assessment.md)

维护校验使用Python 3.11+标准库，CI在Windows/Linux运行：

```powershell
python -X utf8 tools/check_package.py
python -X utf8 -m unittest discover -s test-box-hardware-architecture/evals -p 'test_*.py' -v
```

当前版本1.1.0。公开case只保留匿名证据角色与泛化机制；原始项目名称、文件身份、指纹及非公开设计细节不属于公开包。算术/结构回归与作者SELF评测分别记录，不宣称独立盲测、综合通过或实物验证。代码及原创方法文档采用 [MIT License](LICENSE)；链接的第三方文档保留其原有权利。
