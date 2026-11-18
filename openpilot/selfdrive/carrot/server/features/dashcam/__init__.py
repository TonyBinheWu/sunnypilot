from .routes import register as register_dashcam
from ...services.driving_sei import api_dashcam_sei


def register(app) -> None:
  # Replay is client-computed. The device exposes only the read-only source
  # routes registered by routes.py; legacy rlog scan/query handlers stay off.
  # SEI is a bounded video-packet index and never scans full driving logs.
  register_dashcam(app)
  app.router.add_get('/api/dashcam/sei/{segment}', api_dashcam_sei)

__all__ = ["register"]
