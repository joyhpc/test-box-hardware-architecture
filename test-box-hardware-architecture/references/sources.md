# 官方来源与核验边界

核验日期：2026-09-07。以下为实际访问的公开厂商文档；用于机制与方法，不替代项目的受控规范、具体器件数据表与errata。搜索引擎的发布日期不能当文档修订日期。下述归纳为本Skill的工程推导。

| ID | 来源 | 用途 / 限制 |
|---|---|---|
| EXT-01 | [TI LVDS Owner's Manual, fourth edition, 2008，§4.6](https://www.ti.com/lit/ug/snla187/snla187.pdf) | 端接、failsafe与M-LVDS接收器类型；不将书中历史器件速率当现代标准上限 |
| EXT-02 | [TI SSZT432 powered-off protection](https://www.ti.com/document-viewer/lit/html/SSZT432/GUID-663B212B-D217-43C9-88A4-B7A51ABDEB40) | 信号引脚向掉电域反灌与保护机制；实际Ioff/电压范围查具体器件 |
| EXT-03 | [ADI AN-932 Power Supply Sequencing](https://www.analog.com/en/resources/app-notes/an-932.html) | 电源排序属于器件接口约束；不推导所有芯片共用时序 |
| EXT-04 | [ADI Getting Started with GMSL](https://wiki.analog.com/products/gmsl/getting_started) | 官方硬件/调试文档入口；系列、版本、配置需继续取对应手册 |
| EXT-05 | [TI SDAA295 DP/eDP Link Training Utilizing AUX](https://www.ti.com/lit/an/sdaa295/sdaa295.pdf) | 分开AUX交互、能力读取与主链路训练；不是所有DP代际完整规范 |
| EXT-06 | [TI SLVAFR3 system-level transient immunity](https://www.ti.com/document-viewer/lit/html/SLVAFR3/GUID-7F89B48F-6B8F-45D0-A2F4-22806A8048AB) | 器件HBM/CDM与整机瞬态抗扰度区别；项目等级/测试方法需受控标准 |

不在Skill固化GMSL/FPD-Link/MIPI/DP/PCIe等接口的通用电压或时序数字。每次器件实现按exact part、revision、工作条件查询primary datasheet；未获得的付费/保密标准标UNKNOWN，不编造条款或认证结论。
