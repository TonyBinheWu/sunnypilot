"""Build and sign the ccNC LAN app with Android SDK 35 and JDK 17+."""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--sdk", type=Path, required=True)
  parser.add_argument("--jdk", type=Path, required=True)
  parser.add_argument("--keystore", type=Path, required=True)
  parser.add_argument("--alias", default="formosalink-ccnc")
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()
  root = Path(__file__).resolve().parent
  web = root.parent / "web"
  android = args.sdk / "platforms/android-35/android.jar"
  tools = args.sdk / "build-tools/35.0.0"
  suffix = ".exe" if os.name == "nt" else ""
  env = {**os.environ, "JAVA_HOME": str(args.jdk), "PATH": str(args.jdk / "bin") + os.pathsep + os.environ["PATH"]}
  if not env.get("CCNC_APK_SIGNING_PASSWORD"):
    parser.error("Set CCNC_APK_SIGNING_PASSWORD for the selected release key.")

  def run(*args):
    subprocess.run([str(a) for a in args], check=True, env=env)

  with tempfile.TemporaryDirectory() as temp:
    build = Path(temp)
    res = build / "res/drawable-nodpi"
    res.mkdir(parents=True)
    shutil.copyfile(web / "assets/formosapilot-logo.png", res / "formosa.png")
    assets = build / "assets/web"
    shutil.copytree(web, assets, ignore=shutil.ignore_patterns("package.json", "sw.js", "downloads"))
    html = (assets / "index.html").read_text("utf-8")
    html, count = re.subn(r'src="/app\.js\?v=[^"]+"', 'src="/lan-entry.js"', html)
    if count != 1:
      raise ValueError("Missing workspace entry")
    (assets / "index.html").write_text(html, "utf-8")
    shutil.copyfile(root / "lan-entry.js", assets / "lan-entry.js")
    aapt = tools / ("aapt2" + suffix)
    run(aapt, "compile", "--dir", res.parent, "-o", build / "res.zip")
    unsigned = build / "unsigned.apk"
    run(
      aapt,
      "link",
      "-I",
      android,
      "--manifest",
      root / "AndroidManifest.xml",
      "--min-sdk-version",
      "26",
      "--target-sdk-version",
      "35",
      "-A",
      assets.parent,
      "-o",
      unsigned,
      build / "res.zip",
    )
    classes, dex = build / "classes", build / "dex"
    classes.mkdir()
    dex.mkdir()
    run(
      args.jdk / "bin" / ("javac" + suffix),
      "-encoding",
      "UTF-8",
      "-source",
      "8",
      "-target",
      "8",
      "-bootclasspath",
      os.pathsep.join((str(android), str(tools / "core-lambda-stubs.jar"))),
      "-d",
      classes,
      *sorted((root / "src").rglob("*.java")),
    )
    run(args.jdk / "bin" / ("jar" + suffix), "cf", build / "classes.jar", "-C", classes, ".")
    java = args.jdk / "bin" / ("java" + suffix)
    run(java, "-cp", tools / "lib/d8.jar", "com.android.tools.r8.D8", "--min-api", "26", "--lib", android, "--output", dex, build / "classes.jar")
    # The Windows build of aapt2 emits backslashes in nested asset names. Android's
    # AssetManager uses forward slashes in both the local headers and the directory.
    packaged = build / "packaged.apk"
    with zipfile.ZipFile(unsigned) as resources, zipfile.ZipFile(packaged, "w") as archive:
      for item in resources.infolist():
        name = item.orig_filename.replace("\\", "/")
        archive.writestr(name, resources.read(item), compress_type=item.compress_type)
      archive.write(dex / "classes.dex", "classes.dex", compress_type=zipfile.ZIP_DEFLATED)
      if not {"assets/web/index.html", "assets/web/lan-entry.js", "classes.dex"} <= set(archive.namelist()):
        raise ValueError("Missing packaged companion resources")
    aligned = build / "aligned.apk"
    run(tools / ("zipalign" + suffix), "-f", "-p", "4", packaged, aligned)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    signer = tools / "lib/apksigner.jar"
    run(
      java,
      "-jar",
      signer,
      "sign",
      "--ks",
      args.keystore,
      "--ks-key-alias",
      args.alias,
      "--ks-pass",
      "env:CCNC_APK_SIGNING_PASSWORD",
      "--v4-signing-enabled",
      "false",
      "--out",
      args.output,
      aligned,
    )
    run(java, "-jar", signer, "verify", "--verbose", "--print-certs", args.output)


if __name__ == "__main__":
  main()
