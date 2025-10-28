from pathlib import Path
from ultralytics import YOLO
import yaml
import numpy as np
import warnings


def create_data_yaml(dataset_dir: str, class_names: list):
    """
    Erzeugt eine YOLO-kompatible data.yaml falls noch nicht vorhanden.
    """
    dataset_dir = Path(dataset_dir)
    yaml_path = dataset_dir / "data.yaml"

    if yaml_path.exists():
        print(f"✅ data.yaml bereits vorhanden: {yaml_path}")
        return str(yaml_path)

    data = {
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "nc": len(class_names),
        "names": class_names,
    }

    with open(yaml_path, "w") as f:
        yaml.dump(data, f)

    print(f"📝 data.yaml erstellt unter: {yaml_path}")
    return str(yaml_path)


def train_yolo_model(
    dataset_dir="data/ai/yolo_split",
    class_names=None,
    model_name="yolov8m.pt",
    epochs=50,
    imgsz=640,
    device="mps", 
    project_dir="runs/train",
):
    """
    Trainiert ein YOLOv8-Modell auf dem angegebenen Dataset.
    """

    if class_names is None:
        # Klassen manuell festlegen, falls nicht vorhanden
        # (an dein Mapping angepasst!)
        class_names = ["klasse_0", "klasse_1"]

    # Sicherstellen, dass ultralytics installiert ist
    try:
        import ultralytics
    except ImportError:
        raise RuntimeError("❌ Bitte zuerst installieren: pip install ultralytics")

    # data.yaml erzeugen (falls fehlt)
    data_yaml = create_data_yaml(dataset_dir, class_names)

    # Modell laden
    print(f"🔄 Lade Modell '{model_name}' ...")
    model = YOLO(model_name)

    # Training starten
    print("🚀 Starte Training ...")
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        device=device,
        project=project_dir,
        augment=False,
        name=f"{Path(dataset_dir).name}_run",
    )

    print("✅ Training abgeschlossen!")
    print(f"📂 Ergebnisse gespeichert unter: {results.save_dir}")
    return results


if __name__ == "__main__":
    np.seterr(all="ignore")
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=UserWarning)

    # Beispiel-Aufruf
    train_yolo_model(
        dataset_dir="data/ai/yolo_split",  
        class_names=["logic-component", "logic-block"],  
        model_name="yolov8m.pt",  
        epochs=100,
        imgsz=1280,
        device="mps",  
    )
