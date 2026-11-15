package me.shind0.carrotweb;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.provider.Settings;
import android.speech.SpeechRecognizer;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.net.HttpURLConnection;
import java.net.Inet4Address;
import java.net.NetworkInterface;
import java.util.Collections;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Supplier;

/** Foreground, read-only LAN checks. No permission grants, writes or uploads. */
public final class AppDiagnostics {
  private final Activity activity;
  private final Supplier<String> address;
  private final Runnable search, manual, speech, device;
  private AlertDialog dialog;
  private DeviceProbe probe;
  private ExecutorService worker;
  private int generation;
  private boolean foreground;

  public AppDiagnostics(Activity activity, Supplier<String> address, Runnable search, Runnable manual, Runnable speech, Runnable device) {
    this.activity=activity; this.address=address; this.search=search; this.manual=manual; this.speech=speech; this.device=device;
  }
  private String text(String en,String tw) { return "zh-tw".equals(UiText.languageCode())?tw:en; }
  public void resume() { foreground=true; }
  public void pause() { foreground=false; close(); }
  private void cancelProbe() {
    generation++;
    if(probe!=null){probe.close();probe=null;}
    if(worker!=null){worker.shutdownNow();worker=null;}
  }
  public void close() {
    cancelProbe();
    AlertDialog old=dialog;dialog=null;
    if(old!=null)old.dismiss();
  }
  private void button(LinearLayout root,String en,String tw,Runnable action) {
    Button button=new Button(activity);button.setAllCaps(false);button.setText(text(en,tw));
    button.setOnClickListener(v->{close();if(foreground&&!activity.isFinishing())action.run();});root.addView(button);
  }
  public void open() {
    if(!foreground||activity.isFinishing())return;
    close();
    LinearLayout root=new LinearLayout(activity);root.setOrientation(LinearLayout.VERTICAL);
    int padding=Math.round(16*activity.getResources().getDisplayMetrics().density);root.setPadding(padding,padding,padding,padding);
    TextView result=new TextView(activity);result.setTextSize(16);result.setText(text("Checking connection…","正在檢查連線…"));root.addView(result);
    Button again=new Button(activity);again.setText(text("Check again","重新檢查"));again.setAllCaps(false);root.addView(again);
    again.setOnClickListener(v->check(result,again));
    button(root,"Search for device again","重新搜尋裝置",search);
    button(root,"Enter device IP","重新輸入車機 IP",manual);
    button(root,"Open Wi-Fi settings","開啟 Wi-Fi 設定",()->{
      try{activity.startActivity(new Intent(Settings.ACTION_WIFI_SETTINGS));}catch(Exception ignored){}
    });
    button(root,"Chinese speech model and microphone setup","中文語音檢查與安裝",speech);
    button(root,"Open full device diagnosis","開啟車機完整診斷",device);
    ScrollView scroll=new ScrollView(activity);scroll.addView(root);
    dialog=new AlertDialog.Builder(activity).setTitle(text("Connection diagnosis and repair","連線自我診斷與修復"))
      .setView(scroll).setNegativeButton(text("Close","關閉"),(d,w)->close()).create();
    dialog.setOnDismissListener(d->{cancelProbe();dialog=null;});dialog.show();
    check(result,again);
  }
  private boolean localInterface() {
    try{
      for(NetworkInterface iface:Collections.list(NetworkInterface.getNetworkInterfaces())){
        if(!iface.isUp()||iface.isLoopback()||!iface.getName().matches("(?i)(wlan|wifi|swlan|ap|softap|eth).*"))continue;
        for(java.net.InetAddress ip:Collections.list(iface.getInetAddresses())){
          if(ip instanceof Inet4Address&&DiscoveryPolicy.local(ip.getHostAddress()))return true;
        }
      }
    }catch(Exception ignored){}
    return false;
  }
  private void check(TextView result,Button again) {
    cancelProbe();final int token=generation;final String selected=address.get();
    again.setEnabled(false);result.setText(text("Checking connection…","正在檢查連線…"));
    final DeviceProbe current=new DeviceProbe(url->(HttpURLConnection)url.openConnection());probe=current;
    worker=Executors.newSingleThreadExecutor();worker.execute(()->{
      boolean lan=localInterface(), verified=DiscoveryPolicy.local(selected)&&current.verify(selected);
      activity.runOnUiThread(()->{
        if(!foreground||token!=generation||dialog==null||!dialog.isShowing()||activity.isFinishing())return;
        again.setEnabled(true);
        boolean microphone=activity.checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)==PackageManager.PERMISSION_GRANTED;
        boolean recognizer=false;
        try{recognizer=Build.VERSION.SDK_INT>=31&&SpeechRecognizer.isOnDeviceRecognitionAvailable(activity);}catch(Exception ignored){}
        String message=(lan?text("Local Wi-Fi/hotspot/Ethernet interface found.","已找到區域網路 Wi-Fi／熱點／有線介面。"):
          text("No supported local IPv4 interface found. Check Wi-Fi/hotspot or Ethernet.","未找到可用的區域網路 IPv4 介面，請檢查 Wi-Fi／熱點或有線網路。"));
        message+="\n\n"+(verified?text("Carrot Web responded and passed software checks. This does not prove the camera or CAN is healthy.","Carrot Web 已回應並通過軟體辨識；這不代表鏡頭或 CAN 也正常。"):
          text("Could not verify Carrot Web at the selected address. Check IP/port 7000, device power, boot completion and network isolation. Search again if the IP changed.","無法在選取位址驗證 Carrot Web。請確認 IP／7000 連接埠、車機供電、開機是否完成，以及網路是否隔離；IP 改變時請重新搜尋。"));
        message+="\n\n"+text("Microphone permission: ","麥克風權限：")+(microphone?text("granted","已授予"):text("not granted","尚未授予"));
        message+="\n"+text("On-device speech service: ","裝置端語音服務：")+(recognizer?text("available","可用"):text("not confirmed/unsupported","尚未確認／不支援"));
        message+="\n"+text("Service availability does not confirm that a zh-TW model is installed. Use speech setup to inspect it.","服務可用不代表已安裝 zh-TW 模型，請用「中文語音檢查與安裝」確認。");
        message+="\n\n"+text("Read-only checks. No settings, pairing, permissions or recordings were changed or uploaded.","本次為唯讀檢查，未更改設定、配對、權限或錄影，也沒有上傳資料。");
        result.setText(message);
      });
    });
  }
}
