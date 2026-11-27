# CCNC 低速高扭換算修正

`ccnc-port` 的 HKG CAN-FD 動態高扭功能使用本分支釘選的 opendbc、`HkgLowSpeedTorque` 開關及 CCNC 車型設定。

`2026.003.005` 同步主維護分支的 `HkgTorqueScale` 換算修正。控制器內部使用原本 270 CAN 單位基準，將額外扭力作為可用餘裕；送出前才依當下動態上限換算至正規化需求。同樣的小幅需求不再因低速上限為 409 而被額外放大約 51.5%。

保留 409→270 上限曲線、4／6→2／3 速率、駕駛介入、EPS 高角度保護及既有 Panda safety；沒有修改 CCNC opendbc pin。此版不加入 Honda／Toyota 低速調校。

扭力學習改以 `torqueOutputCan / 270` 使用固定尺度，高扭啟用時學習版本為 101，拒絕舊尺度及開關狀態不同的快取。

新增控制器／車輛介面串接、速度量化、可用上限與快取回歸。主機及模擬器不能模擬 C3X／C4 相機、USB、eGPU 或 CCNC EPS；個別模型與車輛仍需實機紀錄驗證。
