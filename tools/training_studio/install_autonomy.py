"""Install per-user systemd services; no Codex process or API is involved."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

from tools.training_studio.store import Store


def unit_argument(value):
  value=str(value)
  if any(c in value for c in ('\n','\r','\0')):raise ValueError('invalid systemd argument')
  return '"'+value.replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'


def main():
  parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--port',type=int,default=8890);parser.add_argument('--install-only',action='store_true');args=parser.parse_args()
  if os.name!='posix':raise SystemExit('install inside the configured Linux/WSL workstation')
  store=Store(args.root);workspace=Path(__file__).resolve().parents[2];python=Path(sys.executable).absolute();units=Path.home()/'.config/systemd/user';units.mkdir(parents=True,exist_ok=True)
  config=store.config()
  if not config.get('teacher_adaptation',{}).get('external_supervisor') or not config.get('closed_loop',{}).get('enabled'):raise SystemExit('configure the sealed autonomous loop before installing services')
  commands={
    'formosapilot-studio':[python,'-u','-m','tools.training_studio.server','--root',store.root,'--port',str(args.port),'--no-worker'],
    'formosapilot-worker':[python,'-u','-m','tools.training_studio.engine','worker','--root',store.root],
    'formosapilot-teacher-loop':[python,'-u','-m','tools.training_studio.closed_loop','--root',store.root],
  }
  for name,command in commands.items():
    environment=['Environment=PYTHONUTF8=1','Environment=PYTHONPATH='+str(workspace),'Environment=DISPLAY='+config.get('qualification_display',':0')]
    if Path('/run/WSL/1_interop').exists():environment.append('Environment=WSL_INTEROP=/run/WSL/1_interop')
    body='[Unit]\nDescription='+name+'\nAfter=network-online.target\n\n[Service]\nType=simple\nWorkingDirectory='+str(workspace).replace('%','%%')+'\n'+ '\n'.join(environment)+'\nExecStart='+ ' '.join(unit_argument(v) for v in command)+'\nRestart=on-failure\nRestartSec=5\nTimeoutStopSec=40\nKillMode=control-group\n\n[Install]\nWantedBy=default.target\n'
    if name=='formosapilot-worker':body=body.replace('Restart=on-failure','StandardOutput=append:'+str(store.root/'worker.log')+'\nStandardError=append:'+str(store.root/'worker.log')+'\nRestart=on-failure')
    (units/(name+'.service')).write_text(body)
  subprocess.run(['systemctl','--user','daemon-reload'],check=True)
  subprocess.run(['systemctl','--user','enable',*(name+'.service' for name in commands)],check=True)
  if not args.install_only:subprocess.run(['systemctl','--user','start',*(name+'.service' for name in commands)],check=True)
  print('Installed local services: '+', '.join(commands))


if __name__=='__main__':main()
