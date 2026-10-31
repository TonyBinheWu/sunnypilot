# sunnypilot — ccnc-port

由 [TonyBinheWu](https://github.com/TonyBinheWu) 維護，基於 [sunnypilot](https://github.com/sunnypilot/sunnypilot)，並承襲 [comma.ai openpilot](https://github.com/commaai/openpilot)。本分支同時以 **comma 3X（C3X）與 comma four（C4）** 為持續維護對象。

## 分支定位與車種範圍

此分支的維護與驗證範圍限定為 Hyundai／Kia／Genesis 的 **CCNC 車型**，包含對應的車輛辨識、CAN-FD 通訊、控制器與儀表整合。

安裝前請確認實際車型、年式、配備與本分支釘選的 opendbc 資料相符。CCNC 支援仍須按具體平台驗證，不能僅依品牌或螢幕外觀判斷相容性。

其他車種的維護分支請參閱 [hkg-enhanced](https://github.com/TonyBinheWu/sunnypilot/tree/hkg-enhanced)。

## C3X 與 C4 維護目標

| 機種 | 維護方向 |
| --- | --- |
| C3X | 持續移植適用的上游功能、修正與相容性更新，維持可持續更新的使用體驗。 |
| C4 | 跟進上游發展，並驗證本分支車輛支援與客製功能。 |

兩種機器都納入發布檢查。模型、推論效能與硬體相依功能會依機種能力處理；特定機種的功能差異與限制會寫入更新項目。每次發布仍須分別完成 C3X 與 C4 的裝置驗證。

## 版本號與繁體中文更新項目

最新版本與發布日期請查看 [CHANGELOG.md](CHANGELOG.md)。裝置使用的版本定義位於 [SUNNYPILOT_VERSION](openpilot/sunnypilot/common/version.h)。

* 更新說明標示分支名稱、版本號、發布日期，以及使用者可理解的繁體中文變更內容。
* C3X：在軟體設定與更新通知查看對應版本的更新說明。
* C4：在軟體設定查看「更新項目」與「目前版本更新說明」；安裝前先顯示可捲動閱讀的更新內容。
* 將裝置語言設為繁體中文，以使用中文介面與對應字型。新的 C4 說明入口需先安裝包含此功能的版本。

維護者每次發布都需同步更新版本標頭與 `CHANGELOG.md`。完整流程與檢查方式請參閱 [C3X／C4 版本與更新說明](docs/DEVICE_RELEASE_NOTES.md)。

## 安裝與更新

1. 確認車型、硬體與所需線組符合相容性要求，參閱 [sunnypilot 安裝指南](https://community.sunnypilot.ai/t/read-before-installing-sunnypilot/254)。
2. 選用本儲存庫的 **`ccnc-port`** 分支。
3. 在軟體資訊確認儲存庫為 `TonyBinheWu/sunnypilot`、分支為 `ccnc-port`，並核對版本與更新項目。
4. 首次安裝或更新完成後，在停車狀態確認系統、模型與車輛辨識正常，再進行裝置及車型驗證。

## 回報問題與貢獻

請在[本儲存庫 Issues](https://github.com/TonyBinheWu/sunnypilot/issues) 提供分支、版本、C3X／C4 機種、車型年式、問題發生步驟與可供分析的紀錄。提交紀錄前請移除個人敏感資訊。

針對本分支的修正，Pull Request 請以 **`ccnc-port`** 為目標。跨分支共用的更新需分別檢查車種範圍與兩種機器的相容性。

## 上游文件與社群

* [sunnypilot 原始碼](https://github.com/sunnypilot/sunnypilot/tree/master)
* [openpilot 原始碼](https://github.com/commaai/openpilot)
* [sunnypilot 文件](https://docs.sunnypilot.ai/)
* [sunnypilot 社群論壇](https://community.sunnypilot.ai/)

## 資料與隱私

沿用 sunnypilot／openpilot 的資料處理機制。預設會向 comma 伺服器上傳駕駛資料，並可透過 [comma connect](https://connect.comma.ai/) 存取；使用者可依設定停用資料收集。

系統記錄道路攝影機、CAN、GPS、IMU、磁力計、溫度感測器、當機與作業系統紀錄。駕駛攝影機及麥克風僅在使用者明確選擇啟用時記錄。使用本軟體與相關服務會產生可能被記錄及儲存的資料；原有資料使用條款與下列授權聲明仍適用。

By using this software, you understand that use of this software or its related services will generate certain types of user data, which may be logged and stored at the sole discretion of comma. By accepting this agreement, you grant an irrevocable, perpetual, worldwide right to comma for the use of this data.

## Licensing

sunnypilot is released under the [MIT License](LICENSE). This repository includes original work as well as significant portions of code derived from [openpilot by comma.ai](https://github.com/commaai/openpilot), which is also released under the MIT license with additional disclaimers.

The original openpilot license notice, including comma.ai’s indemnification and alpha software disclaimer, is reproduced below as required:

> openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.
>
> Any user of this software shall indemnify and hold harmless Comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.
>
> **THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
> YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
> NO WARRANTY EXPRESSED OR IMPLIED.**

For full license terms, please see the [`LICENSE`](LICENSE) file.

## 💰 Support sunnypilot
If you find any of the features useful, consider becoming a [sponsor on GitHub](https://github.com/sponsors/sunnyhaibin) to support future feature development and improvements.


By becoming a sponsor, you will gain access to exclusive content, early access to new features, and the opportunity to directly influence the project's development.


<h3>GitHub Sponsor</h3>

<a href="https://github.com/sponsors/sunnyhaibin">
  <img src="https://user-images.githubusercontent.com/47793918/244135584-9800acbd-69fd-4b2b-bec9-e5fa2d85c817.png" alt="Become a Sponsor" width="300" style="max-width: 100%; height: auto;">
</a>
<br>

<h3>PayPal</h3>

<a href="https://paypal.me/sunnyhaibin0850" target="_blank">
<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal this" title="PayPal - The safer, easier way to pay online!" border="0" />
</a>
<br></br>

Your continuous love and support are greatly appreciated! Enjoy 🥰

<span>-</span> Jason, Founder of sunnypilot
