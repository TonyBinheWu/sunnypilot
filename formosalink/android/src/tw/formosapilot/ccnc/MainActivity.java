package tw.formosapilot.ccnc;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
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
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.json.JSONObject;

public final class MainActivity extends Activity {
  private static final String UI = "https://ccnc.formosa.invalid";
  private final ExecutorService io = Executors.newSingleThreadExecutor();
  private SharedPreferences prefs;
  private DeviceConnection connection;
  private WebView browser;
  private EditText hostInput, pinInput, codeInput;
  private TextView status;
  private Button connect;
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
    label(panel,
        tr("將手機與車機連上同一個 Wi-Fi。停車後，在車機的 FormosaLink 開啟「區網 "
           + "APK」，按「產生配對碼」。",
            "Join the device Wi-Fi. While parked, open FormosaLink → LAN app on the device and "
            + "choose Pair a phone."),
        17);
    hostInput = field(panel, tr("車機位址", "Device IP"), "192.168.1.20",
        InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
    hostInput.setText(prefs.getString("host", ""));
    pinInput = field(panel, tr("車機顯示的憑證碼", "Certificate code on device"), "ABCD-EF01-2345",
        InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS
            | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
    codeInput = field(
        panel, tr("一次性配對碼", "One-time pairing code"), "123456", InputType.TYPE_CLASS_NUMBER);
    connect = new Button(this);
    connect.setText(tr("連線", "Connect"));
    connect.setMinHeight(dp(52));
    panel.addView(connect);
    connect.setOnClickListener(v -> connectDevice());
    status = label(panel, "", 16);
    status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
    if (prefs.contains("token"))
      status.setText(tr("此手機已配對。再次連線可留空憑證碼與配對碼。",
          "Already paired. Leave both codes empty to reconnect."));
    if (prefs.contains("token")) {
      Button forget = new Button(this);
      forget.setText(tr("忘記此車機", "Forget this device"));
      panel.addView(forget);
      forget.setOnClickListener(v -> {
        prefs.edit().clear().apply();
        form();
      });
    }
  }
  private void connectDevice() {
    final String host = hostInput.getText().toString().trim(),
                 pin = pinInput.getText().toString().trim(),
                 code = codeInput.getText().toString().trim();
    final boolean existing = pin.isEmpty() && code.isEmpty() && prefs.contains("token");
    if (!existing && !code.matches("[0-9]{6}")) {
      status.setText(tr("請輸入六位數配對碼。", "Enter the six-digit code."));
      return;
    }
    final DeviceConnection first;
    try {
      first = new DeviceConnection(host, existing ? prefs.getString("pin", "") : pin,
          existing ? prefs.getString("token", "") : "");
    } catch (Exception e) {
      status.setText(tr("請核對區網 IP 與 12 碼憑證碼。",
          "Check the LAN IPv4 address and 12-character certificate code."));
      return;
    }
    int epoch = ++generation;
    connect.setEnabled(false);
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
              host, first.verifiedPin, new JSONObject(paired.data).getString("token"));
        }
        DeviceConnection.Reply res = client.call("/v1/state", "");
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
          connection = verified;
          selectedId = id;
          workspace();
        });
      } catch (Exception e) {
        runOnUiThread(() -> {
          if (generation != epoch)
            return;
          connect.setEnabled(true);
          status.setText(
              tr("連線失敗。請確認同一個 Wi-Fi、車機位址與憑證碼；配對碼逾時可在車機重新產生。",
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
  protected void onDestroy() {
    generation++;
    io.shutdownNow();
    fileBridge.cancelClip();
    if (browser != null)
      browser.destroy();
    super.onDestroy();
  }
}
