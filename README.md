# HEIC to JPG/PNG Converter

Konvertiert HEIC/HEIF-Dateien (z.B. von iPhone) in JPG oder PNG.

## Schnellstart (Windows)

1. **HEIC-Dateien** in den `fotos/` Ordner legen
2. **`run.bat`** doppelklicken
3. Konvertierte Bilder befinden sich in `converted/`

## Konfiguration

Einstellungen in `config.json` anpassen:

```json
{
    "input_folder": "./fotos",
    "output_folder": "./converted",
    "output_format": "jpg",
    "quality": 95,
    "delete_original": false
}
```

| Option | Beschreibung | Werte |
|--------|--------------|-------|
| `input_folder` | Ordner mit HEIC-Dateien | Pfad |
| `output_folder` | Zielordner | Pfad |
| `output_format` | Ausgabeformat | `jpg` oder `png` |
| `quality` | JPG-Qualität | 1-100 |
| `delete_original` | Originale löschen | `true`/`false` |

## Manuelle Installation

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Ausführen
python convert_heic.py
```

## Voraussetzungen

- Python 3.8+
- Windows / Linux / macOS
