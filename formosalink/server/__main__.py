import argparse
import os
from pathlib import Path
from copy import deepcopy

import uvicorn

from formosalink.server.app import create_app
from openpilot.sunnypilot.formosalink.remote_web_protocol import MAX_MESSAGE


def main():
  parser = argparse.ArgumentParser(description="FormosaLink (one worker; bind loopback behind IIS)")
  parser.add_argument("--data-dir", default=os.environ.get("FORMOSALINK_DATA_DIR"), required=not os.environ.get("FORMOSALINK_DATA_DIR"))
  parser.add_argument("--port", type=int, default=8765)
  parser.add_argument("--log-file", type=Path, help="Rotating log file inside the protected data directory")
  args = parser.parse_args()
  log_config = deepcopy(uvicorn.config.LOGGING_CONFIG)
  if args.log_file:
    log_file = args.log_file.resolve()
    if not log_file.is_relative_to(Path(args.data_dir).resolve()):
      parser.error("log file must be inside the data directory")
    log_config["handlers"]["file"] = {"class":"logging.handlers.RotatingFileHandler", "filename":str(log_file),
                                       "maxBytes":1048576, "backupCount":3, "encoding":"utf-8", "formatter":"default"}
    for logger in log_config["loggers"].values():
      if logger.get("handlers"):
        logger["handlers"] = ["file"]
  uvicorn.run(create_app(args.data_dir), host="127.0.0.1", port=args.port, workers=1,
              access_log=False, proxy_headers=False, ws_max_size=MAX_MESSAGE, ws_max_queue=1,
              ws_per_message_deflate=False, log_config=log_config)


if __name__ == "__main__":
  main()
