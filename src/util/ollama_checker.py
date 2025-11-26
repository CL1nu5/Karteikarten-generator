import subprocess
from typing import List
from loguru import logger

def check_ollama_and_models(models: List[str]):
    """
    Verifies that Ollama is installed and the required models are available.
    Logs errors or instructions if requirements are missing.
    """

    # --- Step 1: Check if Ollama is installed ---
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        logger.error("❌ Ollama isn't installed on your machine.")
        logger.error("➡️  Install it here: https://ollama.ai/download")
        return
    except subprocess.CalledProcessError as e:
        logger.error("⚠️ Ollama coudnt be executed correctly:", e)
        return

    # --- Step 2: Retrieve available models ---
    try:
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, text=True)
        installed_models = [line.split()[0] for line in result.stdout.strip().split("\n")[1:] if line.strip()]
    except Exception as e:
        logger.error("❌ coud't open modellist", e)
        return

    # --- Step 3: Identify missing models ---
    missing = [m for m in models if m not in installed_models]

    if missing:
        logger.error("⚠️ These models are missing:", missing)
        logger.error("➡️ You can install it by executing 'ollama install modelname'.")
    else:
        logger.info("✅ All given models are installed correctly.")