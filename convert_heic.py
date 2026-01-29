#!/usr/bin/env python3
"""
HEIC to JPG/PNG Converter
Konvertiert alle HEIC-Dateien in einem Ordner basierend auf config.json
"""

import json
import sys
from pathlib import Path

try:
    from PIL import Image
    import pillow_heif
except ImportError:
    print("Fehlende Abhängigkeiten. Bitte installieren:")
    print("  pip install pillow pillow-heif")
    sys.exit(1)

# HEIF-Unterstützung für Pillow registrieren
pillow_heif.register_heif_opener()


def load_config(config_path: str = "config.json") -> dict:
    """Lädt die Konfiguration aus der JSON-Datei."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_heic(input_path: Path, output_path: Path, output_format: str, quality: int):
    """Konvertiert eine einzelne HEIC-Datei."""
    with Image.open(input_path) as img:
        # RGB-Konvertierung für JPG (kein Alpha-Kanal)
        if output_format.lower() == "jpg" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        save_kwargs = {}
        if output_format.lower() in ("jpg", "jpeg"):
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif output_format.lower() == "png":
            save_kwargs["optimize"] = True

        img.save(output_path, **save_kwargs)


def main():
    # Konfiguration laden
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.json"

    if not config_path.exists():
        print(f"Fehler: {config_path} nicht gefunden!")
        sys.exit(1)

    config = load_config(config_path)

    # Pfade aus Config
    input_folder = Path(config.get("input_folder", "./fotos"))
    output_folder = Path(config.get("output_folder", "./converted"))
    output_format = config.get("output_format", "jpg").lower()
    quality = config.get("quality", 95)
    delete_original = config.get("delete_original", False)

    # Relative Pfade zum Script-Verzeichnis
    if not input_folder.is_absolute():
        input_folder = script_dir / input_folder
    if not output_folder.is_absolute():
        output_folder = script_dir / output_folder

    # Ordner erstellen falls nötig
    input_folder.mkdir(parents=True, exist_ok=True)
    output_folder.mkdir(parents=True, exist_ok=True)

    # HEIC-Dateien finden (case-insensitive)
    heic_files = list(input_folder.glob("*.heic")) + list(input_folder.glob("*.HEIC"))
    heic_files += list(input_folder.glob("*.heif")) + list(input_folder.glob("*.HEIF"))

    if not heic_files:
        print(f"Keine HEIC/HEIF-Dateien in '{input_folder}' gefunden.")
        sys.exit(0)

    print(f"Gefunden: {len(heic_files)} HEIC/HEIF-Datei(en)")
    print(f"Zielformat: {output_format.upper()}")
    print(f"Ausgabeordner: {output_folder}")
    print("-" * 40)

    converted = 0
    errors = 0

    for heic_file in heic_files:
        output_name = heic_file.stem + "." + output_format
        output_path = output_folder / output_name

        try:
            print(f"Konvertiere: {heic_file.name} -> {output_name}")
            convert_heic(heic_file, output_path, output_format, quality)
            converted += 1

            if delete_original:
                heic_file.unlink()
                print(f"  Original gelöscht: {heic_file.name}")

        except Exception as e:
            print(f"  Fehler bei {heic_file.name}: {e}")
            errors += 1

    print("-" * 40)
    print(f"Fertig! {converted} konvertiert, {errors} Fehler")


if __name__ == "__main__":
    main()
