import subprocess
from typing import List
from loguru import logger

def check_ollama_and_models(models: List[str]):

    # --- Schritt 1: Prüfen, ob ollama installiert ist ---
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        logger.error("❌ Ollama isn't installed on your machine.")
        logger.error("➡️  Install it here: https://ollama.ai/download")
        return
    except subprocess.CalledProcessError as e:
        logger.error("⚠️ Ollama coudnt be executed correctly:", e)
        return

    # --- Schritt 2: Verfügbare Modelle abrufen ---
    try:
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
        installed_models = [line.split()[0] for line in result.stdout.strip().split("\n")[1:] if line.strip()]
    except Exception as e:
        logger.error("❌ coud't open modellist", e)
        return

    # --- Schritt 3: Prüfen, welche Modelle fehlen ---
    missing = [m for m in models if m not in installed_models]

    if missing:
        logger.error("⚠️ These models are missing:", missing)
        logger.error("➡️ You can install it by executing 'ollama install modelname'.")
    else:
        logger.info("✅ All given models are installed correctly.")