#!/usr/bin/env python3
"""
HEIC to JPG/PNG Converter - GUI
Grafische Oberfläche für den HEIC-Konverter
"""

import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

try:
    from PIL import Image
    import pillow_heif
except ImportError:
    import sys
    messagebox.showerror(
        "Fehlende Abhängigkeiten",
        "Bitte installieren:\n  pip install pillow pillow-heif"
    )
    sys.exit(1)

pillow_heif.register_heif_opener()

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.json"


def load_config() -> dict:
    defaults = {
        "input_folder": "./fotos",
        "output_folder": "./converted",
        "output_format": "jpg",
        "quality": 95,
        "delete_original": False,
    }
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            defaults.update(json.load(f))
    return defaults


def save_config(config: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = SCRIPT_DIR / p
    return p.resolve()


def find_heic_files(folder: Path) -> list[Path]:
    files = []
    for ext in ("*.heic", "*.HEIC", "*.heif", "*.HEIF"):
        files.extend(folder.glob(ext))
    return files


def convert_heic(input_path: Path, output_path: Path, output_format: str, quality: int):
    with Image.open(input_path) as img:
        if output_format.lower() == "jpg" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        save_kwargs = {}
        if output_format.lower() in ("jpg", "jpeg"):
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif output_format.lower() == "png":
            save_kwargs["optimize"] = True
        img.save(output_path, **save_kwargs)


class ConverterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HEIC to JPG/PNG Converter")
        self.root.resizable(False, False)
        self.converting = False

        config = load_config()

        # --- Variablen ---
        self.input_var = tk.StringVar(value=str(resolve_path(config["input_folder"])))
        self.output_var = tk.StringVar(value=str(resolve_path(config["output_folder"])))
        self.format_var = tk.StringVar(value=config["output_format"].upper())
        self.quality_var = tk.IntVar(value=config["quality"])
        self.delete_var = tk.BooleanVar(value=config["delete_original"])

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---- UI aufbauen ----
    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # == Ordner ==
        folder_frame = ttk.LabelFrame(self.root, text="Ordner", padding=10)
        folder_frame.pack(fill="x", **pad)

        ttk.Label(folder_frame, text="Eingabe:").grid(row=0, column=0, sticky="w")
        ttk.Entry(folder_frame, textvariable=self.input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(folder_frame, text="...", width=3, command=self._browse_input).grid(row=0, column=2)

        ttk.Label(folder_frame, text="Ausgabe:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        ttk.Entry(folder_frame, textvariable=self.output_var, width=50).grid(row=1, column=1, padx=5, pady=(5, 0))
        ttk.Button(folder_frame, text="...", width=3, command=self._browse_output).grid(row=1, column=2, pady=(5, 0))

        # == Einstellungen ==
        settings_frame = ttk.LabelFrame(self.root, text="Einstellungen", padding=10)
        settings_frame.pack(fill="x", **pad)

        ttk.Label(settings_frame, text="Format:").grid(row=0, column=0, sticky="w")
        fmt_combo = ttk.Combobox(
            settings_frame, textvariable=self.format_var,
            values=["JPG", "PNG"], state="readonly", width=8
        )
        fmt_combo.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(settings_frame, text="Qualität (JPG):").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.quality_label = ttk.Label(settings_frame, text=str(self.quality_var.get()))
        self.quality_label.grid(row=0, column=4, sticky="w", padx=(5, 0))
        quality_scale = ttk.Scale(
            settings_frame, from_=10, to=100, variable=self.quality_var,
            orient="horizontal", length=150,
            command=lambda v: self.quality_label.config(text=str(int(float(v))))
        )
        quality_scale.grid(row=0, column=3, padx=5)

        ttk.Checkbutton(
            settings_frame, text="Originale nach Konvertierung löschen",
            variable=self.delete_var
        ).grid(row=1, column=0, columnspan=5, sticky="w", pady=(5, 0))

        # == Fortschritt ==
        progress_frame = ttk.LabelFrame(self.root, text="Fortschritt", padding=10)
        progress_frame.pack(fill="x", **pad)

        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate", length=400)
        self.progress_bar.pack(fill="x")

        self.status_label = ttk.Label(progress_frame, text="Bereit.", anchor="w")
        self.status_label.pack(fill="x", pady=(5, 0))

        # == Buttons ==
        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.start_btn = ttk.Button(btn_frame, text="Konvertierung starten", command=self._start)
        self.start_btn.pack(side="right")

    # ---- Ordner wählen ----
    def _browse_input(self):
        folder = filedialog.askdirectory(
            title="Eingabeordner wählen",
            initialdir=self.input_var.get()
        )
        if folder:
            self.input_var.set(folder)

    def _browse_output(self):
        folder = filedialog.askdirectory(
            title="Ausgabeordner wählen",
            initialdir=self.output_var.get()
        )
        if folder:
            self.output_var.set(folder)

    # ---- Konvertierung ----
    def _start(self):
        if self.converting:
            return

        input_folder = Path(self.input_var.get())
        output_folder = Path(self.output_var.get())

        if not input_folder.exists():
            messagebox.showerror("Fehler", f"Eingabeordner existiert nicht:\n{input_folder}")
            return

        heic_files = find_heic_files(input_folder)
        if not heic_files:
            messagebox.showinfo("Hinweis", "Keine HEIC/HEIF-Dateien im Eingabeordner gefunden.")
            return

        output_folder.mkdir(parents=True, exist_ok=True)

        # Config speichern
        save_config({
            "input_folder": str(input_folder),
            "output_folder": str(output_folder),
            "output_format": self.format_var.get().lower(),
            "quality": self.quality_var.get(),
            "delete_original": self.delete_var.get(),
        })

        self.converting = True
        self.start_btn.config(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(heic_files)

        thread = threading.Thread(
            target=self._convert_worker,
            args=(heic_files, output_folder, self.format_var.get().lower(), self.quality_var.get(), self.delete_var.get()),
            daemon=True,
        )
        thread.start()

    def _convert_worker(self, files, output_folder, fmt, quality, delete):
        converted = 0
        errors = 0
        total = len(files)

        for i, heic_file in enumerate(files, 1):
            output_name = heic_file.stem + "." + fmt
            output_path = output_folder / output_name

            self.root.after(0, self._update_status, f"[{i}/{total}] {heic_file.name}")

            try:
                convert_heic(heic_file, output_path, fmt, quality)
                converted += 1
                if delete:
                    heic_file.unlink()
            except Exception as e:
                errors += 1
                self.root.after(0, self._update_status, f"Fehler: {heic_file.name} - {e}")

            self.root.after(0, self._update_progress, i)

        self.root.after(0, self._done, converted, errors)

    def _update_status(self, text):
        self.status_label.config(text=text)

    def _update_progress(self, value):
        self.progress_bar["value"] = value

    def _done(self, converted, errors):
        self.converting = False
        self.start_btn.config(state="normal")
        msg = f"Fertig! {converted} konvertiert"
        if errors:
            msg += f", {errors} Fehler"
        self.status_label.config(text=msg)
        messagebox.showinfo("Abgeschlossen", msg)

    def _on_close(self):
        if self.converting:
            if not messagebox.askokcancel("Beenden", "Konvertierung läuft noch. Wirklich beenden?"):
                return
        self.root.destroy()


def main():
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
