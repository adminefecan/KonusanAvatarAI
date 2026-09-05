"""Microphone recording and Whisper transcription."""
from pathlib import Path
import tempfile
import wave

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel("small", device="cpu", compute_type="int8")
    return _MODEL


def record_wav(seconds: int = 5, sample_rate: int = 16000) -> Path:
    audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    path = Path(tempfile.mkstemp(prefix="avatar_record_", suffix=".wav", dir=ROOT / "sesler")[1])
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(np.asarray(audio).tobytes())
    return path


def transcribe(audio_path: Path, language: str = "tr") -> str:
    segments, _ = _model().transcribe(
        str(audio_path),
        language="tr",
        task="transcribe",
        vad_filter=True,
        beam_size=5,
        condition_on_previous_text=False,
        temperature=0.0,
        initial_prompt=(
            "Bu Türkçe bir günlük konuşmadır. Türkçe karakterleri doğru yaz: "
            "ç, ğ, ı, İ, ö, ş, ü. Harflerin adını yazma; söylenen kelimeyi yaz."
        ),
    )
    return " ".join(segment.text.strip() for segment in segments).strip()
