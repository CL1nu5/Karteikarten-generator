import cv2
import layoutparser as lp
import os
import requests
from pathlib import Path

def chunk_images(image_paths: list, output_folder: str):
    os.makedirs(output_folder, exist_ok=True)

    # Create a local directory for models
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    config_path = model_dir / "config.yml"
    model_path = model_dir / "model_final.pth"
    
    # Download if not exists
    if not config_path.exists():
        print("📥 Downloading config...")
        r = requests.get("https://www.dropbox.com/s/u9wbsfwz4y0ziki/config.yml?dl=1")
        config_path.write_bytes(r.content)
        print(f"✅ Config saved to: {config_path}")
    
    if not model_path.exists():
        print("📥 Downloading model (this may take a while)...")
        r = requests.get("https://www.dropbox.com/s/dgy9c10wykk4lq4/model_final.pth?dl=1", stream=True)
        with open(model_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Model saved to: {model_path}")
    
    # Lower the confidence threshold to detect more regions
    model = lp.Detectron2LayoutModel(
        config_path=str(config_path),
        model_path=str(model_path),
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.3],  # Lowered from 0.5 to 0.3
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
    )

    print("✅ Model loaded successfully!")

    for page_num, img_path in enumerate(image_paths):
        image_cv = cv2.imread(img_path)
        if image_cv is None:
            print(f"⚠️ Bild konnte nicht geladen werden: {img_path}")
            continue

        layout = model.detect(image_cv)
        
        # Filter out very large blocks that are likely the whole page
        height, width = image_cv.shape[:2]
        page_area = height * width
        
        filtered_layout = []
        for block in layout:
            x_1, y_1, x_2, y_2 = block.coordinates
            block_area = (x_2 - x_1) * (y_2 - y_1)
            # Skip blocks that cover more than 80% of the page
            if block_area < 0.8 * page_area:
                filtered_layout.append(block)
            else:
                print(f"  ⚠️ Skipping block covering {block_area/page_area*100:.1f}% of page")

        page_folder = os.path.join(output_folder, f"page_{page_num+1:03d}")
        os.makedirs(page_folder, exist_ok=True)

        # Sort blocks by vertical position (top to bottom)
        filtered_layout = sorted(filtered_layout, key=lambda b: b.coordinates[1])

        for i, block in enumerate(filtered_layout):
            x_1, y_1, x_2, y_2 = map(int, block.coordinates)
            crop = image_cv[y_1:y_2, x_1:x_2]
            chunk_path = os.path.join(page_folder, f"{block.type}_{i+1:02d}.png")
            cv2.imwrite(chunk_path, crop)

        print(f"✅ Seite {page_num+1} -> {len(filtered_layout)} Chunks gespeichert (von {len(layout)} erkannt).")