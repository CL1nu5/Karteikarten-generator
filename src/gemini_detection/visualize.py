from PIL import Image, ImageDraw
import json
import os


def visualize_bounding_boxes(image_dir, boxes_dir, output_dir=None, show=True):
    """
    Draws bounding boxes on images based on JSON detection files.
    Optionally saves and/or displays the visualized images.
    """
    results = {}
    os.makedirs(output_dir, exist_ok=True) if output_dir else None

    # Iterate through all JSON detection files
    for file_name in os.listdir(boxes_dir):
        if not file_name.endswith("_boxes.json"):
            continue

        base_name = file_name.replace("_boxes.json", "")
        image_path = os.path.join(image_dir, f"{base_name}.png")

        print(f"Lade Bild: {image_path}")
        if not os.path.exists(image_path):
            print(f"⚠️ Kein passendes Bild gefunden für {file_name}")
            continue

        # Load bounding boxes from JSON
        json_path = os.path.join(boxes_dir, file_name)
        with open(json_path, "r", encoding="utf-8") as f:
            boxes = json.load(f)

        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        # Draw each bounding box
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
