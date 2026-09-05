"""Wav2Lip komut sarmalayıcısı ve video oynatma yardımcıları."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
WAV2LIP_DIR = Path(os.environ.get("WAV2LIP_DIR", str(ROOT / "Wav2Lip")))
CHECKPOINT = Path(
    os.environ.get(
        "WAV2LIP_CHECKPOINT",
        str(WAV2LIP_DIR / "checkpoints" / "wav2lip_gan.pth"),
    )
)


def generate(face_image: Path, audio: Path, output: Path) -> Path:
    """Fotoğraf ve ses dosyasından Wav2Lip videosu üretir."""
    inference = WAV2LIP_DIR / "inference.py"
    if not inference.exists():
        raise FileNotFoundError(f"Wav2Lip bulunamadı: {inference}")
    if not CHECKPOINT.exists():
        raise FileNotFoundError(f"Wav2Lip ağırlığı bulunamadı: {CHECKPOINT}")
    if not face_image.exists():
        raise FileNotFoundError(f"Avatar fotoğrafı bulunamadı: {face_image}")
    if not audio.exists():
        raise FileNotFoundError(f"Ses dosyası bulunamadı: {audio}")

    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(inference),
            "--checkpoint_path",
            str(CHECKPOINT),
            "--face",
            str(face_image),
            "--audio",
            str(audio),
            "--outfile",
            str(output),
            "--resize_factor",
            "2",
            "--nosmooth",
        ],
        cwd=str(WAV2LIP_DIR),
        check=True,
    )
    return output


def _find_player() -> str | None:
    """Önce VIDEO_PLAYER değişkenini, sonra Windows/Linux oynatıcılarını dener."""
    configured = os.environ.get("VIDEO_PLAYER")
    if configured:
        return configured

    candidates = ["mpv", "vlc"]
    if os.name == "nt":
        candidates.extend(
            [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ]
        )
    return next((candidate for candidate in candidates if shutil.which(candidate) or Path(candidate).exists()), None)


def play_fullscreen(video: Path) -> None:
    """Videoyu tam ekran oynatır; Windows'ta VLC veya mpv desteklenir."""
    if not video.exists():
        raise FileNotFoundError(f"Üretilecek video bulunamadı: {video}")

    player = _find_player()
    if not player:
        raise FileNotFoundError(
            "Video oynatıcı bulunamadı. VLC veya mpv kurun ya da VIDEO_PLAYER değişkenini ayarlayın."
        )

    if Path(player).stem.lower() == "vlc":
        command = [player, "--fullscreen", "--play-and-exit", "--no-video-title-show", str(video)]
    else:
        command = [player, "--fs", "--really-quiet", "--keep-open=no", str(video)]
    subprocess.run(command, check=False)
