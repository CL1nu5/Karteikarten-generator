from util.pdf_helper import pdfs_to_images
from util.ollama_checker import check_ollama_and_models

check_ollama_and_models(["gemma3:12b", "gpt-oss:20b"])
images = (pdfs_to_images("data/to_process", "data/processed"))
