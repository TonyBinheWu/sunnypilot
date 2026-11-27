package tw.formosapilot.ccnc;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.net.Network;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.*;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.json.JSONObject;

public final class MainActivity extends Activity {
  private static final String UI = "https://ccnc.formosa.invalid";
  private final ExecutorService io = Executors.newSingleThreadExecutor();
  private SharedPreferences prefs;
  private DeviceConnection connection;
  private WebView browser;
  private final ExecutorService searchWorker = Executors.newSingleThreadExecutor();
  private final Handler handler = new Handler(Looper.getMainLooper());
  private final Map<String, Button> devices = new HashMap<>();
  private LinearLayout deviceList;
  private TextView discoveryStatus;
  private boolean resumed, connecting, autoReconnect = true;
  private long searchUntil;
  private int searchGeneration;
  private Future<?> pendingSearch;
  private final Runnable searchAgain = this::search;
  private TextView status;
  private Button rescan;
  private String selectedId, pendingExport;
  private int generation;
  private final Files fileBridge = new Files();
  private WebChromeClient.CustomViewCallback fullscreen;
  private View fullscreenView;
  private String tr(String zh, String en) {
    return Locale.getDefault().getLanguage().equals("en") ? en : zh;
  }
  @Override
  public void onCreate(Bundle state) {
    super.onCreate(state);
    prefs = getSharedPreferences("local-device", MODE_PRIVATE);
    getWindow().setStatusBarColor(Color.rgb(17, 47, 44));
    getWindow().setNavigationBarColor(Color.rgb(17, 47, 44));
    form();
  }
  private int dp(float n) {
    return Math.round(n * getResources().getDisplayMetrics().density);
  }
  private void display(View view) {
    view.setOnApplyWindowInsetsListener((v, insets) -> {
      v.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
          insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
      return insets.consumeSystemWindowInsets();
    });
    setContentView(view);
    view.requestApplyInsets();
  }
  private TextView label(LinearLayout root, String message, int size) {
    TextView v = new TextView(this);
    v.setText(message);
    v.setTextSize(size);
    v.setTextColor(Color.rgb(24, 56, 50));
    v.setPadding(0, dp(7), 0, dp(4));
    root.addView(v);
    return v;
  }
  private EditText field(LinearLayout root, String title, String hint, int type) {
    TextView l = label(root, title, 16);
    EditText input = new EditText(this);
    input.setId(View.generateViewId());
    l.setLabelFor(input.getId());
    input.setSingleLine(true);
    input.setInputType(type);
    input.setHint(hint);
    input.setTextSize(18);
    input.setMinHeight(dp(48));
    root.addView(input);
    return input;
  }
  private void form() {
    generation++;
    cancelSearch();
    connection = null;
    pendingExport = null;
    if (browser != null) {
      browser.removeJavascriptInterface("CcncDevice");
      browser.removeJavascriptInterface("CcncFiles");
      browser.destroy();
      browser = null;
    }
    ScrollView scroll = new ScrollView(this);
    scroll.setBackgroundColor(Color.rgb(244, 246, 241));
    LinearLayout panel = new LinearLayout(this);
    panel.setOrientation(LinearLayout.VERTICAL);
    panel.setPadding(dp(22), dp(28), dp(22), dp(30));
    scroll.addView(panel);
    display(scroll);
    label(panel, "FormosaLink ccNC", 30);
    label(panel, tr("附近的車機", "Nearby devices"), 23);
    label(panel, tr("手機和車機連上同一個 Wi-Fi。首次配對時，在停車的車機上點「設定 → 區網手機配對」。",
        "Join the same Wi-Fi as your device. To add a phone, open Settings → Pair local phone on the parked device."), 17);
    discoveryStatus = label(panel, "", 16);
    discoveryStatus.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
    deviceList = new LinearLayout(this);
    deviceList.setOrientation(LinearLayout.VERTICAL);
    panel.addView(deviceList);
    devices.clear();
    connecting = false;
    rescan = action(panel, tr("重新搜尋", "Search again"), v -> beginSearch());
    status = label(panel, "", 16);
    status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
    if (prefs.contains("token")) {
      action(panel, tr("連線上次配對的車機", "Connect to last paired device"), v ->
          connectDevice(prefs.getString("host", ""), prefs.getString("pin", ""), "", null, true));
    }
    action(panel, tr("手動連線（舊版車機）", "Manual connection (older devices)"), v -> {
      autoReconnect = false;
      pairingDialog("", "", null);
    });
    if (prefs.contains("token")) {
      Button forget = new Button(this);
      forget.setText(tr("忘記此車機", "Forget this device"));
      panel.addView(forget);
      forget.setOnClickListener(v -> {
        prefs.edit().clear().apply();
        form();
      });
    }
    if (resumed) beginSearch();
  }
  private Button action(LinearLayout panel, String title, View.OnClickListener click) {
    Button b = new Button(this);
    b.setText(title);
    b.setAllCaps(false);
    b.setMinHeight(dp(48));
    b.setOnClickListener(click);
    panel.addView(b);
    return b;
  }

