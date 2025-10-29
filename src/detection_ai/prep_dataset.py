import os
import zipfile
import random
import shutil
from pathlib import Path

def adjust_label_classes(label_path: Path, out_path: Path):
    """
    Liest eine YOLO-Labeldatei und schreibt sie neu mit angepassten Klassen-IDs.
    Mapping:
      1, 3 -> 0
      2    -> 1
      andere bleiben gleich
    """
    if not label_path.exists():
        return

    new_lines = []
    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            cls = int(parts[0])
            # Mapping anwenden
            if cls in [1, 3]:
                cls = 0
            elif cls == 2:
                cls = 1
            # Rest unverändert
            new_line = " ".join([str(cls)] + parts[1:])
            new_lines.append(new_line)

    with open(out_path, "w") as f:
        f.write("\n".join(new_lines))


def split_yolo_dataset(
    zip_path: str,
    output_dir: str = "data/split",
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42,
):
    """
    Entpackt ein YOLO-Dataset (.zip), teilt es in train/val/test auf
    und passt Label-Klassen nach definiertem Mapping an.
    Erwartet: images/ + labels/ Struktur im ZIP.
    """

    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Summe der Splits muss 1 sein!"

    random.seed(seed)

    # -------------------------
    # 1️⃣ ZIP entpacken
    # -------------------------
    extract_dir = Path(output_dir) / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Entpacke {zip_path} ...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    print("✅ Entpackt!")

    # YOLO-Struktur finden
    images_dir = None
    labels_dir = None
    for root, dirs, files in os.walk(extract_dir):
        if "images" in dirs and "labels" in dirs:
            images_dir = Path(root) / "images"
            labels_dir = Path(root) / "labels"
            break

    if images_dir is None or labels_dir is None:
        raise RuntimeError("❌ Konnte keine 'images' und 'labels' Verzeichnisse im ZIP finden!")

    # -------------------------
    # 2️⃣ Dateien listen
    # -------------------------
    image_files = sorted([f for f in images_dir.glob("*") if f.suffix.lower() in [".jpg", ".png", ".jpeg"]])
    print(f"🖼️  {len(image_files)} Bilder gefunden")

    # Shuffle
    random.shuffle(image_files)

    n_total = len(image_files)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    splits = {
        "train": image_files[:n_train],
        "val": image_files[n_train:n_train + n_val],
        "test": image_files[n_train + n_val:],
    }

    # -------------------------
    # 3️⃣ Split-Ordner erstellen
    # -------------------------
    for split in splits:
        (Path(output_dir) / split / "images").mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / split / "labels").mkdir(parents=True, exist_ok=True)

    # -------------------------
    # 4️⃣ Dateien kopieren + Label anpassen
    # -------------------------
    for split, files in splits.items():
        print(f"✂️  Erstelle Split '{split}' ({len(files)} Dateien)")
        for img_path in files:
            label_path = labels_dir / f"{img_path.stem}.txt"

            # Zielpfade
            out_img = Path(output_dir) / split / "images" / img_path.name
            out_lbl = Path(output_dir) / split / "labels" / label_path.name

            shutil.copy(img_path, out_img)

            if label_path.exists():
                adjust_label_classes(label_path, out_lbl)
            else:
                print(f"⚠️ Kein Label für {img_path.name}")

    print("✅ Fertig! Aufteilung gespeichert in:", Path(output_dir).resolve())


if __name__ == "__main__":
    # Beispiel-Aufruf:
    split_yolo_dataset(
        zip_path="data/ai/project-1-at-2025-10-28-18-13-4536c3b2.zip",
        output_dir="data/ai/yolo_split",
        train_ratio=0.6,
        val_ratio=0.3,
        test_ratio=0.1,
    )
