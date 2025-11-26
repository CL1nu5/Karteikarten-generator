# Karteikarten Generator

Ein Tool zur automatischen Extraktion von logischen Blöcken (Text, Bilder, Tabellen) aus PDF-Dokumenten mithilfe von Google Gemini und Ollama.

## Voraussetzungen

Bevor du startest, stelle sicher, dass du folgende Tools installiert hast:

- **Python 3.10+**
- **Ollama**: [Download hier](https://ollama.ai/download). Stelle sicher, dass die Modelle `gemma3:12b` und `gpt-oss:20b` (oder die in der Config definierten) installiert sind.
- **Google Gemini API Key**: Du benötigst einen API Key von Google AI Studio.

## Installation

1.  **Repository klonen:**
    ```bash
    git clone <repository-url>
    cd karteikarten-gen
    ```

2.  **Virtuelle Umgebung erstellen und aktivieren:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Mac/Linux
    # .venv\Scripts\activate  # Windows
    ```

3.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    # Oder falls du uv nutzt:
    uv sync
    ```

4.  **Umgebungsvariablen setzen:**
    Erstelle eine `.env` Datei im Hauptverzeichnis und füge deine API Keys hinzu:
    ```env
    GEMINI_API_KEY=dein_gemini_api_key
    OLLAMA_API_KEY=optional_falls_benötigt
    ```

## Nutzung

1.  Lege deine PDF-Dateien in den Ordner `data/to_process/`.
2.  Starte das Skript:
    ```bash
    python src/main.py
    ```
3.  Die Ergebnisse findest du in:
    -   `data/processed/`: Die in Bilder konvertierten PDF-Seiten.
    -   `data/detections/`: Die erkannten Bounding Boxes als JSON.
    -   `data/visualizations/`: Visualisierung der erkannten Blöcke auf den Bildern.

## Konfiguration

Die Konfiguration erfolgt über `config/config.toml`. Hier kannst du Modelle, Pfade und Caching-Einstellungen anpassen.

```toml
[PROCESS_SETTINGS]
CACHE_PDF_TO_IMAGE_CREATION = true # Aktiviert Caching für PDF-Konvertierung

[CHAT_MODELS]
MODELS = ["gemma3:12b", "gpt-oss:20b"] # Ollama Modelle
GEMINI_MODELS = ["gemini-2.5-pro", ...] # Gemini Modelle
```
