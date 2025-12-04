from pathlib import Path
from typing import Optional

def transcribe_with_whisper_local(wav_path: str, model_name: str = "small") -> str:
    """
    Sử dụng openai-whisper (local) để chuyển WAV -> text.
    model_name có thể là 'tiny','base','small','medium','large' tùy cài đặt.
    """
    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"{wav_path} not found")

    try:
        import whisper
        model = whisper.load_model(model_name)
        result = model.transcribe(str(wav_path))
        text = result.get("text", "").strip()
        return text
    except Exception as e:
        # Nếu user cài faster-whisper thay thế
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel(model_name, device="cpu")  
            segments, info = model.transcribe(str(wav_path))
            text = " ".join([seg.text for seg in segments]).strip()
            return text
        except Exception:
            raise RuntimeError(f"Local transcription failed: {e}")
