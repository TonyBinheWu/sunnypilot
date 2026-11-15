"""Short localized catalog labels; native settings IDs remain unchanged."""
import re

ROWS = """
FormosaPilot Instrument Display (Experimental)|FormosaPilot 儀表顯示（實驗）|FormosaPilot メーター表示（実験）
Camera CAN-FD only. Restart required; keeps OEM warnings.|限相機側 CAN-FD，保留原廠警告，重啟後生效。|カメラ側 CAN-FD 専用。純正警告を保持。再起動が必要です。
Steering|轉向|ステアリング
Cruise|巡航|クルーズ
Display|顯示|表示
Visuals|畫面|画面
Toggles|一般|一般
Device|裝置|デバイス
Software|軟體|ソフトウェア
Developer|進階|詳細
Models|模型|モデル
Vehicle|車輛|車両
Enable Modular Assistive Driving System (MADS)|模組化輔助駕駛（MADS）|モジュール式運転支援（MADS）
Toggle with Main Cruise|主巡航按鈕切換|メインクルーズで切り替え
Unified Engagement Mode (UEM)|統一啟用模式（UEM）|統合開始モード（UEM）
Steering Mode on Brake Pedal|煞車時轉向模式|ブレーキ時の操舵モード
Pause Lateral Control with Blinker|方向燈暫停轉向輔助|方向指示器で操舵支援を一時停止
Minimum Speed to Pause Lateral Control|暫停轉向輔助的最低速度|操舵支援を一時停止する最低速度
Post-Blinker Delay|方向燈關閉後延遲|方向指示器解除後の遅延
Enforce Torque Lateral Control|強制使用扭力轉向控制|トルク操舵制御を使用
Lateral Jerk Torque Controller|橫向加加速度控制器|横方向ジャーク制御
Self-Tune|自動調校|自動調整
Less Restrict Settings for Self-Tune (Beta)|放寬自動調校限制（測試）|自動調整の制限を緩和（ベータ）
Enable Custom Tuning|自訂調校|カスタム調整
Manual Real-Time Tuning|手動即時調校|手動リアルタイム調整
Lateral Acceleration Factor|橫向加速度係數|横加速度係数
Friction|摩擦係數|摩擦係数
Torque Control Tune Version|扭力控制版本|トルク制御バージョン
HKG Low-Speed Steering Torque (Experimental)|HKG 低速轉向扭力（實驗）|HKG 低速操舵トルク（実験）
Honda / Toyota Low-Speed Steering Tune (Experimental)|Honda／Toyota 低速轉向調校（實驗）|Honda／Toyota 低速操舵調整（実験）
Auto Lane Change by Blinker|方向燈自動變換車道|方向指示器で自動車線変更
Block Lane Change: Road Edge Detection|偵測道路邊緣時禁止變換車道|道路端の検出時は車線変更を禁止
Auto Lane Change: Delay with Blind Spot|盲點延遲變換車道|死角検出時に車線変更を遅延
Experimental Mode|實驗模式|実験モード
Dynamic Experimental Control|動態實驗控制|動的実験制御
Disengage Cruise on Accelerator Pedal|踩油門取消巡航|アクセルでクルーズを解除
Driving Personality|駕駛風格|運転スタイル
Intelligent Cruise Button Management (ICBM) (Alpha)|智慧巡航按鍵管理（測試）|クルーズボタン管理（アルファ）
Enable Custom ACC Speed Intervals|自訂 ACC 速度間隔|ACC の速度間隔を変更
Short Press Increment|短按增量|短押しの増分
Long Press Increment|長按增量|長押しの増分
Speed Limit Assist Mode|速限輔助模式|速度制限支援モード
Speed Limit Source|速限來源|速度制限の取得元
Speed Limit Offset Type|速限偏移類型|速度制限の補正方式
Speed Limit Offset Value|速限偏移值|速度制限の補正値
Vision|視覺|カメラ
Map|地圖|地図
Onroad Brightness|行車亮度|走行中の輝度
Onroad Brightness Delay|行車亮度延遲|走行中の輝度変更の遅延
Interactivity Timeout|互動逾時|操作タイムアウト
Screen Saver|螢幕保護|スクリーンセーバー
Screen Saver Duration|螢幕保護時間|スクリーンセーバー時間
Show Blind Spot Warnings|盲點警示|死角警告
Steering Arc|轉向弧線|操舵の円弧
Display Turn Signals|顯示方向燈|方向指示器を表示
Display Road Name|顯示道路名稱|道路名を表示
Standstill Timer|停車計時|停車タイマー
Real-time Acceleration Bar|即時加速度條|加速度バー
Display Metrics Below Chevron|前車圖示下顯示資訊|先行車アイコンの下に情報を表示
Developer UI|進階資訊|詳細情報
Speedometer: Always Display True Speed|顯示實際車速|実速度を常に表示
Speedometer: Hide from Onroad Screen|隱藏行車車速|走行画面で速度を非表示
Green Traffic Light Alert (Beta)|綠燈提醒（測試）|青信号通知（ベータ）
Lead Departure Alert (Beta)|前車起步提醒（測試）|先行車発進通知（ベータ）
Tesla Rainbow Mode|Tesla 彩虹模式|Tesla レインボーモード
Tesla Rainbow Mode Style|Tesla 彩虹樣式|Tesla レインボーの種類
Model Predicted Stop Position|模型預測停止位置|モデル予測の停止位置
Enable sunnypilot|啟用 sunnypilot|sunnypilot を有効化
Enable Lane Departure Warnings|車道偏離警示|車線逸脱警告
Always-On Driver Monitoring|持續駕駛監控|常時ドライバー監視
Use Metric System|使用公制|メートル法を使用
Quiet Mode|安靜模式|静音モード
Onroad Uploads|行車時上傳|走行中のアップロード
Max Time Offroad|停車最長運作時間|停車中の最大稼働時間
Language|語言|言語
Disable Updates|停用更新|更新を無効化
Update Progress|更新進度|更新状況
Remote Update Request|遠端更新請求|遠隔更新リクエスト
Installed Version|已安裝版本|インストール済みバージョン
Downloaded Version|已下載版本|ダウンロード済みバージョン
sunnypilot Longitudinal Control (Alpha)|sunnypilot 縱向控制（測試）|sunnypilot 縦制御（アルファ）
UI Debug Mode|介面除錯模式|UI デバッグモード
Show Advanced Controls|顯示進階控制|詳細な制御を表示
Quickboot Mode|快速啟動|高速起動
Use Lane Turn Desires|使用車道轉彎預測|車線の旋回予測を使用
Adjust Lane Turn Speed|車道轉彎速度|車線旋回速度
Live Learning Steer Delay|即時學習轉向延遲|操舵遅延のリアルタイム学習
Adjust Software Delay|軟體延遲|ソフトウェア遅延
Neural Network Lateral Control (NNLC)|神經網路轉向控制（NNLC）|ニューラルネット操舵制御（NNLC）
Adjust Camera Offset|攝影機偏移|カメラ位置の補正
Custom Longitudinal Tuning|自訂縱向調校|縦制御のカスタム調整
Stop and Go (Beta)|走停功能（測試）|停止と再発進（ベータ）
Stop and Go for Manual Parking Brake (Beta)|手動手煞車走停功能（測試）|手動駐車ブレーキ用の停止と再発進（ベータ）
Cooperative Steering (Beta)|協同轉向（測試）|協調操舵（ベータ）
MADS Screen Activation|MADS 螢幕啟用方式|MADS の画面操作
Enforce Factory Longitudinal Control|使用原廠縱向控制|純正の縦制御を使用
Stop and Go Hack (Alpha)|走停擴充（測試）|停止と再発進の拡張（アルファ）
Default|預設|標準
Off|關閉|オフ
On|開啟|オン
All|全部|すべて
Always On|常時開啟|常時オン
Auto (Default)|自動（預設）|自動（標準）
Auto (Dark)|自動（深色）|自動（暗い）
Assist|輔助|支援
Warning|警示|警告
Disengage|取消|解除
Pause|暫停|一時停止
Remain Active|保持啟用|有効を維持
Nudge|輕推方向盤|軽く操舵
Nudgeless|無須輕推|操舵不要
Fixed|固定|固定
Percentage|百分比|割合
Speed|速度|速度
Distance|距離|距離
Time|時間|時間
Combined|綜合|複合
Information|資訊|情報
Right|右側|右
Bottom|下方|下
Right & Bottom|右側與下方|右と下
Screen Off|關閉螢幕|画面オフ
Car State Only|僅車輛資訊|車両情報のみ
Car State Priority|優先車輛資訊|車両情報を優先
Map Data Only|僅地圖資訊|地図情報のみ
Map Data Priority|優先地圖資訊|地図情報を優先
Dynamic|動態|動的
Predictive|預測|予測
Dynamic Blue Bars|動態藍色條|動的な青いバー
Rainbow Road|彩虹道路|レインボーロード
3-Finger|三指|3 本指
4-Finger|四指|4 本指
5-Finger|五指|5 本指
30h (Default)|30 小時（預設）|30 時間（標準）
"""
LABELS = {en: {"en": en,"zh-TW": zh,"ja": ja} for en, zh, ja in (row.split("|") for row in ROWS.strip().splitlines())}


def localize(text, native=None):
  if text in LABELS:
    return LABELS[text]
  match = re.fullmatch(r"([0-9.]+)\s*(second|seconds|s|h|m)",text)
  if match:
    number, unit = match.groups()
    units = {"second":("秒","秒"),"seconds":("秒","秒"),"s":("秒","秒"),"h":("小時","時間"),
             "m":("公尺" if ' ' in text else "分鐘","m" if ' ' in text else "分")}
    zh,ja = units[unit]
    return {"en":text,"zh-TW":number+" "+zh,"ja":number+" "+ja}
  return native(text) if native else {"en":text,"zh-TW":text,"ja":text}
