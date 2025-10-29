import cv2
from ultralytics import YOLO
from pathlib import Path

def predict_and_show(model_path: str, image_path: str, save_result: bool = False):
    """
    Lädt ein YOLO-Modell, führt Inferenz auf einem Bild aus und zeigt das Ergebnis.
    """
    model_path = Path(model_path)
    image_path = Path(image_path)

    if not model_path.exists():
        raise FileNotFoundError(f"❌ Modell nicht gefunden: {model_path}")
    if not image_path.exists():
        raise FileNotFoundError(f"❌ Bild nicht gefunden: {image_path}")

    print(f"🔄 Lade Modell: {model_path}")
    model = YOLO(model_path)

    print(f"🖼️ Analysiere Bild: {image_path}")
    results = model.predict(source=str(image_path), device="mps", verbose=False, conf=0.6)

    # Erstes Ergebnis extrahieren
    result = results[0]

    # Annotiertes Bild abrufen (BGR)
    annotated_frame = result.plot()

    # Bild anzeigen
    cv2.imshow("YOLO Prediction", annotated_frame)
    print("👁️  Fenster geöffnet – drücke [q], um zu beenden.")
    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()

    # Optional speichern
    if save_result:
        out_path = image_path.parent / f"{image_path.stem}_pred.jpg"
        cv2.imwrite(str(out_path), annotated_frame)
        print(f"💾 Ergebnis gespeichert unter: {out_path}")


if __name__ == "__main__":
    # 🔧 HIER kannst du einfach deine Pfade eintragen:
    model_path = "runs/train/yolo_split_run5/weights/best.pt"
    image_path = "data/ai/yolo_split/test/images/87f79a1b-page_00002.png"
    save_result = False  # auf False setzen, wenn du nicht speichern willst

    predict_and_show(model_path, image_path, save_result)
