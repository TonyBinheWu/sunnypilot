package me.shind0.carrotweb;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/** Native host follows the phone language; Carrot Web keeps its own preference. */
public final class UiText {
  private static final Map<String, String> TRADITIONAL = new HashMap<>();
  static {
    TRADITIONAL.put("Start the voice assistant when Carrot Web connects", "Carrot Web 連線後啟動語音助手");
    TRADITIONAL.put("Listen for commands on this phone first", "優先在此手機聆聽指令");
    TRADITIONAL.put("Direct listening handles lane requests and turn signal settings. Repeat questions in the default assistant. Turn off direct listening to start in the assistant overlay.\n\nInstall updates while parked.", "直接聆聽支援繁體中文搜尋與修改設定、變換車道及調整巡航速度。其他問題請向預設助手重述。關閉直接聆聽後，會啟動助手浮動視窗。\n\n請停車後安裝更新。");
    TRADITIONAL.put("Check for updates", "檢查更新");
    TRADITIONAL.put("Install update", "安裝更新");
    TRADITIONAL.put("Copy ChatGPT instructions", "複製 ChatGPT 自訂指示");
    TRADITIONAL.put("Close", "關閉");
    TRADITIONAL.put("Custom instructions copied", "已複製自訂指示");
    TRADITIONAL.put("Press and hold the text to copy", "請長按文字以複製");
    TRADITIONAL.put("Done", "完成");
    TRADITIONAL.put("Could not check for updates. Check your Internet connection.", "無法檢查更新，請確認網際網路連線。");
    TRADITIONAL.put("A CarrotAssist update is available. Tap the device name at the top to update.", "CarrotAssist 有可用更新，請點上方裝置名稱更新。");
    TRADITIONAL.put("You are up to date.", "目前已是最新版本。");
    TRADITIONAL.put("Download the update and open the Android installer? The app may close during installation. Please park first.", "下載更新並開啟 Android 安裝程式？安裝期間 App 可能關閉，請先安全停車。");
    TRADITIONAL.put("Download", "下載");
    TRADITIONAL.put("Later", "稍後");
    TRADITIONAL.put("Downloading and verifying the update.", "正在下載並驗證更新。");
    TRADITIONAL.put("Update verification failed. Nothing was installed. Check your Internet connection or the release file.", "更新驗證失敗，未安裝任何項目。請檢查網際網路或發行檔案。");
    TRADITIONAL.put("Could not open the installer. Try again from app information.", "無法開啟安裝程式，請從 App 資訊重試。");
    TRADITIONAL.put("Update stopped because installation permission was not allowed.", "未允許安裝權限，更新已停止。");
    TRADITIONAL.put("Could not restore the ChatGPT connection. Check the Internet connection and Carrot device, then search again.", "無法恢復 ChatGPT 連線，請檢查網際網路與 Carrot 裝置，再重新搜尋。");
    TRADITIONAL.put("Carrot Web is not responding yet. Wait for the web page to open and try again.", "Carrot Web 尚未回應，請等候頁面開啟後重試。");
    TRADITIONAL.put("No ChatGPT account link was verified for this Carrot Web. Check the ChatGPT assistant in Tools.", "未驗證此 Carrot Web 的 ChatGPT 帳號連線，請檢查工具中的 ChatGPT 助手。");
    TRADITIONAL.put("Could not verify the Carrot Web connection to ChatGPT. Try again in a moment.", "無法驗證 Carrot Web 與 ChatGPT 的連線，請稍後重試。");
    TRADITIONAL.put("Could not verify the saved ChatGPT connection. Check your Internet connection and ChatGPT connection settings.", "無法驗證儲存的 ChatGPT 連線，請檢查網際網路與連線設定。");
    TRADITIONAL.put("Open voice assistant. Drag to move", "開啟語音助手，可拖曳移動");
    TRADITIONAL.put("Update the device software to switch Vision layouts.", "請更新車機程式，才能切換 Vision 顯示版面。");
    TRADITIONAL.put("Switch Vision layout; long press to show or hide tools", "切換 Vision 版面；長按顯示或隱藏工具列");
    TRADITIONAL.put("Open Carrot Vision and switch to Live View first.", "請先開啟 Carrot Vision 並切換至 Live View。");
    TRADITIONAL.put("Switch Vision layout", "切換 Vision 顯示版面");
    TRADITIONAL.put("Open the device web page first.", "請先開啟裝置網頁。");
    TRADITIONAL.put("Find Carrot", "尋找 Carrot");
    TRADITIONAL.put("Device name · App information and updates", "裝置名稱 · App 資訊與更新");
    TRADITIONAL.put("Looking for Carrot", "正在尋找 Carrot");
    TRADITIONAL.put("Connect to the same Wi-Fi or phone hotspot.\nOne device found within five seconds opens automatically.", "請連至相同 Wi-Fi 或手機熱點。\n五秒內找到唯一裝置時會自動開啟。");
    TRADITIONAL.put("Preparing search…", "正在準備搜尋…");
    TRADITIONAL.put("Search again", "重新搜尋");
    TRADITIONAL.put("Enter IP address", "輸入 IP 位址");
    TRADITIONAL.put("Stop search", "停止搜尋");
    TRADITIONAL.put("Search stopped. You can select a device already found.", "已停止搜尋，可選擇已找到的裝置。");
    TRADITIONAL.put("No Wi-Fi network found. Check the connection or enter an IP address.", "未找到 Wi-Fi 網路，請檢查連線或輸入 IP 位址。");
    TRADITIONAL.put("No device found within one minute. Check that you are on the same Wi-Fi and search again.", "一分鐘內未找到裝置，請確認連至相同 Wi-Fi 並重新搜尋。");
    TRADITIONAL.put("Search complete. Select a device to connect.", "搜尋完成，請選擇裝置連線。");
    TRADITIONAL.put(" devices found. Select one. · ", " 個裝置，請選擇一個。 · ");
    TRADITIONAL.put("s remaining", " 秒後結束");
    TRADITIONAL.put("Quick search · ", "快速搜尋 · ");
    TRADITIONAL.put("s · Found ", " 秒 · 已找到 ");
    TRADITIONAL.put("Searching · ", "搜尋中 · ");
    TRADITIONAL.put("Carrot device IP address", "Carrot 裝置 IP 位址");
    TRADITIONAL.put("Cancel", "取消");
    TRADITIONAL.put("OK", "確定");
    TRADITIONAL.put("Enter an IP address on your local network. Carrot Web uses port 7000.", "請輸入區域網路 IP 位址，Carrot Web 使用 7000 埠。");
    TRADITIONAL.put("Checking for Carrot Web…", "正在檢查 Carrot Web…");
    TRADITIONAL.put("Carrot Web was not found at that address. Check the IP address and Wi-Fi connection.", "此位址未找到 Carrot Web，請檢查 IP 與 Wi-Fi。");
    TRADITIONAL.put("A browser is required to open this link.", "需要瀏覽器才能開啟此連結。");
    TRADITIONAL.put("Device disconnected · Use search on the left", "裝置已中斷，請使用左側搜尋");
    TRADITIONAL.put("Connecting to Carrot…\nChecking your saved ChatGPT connection.", "正在連線至 Carrot…\n檢查儲存的 ChatGPT 連線。");
    TRADITIONAL.put("Check ChatGPT connection · ", "檢查 ChatGPT 連線 · ");
    TRADITIONAL.put("Connecting to Carrot Web. Voice is available when the page opens.", "正在連線至 Carrot Web，頁面開啟後可使用語音。");
    TRADITIONAL.put("Connect to Carrot Web first.", "請先連線至 Carrot Web。");
    TRADITIONAL.put("Carrot Web has not opened yet.", "Carrot Web 尚未開啟。");
    TRADITIONAL.put("Update and restart the parked Carrot device. Direct voice commands need the updated Carrot Web.", "請停車後更新並重新啟動 Carrot 裝置，直接語音需要新版 Carrot Web。");
    TRADITIONAL.put("Microphone permission is required for direct voice commands.", "直接語音需要麥克風權限。");
    TRADITIONAL.put("Please repeat the setting name and number.", "請重述設定名稱與數字。");
    TRADITIONAL.put("Search for settings first.", "請先搜尋設定。");
    TRADITIONAL.put("Update and restart the parked Carrot device.", "請停車後更新並重新啟動 Carrot 裝置。");
    TRADITIONAL.put("Say confirm left if you mean left.", "若要向左，請說「確認向左」。");
    TRADITIONAL.put("Say confirm right if you mean right.", "若要向右，請說「確認向右」。");
    TRADITIONAL.put("Opening the assistant. Please repeat your question there.", "正在開啟助手，請在助手中重述問題。");
    TRADITIONAL.put("Direction uncertain. No request sent.", "方向不明確，未送出請求。");
    TRADITIONAL.put("Command not recognized.", "無法辨識指令。");
    TRADITIONAL.put("No matching settings.", "找不到符合的設定。");
    TRADITIONAL.put("While parked, allow setting reads and changes in Carrot Web Tools.", "請停車後，在 Carrot Web 工具允許讀取與修改設定。");
    TRADITIONAL.put("That item is not in the current search results.", "該項目不在目前搜尋結果中。");
    TRADITIONAL.put("Please say the name of one setting.", "請說出一個設定名稱。");
    TRADITIONAL.put("Opened the turn signal setting.", "已開啟方向燈設定。");
    TRADITIONAL.put("Left request received.", "已收到向左請求。");
    TRADITIONAL.put("Right request received.", "已收到向右請求。");
    TRADITIONAL.put("Lane change in progress.", "正在變換車道。");
    TRADITIONAL.put("Lane change completed.", "車道變換完成。");
    TRADITIONAL.put("While parked, allow driving commands in Carrot Web Tools.", "請停車後，在 Carrot Web 工具允許駕駛指令。");
    TRADITIONAL.put("Recent request. No repeat sent.", "已有近期請求，未重複送出。");
    TRADITIONAL.put("The lane change request ended.", "車道變換請求已結束。");
    TRADITIONAL.put("Setting unavailable on this device.", "此裝置無法使用該設定。");
    TRADITIONAL.put("Result unavailable.", "無法取得結果。");
    TRADITIONAL.put("Checking Carrot Web", "正在檢查 Carrot Web");
    TRADITIONAL.put("Check again", "再次檢查");
    TRADITIONAL.put("Open assistant only", "僅開啟助手");
    TRADITIONAL.put("Default voice assistant", "預設語音助手");
    TRADITIONAL.put("Choose your default Android digital assistant. The microphone opens your selected app, such as ChatGPT or Gemini. Carrot setting search and screen navigation have been tested with ChatGPT. The voice window depends on the assistant app.", "選擇 Android 預設數位助手。麥克風會開啟您選擇的 App，例如 ChatGPT 或 Gemini。Carrot 設定搜尋與畫面導覽已使用 ChatGPT 測試；語音視窗依助手 App 而定。");
    TRADITIONAL.put("Open settings", "開啟設定");
    TRADITIONAL.put("Choose the default digital assistant in your phone settings.", "請在手機設定選擇預設數位助手。");
    TRADITIONAL.put("Search paused. Tap Search again.", "搜尋已暫停，請點重新搜尋。");
    TRADITIONAL.put("Listening ended.", "聆聽已結束。");
    TRADITIONAL.put("On-device speech recognition is unavailable. Check the phone’s speech language pack.", "無法使用裝置端語音辨識，請檢查手機語音語言包。");
    TRADITIONAL.put("Listening · tap the mic to stop", "正在聆聽 · 點麥克風停止");
    TRADITIONAL.put("Recognition arrived too late.", "辨識結果已逾時。");
    TRADITIONAL.put("The recognition alternatives disagree.", "辨識候選結果互相衝突。");
    TRADITIONAL.put("Recognition confidence is low.", "辨識可信度過低。");
    TRADITIONAL.put("Please repeat the command.", "請重述指令。");
    TRADITIONAL.put("Speech was detected but no words were recognized.", "偵測到聲音，但未辨識出文字。");
    TRADITIONAL.put("Listening ended · tap the mic to start", "聆聽已結束 · 點麥克風開始");
    TRADITIONAL.put("Check the phone’s on-device speech language pack.", "請檢查手機的裝置端語音語言包。");
    TRADITIONAL.put("Speech unavailable. Check microphone permission and availability.", "無法使用語音，請檢查麥克風權限與可用狀態。");
    TRADITIONAL.put("Preparing on-device speech", "正在準備裝置端語音");
    TRADITIONAL.put("Phone speech recognition is unavailable.", "無法使用手機語音辨識。");
    TRADITIONAL.put("Hello. Drive safely.", "您好，請注意行車安全。");
    TRADITIONAL.put(" An update is available for your Carrot device.", " 您的 Carrot 裝置有可用更新。");
    TRADITIONAL.put("I heard “%s”. ", "我聽到「%s」。 ");
    TRADITIONAL.put("Found %s. First is %s.", "找到 %s 個，第一個是 %s。");
    TRADITIONAL.put("%s set to %s.", "已將 %s 設為 %s。");
    TRADITIONAL.put("Allowed range is %s to %s.", "允許範圍為 %s 至 %s。");
    TRADITIONAL.put("%s is already %s.", "%s 已經是 %s。");
    TRADITIONAL.put("When we talk about driving or vehicle settings, Carrot means CarrotPilot (CarrotAssist). When I ask you to find or change a CarrotPilot setting, or give a driving command such as “change lanes left”, use the connected CarrotAssist tool. Briefly report the result returned by the tool.", "討論駕駛或車輛設定時，我說的 Carrot 是指 CarrotPilot（CarrotAssist）。當我要求尋找或修改 CarrotPilot 設定，或提出「向左變換車道」等駕駛指令時，請使用已連線的 CarrotAssist 工具，並簡短回報工具實際傳回的結果。");
    TRADITIONAL.put("1. Open the menu in ChatGPT and tap your profile.\n2. In Settings, scroll to Customize ChatGPT and open Personality. The Custom instructions field is below the style controls.\n3. Paste below any existing instructions and tap Save at the top right.\n\nTry “Find acceleration settings” in a new chat.", "1. 在 ChatGPT 開啟選單並點選個人資料。\n2. 在設定中找到「自訂 ChatGPT」並開啟「個性」，在風格設定下方找到「自訂指示」。\n3. 貼在既有指示下方，再點右上角「儲存」。\n\n在新對話中試說「尋找加速設定」。");
    TRADITIONAL.put("Please repeat the cruise command.", "請重新說出巡航速度指令。");
    TRADITIONAL.put("Cruise confirmation did not match or expired.", "巡航指令確認不符或已逾期，未送出請求。");
    TRADITIONAL.put("Please repeat: %s", "請覆誦：「%s」。");
    TRADITIONAL.put("Cruise target is %s km/h.", "巡航設定速度為每小時 %s 公里。");
    TRADITIONAL.put("Cruise request received; application is not yet verified.", "已收到巡航速度請求，尚未確認套用。");
    TRADITIONAL.put("Cruise request was not applied. Check active assistance and vehicle conditions.", "巡航請求未套用，請確認輔助啟用狀態與車輛條件。");
    TRADITIONAL.put("Chinese speech model and microphone setup", "中文語音檢查與安裝");
    TRADITIONAL.put("Checking the Mandarin speech model", "正在檢查國語語音模型");
  }

  public static String get(String korean, String english) {
    Locale locale = Locale.getDefault();
    if ("ko".equals(locale.getLanguage())) return korean;
    if ("zh".equals(locale.getLanguage()) &&
        ("Hant".equals(locale.getScript()) || (locale.getScript().isEmpty() &&
         ("TW".equals(locale.getCountry()) || "HK".equals(locale.getCountry()) || "MO".equals(locale.getCountry()))))) {
      String translated = TRADITIONAL.get(english);
      if (translated != null) return translated;
    }
    return english;
  }
  public static String languageCode() {
    Locale locale = Locale.getDefault();
    if ("ko".equals(locale.getLanguage())) return "ko";
    if ("zh".equals(locale.getLanguage()) && ("Hant".equals(locale.getScript()) || locale.getScript().isEmpty() &&
        ("TW".equals(locale.getCountry()) || "HK".equals(locale.getCountry()) || "MO".equals(locale.getCountry())))) return "zh-tw";
    return "en";
  }
  public static String format(String korean, String english, Object... values) {
    return String.format(Locale.getDefault(), get(korean, english), values);
  }

  private UiText() {}
}
