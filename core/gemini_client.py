import os
from typing import Optional
import google.generativeai as genai

_api_key: Optional[str] = None

def configure():
    global _api_key
    _api_key = os.getenv("GEMINI_API_KEY")
    if not _api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in environment")
    genai.configure(api_key=_api_key)

def get_model(name: str = "gemini-2.5-flash"):
    if _api_key is None:
        configure()
    return genai.GenerativeModel(name)
