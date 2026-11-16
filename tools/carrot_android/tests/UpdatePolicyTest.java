import me.shind0.carrotweb.UpdatePolicy;

public class UpdatePolicyTest {
  private static int checks;
  private static void check(boolean value) { checks++; if (!value) throw new AssertionError("Update check "+checks); }
  public static void main(String[] args) {
    String url="https://github.com/TonyBinheWu/sunnypilot/releases/download/carrot-assist-tw-v0.2.0/CarrotAssist-TW-0.2.0.apk";
    String hash=new String(new char[64]).replace('\0','a');
    check(UpdatePolicy.valid(5,6,"0.2.0",url,hash));
    check(!UpdatePolicy.valid(6,6,"0.2.0",url,hash));
    check(!UpdatePolicy.valid(7,6,"0.2.0",url,hash));
    check(!UpdatePolicy.valid(5,6,"0.2.0",url.replace("TonyBinheWu","other"),hash));
    check(!UpdatePolicy.valid(5,6,"0.2.0",url+"?redirect=evil",hash));
    check(!UpdatePolicy.valid(5,6,"0.2.0",url,"bad"));
    check(!UpdatePolicy.valid(5,6,"0.2.0/../x",url,hash));
    check(!UpdatePolicy.valid(5,6,"0.2.0","https://github.com/ajouatom/openpilot/releases/download/carrot-assist-v0.2.0/CarrotAssist-0.2.0.apk",hash));
    check(UpdatePolicy.downloadHost(url));
    String cockpit="me.shind0.carrotweb.tw.cockpit";
    String cockpitUrl="https://github.com/TonyBinheWu/sunnypilot/releases/download/carrot-cockpit-tw-v0.1.0/CarrotCockpit-TW-0.1.0.apk";
    check(UpdatePolicy.validFor(cockpit,1,2,"0.1.0",cockpitUrl,hash));
    check(!UpdatePolicy.validFor(cockpit,1,2,"0.2.0",url,hash));
    check(!UpdatePolicy.validFor("me.shind0.carrotweb.tw",1,2,"0.1.0",cockpitUrl,hash));
    check(!UpdatePolicy.validFor("unknown",1,2,"0.2.0",url,hash));
    check(!UpdatePolicy.validFor(cockpit,2,2,"0.1.0",cockpitUrl,hash));
    check(!UpdatePolicy.validFor(cockpit,1,2,"0.1.0",cockpitUrl+"?x",hash));
    check(!UpdatePolicy.manifest(cockpit).equals(UpdatePolicy.MANIFEST));
    check(UpdatePolicy.manifest("me.shind0.carrotweb.tw").equals(UpdatePolicy.MANIFEST));
    check(UpdatePolicy.downloadHost("https://release-assets.githubusercontent.com/a?signature=b"));
    for(String bad:new String[]{"http://github.com/a","https://github.com.evil.test/a","https://evil@github.com/a","https://github.com:7000/a","file:///tmp/a","https://127.0.0.1/a"}) check(!UpdatePolicy.downloadHost(bad));
    System.out.println("Update policy checks passed: "+checks);
  }
}
