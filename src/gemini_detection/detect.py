from google import genai
from google.genai import types
from google.genai.errors import ServerError

from PIL import Image
import json
import os
from loguru import logger
from dotenv import load_dotenv
from util.config_reader import ConfigLoader


def detect_logical_blocks_with_gemini(image_paths: list[str], output_dir: str, config_loader: ConfigLoader, test_mode=False):

    load_dotenv()
    client = genai.Client()
    
    prompt = (
        """ Detect and label all distinct logical content regions in the image, such as handwritten text blocks, printed text boxes, images, tables, diagrams, or formulas.
            For each detected region, return its bounding box coordinates as [ymin, xmin, ymax, xmax], normalized to a 0–1000 scale.

            Ensure that:
            -   Each bounding box tightly encloses its corresponding content region.
            -   Overlapping or nested boxes are avoided unless clearly separate content types exist (e.g., an image inside a text block).
            -   Ignore irrelevant margins, decorations, or background noise.
            -   Use consistent scaling across the entire image."""
    )

    os.makedirs(output_dir, exist_ok=True)
    results = {}

    if test_mode:
        image_paths = image_paths[:3]
        logger.info("🔍 Testmodus aktiviert – analysiere nur ersten 3 Bilder.")

    for image_path in image_paths:
        logger.info(f"Analysiere Bild: {image_path}")
        image = Image.open(image_path)

        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )

        response = None
        models = config_loader.to_dict().get("CHAT_MODELS_GEMINI_MODELS", [])
        index = 0

        while response is None and index < len(models):
            try:
                # Anfrage an Gemini senden
                response = client.models.generate_content(
                    model=models[index],
                    contents=[image, prompt],
                    config=config
                )
            except ServerError as e:
                logger.warning(f"⚠️ Fehler bei Modell {models[index]}: {e}")
                index += 1
        
        if response is None:
            logger.error(f"❌ Alle Modelle fehlgeschlagen für Bild {image_path}. Überspringe...")
            continue

        # Bounding Boxes auslesen
        try:
            bounding_boxes = json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning(f"⚠️ JSON konnte für {image_path} nicht dekodiert werden.")
            bounding_boxes = []

        width, height = image.size
        converted_bounding_boxes = []

        for bbox in bounding_boxes:
            abs_y1 = int(bbox["box_2d"][0] / 1000 * height)
            abs_x1 = int(bbox["box_2d"][1] / 1000 * width)
            abs_y2 = int(bbox["box_2d"][2] / 1000 * height)
            abs_x2 = int(bbox["box_2d"][3] / 1000 * width)
            converted_bounding_boxes.append([abs_x1, abs_y1, abs_x2, abs_y2])

        # Ergebnisse speichern
        base_name = os.path.basename(image_path)
        output_file = os.path.join(output_dir, f"{os.path.splitext(base_name)[0]}_boxes.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(converted_bounding_boxes, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Ergebnisse gespeichert in: {output_file}")
        results[base_name] = converted_bounding_boxes

    return results
