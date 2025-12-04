import os
from pathlib import Path
from typing import Optional

def transcribe_with_openai_api(wav_path: str, openai_api_key: Optional[str] = None) -> str:
    """
    Sử dụng OpenAI's speech-to-text (whisper-1) - cần API key (OPENAI_API_KEY env var hoặc truyền vào).
    Trả về chuỗi text.
    """
    try:
        import openai
    except ImportError:
        raise ImportError("Bạn cần cài package 'openai' (pip install openai)")

    if openai_api_key is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("API key not provided. Set OPENAI_API_KEY env var or pass openai_api_key param.")

    openai.api_key = openai_api_key

    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"{wav_path} not found")

    # gửi file audio (wav/mp3/m4a) tới OpenAI
    with open(wav_path, "rb") as f:
        resp = openai.Audio.transcriptions.create(
            file=f,
            model="whisper-1"
        )

    text = resp.get("text") if isinstance(resp, dict) else getattr(resp, "text", "")
    return text.strip() if text else ""
