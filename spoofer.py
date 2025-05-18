import os
import random
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import piexif
from datetime import datetime, timedelta

# ===== Obróbka obrazu =====

def adjust_color(image):
    color_factor = random.uniform(1.05, 1.15)  # bardziej kolorowo
    bright_factor = random.uniform(1.00, 1.10)  # częściej jaśniej
    contrast_factor = random.uniform(0.97, 1.05)

    image = ImageEnhance.Color(image).enhance(color_factor)
    image = ImageEnhance.Brightness(image).enhance(bright_factor)
    image = ImageEnhance.Contrast(image).enhance(contrast_factor)
    return image

def crop_edges(image):
    w, h = image.size
    crop_percent = random.uniform(0.01, 0.025)
    return image.crop((int(w * crop_percent), int(h * crop_percent), int(w * (1 - crop_percent)), int(h * (1 - crop_percent))))

def warmify_colors(image):
    r, g, b = image.split()
    r = r.point(lambda i: min(255, i + random.randint(2, 6)))  # cieplej
    b = b.point(lambda i: max(0, i - random.randint(1, 4)))
    return Image.merge('RGB', (r, g, b))

def add_noise(image):
    np_image = np.array(image)
    noise = np.random.normal(0, 1.5, np_image.shape).astype(np.int16)
    np_image = np.clip(np_image + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(np_image)

def slight_blur(image):
    return image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.2, 0.5)))

# ===== EXIF metadane =====

def random_date():
    start = datetime(2015, 1, 1)
    end = datetime(2023, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_time = start + timedelta(days=random_days, seconds=random.randint(0, 86400))
    return random_time.strftime("%Y:%m:%d %H:%M:%S").encode()

def modify_metadata(path):
    try:
        exif_dict = piexif.load(path)
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    make_options = [b"Canon", b"Nikon", b"Fujifilm", b"Leica", b"SONY", b"Panasonic"]
    model_options = [b"Alpha 7", b"D3500", b"X-T3", b"Z50", b"RX100", b"EOS 5D", b""]

    artist_options = [
        b"Anon", b"Shot", b"Not specified", b"StreetCollective", b"Unknown Artist",
        b"Studio XYZ", b"Visual Archive", b"User_013", b"Captured by H.", b"Filmframe.io", b"Studio", b"VisualC", b"User", b"Captured", b"Artist", b""]

    exif_dict["0th"].update({
        piexif.ImageIFD.Make: random.choice(make_options),
        piexif.ImageIFD.Model: random.choice(model_options),
        piexif.ImageIFD.Artist: random.choice(artist_options),
        piexif.ImageIFD.Software: random.choice([b"Adobe Lightroom", b"Capture One", b"spoofer.py", b""]),
        piexif.ImageIFD.ImageDescription: random.choice([
            b"Shot on location", b"Film look", b"AI enhanced", b"", b"Private photo"
        ]),
        piexif.ImageIFD.Copyright: random.choice([
            b"Copyright 2023", b"All rights reserved", b"Free for use", b""
        ]),
        piexif.ImageIFD.XResolution: (300, 1),
        piexif.ImageIFD.YResolution: (300, 1),
    })

    exif_dict["Exif"].update({
        piexif.ExifIFD.DateTimeOriginal: random_date(),
        piexif.ExifIFD.DateTimeDigitized: random_date(),
        piexif.ExifIFD.LensModel: random.choice([
            b"24-70mm f/2.8", b"50mm f/1.8", b"85mm f/1.4", b"35mm f/2", b"18-135mm", b""
        ]),
        piexif.ExifIFD.LensMake: random.choice(make_options),
        piexif.ExifIFD.LensSerialNumber: f"{random.randint(100000,999999)}".encode(),
        piexif.ExifIFD.ExposureTime: (1, random.choice([60, 125, 200, 250, 500])),
        piexif.ExifIFD.FNumber: (random.choice([18, 20, 28, 32]), 10),
        piexif.ExifIFD.ISOSpeedRatings: random.choice([100, 200, 400, 800, 1600]),
        piexif.ExifIFD.ShutterSpeedValue: (random.randint(300, 800), 100),
    })

    # ❌ Usuwamy dane GPS:
    exif_dict["GPS"] = {}

    return piexif.dump(exif_dict)

# ===== Przetwarzanie obrazu =====

def process_image(path, output_dir, num_variants=3, randomize=True):
    name = os.path.basename(path)
    name_no_ext, _ = os.path.splitext(name)
    image_base = Image.open(path).convert('RGB')

    for i in range(1, num_variants + 1):
        image = image_base.copy()

        if randomize:
            image = adjust_color(image)
            image = crop_edges(image)
            image = warmify_colors(image)
            image = add_noise(image)
            image = slight_blur(image)

        exif_bytes = modify_metadata(path)
        output_path = os.path.join(output_dir, f"{name_no_ext}_mod_{i}.jpg")
        image.save(output_path, "JPEG", quality=random.randint(92, 97), exif=exif_bytes)

# ===== GUI Drag & Drop =====

class ImageApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Spoofer")
        self.geometry("420x340")
        self.configure(bg="#f9f9f9")

        label = ttk.Label(self, text="Przeciągnij tutaj pliki JPG lub PNG", font=("Arial", 13))
        label.pack(pady=20)

        ttk.Label(self, text="Ilość wariantów na plik:", font=("Arial", 10)).pack()
        self.variant_entry = ttk.Entry(self)
        self.variant_entry.insert(0, "3")
        self.variant_entry.pack(pady=5)

        self.random_styles_var = tk.BooleanVar(value=True)
        random_check = ttk.Checkbutton(self, text="Generuj losowe style", variable=self.random_styles_var)
        random_check.pack(pady=5)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

        self.status = ttk.Label(self, text="", foreground="green")
        self.status.pack(pady=10)

    def handle_drop(self, event):
        try:
            num_variants = int(self.variant_entry.get())
        except ValueError:
            self.status.config(text="❌ Błąd: wpisz liczbę wariantów.")
            return

        randomize = self.random_styles_var.get()
        files = self.tk.splitlist(event.data)
        output_dir = os.path.join(os.path.dirname(files[0]), "zmodyfikowane")
        os.makedirs(output_dir, exist_ok=True)
        count = 0
        for file_path in files:
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    process_image(file_path, output_dir, num_variants=num_variants, randomize=randomize)
                    count += 1
                except Exception as e:
                    print(f"Błąd przetwarzania {file_path}: {e}")
        self.status.config(text=f"✔ Przetworzono {count} plików × {num_variants} wariantów. Folder: zmodyfikowane")

# ===== Start aplikacji =====

if __name__ == "__main__":
    app = ImageApp()
    app.mainloop()
