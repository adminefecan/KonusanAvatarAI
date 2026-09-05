#!/usr/bin/env python3
"""Windows/Linux uyumlu sürekli mikrofon -> STT -> LLM -> TTS -> lip-sync döngüsü."""
from pathlib import Path
import subprocess
import sys
import time
import traceback

import llm
import lipsync
import stt
import tts

ROOT = Path(__file__).resolve().parent
PHOTO = ROOT / "foto" / "islenmis.png"
SESSIONS = ROOT / "sesler"
VIDEOS = ROOT / "videolar"
SETUP_SCRIPT = ROOT / "setup.py"


def ensure_directories() -> None:
    """Gerekli çıktı klasörlerini oluşturur."""
    for folder in (PHOTO.parent, SESSIONS, VIDEOS):
        folder.mkdir(parents=True, exist_ok=True)


def ensure_photo() -> None:
    """İşlenmiş fotoğraf yoksa setup.py'yi mevcut Python ile çalıştırır."""
    ensure_directories()
    if PHOTO.exists():
        return

    result = subprocess.run(
        [sys.executable, str(SETUP_SCRIPT)],
        cwd=str(ROOT),
        check=False,
    )
    if result.returncode != 0 or not PHOTO.exists():
        raise RuntimeError("Fotoğraf kurulumu tamamlanmadı veya fotoğraf seçilmedi.")


def run_once() -> None:
    print("Dinliyorum...", flush=True)
    audio_in = stt.record_wav(seconds=5)
    try:
        text = stt.transcribe(audio_in)
    finally:
        # Geçici mikrofon kaydını işlemden sonra silmeye çalışır.
        try:
            audio_in.unlink(missing_ok=True)
        except OSError:
            pass

    if not text:
        print("Konuşma algılanmadı.", flush=True)
        return

    print(f"Siz: {text}", flush=True)
    response = llm.answer(text)
    if not response:
        print("Model boş cevap verdi.", flush=True)
        return

    print(f"Avatar: {response}", flush=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    audio_out = SESSIONS / f"cevap-{stamp}.wav"
    video_out = VIDEOS / f"avatar-{stamp}.mp4"
    tts.synthesize(response, audio_out)
    lipsync.generate(PHOTO, audio_out, video_out)
    lipsync.play_fullscreen(video_out)


def main() -> None:
    ensure_photo()
    print("Konuşan avatar hazır. Çıkmak için Ctrl+C kullanın.", flush=True)
    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            print("\nProgram kapatıldı.", flush=True)
            break
        except Exception as exc:
            print(f"Bu turda hata oluştu: {exc}", flush=True)
            traceback.print_exc()
            print("Bir sonraki dinleme turuna geçiliyor...", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main()
