import json
import re
import uuid
from typing import Any, Dict, List

def safe_json_parse(text: str, fallback: Any = None) -> Any:
    """
    Try to extract JSON from LLM text (handles fenced code blocks).
    """
    if text is None:
        return fallback
    m = re.search(r"\{.*\}|\[.*\]", text, flags=re.DOTALL)
    raw = m.group(0) if m else text
    try:
        return json.loads(raw)
    except Exception:
        return fallback

def gen_id(prefix: str = "q") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"
