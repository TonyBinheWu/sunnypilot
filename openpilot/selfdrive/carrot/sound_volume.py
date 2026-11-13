"""Independent navigation voice gain; other alerts keep their existing gains."""

NAVIGATION_VOICE_FILES = frozenset({"audio_turn.wav", "audio_speed_down.wav", *(f"audio_{i}.wav" for i in range(1, 11))})


def read_voice_volume(params) -> float:
  try:
    return max(5, min(300, int(params.get("SoundLanguageVolume", return_default=True)))) / 100.0
  except (ValueError, TypeError, KeyError, OverflowError, OSError):
    return 1.0