  private static String shortPin(String pin) {
    String s = pin.substring(0, 12).toUpperCase(Locale.ROOT);
    return s.substring(0, 4) + "-" + s.substring(4, 8) + "-" + s.substring(8);
  }

  private void pairingDialog(String host, String pin, Network network) {
    boolean manual = host.isEmpty();
    LinearLayout box = new LinearLayout(this);
    box.setPadding(dp(22), dp(10), dp(22), dp(8));
    box.setOrientation(LinearLayout.VERTICAL);
    ScrollView fields = new ScrollView(this);
    fields.addView(box);
    EditText ip = manual ? field(box, tr("車機位址", "Device IP"), "", InputType.TYPE_CLASS_TEXT) : null;
    EditText cert = manual ? field(box, tr("車機識別碼", "Certificate code"), "", InputType.TYPE_CLASS_TEXT) : null;
    if (manual) ip.setText(prefs.getString("host", ""));
    else {
      label(box, shortPin(pin), 25);
      label(box, tr("確認這組識別碼與車機畫面相同，再輸入車機顯示的六位數配對碼。",
          "Match this ID with the one on the device, then enter its six-digit pairing code."), 16);
    }
    EditText code = field(box, tr("六位數配對碼", "Six-digit pairing code"), "", InputType.TYPE_CLASS_NUMBER);
    code.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(6)});
    AlertDialog dialog = new AlertDialog.Builder(this)
        .setTitle(tr("配對車機", "Pair device")).setView(fields)
        .setNegativeButton(android.R.string.cancel, null)
        .setPositiveButton(tr("配對", "Pair"), null).create();
    dialog.show();
    dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
      String entered = code.getText().toString();
      if (!entered.matches("[0-9]{6}")) {
        code.setError(tr("請輸入六位數", "Enter six digits"));
        return;
      }
      autoReconnect = false;
      dialog.dismiss();
      connectDevice(manual ? ip.getText().toString().trim() : host,
          manual ? cert.getText().toString().trim() : pin, entered, network, false);
    });
  }

  private void beginSearch() {
    cancelSearch();
    devices.clear();
    deviceList.removeAllViews();
    searchUntil = SystemClock.elapsedRealtime() + 60000;
    discoveryStatus.setText(tr("正在搜尋同一個區網的車機…", "Searching your local network…"));
    search();
  }

  private void cancelSearch() {
    searchGeneration++;
    handler.removeCallbacks(searchAgain);
    if (pendingSearch != null) pendingSearch.cancel(true);
  }

  private void search() {
    if (!resumed || browser != null || connecting) return;
    int epoch = searchGeneration;
    rescan.setEnabled(false);
    pendingSearch = searchWorker.submit(() -> {
      try {
        LanDiscovery.search(this, (host, pin, network) -> runOnUiThread(() -> {
          if (epoch != searchGeneration || !resumed || browser != null || connecting) return;
          boolean known = prefs.contains("token") && pin.equals(prefs.getString("pin", ""));
          String key = pin + "/" + host;
          if (!devices.containsKey(key) && devices.size() < 12) {
            String title = (known ? tr("已配對", "Paired") : "FormosaLink") + "  " + shortPin(pin);
            devices.put(key, action(deviceList, title, v -> {
              if (known) connectDevice(host, pin, "", network, true);
              else { autoReconnect = false; pairingDialog(host, pin, network); }
            }));
          }
          discoveryStatus.setText(tr("請選擇車機", "Select your device"));
          if (known && autoReconnect) {
            autoReconnect = false;
            connectDevice(host, pin, "", network, true);
          }
        }));
      } catch (IOException | RuntimeException ignored) { /* Wi-Fi may be switching. */ }
      runOnUiThread(() -> {
        if (epoch != searchGeneration || !resumed || browser != null) return;
        rescan.setEnabled(true);
        if (devices.isEmpty()) discoveryStatus.setText(tr("尚未找到車機。請確認同一個 Wi-Fi、車機已更新並開機。",
            "No device found. Check that it is updated, powered on and on the same Wi-Fi."));
        if (SystemClock.elapsedRealtime() < searchUntil) handler.postDelayed(searchAgain, 3000);
      });
    });
  }

  private void connectDevice(String host, String pin, String code, Network network, boolean existing) {
    if (connecting) return;
    if (!existing && !code.matches("[0-9]{6}")) {
      status.setText(tr("請輸入六位數配對碼。", "Enter the six-digit code."));
      return;
    }
    final DeviceConnection first;
    try {
      first = new DeviceConnection(host, pin, existing ? prefs.getString("token", "") : "", network);
    } catch (Exception e) {
      status.setText(tr("請核對區網 IP 與 12 碼憑證碼。",
          "Check the LAN IPv4 address and 12-character certificate code."));
      return;
    }
    int epoch = ++generation;
    cancelSearch();
    connecting = true;
    rescan.setEnabled(false);
    status.setText(tr("連線中…", "Connecting…"));
    io.execute(() -> {
      try {
        DeviceConnection client = first;
        if (!existing) {
          DeviceConnection.Reply paired =
              client.call("/v1/pair", new JSONObject().put("code", code).toString());
          if (paired.status != 200)
            throw new IllegalArgumentException("pair");
          client = new DeviceConnection(
              host, first.verifiedPin, new JSONObject(paired.data).getString("token"), network);
        }
        DeviceConnection.Reply res = client.call("/v1/state", "");
        if (res.status == 401 && existing) {
          runOnUiThread(() -> {
            if (generation != epoch || isFinishing()) return;
            prefs.edit().clear().apply();
            autoReconnect = false;
            form();
            status.setText(tr("車機已解除配對。請在車機產生新的配對碼。", "Pairing was revoked. Request a new code on the device."));
          });
          return;
        }
        if (res.status != 200)
          throw new IllegalArgumentException("auth");
        JSONObject state = new JSONObject(res.data);
        if (!"FormosaLink-ccnc".equals(state.getString("product")))
          throw new IllegalArgumentException("product");
        String id = state.getString("device");
        final DeviceConnection verified = client;
        runOnUiThread(() -> {
          if (generation != epoch || isFinishing())
            return;
          prefs.edit()
              .putString("host", host)
              .putString("pin", verified.verifiedPin)
              .putString("token", verified.token)
              .apply();
          connecting = false;
          autoReconnect = false;
          connection = verified;
          selectedId = id;
          workspace();
        });
      } catch (Exception e) {
        runOnUiThread(() -> {
          if (generation != epoch)
            return;
          connecting = false;
          rescan.setEnabled(true);
          status.setText(
              tr("無法連線。請重新搜尋車機；配對碼過期或手機已解除配對時，請在車機新增配對碼。",
                  "Connection failed. Check Wi-Fi, address and certificate. Request a fresh "
                  + "pairing code if it expired."));
        });
      }
    });
  }
  private void workspace() {
    browser = new WebView(this);
    WebSettings s = browser.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setAllowFileAccess(false);
    s.setAllowContentAccess(false);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setSupportMultipleWindows(false);
    browser.addJavascriptInterface(new DeviceBridge(), "CcncDevice");
    browser.addJavascriptInterface(fileBridge, "CcncFiles");
    browser.setWebChromeClient(new WebChromeClient() {
      @Override
      public void onShowCustomView(View view, CustomViewCallback callback) {
        if (fullscreen != null) {
          callback.onCustomViewHidden();
          return;
        }
        fullscreen = callback;
        fullscreenView = view;
        addContentView(view, new FrameLayout.LayoutParams(-1, -1));
      }
      @Override
      public void onHideCustomView() {
        leaveFullscreen();
      }
    });
    browser.setWebViewClient(new WebViewClient() {
      @Override
      public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
        Uri u = r.getUrl();
        if ("https".equals(u.getScheme()) && "www.openstreetmap.org".equals(u.getHost())
            && r.hasGesture())
          startActivity(new Intent(Intent.ACTION_VIEW, u));
        return !UI.equals(u.getScheme() + "://" + u.getAuthority())
            || !"/index.html".equals(u.getPath());
      }
      @Override
      public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
        Uri u = r.getUrl();
        String path = u.getPath();
        if (UI.equals(u.getScheme() + "://" + u.getAuthority()) && path != null
            && path.matches("/(?:[a-z0-9.-]+|assets/[a-z0-9.-]+)") && !path.contains("..")) {
          try {
            InputStream input = getAssets().open("web" + path);
            String mime = path.endsWith(".js") ? "text/javascript"
                : path.endsWith(".css")        ? "text/css"
                : path.endsWith(".html")       ? "text/html"
                : path.endsWith(".png")        ? "image/png"
                                               : "application/json";
            WebResourceResponse res =
                new WebResourceResponse(mime, path.endsWith(".png") ? null : "UTF-8", input);
            res.setResponseHeaders(java.util.Collections.singletonMap("Content-Security-Policy",
                "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src "
                + "'self' data: blob:; media-src blob:; connect-src 'none'; frame-src 'none'; "
                + "object-src 'none'; base-uri 'none'; form-action 'none'"));
            return res;
          } catch (IOException e) {
            android.util.Log.w("FormosaLink", "Packaged interface asset unavailable", e);
          }
        }
        return new WebResourceResponse(
            "text/plain", "UTF-8", 404, "Unavailable", null, new ByteArrayInputStream(new byte[0]));
      }
    });
    display(browser);
    browser.loadUrl(UI + "/index.html");
  }
  private final class DeviceBridge {
    @JavascriptInterface
    public String identity() {
      JSONObject v = new JSONObject();
      try {
        v.put("device", selectedId);
      } catch (Exception ignored) {
      }
      return v.toString();
    }
    @JavascriptInterface
    public void connections() {
      runOnUiThread(() -> form());
    }
    @JavascriptInterface
    public void request(int id, String path, String body) {
      final DeviceConnection client = connection;
      final int epoch = generation;
      if (client == null || body.length() > 8192
          || !(path.equals("/v1/state") && body.isEmpty()
              || path.equals("/v1/settings") && !body.isEmpty()
              || (path.equals("/v1/frame/wide-road") || path.equals("/v1/frame/driver"))
                  && body.isEmpty()))
        return;
      io.execute(() -> {
        DeviceConnection.Reply r;
        try {
          r = client.call(path, body);
        } catch (Exception ex) {
          r = new DeviceConnection.Reply(0, "{}");
        }
        final DeviceConnection.Reply result = r;
        runOnUiThread(() -> {
          if (generation == epoch && browser != null)
            browser.evaluateJavascript("window.ccncReply(" + id + "," + result.status + ","
                    + JSONObject.quote(result.data) + ")",
                null);
        });
      });
    }
  }
  private final class Files {
    private File recording;
    private OutputStream output;
    private long expected;
    private boolean mp4;
    @JavascriptInterface
    public synchronized boolean beginClip(boolean isMp4, long size) {
      if (recording != null || size <= 0 || size > 18 * 1024 * 1024)
        return false;
      try {
        recording = File.createTempFile("ccnc-recording-", ".tmp", getCacheDir());
        output = new FileOutputStream(recording);
        expected = size;
        mp4 = isMp4;
        return true;
      } catch (IOException e) {
        cancelClip();
        return false;
      }
    }
    @JavascriptInterface
    public synchronized boolean appendClip(String encoded) {
      if (output == null || encoded.length() > 44000)
        return false;
      try {
        byte[] bytes = android.util.Base64.decode(encoded, android.util.Base64.NO_WRAP);
        if (recording.length() + bytes.length > expected)
          return false;
        output.write(bytes);
        return true;
      } catch (IOException | IllegalArgumentException e) {
        return false;
      }
    }
    @JavascriptInterface
    public synchronized void cancelClip() {
      if (output != null)
        try {
          output.close();
        } catch (IOException ignored) {
        }
      output = null;
      if (recording != null)
        recording.delete();
      recording = null;
    }
    @JavascriptInterface
    public synchronized void saveClip() {
      if (output == null)
        return;
      try {
        output.close();
        output = null;
      } catch (IOException e) {
        cancelClip();
        return;
      }
      if (recording.length() != expected) {
        cancelClip();
        return;
      }
      String mime = mp4 ? "video/mp4" : "video/webm";
      String name = "FormosaLink-" + System.currentTimeMillis() + (mp4 ? ".mp4" : ".webm");
      runOnUiThread(() -> {
        if (browser == null) {
          cancelClip();
          return;
        }
        Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT)
                       .addCategory(Intent.CATEGORY_OPENABLE)
                       .setType(mime);
        startActivityForResult(i.putExtra(Intent.EXTRA_TITLE, name), 43);
      });
    }
    synchronized void copyClip(Uri uri) throws IOException {
      if (recording == null || output != null)
        throw new IOException("clip unavailable");
      try (InputStream in = new FileInputStream(recording);
          OutputStream out = getContentResolver().openOutputStream(uri, "wt")) {
        if (out == null)
          throw new IOException("output unavailable");
        byte[] buffer = new byte[32768];
        int n;
        while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
      } finally {
        cancelClip();
      }
    }
    @JavascriptInterface
    public void save(String json) {
      if (json.getBytes(StandardCharsets.UTF_8).length > 131072)
        return;
      runOnUiThread(() -> {
        if (browser == null)
          return;
        pendingExport = json;
        Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT)
                       .addCategory(Intent.CATEGORY_OPENABLE)
                       .setType("application/json");
        i.putExtra(Intent.EXTRA_TITLE, "FormosaLink-settings.json");
        startActivityForResult(i, 41);
      });
    }
    @JavascriptInterface
    public void open() {
      runOnUiThread(() -> {
        if (browser != null)
          startActivityForResult(new Intent(Intent.ACTION_OPEN_DOCUMENT)
                                     .addCategory(Intent.CATEGORY_OPENABLE)
                                     .setType("*/*"),
              42);
      });
    }
  }
  @Override
  protected void onActivityResult(int request, int result, Intent data) {
    super.onActivityResult(request, result, data);
    String export = pendingExport;
    pendingExport = null;
    if (result != RESULT_OK || data == null || data.getData() == null || browser == null) {
      if (request == 43)
        fileBridge.cancelClip();
      return;
    }
    int epoch = generation;
    Uri uri = data.getData();
    io.execute(() -> {
      try {
        if (request == 43)
          fileBridge.copyClip(uri);
        if (request == 41 && export != null) {
          try (OutputStream out = getContentResolver().openOutputStream(uri, "wt")) {
            out.write(export.getBytes(StandardCharsets.UTF_8));
          }
        }
        if (request == 42) {
          try (InputStream in = getContentResolver().openInputStream(uri)) {
            deliverFile(epoch, DeviceConnection.read(in, 131072));
          }
        }
      } catch (Exception e) {
        if (request == 42)
          deliverFile(epoch, "");
        else
          runOnUiThread(
              ()
                  -> Toast
                      .makeText(this, tr("無法儲存檔案", "Could not save file"), Toast.LENGTH_LONG)
                      .show());
      }
    });
  }
  private void deliverFile(int epoch, String text) {
    runOnUiThread(() -> {
      if (generation == epoch && browser != null)
        browser.evaluateJavascript("window.ccncImport?.(" + JSONObject.quote(text) + ")", null);
    });
  }
  private void leaveFullscreen() {
    if (fullscreen == null)
      return;
    WebChromeClient.CustomViewCallback callback = fullscreen;
    fullscreen = null;
    if (fullscreenView.getParent() instanceof android.view.ViewGroup)
      ((android.view.ViewGroup) fullscreenView.getParent()).removeView(fullscreenView);
    fullscreenView = null;
    callback.onCustomViewHidden();
  }
  @Override
  public void onBackPressed() {
    if (fullscreen != null)
      leaveFullscreen();
    else if (browser != null)
      form();
    else
      super.onBackPressed();
  }
  @Override
  protected void onResume() {
    super.onResume();
    resumed = true;
    if (browser == null && !connecting) beginSearch();
  }
  @Override
  protected void onPause() {
    resumed = false;
    cancelSearch();
    super.onPause();
  }
  @Override
  protected void onDestroy() {
    generation++;
    cancelSearch();
    searchWorker.shutdownNow();
    io.shutdownNow();
    fileBridge.cancelClip();
    if (browser != null)
      browser.destroy();
    super.onDestroy();
  }
}
