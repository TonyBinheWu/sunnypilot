# Toyota 低速轉向調校與上限核對

2026-11-01，目標分支：`hkg-enhanced`。已取得 StarPilot 參考來源，維護者選擇移植低速控制調校並保留原有上限。實作與設定見 [Honda／Toyota 低速轉向調校](https://github.com/TonyBinheWu/sunnypilot/blob/hkg-enhanced/docs/LOW_SPEED_STEERING_TUNE.md)。opendbc 仍釘選 `1c51731784729da5ebaf24b3c34106bd27aaf94b`，未變更 Toyota 車型控制器及 Panda safety。

## 已確認的架構

* Toyota／Lexus 平台定義共 39 個；不等於所有年式、EPS 韌體都受支援。
* `opendbc/car/toyota/values.py` 的扭力指令上限為 1500，`opendbc/safety/modes/toyota.h` 也以 1500 檢查；控制器另有 motor torque 差值、駕駛介入及轉向速率故障避免。
* `TOYOTA_RAV4_TSS2_2023` 在目前資料中明確使用 `ANGLE_CONTROL`，初始化時設定 angle steering 與 LTA safety；不能把扭力指令曲線直接套到此車型。
* HKG 的 270→409 是 HKG CAN-FD 指令數值，不能當成 Toyota 的相同物理扭矩，也不能直接據此增加 Toyota 限制。
* Toyota 既有 `ToyotaStopAndGoHack` 與縱向設定不代表已支援低速高扭；本次未改動它們。

## 另行提高上限所需資料

1. 可作為依據的參考分支／PR，或已驗證的車型、EPS 韌體與紀錄。
2. Toyota 自身的速度斷點、扭力上限、升降速率及 realtime 限制；須與 HKG 的數值分開定義。
3. 角度控制車型是否保持原 LTA 控制，或有獨立且經驗證的需求；不以強制改成 torque steering 達成表面上的全車型支援。

## 實作與驗證邊界

確認上述資料後，將能力判斷、預設關閉且非行車可調的設定、`get_car` 初始化旗標、controller、CAN 輪速來源與 Panda safety 視為同一升級單位。扭力與角度控制採各自的能力判斷。

回歸至少涵蓋：所有已收錄 Toyota／Lexus 平台的初始化與排除條件、開關關閉的原始行為、速度與量化邊界、指令變化率、motor／driver torque、realtime 限制、停用時歸零、旗標重設及其他品牌隔離。車型 controller 與 safety／mutation 測試通過後，再驗證實車 EPS 行為。

軟體測試只能驗證控制與限制的一致性，無法證明各車型 EPS 接受更高指令。尚未取得曲線及車型證據前，發布說明不宣稱 Toyota 已支援此功能。
