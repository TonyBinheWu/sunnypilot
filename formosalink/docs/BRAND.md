# FormosaPilot / FormosaLink brand asset

Logo: `formosalink/web/assets/formosapilot-logo.png`, original RGBA PNG, 1254 × 1254. Generated with the built-in image generation tool, then copied unchanged into the repository. The original generated alpha is preserved. Taiwan's mountain ridge, a winding road and warm sunrise form an abstract F mark. Login, navigation and home-screen manifest share the same asset. Interface languages: 繁體中文、English、日本語.

Final generation prompt:

> Use case: logo-brand. Create the original standalone brand symbol for FormosaPilot, a Taiwan-rooted open-source driver assistance project with companion FormosaLink. A refined compact icon suggesting Taiwan's mountain ridge seamlessly becoming a forward road, with an understated F monogram in the negative space. Clean geometric vector-like flat mark, distinctive at app-icon size, confident and calm, generous clear margins, centered square composition. Transparent background, preserve alpha. No text, no letters outside the abstract mark, no wordmark, no gradients, no shadows, no mockup, no border. Designed to work on a dark navy mobile dashboard and also white. A restrained teal/cyan symbol with a small warm pale accent if needed. One finished logo, not a sheet of alternatives.


## 裝置入口 / Device entry / デバイスの入口

C3X 與 C4：設定 → FormosaPilot。顯示原創 Logo、FormosaPilot 0.6.2、已安裝分支與 commit，並直接開啟 FormosaLink QR 配對。SIM 行動數據開關仍在網路設定。更新對應分支後重新啟動裝置；原生 sunnypilot 版本號及 sunnylink 服務入口保留。

C3X and C4: Settings → FormosaPilot. Shows the original logo, companion version, installed branch and commit, with direct FormosaLink QR pairing. Cellular data is under Network. Update the matching branch and restart. Upstream sunnypilot version and sunnylink service keep their original identity.

C3X・C4：設定 → FormosaPilot。ロゴ、独立したバージョン、インストール済みブランチとコミット、FormosaLink の QR 登録を表示します。モバイル通信はネットワーク設定にあります。対応ブランチを更新して再起動してください。sunnypilot のバージョンと sunnylink サービスは維持します。

Native asset: `openpilot/sunnypilot/formosalink/assets/formosapilot-logo.png`, byte-identical to the web original and stored without Git LFS. This page changes only offroad UI; driving, vehicle identification, controllers and safety code are untouched. The companion version is independent of upstream's release version. Native rendering and top-level navigation are tested on both C3X and C4 PC profiles in all three languages; physical device rendering still needs confirmation.


### 配對畫面 / Pairing screen / 登録画面

「裝置 → FormosaLink」與「FormosaPilot → 掃描 QR 配對」共用全螢幕配對頁。文字、三個直列操作按鈕及 QR Code 依 C3X／C4 畫面等比例配置；QR 使用整數模組縮放，狀態文字會換行並避開按鈕。保持停車操作限制及原有配對流程。

Both Device → FormosaLink and FormosaPilot → Scan QR use the same full-screen pairing page. Text and three stacked touch targets scale to C3X/C4, while QR modules stay at integer pixel sizes. Status wrapping is measured against the available area. Existing pairing and parked-only guards are unchanged.

「デバイス → FormosaLink」と「FormosaPilot → QR 登録」は共通の全画面ページです。文字・縦に並ぶ操作ボタン・QR を C3X/C4 に合わせて配置します。QR は整数ピクセルで拡大し、状態文はボタンに重ならないよう折り返します。登録の処理と停車中のみの制限は維持します。


## 完整裝置品牌 / Native product branding / デバイスのブランド

首頁、啟動 Logo、螢幕保護程式與一般設定／警示的產品名稱改用 FormosaPilot。C3X/C4 首頁都使用原創 F 標誌。品牌轉換只發生於翻譯後的顯示文字、排版測量與圖片載入，不修改翻譯鍵、參數、Git 來源、API、車型或行車邏輯。原始作者／授權、官方贊助／法律及第三方服務引用保留正確來源；網址與內部模組路徑不會被替換。FormosaLink 網站已使用同一原創 Logo。

Home, boot, screensaver and general product settings/alerts display FormosaPilot. Both home profiles use the original F symbol. Mapping applies only after translation and consistently before wrapping, measurement and drawing; asset aliases load the bundled logo without overwriting upstream originals. Translation keys, Params, repository origins, API endpoints and driving behavior remain unchanged. Attribution, licenses, actual third-party sponsorship/legal references, URLs and internal module paths retain their real identities. Shared UI edits must be ported as narrow changes, preserving each branch's font scaling. The synchronization tool includes the two independent branding modules.

ホーム・起動画面・スクリーンセーバー・一般設定と警告の製品名は FormosaPilot に統一し、両デバイスのホームに独自の F ロゴを表示します。翻訳後の表示・文字計測・折り返し・描画・画像読み込みのみを変更します。翻訳キー・設定・Git 参照・API・走行処理は維持し、著作権・ライセンス・実際の第三者サービス／スポンサー・法律上の参照・URL は正しい名称を保持します。
