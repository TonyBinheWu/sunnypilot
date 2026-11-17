"""Versioned, opt-in driving-data contribution contract; no cabin/audio files."""
import hashlib
import re

POLICY = "alpamayo-n16-driving-v1"
CHUNK_BYTES = 256 * 1024  # base64 + signed envelope stays below the existing IIS 512 KiB request limit
MAX_FILE_BYTES = 1024 * 1024 * 1024
FILES = {"rlog", "rlog.zst", "rlog.bz2", "fcamera.hevc", "ecamera.hevc"}
NOTICE = {
  "zh-TW": "同意將授權後記錄的 rlog 與前向雙鏡頭影片上傳至 FormosaPilot，用於 Alpamayo 教師標註及 N16 模型訓練。資料可能含位置、行車狀態及路人／車牌影像；不收集車內鏡頭或音訊。有網路且停車時自動續傳，可能使用行動數據。可隨時停止未來上傳；已用於訓練的權重無法保證回溯移除。",
  "en": "Contribute future rlog and both front-camera videos to FormosaPilot for Alpamayo labeling and N16 training. Includes location, driving state, people and plates; excludes cabin/audio. Upload resumes while parked with Internet, including cellular. Revoke future uploads anytime; previously trained weights cannot be reliably unlearned.",
  "ja": "同意後の rlog と前方2カメラ映像を Alpamayo ラベル生成・N16 学習に提供します。位置・走行状態・人物・ナンバーを含む場合があります。車内映像・音声は対象外。停車中に携帯回線を含むネット接続で再開します。今後の送信は停止できますが、学習済み重みからの除去は保証できません。",
}


def digest_file(path):
  with path.open("rb") as stream:
    return hashlib.file_digest(stream, "sha256").hexdigest()


def valid_hash(value):
  return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def validate_file(value):
  if not isinstance(value, dict) or set(value) != {"segment", "filename", "sha256", "size", "consent_revision"}:
    raise ValueError("invalid file declaration")
  if not valid_hash(value["segment"]) or not valid_hash(value["sha256"]) or value["filename"] not in FILES:
    raise ValueError("unsupported training file")
  if type(value["size"]) is not int or not 0 < value["size"] <= MAX_FILE_BYTES:
    raise ValueError("invalid training file size")
  if type(value["consent_revision"]) is not int or value["consent_revision"] < 1:
    raise ValueError("invalid consent revision")
  return value
