# map for all models
MODEL_MAP = {
    "Hermes LLama 3.1 8B": "hermes-3-llama-3.1-8b",
    "Hermes LLama 3.2 3B": "hermes-3-llama-3.2-3b",
    "IBM Granite 3.1 8B": "granite-3.1-8b-instruct",
    "HuggingFace - Mistral Nemo Instruct": "mistral-nemo-instruct-2407",
    "LM Studio - LLama3.2 3B": "llama-3.2-3b-instruct",
    "QWEN 2.5 Instruct": "qwen2.5-14b-instruct",
}

# LLM settings
LLM_CONFIG = {
    "BASE_URL": "http://localhost:1234/v1",
    "API_KEY": "lm-studio",
    "TEMPERATURE": 0.15,
}
