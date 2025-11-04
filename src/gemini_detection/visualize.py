from PIL import Image, ImageDraw
import json
import os


def visualize_bounding_boxes(image_dir, boxes_dir, output_dir=None, show=True):
    """
    Liest gespeicherte Bounding Boxes ein, zeichnet sie auf den jeweiligen Bildern
    und zeigt bzw. speichert die Ergebnisse.

    Parameter:
        image_dir (str): Pfad zum Ordner mit den Originalbildern.
        boxes_dir (str): Pfad zum Ordner mit den gespeicherten *_boxes.json-Dateien.
        output_dir (str, optional): Falls angegeben, werden die visualisierten Bilder gespeichert.
        show (bool): Wenn True, wird das Bild direkt angezeigt.

    Rückgabe:
        dict: {bildname: pfad_zum_visualisierten_bild}
    """
    results = {}
    os.makedirs(output_dir, exist_ok=True) if output_dir else None

    # Alle JSON-Dateien durchlaufen
    for file_name in os.listdir(boxes_dir):
        if not file_name.endswith("_boxes.json"):
            continue

        base_name = file_name.replace("_boxes.json", "")
        image_path = os.path.join(image_dir, f"{base_name}.png")

        if not os.path.exists(image_path):
            print(f"⚠️ Kein passendes Bild gefunden für {file_name}")
            continue

        # JSON-Datei laden
        json_path = os.path.join(boxes_dir, file_name)
        with open(json_path, "r", encoding="utf-8") as f:
            boxes = json.load(f)

        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        # Bounding Boxes einzeichnen
        for box in boxes:
            x1, y1, x2, y2 = box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

        if output_dir:
            output_path = os.path.join(output_dir, f"{base_name}_visualized.png")
            image.save(output_path)
            results[base_name] = output_path
            print(f"💾 Visualisiertes Bild gespeichert unter: {output_path}")

        if show:
            image.show(title=base_name)

    return results
