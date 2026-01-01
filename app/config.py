import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_KEYS = [val for key, val in os.environ.items() if key.startswith("GEMINI_KEY_") and val]
    GROQ_KEY = os.getenv("GROQ_API_KEY")
    SMART_MODELS = [
        "gemini/gemini-2.5-flash",
        "gemini/gemini-2.5-flash-lite",
    ]
    FAST_MODELS = [
        "groq/llama-3.1-8b-instant",
        "groq/llama-3.3-70b-versatile",
    ]
    PROMPT_DIR = Path("prompts")

    @staticmethod
    def load_prompt(filename):
        path = Config.PROMPT_DIR / filename
        if not path.exists():
            return "{input}"
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()