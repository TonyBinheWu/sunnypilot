package me.shind0.carrotweb;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.speech.RecognitionSupport;
import android.speech.RecognitionSupportCallback;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;

/** Main-thread, cancellable metadata query. It never records audio or starts a download. */
final class SpeechProbe {
  interface Result { void accept(SpeechModelPolicy.State state, String detail); }
  private final Context context;
  private final Handler ui = new Handler(Looper.getMainLooper());
  private SpeechRecognizer checker;
  private int generation;
  private Runnable timeout;
  SpeechProbe(Context context) { this.context = context; }
  static boolean microphone(Context context) { return context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED; }
  static boolean service(Context context) {
    try { return Build.VERSION.SDK_INT >= 31 && SpeechRecognizer.isOnDeviceRecognitionAvailable(context); }
    catch (RuntimeException error) { return false; }
  }
  static Intent intent(String language) {
    return new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
      .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
      .putExtra(RecognizerIntent.EXTRA_LANGUAGE, language)
      .putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true);
  }
  void check(String language, Result result) {
    cancel();
    final int token = generation;
    SpeechModelPolicy.State state = SpeechModelPolicy.prerequisite(Build.VERSION.SDK_INT, microphone(context), service(context));
    if (state != SpeechModelPolicy.State.CHECKING) { result.accept(state, ""); return; }
    timeout = () -> finish(token, result, SpeechModelPolicy.State.UNKNOWN, "語音服務未在 10 秒內回應，尚未確認模型。可稍後重新檢查或開啟語音輸入設定。");
    ui.postDelayed(timeout, 10000);
    try {
      checker = SpeechRecognizer.createOnDeviceSpeechRecognizer(context);
      checker.checkRecognitionSupport(intent(language), task -> ui.post(task), new RecognitionSupportCallback() {
        public void onSupportResult(RecognitionSupport support) {
          if (support == null) { finish(token, result, SpeechModelPolicy.State.UNKNOWN, "語音服務沒有回傳模型資訊。"); return; }
          finish(token, result, SpeechModelPolicy.classify(language, support.getInstalledOnDeviceLanguages(),
            support.getPendingOnDeviceLanguages(), support.getSupportedOnDeviceLanguages()), "");
        }
        public void onError(int error) {
          finish(token, result, SpeechModelPolicy.State.UNKNOWN, "語音服務無法查詢模型（代碼 " + error + "），這不代表模型已安裝或一定缺少。請使用下方設定引導。");
        }
      });
    } catch (RuntimeException error) {
      finish(token, result, SpeechModelPolicy.State.UNKNOWN, "目前語音服務無法提供模型查詢，請使用下方手動設定引導。");
    }
  }
  private void finish(int token, Result result, SpeechModelPolicy.State state, String detail) {
    if (token != generation) return;
    cancel();
    result.accept(state, detail);
  }
  void cancel() {
    generation++;
    if (timeout != null) ui.removeCallbacks(timeout);
    timeout = null;
    SpeechRecognizer previous = checker; checker = null;
    if (previous != null) try { previous.destroy(); } catch (RuntimeException ignored) {}
  }
}
