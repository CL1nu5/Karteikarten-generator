import os
from pdf2image import convert_from_path
from loguru import logger

def pdfs_to_images(source_folder: str, target_folder: str, dpi: int = 600):
    # Sicherstellen, dass Zielordner existiert
    os.makedirs(target_folder, exist_ok=True)

    # Alle PDF-Dateien im Quellordner finden
    pdf_files = [f for f in os.listdir(source_folder) if f.lower().endswith(".pdf")]

    image_paths = []

    if not pdf_files:
        logger.warning("Keine PDF-Dateien im Quellordner gefunden.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(source_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        output_subfolder = os.path.join(target_folder, pdf_name)

        # Unterordner für jede PDF anlegen
        os.makedirs(output_subfolder, exist_ok=True)

        # PDF in Bilder umwandeln
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            for i, image in enumerate(images):
                image_path = os.path.join(output_subfolder, f"page_{i+1:05d}.png")
                image.save(image_path, "PNG")
                image_paths.append(image_path)
            logger.info(f"✅ {pdf_file} -> {len(images)} Seiten exportiert.")
        except Exception as e:
            logger.error(f"❌ Fehler bei {pdf_file}: {e}")
            return []
    
    return image_paths
    