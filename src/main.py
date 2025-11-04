from util.pdf_helper import pdfs_to_images
from util.ollama_checker import check_ollama_and_models
from gemini_detection.detect import detect_logical_blocks_with_gemini
from gemini_detection.visualize import visualize_bounding_boxes

#check_ollama_and_models(["gemma3:12b", "gpt-oss:20b"])
#images = (pdfs_to_images("data/to_process", "data/processed"))
#detect_logical_blocks_with_gemini(images, "data/detections", test_mode=True)

visualize_bounding_boxes(
    image_dir="data/processed/Lineare Algebra",
    boxes_dir="data/detections",
    output_dir="data/visualizations",
    show=False
)


