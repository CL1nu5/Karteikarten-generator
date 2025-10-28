import os
import cv2
import torch
import numpy as np
from pathlib import Path
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

_sam_cache = None
_mask_generator_cache = None


def get_sam_model(device=None):
    """Lädt das SAM-Modell einmalig und cached es."""
    global _sam_cache, _mask_generator_cache

    # Für Apple Silicon: MPS vermeiden, SAM auf CPU laden
    if device is None:
        if torch.backends.mps.is_available():
            print("⚙️  MPS erkannt, aber SAM läuft stabiler auf CPU (float32 only)")
            device = "cpu"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    if _sam_cache is not None:
        return _sam_cache, _mask_generator_cache, device

    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    model_path = model_dir / "sam_vit_b_01ec64.pth"

    if not model_path.exists():
        print("📥 Lade SAM-Checkpoint (375 MB)…")
        import urllib.request
        url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
        urllib.request.urlretrieve(url, model_path)
        print("✅ Download abgeschlossen")

    print(f"🔄 Lade SAM auf {device} …")
    sam = sam_model_registry["vit_b"](checkpoint=str(model_path))
    sam.to(device=device)

    mask_generator = SamAutomaticMaskGenerator(
        model=sam,
        points_per_side=32,
        pred_iou_thresh=0.88,
        stability_score_thresh=0.9,
        min_mask_region_area=10000,
    )

    print("✅ SAM initialisiert!")
    _sam_cache = sam
    _mask_generator_cache = mask_generator
    return sam, mask_generator, device


def chunk_images(image_paths, output_folder, resize_max=1024):
    os.makedirs(output_folder, exist_ok=True)
    _, mask_generator, device = get_sam_model()

    for idx, path in enumerate(image_paths):
        img = cv2.imread(path)
        if img is None:
            print(f"⚠️  Konnte nicht lesen: {path}")
            continue

        h, w = img.shape[:2]
        if max(h, w) > resize_max:
            scale = resize_max / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(f"🔍 Seite {idx+1}: Generiere Masken...")

        try:
            masks = mask_generator.generate(img_rgb)
        except Exception as e:
            print(f"❌ Fehler bei Seite {idx+1}: {e}")
            continue

        masks = sorted(masks, key=lambda x: x["area"], reverse=True)
        page_folder = os.path.join(output_folder, f"page_{idx+1:03d}")
        os.makedirs(page_folder, exist_ok=True)

        saved = 0
        for i, m in enumerate(masks[:30]):
            x, y, w, h = map(int, m["bbox"])
            crop = img[y:y+h, x:x+w]
            if crop.size == 0:
                continue
            cv2.imwrite(os.path.join(page_folder, f"segment_{i:02d}.png"), crop)
            saved += 1

        print(f"✅ Seite {idx+1}: {saved} Segmente gespeichert")
