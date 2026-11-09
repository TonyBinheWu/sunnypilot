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

1. 沿用原控制器既有的低速比例增益，不再額外放大橫向誤差。舊版移植的二次放大也會影響積分與摩擦補償，可能加劇小幅左右需求的反覆修正；本次移除此疊加，不增加 CAN 指令上限。
2. 用曲率歷史乘以當前車速平方重建延遲加速度，減少起步加速本身產生的假 jerk。
3. 在 0.5～2.5 m/s 淡入 roll／offset 前饋修正；避免接近步行速度時，固定偏差壓過轉向需求。
4. 在近中心區抑制微小 jerk 對摩擦補償的反覆觸發，並限制這項摩擦前瞻的 jerk 輸入。
5. 此次移植額外於 10～15 m/s（36～54 km/h）將歷史與摩擦修正漸退；15 m/s 起回到原有計算。沒有移植 StarPilot 全車種的 PI 係數與專屬車型調校。
6. 新功能啟用時，在停用／駕駛接管重設其歷史與積分器；輸出維持正規化 ±1 範圍，車型 controller 及 safety 仍執行既有的速率、扭力、motor／driver torque 與故障避免限制。

本次修正後，記錄中的 `LateralTorqueState.version` 為 200（v0＋此調校）或 201（v1＋此調校）；舊版為 100／101，關閉或不符合條件時維持原版本。這個標記表示選中的調校路徑，不表示每一幀都在施加低速補償。

## 大模型與方向盤左右晃動修正

大、小模型都將轉向需求交給相同的車輛控制器，此調校不依模型名稱切換增益。原控制器在 5 m/s（18 km/h）已有 `kp = 11.5`；舊調校又將誤差乘上約 1.44，且同一份放大誤差進入 P、I 與摩擦補償。新模型的小幅正負變化可能因此被加劇，單純限制最終扭力上限無法排除此問題。

`2026.003.008` 移除 v0／v1 的二次誤差增益，保留曲率歷史、roll／offset 淡入、中心 jerk deadzone，以及原車型的扭力／速率與 safety 限制。此修正不變更模型輸出或增加濾波延遲。HKG CAN-FD 的另一套動態扭力換算修正另見 [HKG 說明](HKG_LOW_SPEED_TORQUE.md)，不套用本節的 Honda／Toyota 調校。

新增以 20 Hz 小幅正負交替需求驅動實際 v0／v1 控制器的回歸測試，覆蓋 RAV4 TSS2、Honda Civic 與六個速度點，逐幀比對原控制器的 P、I 與誤差，避免飽和輸出掩蓋增益疊加。這是控制器層測試，沒有執行指定大模型權重或模擬實際 EPS；尚需故障車型、模型名稱及 rlog 確認是否還有延遲、校正或其他震盪因素，不能據此宣稱所有大模型與車型均已完成實車驗證。

## C4 顯示不可用時

`2026.003.004` 起，C4「轉向」頁面先顯示目前狀態，區分尚未辨識車型、仍在行車模式、NNLC／橫向 Jerk 衝突、角度控制、僅記錄模式或轉向設定未就緒。

RAV4 2019–2020 對應的 `TOYOTA_RAV4_TSS2`，以及 `TOYOTA_COROLLA`／`TOYOTA_COROLLA_TSS2` 的序列化車型資料，都可通過目前的 C4 設定判斷。若啟用 NNLC 或 Lateral Jerk Torque Controller，開關仍會依原設計禁用；不能只根據「不可用」推斷該年式不受支援。個別車輛仍以實際辨識平台及設定為準。

衝突時可於非行車狀態按 **關閉 NNLC／Jerk**，明確關閉這兩項調校後再選擇低速調校。此操作不會自動開啟低速調校，也不更改強制扭力控制、車型或 safety 限制；下次行車才使用新的控制器設定。若狀態提示需要扭力控制，再依既有設定啟用「強制扭力橫向控制」。

若新版狀態仍不符合預期，可在已完成編譯的裝置執行唯讀診斷：

```bash
cd /data/openpilot
python tools/diagnostics/check_low_speed_steering.py
```

報告只讀取機種、版本、相關開關與必要的車型／轉向設定，不變更 Params，也不包含 VIN、路線或金鑰。`block_reason` 會列出實際禁用原因；`would_enable_with_current_car_params` 是依目前資料重建控制器時的判斷，不代表正在行車的控制器已即時切換。

## 驗證與維護

`test_low_speed_steering.py` 驗證車型排除、Toyota 平台初始化不變、v0／v1 的低速反應與輸出界限、停用／接管／重啟、其他控制器排除、前饋與速度邊界、sunnylink 能力及中文抽取。

關閉功能的數值基準取自修改前的 `hkg-enhanced@ef3e9ec8cde918d71c64e2f8986ed550e6e44cb8`，使用既有 opendbc pin；fixture 不是由新實作覆寫生成。更新此基準必須先解釋控制行為差異。

軟體測試與主機 UI 驗證不代表已完成 C3X／C4、各 EPS 韌體或實車操控驗證。保持預設關閉，實車驗證需分別記錄車型、版本、controller v0／v1、車速、橫向誤差、飽和、駕駛介入及轉向紀錄。若需回復，在非行車狀態關閉開關，於下次行車恢復原調校。

初次移植的驗證結果：10 項新調校測試、95 項 sunnylink／翻譯／更新說明回歸，以及 C3X／C4 各 5 項正常 UI／平台檢查通過；當時的 Ruff 與 sunnylink 產生檔一致性通過。另以 headless 介面核對兩機種的車型限制、非行車限制及中文開關，C4 也檢查 NNLC／jerk 互斥和禁用時不寫入設定。

2026-11-09 修正驗證：原生 Linux 控制器測試中，舊版在 24 組交替需求條件中有 20 組重現額外誤差放大；修正後全數通過。低速調校、可用性、控制器緩衝、控制器延伸與更新說明共 31 項測試通過，修改檔案的 Ruff 及版本／繁體中文更新項目一致性檢查通過。此輪未執行模型推論、硬體或道路測試。
