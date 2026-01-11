# config.py
# Apollo configuration (edit this)

# IMPORTANT: Use a raw string r"..." or forward slashes to avoid Windows \U unicode escapes.
MODEL_PATH = r"C:\Users\oscar\PycharmProjects\Apollo\LLm\mistral-7b-instruct-v0.2.Q2_K.gguf"

# LLM performance settings
N_THREADS = 1
N_GPU_LAYERS = 0
N_CTX = 2048    # Set 0 if you don't have compatible GPU acceleration

# Generation settings
MAX_TOKENS = 128
TEMPERATURE = 0.7
TOP_P = 0.95

# Memory settings
MEMORY_FILE = "storage/memory.json"
MAX_TURNS_IN_CONTEXT = 10  # short-term conversation window size

# UI
APP_TITLE = "Apollo"
