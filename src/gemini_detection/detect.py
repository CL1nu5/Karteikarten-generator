from google import genai
from google.genai import types
from PIL import Image
import json
import os
from dotenv import load_dotenv


def detect_logical_blocks_with_gemini(image_paths, output_dir, test_mode=False):
    """
    Führt Object Detection auf einer Liste von Bildern durch, um logische Blöcke zu erkennen.
    Ergebnisse (Bounding Boxes) werden als JSON im Output-Ordner gespeichert.

    Parameter:
        image_paths (list[str]): Liste der Pfade zu den Bildern.
        output_dir (str): Pfad, in dem die Bounding Box-Ergebnisse gespeichert werden sollen.
        test_mode (bool): Wenn True, wird nur das erste Bild analysiert (für Testzwecke).

    Rückgabe:
        dict: Ein Dictionary {bildname: bounding_boxes}
              bounding_boxes = Liste von [x1, y1, x2, y2] (absolute Pixelkoordinaten)
    """
    load_dotenv()
    client = genai.Client()
    prompt = (
        "Detect all prominent logical content blocks (e.g., text boxes, images, tables, etc.) "
        "in the image. The box_2d should be [ymin, xmin, ymax, xmax] normalized to 0-1000."
    )

    os.makedirs(output_dir, exist_ok=True)
    results = {}

    if test_mode:
        image_paths = image_paths[:3]
        print("🔍 Testmodus aktiviert – analysiere nur ersten 3 Bilder.")

    for image_path in image_paths:
        print(f"Analysiere Bild: {image_path}")
        image = Image.open(image_path)

        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )

        # Anfrage an Gemini senden
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, prompt],
            config=config
        )

        # Bounding Boxes auslesen
        try:
            bounding_boxes = json.loads(response.text)
        except json.JSONDecodeError:
            print(f"⚠️ JSON konnte für {image_path} nicht dekodiert werden.")
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

        print(f"💾 Ergebnisse gespeichert in: {output_file}")
        results[base_name] = converted_bounding_boxes

    return results
