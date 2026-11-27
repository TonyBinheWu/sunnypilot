package tw.formosapilot.ccnc;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.LinkProperties;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.os.SystemClock;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.InterfaceAddress;
import java.net.MulticastSocket;
import java.net.NetworkInterface;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

final class LanDiscovery {
  private static final int PORT = 8787;
  private static final String GROUP = "239.255.87.87";

  interface Receiver {
    void found(String host, String pin, Network network);
  }

  // Pin the request and the subsequent HTTPS session to the same Wi-Fi/Ethernet link.
  // Android hotspots may expose a local interface without a ConnectivityManager Network.
  static void search(Context context, Receiver receiver) throws IOException {
    ConnectivityManager cm = context.getSystemService(ConnectivityManager.class);
    Map<String, Network> links = new LinkedHashMap<>();
    for (Network network : cm.getAllNetworks()) {
      NetworkCapabilities caps = cm.getNetworkCapabilities(network);
      LinkProperties props = cm.getLinkProperties(network);
      if (caps != null && props != null && (caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
          || caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)) && props.getInterfaceName() != null)
        links.put(props.getInterfaceName(), network);
    }
    for (NetworkInterface nic : Collections.list(NetworkInterface.getNetworkInterfaces())) {
      String name = nic.getName();
      if (name.matches("(wlan|swlan|softap|ap|eth|en)[a-zA-Z0-9_.-]*") && nic.isUp() && !nic.isLoopback())
        links.putIfAbsent(name, null);
    }

    String nonce = UUID.randomUUID().toString().replace("-", "");
    byte[] query = ("FormosaLink-ccNC/1 FIND " + nonce).getBytes(StandardCharsets.US_ASCII);
    String prefix = "FormosaLink-ccNC/1 HERE " + nonce + " ";
    List<Link> opened = new ArrayList<>();
    Set<String> seen = new HashSet<>();
    try {
      for (Map.Entry<String, Network> entry : links.entrySet()) {
        NetworkInterface nic = NetworkInterface.getByName(entry.getKey());
        if (nic == null) continue;
        for (InterfaceAddress local : nic.getInterfaceAddresses()) {
          if (!(local.getAddress() instanceof Inet4Address) || local.getBroadcast() == null) continue;
          try {
            opened.add(new Link(entry.getValue(), nic, local));
          } catch (IOException ignored) { /* Interface disappeared. */ }
        }
      }
      long end = SystemClock.elapsedRealtime() + 2700, next = 0;
      while (!opened.isEmpty() && SystemClock.elapsedRealtime() < end && !Thread.currentThread().isInterrupted()) {
        if (SystemClock.elapsedRealtime() >= next) {
          next = SystemClock.elapsedRealtime() + 900;
          for (Link link : opened) link.query(query);
        }
        for (Link link : opened) {
          DatagramPacket packet = new DatagramPacket(new byte[160], 160);
          try {
            link.socket.receive(packet);
            String reply = new String(packet.getData(), 0, packet.getLength(), StandardCharsets.US_ASCII);
            if (packet.getPort() != PORT || !link.contains(packet.getAddress()) || !reply.startsWith(prefix)) continue;
            String pin = reply.substring(prefix.length());
            String host = packet.getAddress().getHostAddress();
            if (pin.matches("[0-9a-f]{64}") && seen.add(host + "/" + pin)) receiver.found(host, pin, link.network);
          } catch (SocketTimeoutException ignored) {
          } catch (IOException ignored) { /* Try the other local links. */ }
        }
      }
    } finally {
      for (Link link : opened) link.socket.close();
    }
  }

  private static final class Link {
    final Network network;
    final InterfaceAddress local;
    final MulticastSocket socket;
    Link(Network network, NetworkInterface nic, InterfaceAddress local) throws IOException {
      this.network = network;
      this.local = local;
      socket = new MulticastSocket(null);
      try {
        if (network != null) network.bindSocket(socket);
        socket.bind(new InetSocketAddress(local.getAddress(), 0));
        socket.setNetworkInterface(nic);
        socket.setTimeToLive(1);
        socket.setBroadcast(true);
        socket.setSoTimeout(120);
      } catch (IOException | RuntimeException e) {
        socket.close();
        throw e;
      }
    }
    void query(byte[] data) {
      for (String dest : new String[]{GROUP, local.getBroadcast().getHostAddress()}) {
        try {
          socket.send(new DatagramPacket(data, data.length, InetAddress.getByName(dest), PORT));
        } catch (IOException ignored) { /* Some networks allow only one discovery method. */ }
      }
    }
    boolean contains(InetAddress peer) {
      byte[] target = peer.getAddress(), own = local.getAddress().getAddress();
      if (target.length != 4) return false;
      int bits = local.getNetworkPrefixLength();
      if (bits < 1 || bits > 32) return false;
      for (int i = 0; i < 4 && bits > 0; i++, bits -= 8) {
        int mask = 0xff << Math.max(0, 8 - bits);
        if (((target[i] ^ own[i]) & mask & 0xff) != 0) return false;
      }
      return true;
    }
  }
}
