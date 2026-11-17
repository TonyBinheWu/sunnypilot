"""Apply narrow collection hooks to another checkout without copying its existing companion code."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time

SOURCE=Path(__file__).resolve().parents[2]
NEW_FILES=("formosalink/server/training.py","formosalink/web/training-data.js",
  "openpilot/sunnypilot/formosalink/training_protocol.py","openpilot/sunnypilot/formosalink/training_upload.py",
  "openpilot/sunnypilot/formosalink/training_ui.py","openpilot/sunnypilot/formosalink/training_models.py")


def once(text,old,new):
  if new in text:
    return text
  if text.count(old)!=1:
    raise ValueError("integration anchor changed; review manually: "+old[:70])
  return text.replace(old,new,1)


def changes(checkout):
  checkout=Path(checkout).resolve()
  result={}
  for name in NEW_FILES:
    result[name]=(SOURCE/name).read_text(encoding="utf-8")
  name="formosalink/server/app.py"
  text=(checkout/name).read_text(encoding="utf-8")
  if '"/api/v1/agent/training"' not in text:
    text=once(text,'"/api/v1/agent/media/watch"','"/api/v1/agent/media/watch", "/api/v1/agent/training"')
  if '"/api/v1/training-worker"' not in text:
    text=once(text,'"/api/v1/agent/training"','"/api/v1/agent/training", "/api/v1/training-worker"')
  if 'limit = 768 * 1024 if' not in text:
    text=once(text,'limit = MAX_MEDIA_BYTES if','limit = 768 * 1024 if request.url.path == "/api/v1/agent/training" else MAX_MEDIA_BYTES if')
  text=once(text,'  from formosalink.server.media import register as register_media\n',
    '  from formosalink.server.media import register as register_media\n  from formosalink.server.training import attach as attach_training\n  attach_training(app, directory, store, owner, rate)\n')
  result[name]=text
  name="openpilot/sunnypilot/formosalink/agent.py"
  text=(checkout/name).read_text(encoding="utf-8")
  text=once(text,'    start_cameras(directory,stop)\n','    start_cameras(directory,stop)\n    from openpilot.sunnypilot.formosalink.training_upload import start as start_training_upload\n    start_training_upload(directory,stop)\n')
  result[name]=text
  name="openpilot/sunnypilot/formosalink/ui.py"
  text=(checkout/name).read_text(encoding="utf-8")
  text=once(text,'    self._remote.set_enabled(ui_state.is_offroad)\n',
    '    self._remote.set_enabled(ui_state.is_offroad)\n    from openpilot.sunnypilot.formosalink.training_ui import open_training\n    self._training = Button(lambda: {"zh-TW": "訓練授權", "en": "Training data", "ja": "学習データ"}[language()], open_training, button_style=ButtonStyle.NORMAL)\n')
  anchor='      self._close.render(rl.Rectangle(rect.x+rect.width-margin-80*scale, rect.y+8*scale, 80*scale, button_height))\n'
  text=once(text,anchor,anchor+'    self._training._label.set_font_size(15*scale)\n    self._training.render(rl.Rectangle(rect.x+rect.width-margin-205*scale, rect.y+8*scale, 118*scale, 35*scale))\n')
  result[name]=text
  name="formosalink/web/app.js"
  text=(checkout/name).read_text(encoding="utf-8")
  if "import {contributionDialog}" not in text:
    text="import {contributionDialog} from './training-data.js?v=1';\n"+text
  anchor='bottom.append(detail);const revoke='
  addition='bottom.append(detail);const contribute=element("button",({"zh-TW":"訓練資料授權",en:"Training data",ja:"学習データ提供"}[language]),"secondary");contribute.type="button";contribute.addEventListener("click",()=>contributionDialog(device,api,language).catch(e=>notify(e.key||"serverError",true)));bottom.append(contribute);const revoke='
  text=once(text,anchor,addition)
  result[name]=text
  name="launch_env.sh"
  text=(checkout/name).read_text(encoding="utf-8")
  if 'formosalink.training_models manifest-url' not in text:
    text+='\n# A manually selected, verified Studio release takes effect only on the next boot.\nif [ -z "${CARROT_BIG_MODEL_MANIFEST:-}" ]; then\n  studio_manifest="$(python3 -m openpilot.sunnypilot.formosalink.training_models manifest-url 2>/dev/null)"\n  if [ -n "$studio_manifest" ]; then export CARROT_BIG_MODEL_MANIFEST="$studio_manifest"; fi\n  unset studio_manifest\nfi\n'
  result[name]=text
  return {name:text for name,text in result.items() if not (checkout/name).is_file() or (checkout/name).read_text(encoding="utf-8")!=text}


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--checkout",type=Path,required=True)
  parser.add_argument("--write",action="store_true")
  args=parser.parse_args()
  checkout=args.checkout.resolve()
  if not (checkout/".git").exists():
    raise ValueError("target must be an existing git checkout")
  planned=changes(checkout)
  backup=SOURCE/"build/training-studio-integration"/time.strftime("%Y%m%dT%H%M%S")
  if args.write:
    for name in planned:
      path=checkout/name
      if not path.resolve().is_relative_to(checkout):
        raise ValueError("integration path escaped checkout")
      if path.exists():
        saved=backup/name
        saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,saved)
    for name,text in planned.items():
      path=checkout/name
      path.parent.mkdir(parents=True,exist_ok=True)
      path.write_text(text,encoding="utf-8",newline="\n")
  print(json.dumps({"checkout":str(checkout),"written":args.write,"files":list(planned),"backup":str(backup) if args.write else None},ensure_ascii=False))


if __name__=="__main__":
  main()
