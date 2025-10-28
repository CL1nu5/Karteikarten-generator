import subprocess
from typing import List
from loguru import logger

def check_ollama_and_models(models: List[str]):

    # --- Schritt 1: Prüfen, ob ollama installiert ist ---
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        logger.error("❌ Ollama ist NICHT installiert.")
        logger.error("➡️  Installiere es über: https://ollama.ai/download")
        return
    except subprocess.CalledProcessError as e:
        logger.error("⚠️  Ollama konnte nicht korrekt ausgeführt werden:", e)
        return

    # --- Schritt 2: Verfügbare Modelle abrufen ---
    try:
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
        installed_models = [line.split()[0] for line in result.stdout.strip().split("\n")[1:] if line.strip()]
    except Exception as e:
        logger.error("❌ Konnte Modellliste nicht abrufen:", e)
        return

    # --- Schritt 3: Prüfen, welche Modelle fehlen ---
    missing = [m for m in models if m not in installed_models]

    if missing:
        logger.error("⚠️  Diese Modelle fehlen:", missing)
        logger.error("➡️  Du kannst sie mit z. B. `ollama pull modelname` installieren.")
    else:
        logger.info("✅ Alle angegebenen Modelle und ollama sind korrekt installiert.")