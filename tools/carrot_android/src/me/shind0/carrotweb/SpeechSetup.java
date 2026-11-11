package me.shind0.carrotweb;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.speech.ModelDownloadListener;
import android.speech.SpeechRecognizer;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.Locale;

/** Chinese model/permission help is available without a car connection. No automatic speech restart. */
final class SpeechSetup {
  static final int PERMISSION_REQUEST = 43;
  private final Activity activity;
  private final Handler ui = new Handler(Looper.getMainLooper());
  private final SpeechProbe probe;
  private AlertDialog dialog;
  private TextView report;
  private Button download, permission, recheck;
  private SpeechRecognizer downloader;
  private SpeechModelPolicy.State state = SpeechModelPolicy.State.UNKNOWN;
  private String detail = "";
  private int generation;
  private boolean paused;
  SpeechSetup(Activity activity) { this.activity = activity; this.probe = new SpeechProbe(activity); }
  boolean showing() { return dialog != null && dialog.isShowing(); }
  private int dp(int n) { return Math.round(n * activity.getResources().getDisplayMetrics().density); }
  private Button button(LinearLayout box, String label, Runnable action) {
    Button b = new Button(activity); b.setText(label); b.setAllCaps(false); b.setOnClickListener(v -> action.run());
    box.addView(b, new LinearLayout.LayoutParams(-1, -2)); return b;
  }
  void show(String reason) {
    close(); paused = false;
    LinearLayout box = new LinearLayout(activity); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(20), dp(10), dp(20), dp(10));
    if (reason != null && !reason.isEmpty()) {
      TextView why = new TextView(activity); why.setText(reason + "\n"); why.setTextSize(16); box.addView(why);
    }
    report = new TextView(activity); report.setTextSize(16); report.setTextIsSelectable(true); box.addView(report);
    recheck = button(box, "重新檢查中文語音模型", this::check);
    download = button(box, "下載中文語音模型", this::download);
    permission = button(box, "授予麥克風權限", () -> {
      if (!showing() || paused || activity.isFinishing()) return;
      cancelWork();
      activity.requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, PERMISSION_REQUEST);
    });
    button(box, "開啟 App 權限設定", () -> settings(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + activity.getPackageName()))));
    button(box, "開啟語音輸入設定", () -> settings(new Intent(Settings.ACTION_VOICE_INPUT_SETTINGS)));
    button(box, "開啟系統隱私設定", () -> settings(new Intent(Settings.ACTION_PRIVACY_SETTINGS)));
    button(box, "開啟手機語言設定", () -> settings(new Intent(Settings.ACTION_LOCALE_SETTINGS)));
    TextView guide = new TextView(activity); guide.setTextSize(15);
    guide.setText("\n設定步驟\n請先確認手機系統使用繁體中文（台灣），App 才會要求 zh-TW 中文辨識。\n1. 在 App 權限設定中，將『麥克風』設為使用期間允許。\n2. 檢查手機快速設定或隱私設定的『麥克風存取』總開關。\n3. 在語音輸入／語音辨識服務中，選擇『中文（台灣）／國語／zh-TW』並下載離線語音。選單名稱會因手機與語音服務而異。\n4. 若服務未提供國語離線模型，先由手機官方商店更新語音辨識服務；仍不支援時，無法用此裝置的離線中文指令。\n5. 回到本頁按『重新檢查』。完成後關閉本頁，再手動點麥克風開始，安裝或檢查不會自動執行任何指令。\n\nAndroid 13 以上可提出模型下載請求；Android 14 以上且服務支援時才會回報進度。Android 12 僅能顯示手動引導。系統可要求你另外同意下載；請保持網路連線。\n\n此頁檢查的是中文語音（zh-TW），不會下載 ChatGPT 或變更車機設定。模型安裝狀態不代表已完成實際辨識測試。");
    box.addView(guide);
    ScrollView scroll = new ScrollView(activity); scroll.addView(box);
    dialog = new AlertDialog.Builder(activity).setTitle("中文語音檢查與安裝").setView(scroll).setNegativeButton("關閉", null).create();
    final AlertDialog created = dialog;
    dialog.setOnDismissListener(d -> { if (dialog == created) { cancelWork(); dialog = null; } });
    dialog.show(); check();
  }
  private void check() {
    if (!showing() || paused) return;
    generation++; probe.cancel(); final int token = generation;
    state = SpeechModelPolicy.State.CHECKING; detail = ""; render();
    probe.check("zh-TW", (next, extra) -> {
      if (!active(token)) return;
      state = next; detail = extra; render();
    });
  }
  private boolean active(int token) { return token == generation && !paused && showing() && !activity.isFinishing(); }
  private void render() {
    if (!showing()) return;
    String status;
    switch (state) {
      case OLD_ANDROID: status = "需要 Android 12 以上才能使用本 App 的裝置端語音。"; break;
      case PERMISSION: status = "尚未取得麥克風權限。請點『授予麥克風權限』，或在 App 權限設定中允許麥克風。"; break;
      case NO_SERVICE: status = "手機目前沒有可用的裝置端語音辨識服務。請先在系統語音輸入設定啟用／更新辨識服務。"; break;
      case MANUAL: status = "Android 12 無法查詢模型清單。模型是否安裝尚未確認，請依下方步驟手動檢查。"; break;
      case CHECKING: status = "正在檢查中文（台灣）語音模型…"; break;
      case INSTALLED: status = "語音服務回報 zh-TW 模型已安裝。尚未進行實際辨識測試；關閉本頁後可手動點麥克風試用。"; break;
      case DOWNLOADABLE: status = "中文（台灣）模型尚未安裝，但語音服務表示可下載。請點『下載中文語音模型』。"; break;
      case PENDING: status = "中文模型正在等待系統下載。尚未確認安裝完成；請保持連線，稍後重新檢查。"; break;
      case UNSUPPORTED: status = "目前語音服務的模型清單未包含 zh-TW。請開啟語音輸入設定確認支援的語言；本 App 無法強制安裝服務未提供的模型。"; break;
      case REQUESTED: status = "已送出中文模型下載請求，尚未確認安裝完成。請處理系統可能顯示的確認畫面，稍後按重新檢查。"; break;
      case DOWNLOADING: status = "中文語音模型下載中，尚未確認安裝完成。"; break;
      case ERROR: status = "模型下載沒有完成。請確認網路、儲存空間及語音服務設定，之後重新檢查。"; break;
      default: status = "目前無法確認中文模型是否安裝。請使用下方設定引導，或重新檢查。";
    }
    report.setText("檢查語言：中文（台灣）／國語，zh-TW\n手機語言：" + Locale.getDefault().toLanguageTag() + "\n麥克風權限：" + (SpeechProbe.microphone(activity) ? "已允許" : "未允許") + "\n\n" + status + (detail.isEmpty() ? "" : "\n\n" + detail) + "\n");
    permission.setEnabled(Build.VERSION.SDK_INT >= 31 && !SpeechProbe.microphone(activity));
    download.setEnabled(SpeechModelPolicy.canDownload(state, Build.VERSION.SDK_INT, SpeechProbe.microphone(activity), SpeechProbe.service(activity)));
    recheck.setEnabled(state != SpeechModelPolicy.State.CHECKING);
  }
  private void download() {
    if (!showing() || paused || !SpeechModelPolicy.canDownload(state, Build.VERSION.SDK_INT, SpeechProbe.microphone(activity), SpeechProbe.service(activity))) return;
    cancelWork(); final int token = generation;
    state = SpeechModelPolicy.State.REQUESTED; detail = ""; render();
    try {
      downloader = SpeechRecognizer.createOnDeviceSpeechRecognizer(activity);
      if (Build.VERSION.SDK_INT >= 34) {
        downloader.triggerModelDownload(SpeechProbe.intent("zh-TW"), task -> ui.post(task), new ModelDownloadListener() {
          public void onProgress(int percent) {
            if (!active(token)) return;
            state = SpeechModelPolicy.State.DOWNLOADING; detail = percent >= 0 && percent <= 100 ? "系統回報進度：" + percent + "%" : "語音服務沒有回報有效進度。"; render();
          }
          public void onSuccess() { if (active(token)) { releaseDownloader(); check(); } }
          public void onScheduled() {
            if (!active(token)) return;
            state = SpeechModelPolicy.State.PENDING; detail = "系統只排定下載，還沒有回報完成。"; render();
          }
          public void onError(int error) {
            if (!active(token)) return;
            state = SpeechModelPolicy.State.ERROR; detail = "語音服務回報代碼 " + error + "。若此服務不支援下載回報，請改用語音輸入設定並重新檢查。"; render();
          }
        });
      } else downloader.triggerModelDownload(SpeechProbe.intent("zh-TW"));
    } catch (RuntimeException error) {
      if (!active(token)) return;
      state = SpeechModelPolicy.State.ERROR; detail = "此語音服務無法從 App 提出下載，請改用『開啟語音輸入設定』。"; render();
    }
  }
  private void settings(Intent intent) {
    if (!showing() || paused || activity.isFinishing()) return;
    cancelWork();
    try { activity.startActivity(intent); }
    catch (ActivityNotFoundException | SecurityException error) {
      try { activity.startActivity(new Intent(Settings.ACTION_SETTINGS)); }
      catch (ActivityNotFoundException | SecurityException unavailable) { Toast.makeText(activity, "此手機未提供設定入口，請手動開啟系統設定。", Toast.LENGTH_LONG).show(); }
    }
  }
  void permissionResult() { if (showing()) check(); }
  void pause() { paused = true; generation++; probe.cancel(); }
  void resume() { paused = false; if (showing()) check(); }
  private void cancelWork() {
    generation++; probe.cancel(); releaseDownloader();
  }
  private void releaseDownloader() {
    SpeechRecognizer previous = downloader; downloader = null;
    if (previous != null) try { previous.destroy(); } catch (RuntimeException ignored) {}
  }
  void close() {
    cancelWork(); AlertDialog previous = dialog; dialog = null;
    if (previous != null) previous.dismiss();
  }
}
