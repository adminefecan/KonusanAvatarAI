#!/usr/bin/env python3
"""First-run photo preparation wizard for the talking avatar project."""
from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk
from rembg import remove

ROOT = Path(__file__).resolve().parent
PHOTO_DIR = ROOT / "foto"
ORIGINAL = PHOTO_DIR / "orijinal.jpg"
PROCESSED = PHOTO_DIR / "islenmis.png"
BACKGROUND = (24, 28, 36)


def prepare_photo(source: str) -> None:
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(source).convert("RGB")
    image.save(ORIGINAL, quality=95)

    cutout = remove(image).convert("RGBA")
    canvas = Image.new("RGB", cutout.size, BACKGROUND)
    canvas.paste(cutout, mask=cutout.getchannel("A"))
    canvas.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
    canvas.save(PROCESSED, "PNG")


def run() -> bool:
    result = {"ok": False}
    root = tk.Tk()
    root.title("Konuşan Avatar - Fotoğraf Kurulumu")
    root.geometry("560x500")
    root.resizable(False, False)

    title = tk.Label(root, text="Avatar fotoğrafını hazırla", font=("Arial", 18, "bold"))
    title.pack(pady=(20, 8))
    status = tk.Label(root, text="Bir JPG veya PNG fotoğraf seçin.", wraplength=500)
    status.pack(pady=8)
    preview = tk.Label(root)
    preview.pack(pady=10)

    def choose():
        path = filedialog.askopenfilename(
            title="Avatar fotoğrafını seç",
            filetypes=[("Resimler", "*.jpg *.jpeg *.png *.webp")],
        )
        if not path:
            return
        try:
            status.config(text="Arka plan kaldırılıyor; ilk çalıştırmada biraz sürebilir...")
            root.update_idletasks()
            prepare_photo(path)
            img = Image.open(PROCESSED)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            preview.image = ImageTk.PhotoImage(img)
            preview.config(image=preview.image)
            status.config(text="Fotoğraf hazır. Ana programı başlatabilirsiniz.")
            result["ok"] = True
        except Exception as exc:
            status.config(text="Fotoğraf işlenemedi.")
            messagebox.showerror("Kurulum hatası", str(exc))

    def close():
        root.destroy()

    tk.Button(root, text="Fotoğrafını Seç", command=choose, width=24, height=2).pack(pady=8)
    tk.Button(root, text="Kapat", command=close, width=24).pack(pady=4)
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()
    return result["ok"]


def main():
    return run()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
