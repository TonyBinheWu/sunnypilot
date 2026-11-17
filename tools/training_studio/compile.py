"""Compile a qualified N16 candidate on an actual gfx1200 AMD worker and package its runtime."""
import argparse
import gzip
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tarfile

from tools.training_studio.store import read_json, write_json
from openpilot.sunnypilot.formosalink.training_protocol import digest_file


def package_runtime(source, output):
  """The exact code which produced the pickle travels with that pickle."""
  with output.open("wb") as raw, gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0) as compressed:
    with tarfile.open(fileobj=compressed,mode="w") as archive:
      paths = [*source.joinpath("tinygrad").rglob("*.py"), *source.joinpath("examples/openpilot").rglob("*.py"), source/"LICENSE"]
      for path in sorted(paths):
        if "__pycache__" in path.parts or not path.is_file() or path.is_symlink():
          continue
        body=path.read_bytes()
        member=tarfile.TarInfo(path.relative_to(source).as_posix())
        member.size,member.mode,member.mtime=len(body),0o644,0
        archive.addfile(member,io.BytesIO(body))


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--run",type=Path,required=True)
  parser.add_argument("--tinygrad",type=Path,default=Path(__file__).resolve().parents[2]/"tinygrad_repo")
  args=parser.parse_args()
  folder=args.run.resolve()
  source=args.tinygrad.resolve()
  # Isolate from the training machine's torch/NVIDIA environment.
  environment={**os.environ,"PYTHONPATH":str(source),"DEV":"AMD"}
  probe=subprocess.run([sys.executable,"-c","from tinygrad.device import Device; d=Device['AMD']; print(d.arch)"],
    env=environment,text=True,capture_output=True,timeout=60)
  if probe.returncode or "gfx1200" not in probe.stdout:
    raise RuntimeError("需要實際 RX 9060 / gfx1200 AMD 編譯工作站；DGX 推論結果不能替代 AMD 編譯")
  release=folder/"release"
  release.mkdir(exist_ok=True)
  artifact=release/"big_driving_tinygrad.pkl"
  subprocess.run([sys.executable,str(source/"examples/openpilot/compile_onnx.py"),str(folder/"candidate.onnx"),str(artifact),
    "--out-of-band","--retargetable","--benchmark-runs","50"],env=environment,check=True)
  runtime=release/"precompiled-runtime.tar.gz"
  package_runtime(source,runtime)
  plan=read_json(folder/"plan.json")
  checksum=digest_file(artifact)
  manifest={"model_id":folder.name,"filename":artifact.name,"size":artifact.stat().st_size,"sha256":checksum,"url":artifact.name}
  runtime_commit=subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()
  metadata={"protocol":1,"format":"comma-generic-onnx","serialization":"persistent-buffer-v1","gpu_arch":"gfx1200","frame_skip":4,
    "camera_resolutions":[[1928,1208],[1344,760]],"model_sha256":checksum,"model_checkpoint":plan["base"]["path"].removesuffix("/big_driving_supercombo.onnx"),
    "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"tinygrad_commit":runtime_commit,
    "pickle":{"url":artifact.name,"size":artifact.stat().st_size,"sha256":checksum},
    "runtime":{"url":runtime.name,"size":runtime.stat().st_size,"sha256":digest_file(runtime)}}
  write_json(release/"manifest.json",manifest)
  write_json(release/"precompiled.json",metadata)
  write_json(folder/"compile.json",{"onnx_sha256":digest_file(folder/"candidate.onnx"),"artifact_sha256":checksum,
    "runtime_sha256":digest_file(runtime),"gpu_arch":"gfx1200","retargetable":True,"tinygrad_commit":runtime_commit,
    "device_acceptance":False,"note":"compiler benchmarks do not qualify end-to-end timing or fallback"})


if __name__=="__main__":
  main()
