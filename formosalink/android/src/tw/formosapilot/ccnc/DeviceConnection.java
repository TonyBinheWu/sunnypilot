package tw.formosapilot.ccnc;

import android.net.Network;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Proxy;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.util.Locale;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

final class DeviceConnection {
  final String host, expectedPin, token;
  final Network network;
  volatile String verifiedPin = "";

  DeviceConnection(String host, String pin, String token, Network network) {
    this.network = network;
    this.host = host.trim();
    String[] parts = this.host.split("\\.", -1);
    if (parts.length != 4)
      throw new IllegalArgumentException("IP");
    int[] octets = new int[4];
    for (int i = 0; i < 4; i++) {
      if (!parts[i].matches("0|[1-9][0-9]{0,2}") || (octets[i] = Integer.parseInt(parts[i])) > 255)
        throw new IllegalArgumentException("IP");
    }
    if (!(octets[0] == 10 || octets[0] == 192 && octets[1] == 168
            || octets[0] == 172 && octets[1] >= 16 && octets[1] <= 31
            || octets[0] == 169 && octets[1] == 254))
      throw new IllegalArgumentException("IP");
    expectedPin = pin.replace("-", "").replace(" ", "").toLowerCase(Locale.ROOT);
    if (!expectedPin.matches("[a-f0-9]{64}") && !(token.isEmpty() && expectedPin.matches("[a-f0-9]{12}")))
      throw new IllegalArgumentException("pin");
    this.token = token;
  }

  static final class Reply {
    final int status;
    final String data;
    Reply(int status, String data) {
      this.status = status;
      this.data = data;
    }
  }

  Reply call(String path, String body) throws Exception {
    if (!(path.equals("/v1/pair") || path.equals("/v1/state") || path.equals("/v1/settings")
            || path.equals("/v1/frame/wide-road") || path.equals("/v1/frame/driver")))
      throw new IllegalArgumentException("path");
    SSLContext context = SSLContext.getInstance("TLS");
    context.init(null,new TrustManager[]{new X509TrustManager() {
      public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0];
  }
  public void checkClientTrusted(X509Certificate[] c, String a) throws CertificateException {
    throw new CertificateException();
  }
  public void checkServerTrusted(X509Certificate[] chain, String a) throws CertificateException {
    try {
      if (chain == null || chain.length == 0)
        throw new CertificateException();
      chain[0].checkValidity();
      byte[] digest = MessageDigest.getInstance("SHA-256").digest(chain[0].getEncoded());
      StringBuilder hex = new StringBuilder();
      for (byte b : digest) hex.append(String.format(Locale.ROOT, "%02x", b & 255));
      String value = hex.toString();
      if (!MessageDigest.isEqual(expectedPin.getBytes(StandardCharsets.US_ASCII),
              value.substring(0, expectedPin.length()).getBytes(StandardCharsets.US_ASCII)))
        throw new CertificateException("device identity");
      verifiedPin = value;
    } catch (Exception e) {
      throw new CertificateException("device identity", e);
    }
  }
}
},null);
URL url = new URL("https://" + host + ":8787" + path);
HttpsURLConnection conn = (HttpsURLConnection) (network == null ? url.openConnection(Proxy.NO_PROXY) : network.openConnection(url, Proxy.NO_PROXY));
conn.setSSLSocketFactory(context.getSocketFactory());
conn.setHostnameVerifier((name, session) -> name.equals(host) && !verifiedPin.isEmpty());
conn.setInstanceFollowRedirects(false);
conn.setUseCaches(false);
conn.setConnectTimeout(4500);
conn.setReadTimeout(6500);
if (!token.isEmpty())
  conn.setRequestProperty("Authorization", "Bearer " + token);
try {
  if (!body.isEmpty()) {
    byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
    if (bytes.length > 8192)
      throw new IllegalArgumentException("body");
    conn.setRequestMethod("POST");
    conn.setDoOutput(true);
    conn.setRequestProperty("Content-Type", "application/json");
    conn.setFixedLengthStreamingMode(bytes.length);
    try (OutputStream stream = conn.getOutputStream()) {
      stream.write(bytes);
    }
  }
  int status = conn.getResponseCode();
  try (InputStream stream = status < 400 ? conn.getInputStream() : conn.getErrorStream()) {
    return new Reply(status, stream == null ? "{}" : read(stream, 600 * 1024));
  }
} finally {
  conn.disconnect();
}
}

static String read(InputStream stream, int limit) throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] buffer = new byte[8192];
  int n;
  while ((n = stream.read(buffer)) != -1) {
    if (out.size() + n > limit)
      throw new IllegalArgumentException("size");
    out.write(buffer, 0, n);
  }
  return out.toString("UTF-8");
}
}
