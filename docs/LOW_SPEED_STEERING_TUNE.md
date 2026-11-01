# Honda／Toyota 低速轉向調校

適用分支：`hkg-enhanced`。此功能不加入僅維護 CCNC 的 `ccnc-port`。

本功能依維護者選擇，移植 StarPilot 的低速控制調校並保留原有車輛扭力上限。它與 HKG 的低速動態 CAN 扭力上限是不同設定；不改寫 opendbc、Panda safety、EPS 韌體、最低轉向速度或停車轉向能力。

## 來源與移植範圍

參考 `StarPilotHQ/StarPilot` 的 `StarPilot` 分支，固定提交 `98f8443122909a86c5a5fd628337c4077cd1f957`。來源的 [torque controller](https://github.com/StarPilotHQ/StarPilot/blob/98f8443122909a86c5a5fd628337c4077cd1f957/selfdrive/controls/lib/latcontrol_torque.py)提供低速誤差補償、曲率歷史、roll／offset 淡入及中心 jerk deadzone。

該提交的 Toyota [controller 參數](https://github.com/StarPilotHQ/StarPilot/blob/98f8443122909a86c5a5fd628337c4077cd1f957/opendbc_repo/opendbc/car/toyota/values.py)與 [safety](https://github.com/StarPilotHQ/StarPilot/blob/98f8443122909a86c5a5fd628337c4077cd1f957/opendbc_repo/opendbc/safety/modes/toyota.h)仍為 1500 上限，不能作為全 Toyota 提高上限的依據。其 [Honda controller](https://github.com/StarPilotHQ/StarPilot/blob/98f8443122909a86c5a5fd628337c4077cd1f957/opendbc_repo/opendbc/car/honda/carcontroller.py)另有修改 EPS Civic 的濾波與接管判斷，本次不移植這些韌體相關調校，也不把個別車型的左右側係數擴大到所有車型。

StarPilot 為 MIT 授權；改編模組內保留完整來源版權及授權文字。新功能用共用 helper 接入本專案的 torque v0 與 v1，保留既有控制器選擇方式及 MADS 啟用判斷。

## 設定與適用條件

* C3X：Settings → Steering → **Honda／Toyota 低速轉向調校（實驗功能）**。
* C4：設定 → **轉向 → 低速轉向調校**。同頁提供既有的「強制扭力橫向控制」設定，供原本使用 PID 的相容平台選用。
* 預設關閉。僅在非行車狀態可調，於控制器下次建立時讀取；行車中直接寫入 Params 不會即時換調校。
* 必須是本分支 opendbc 已收錄的 Honda／Toyota／Lexus 平台、實體扭力轉向、有效的對應 safety mode，且不是 dashcamOnly。
* **實際使用 torque lateral controller 才會生效。** 原本為 PID 的 Honda 車型需先選用既有的強制扭力控制；此功能不會自行切換控制模式。
* 角度控制／LTA、未知平台及其他品牌排除。若 NNLC 或 Lateral Jerk Torque Controller 開啟，此功能不生效，避免疊加兩套計算。
* sunnylink 使用相同能力判斷及非行車限制。

目前 pin 的程式能力候選為 Toyota／Lexus 38／39 個平台、Honda 36／36 個平台；被排除的 Toyota 角度控制平台為 `TOYOTA_RAV4_TSS2_2023`。這是平台與實體控制模式的判斷，不代表全部候選都已選用 torque controller，亦不是實車驗證清單。

## 實際行為

1. 在低速放大橫向誤差的比例補償，減輕低速幾何模型造成的不足；不是增加 CAN 指令上限。
2. 用曲率歷史乘以當前車速平方重建延遲加速度，減少起步加速本身產生的假 jerk。
3. 在 0.5～2.5 m/s 淡入 roll／offset 前饋修正；避免接近步行速度時，固定偏差壓過轉向需求。
4. 在近中心區抑制微小 jerk 對摩擦補償的反覆觸發，並限制這項摩擦前瞻的 jerk 輸入。
5. 此次移植額外於 10～15 m/s（36～54 km/h）將低速增益與歷史修正漸退；15 m/s 起回到原有計算。沒有移植 StarPilot 全車種的 PI 係數與專屬車型調校。
6. 新功能啟用時，在停用／駕駛接管重設其歷史與積分器；輸出維持正規化 ±1 範圍，車型 controller 及 safety 仍執行既有的速率、扭力、motor／driver torque 與故障避免限制。

記錄中的 `LateralTorqueState.version` 為 100（v0＋此調校）或 101（v1＋此調校）；關閉或不符合條件時維持原版本。這個標記表示選中的調校路徑，不表示每一幀都在施加低速補償。

## 驗證與維護

`test_low_speed_steering.py` 驗證車型排除、Toyota 平台初始化不變、v0／v1 的低速反應與輸出界限、停用／接管／重啟、其他控制器排除、前饋與速度邊界、sunnylink 能力及中文抽取。

關閉功能的數值基準取自修改前的 `hkg-enhanced@ef3e9ec8cde918d71c64e2f8986ed550e6e44cb8`，使用既有 opendbc pin；fixture 不是由新實作覆寫生成。更新此基準必須先解釋控制行為差異。

軟體測試與主機 UI 驗證不代表已完成 C3X／C4、各 EPS 韌體或實車操控驗證。保持預設關閉，實車驗證需分別記錄車型、版本、controller v0／v1、車速、橫向誤差、飽和、駕駛介入及轉向紀錄。若需回復，在非行車狀態關閉開關，於下次行車恢復原調校。

本機驗證結果：10 項新調校測試、95 項 sunnylink／翻譯／更新說明回歸，以及 C3X／C4 各 5 項正常 UI／平台檢查通過；新版 Ruff 與 sunnylink 產生檔一致性通過。另以 headless 介面核對兩機種的車型限制、非行車限制及中文開關，C4 也檢查 NNLC／jerk 互斥和禁用時不寫入設定。
