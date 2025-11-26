from util.pdf_helper import pdfs_to_images, cache_image_creation, load_cached_pdfs
from util.ollama_checker import check_ollama_and_models
from gemini_detection.detect import detect_logical_blocks_with_gemini
from gemini_detection.visualize import visualize_bounding_boxes
from util.config_reader import ConfigLoader
import os

# Initialize configuration loader and retrieve config as dictionary
config_loader = ConfigLoader()
config = config_loader.to_dict()

# Verify that required Ollama models are installed
models_to_check = config.get("CHAT_MODELS_MODELS", [])
check_ollama_and_models(models_to_check)

# Identify PDF files to process in the data directory
pdf_files = [os.path.join("data/to_process", f) for f in os.listdir("data/to_process") if f.lower().endswith(".pdf")]

# If caching is enabled, filter out PDFs that have already been processed and are up-to-date
if config.get("PROCESS_SETTINGS_CACHE_PDF_TO_IMAGE_CREATION", False):
    pdf_files = load_cached_pdfs(set(pdf_files), config_loader)

# Convert PDFs to images and handle caching if enabled
images = (pdfs_to_images(pdf_files, "data/processed"))
if config.get("PROCESS_SETTINGS_CACHE_PDF_TO_IMAGE_CREATION", False):
    cache_image_creation(images, config_loader)
    # Load all cached images for processing
    images = [img_path for img_path, _ in config_loader._config.get("CACHE", {}).get("CONVERTED_IMAGES", {}).items()]

# Detect logical blocks in images using Gemini API (test_mode limits to first 3 images)
print(detect_logical_blocks_with_gemini(images, "data/detections", config_loader, test_mode=True))

# Visualize detected bounding boxes on the images
visualize_bounding_boxes(
    image_dir="data/processed/Analysis",
    boxes_dir="data/detections",
    output_dir="data/visualizations",
    show=False
)


