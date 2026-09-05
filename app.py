"""Windows masaüstü avatar uygulaması: VLC yerine Tkinter penceresinde video oynatır."""
from pathlib import Path
import threading
import time
import traceback
import tkinter as tk
from tkinter import messagebox

try:
    import winsound
except ImportError:
    winsound = None

import cv2
from PIL import Image, ImageTk

import llm
import lipsync
import stt
import tts

ROOT = Path(__file__).resolve().parent
PHOTO = ROOT / "foto" / "islenmis.png"
SESSIONS = ROOT / "sesler"
VIDEOS = ROOT / "videolar"


class AvatarApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Konuşan Avatar")
        self.root.geometry("900x700")
        self.root.configure(bg="#111827")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.running = False
        self.closed = False
        self.video_capture = None
        self.video_path = None
        self.video_done = threading.Event()

        self.video_label = tk.Label(root, bg="#111827")
        self.video_label.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        self.status = tk.StringVar(value="Başlamak için butona basın.")
        tk.Label(root, textvariable=self.status, fg="white", bg="#111827", font=("Segoe UI", 12)).pack(pady=4)
        self.start_button = tk.Button(
            root, text="Konuşmayı Başlat", command=self.start,
            font=("Segoe UI", 12, "bold"), width=22, height=2,
        )
        self.start_button.pack(pady=(4, 16))

        if PHOTO.exists():
            self.show_still(PHOTO)
        else:
            self.status.set("Fotoğraf hazırlanmadı. Önce setup.py çalıştırın.")

    def show_still(self, path: Path):
        image = cv2.imread(str(path))
        if image is None:
            return
        self._show_frame(image)

    def _show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        image.thumbnail((850, 580), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.video_label.configure(image=photo)
        self.video_label.image = photo

    def start(self):
        if self.running:
            return
        if not PHOTO.exists():
            messagebox.showwarning("Fotoğraf eksik", "Önce setup.py ile fotoğrafınızı hazırlayın.")
            return
        self.running = True
        self.start_button.configure(state="disabled", text="Dinliyor...")
        threading.Thread(target=self.conversation_loop, daemon=True).start()

    def conversation_loop(self):
        while self.running and not self.closed:
            try:
                self.set_status("Dinliyorum... 3 saniye konuşun.")
                audio_in = stt.record_wav(seconds=3)
                text = stt.transcribe(audio_in)
                try:
                    audio_in.unlink(missing_ok=True)
                except OSError:
                    pass
                if not text:
                    self.set_status("Konuşma algılanmadı; tekrar dinliyorum.")
                    continue
                self.set_status(f"Siz: {text}")
                response = llm.answer(text)
                if not response:
                    continue
                self.set_status(f"Avatar: {response}")
                stamp = time.strftime("%Y%m%d-%H%M%S")
                audio_out = SESSIONS / f"cevap-{stamp}.wav"
                video_out = VIDEOS / f"avatar-{stamp}.mp4"
                tts.synthesize(response, audio_out)
                self.set_status("Ağız hareketi hazırlanıyor...")
                lipsync.generate(PHOTO, audio_out, video_out)
                self.video_done.clear()
                self.root.after(0, lambda p=video_out, a=audio_out: self.play_video(p, a))
                while self.running and not self.closed and not self.video_done.wait(0.1):
                    pass
            except Exception as exc:
                traceback.print_exc()
                self.set_status(f"Hata: {exc}")
                time.sleep(2)

    def play_video(self, path: Path, audio_path: Path):
        if self.video_capture is not None:
            self.video_capture.release()
        self.video_path = path
        self.video_capture = cv2.VideoCapture(str(path))
        if winsound is not None and audio_path.exists():
            winsound.PlaySound(
                str(audio_path),
                winsound.SND_FILENAME | winsound.SND_ASYNC,
            )
        self._next_frame()

    def _next_frame(self):
        if not self.video_capture or not self.running or self.closed:
            return
        ok, frame = self.video_capture.read()
        if not ok:
            self.video_capture.release()
            self.video_capture = None
            if winsound is not None:
                winsound.PlaySound(None, winsound.SND_PURGE)
            self.video_done.set()
            return
        self._show_frame(frame)
        fps = self.video_capture.get(cv2.CAP_PROP_FPS) or 25
        self.root.after(max(1, int(1000 / fps)), self._next_frame)

    def set_status(self, text: str):
        if not self.closed:
            self.root.after(0, lambda: self.status.set(text))

    def close(self):
        self.closed = True
        self.running = False
        if self.video_capture is not None:
            self.video_capture.release()
        if winsound is not None:
            winsound.PlaySound(None, winsound.SND_PURGE)
        self.video_done.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    AvatarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
