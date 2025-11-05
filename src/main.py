from util.pdf_helper import pdfs_to_images, cache_image_creation, load_cached_pdfs
from util.ollama_checker import check_ollama_and_models
from gemini_detection.detect import detect_logical_blocks_with_gemini
from gemini_detection.visualize import visualize_bounding_boxes
from util.config_reader import ConfigLoader
import os

# load configuration
config_loader = ConfigLoader()
config = config_loader.to_dict()

# check for required models in Ollama
models_to_check = config.get("CHAT_MODELS_MODELS", [])
check_ollama_and_models(models_to_check)

# load chaced pdf files
pdf_files = [os.path.join("data/to_process", f) for f in os.listdir("data/to_process") if f.lower().endswith(".pdf")]

if config.get("PROCESS_SETTINGS_CACHE_PDF_TO_IMAGE_CREATION", False):
    pdf_files = load_cached_pdfs(set(pdf_files), config_loader)

# create images and chache them
images = (pdfs_to_images(pdf_files, "data/processed"))
if config.get("PROCESS_SETTINGS_CACHE_PDF_TO_IMAGE_CREATION", False):
    cache_image_creation(images, config_loader)

#check_ollama_and_models(["gemma3:12b", "gpt-oss:20b"])
#images = (pdfs_to_images("data/to_process", "data/processed"))
#detect_logical_blocks_with_gemini(images, "data/detections", test_mode=True)

visualize_bounding_boxes(
    image_dir="data/processed/Lineare Algebra",
    boxes_dir="data/detections",
    output_dir="data/visualizations",
    show=False
)


