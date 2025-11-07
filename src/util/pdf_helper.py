import os
from pdf2image import convert_from_path
from loguru import logger
from util.config_reader import ConfigLoader
from pathlib import Path

# Convert pdf files to images and save them in the target folder
def pdfs_to_images(source_pdf_files: set, target_folder: str, dpi: int = 300) -> list[tuple[str, str]]:
    os.makedirs(target_folder, exist_ok=True)

    image_paths = []

    if not source_pdf_files:
        logger.info("ℹ️  No pdf documents were found to convert.")
        return []
    else:
        logger.info(f"ℹ️  Found pdf documents: {len(source_pdf_files)}. starting converison...")

    for pdf_file in source_pdf_files:
        pdf_name = os.path.splitext(pdf_file)[0]
        output_subfolder = os.path.join(target_folder, pdf_name)

        os.makedirs(output_subfolder, exist_ok=True)

        try:
            images = convert_from_path(pdf_file, dpi=dpi)
            for i, image in enumerate(images):
                image_path = os.path.join(output_subfolder, f"page_{i+1:05d}.png")
                image.save(image_path, "PNG")
                image_paths.append((image_path, pdf_file))
            logger.info(f"✅ {pdf_file} -> {len(images)} pages exportet.")
        except Exception as e:
            logger.error(f"❌ Error ar {pdf_file}: {e}")
            return []
    
    return image_paths

# Cache the created image paths along with their source PDF files
def cache_image_creation(image_paths: list[tuple[str, str]], config: ConfigLoader) -> None:
    cache_list = []

    for image_path, pdf_file in image_paths:
        cache_list.append(("CONVERTED_IMAGES <--> " + image_path, pdf_file))
    
    config.cache_values(
        path=config._config["GENENERAL_CONFIGURATION"]["CACHE_FILES"]["TRANSFORMATION"],
        items=cache_list,
        split_char=" <--> ",
        split=True
    )

# Loades only the pdf file pahts, that are not chaced or outdated
def load_cached_pdfs(pdf_paths: set[str], config: ConfigLoader) -> set[str]:

    image_pdf_pairs = config._config.get("CACHE", {}).get("CONVERTED_IMAGES", {}).items()
    
    for image_path, pdf_path in image_pdf_pairs:
        image_file = Path(image_path)
        pdf_file = Path(pdf_path)
        
        if (not pdf_file.exists()) and image_file.exists():
            try:
                image_file.unlink()
                print(f"Deleted image: {image_path}")
                
                parent_dir = image_file.parent
                if parent_dir.exists() and not any(parent_dir.iterdir()):
                    parent_dir.rmdir()
                    print(f"Deleted empty directory: {parent_dir}")
            except Exception as e:
                print(f"Error deleting image or directory: {e}")

        if pdf_file.exists() and image_file.exists():
            try:
                pdf_mtime = pdf_file.stat().st_mtime
                image_mtime = image_file.stat().st_mtime
                
                if pdf_mtime < image_mtime and pdf_path in pdf_paths:
                    pdf_paths.remove(pdf_path)
                    
            except Exception as e:
                print(f"Error checking modification times: {e}")
    
    return pdf_paths
    