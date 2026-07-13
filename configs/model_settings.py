
RETRIEVAL_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

COMPRESSOR_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

MEMORY_EMBEDDING_MODEL = "intfloat/multilingual-e5-base"

CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CHAT_LLM = "unsloth/Qwen3-4B-Instruct-2507-bnb-4bit"

# Swap to see which one fit
# High VRAM consume, bad following instruction
CHAT_VLM = "unsloth/Qwen3-VL-4B-Instruct-unsloth-bnb-4bit"

# Medimum VRAM consume, bad reasoning and never follow instruction
# CHAT_VLM = "unsloth/Qwen2.5-3B-Instruct-unsloth-bnb-4bit"

# Used for Vision-to-LLM Architecture
# CHAT_VLM = "unsloth/Qwen3-VL-2B-Instruct-unsloth-bnb-4bit"