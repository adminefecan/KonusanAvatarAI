"""Piper text-to-speech wrapper; Windows ve Linux uyumlu."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PIPER_BIN = os.environ.get("PIPER_BIN", "piper")
PIPER_MODEL = Path(os.environ.get("PIPER_MODEL", str(ROOT / "models" / "tr_TR-model.onnx")))


def _piper_command() -> list[str]:
    """Önce piper çalıştırıcısını, yoksa aktif Python modülünü kullanır."""
    configured = os.environ.get("PIPER_BIN")
    if configured:
        return [configured]

    executable = shutil.which("piper")
    if executable:
        return [executable]

    # Windows'ta avatar-env etkinleştirilmemiş olsa bile doğru Python'u kullanır.
    return [sys.executable, "-m", "piper"]


def synthesize(text: str, output_path: Path) -> Path:
    if not PIPER_MODEL.exists():
        raise FileNotFoundError(
            f"Piper modeli bulunamadı: {PIPER_MODEL}. PIPER_MODEL değişkeniyle model yolunu belirtin."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = _piper_command() + [
        "--model",
        str(PIPER_MODEL),
        "--output_file",
        str(output_path),
    ]
    try:
        subprocess.run(
            command,
            input=text,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Piper çalıştırılamadı. avatar-env içinde 'pip install piper-tts' komutunu çalıştırın."
        ) from exc
    return output_path
