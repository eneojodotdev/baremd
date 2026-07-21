import io
import sys
import os
import tempfile
from typing import BinaryIO
from .._exceptions import MissingDependencyException

_dependency_exc_info = None
try:
    from faster_whisper import WhisperModel
except ImportError:
    _dependency_exc_info = sys.exc_info()

# Load the model globally to avoid reloading on every transcription
_whisper_model = None

def transcribe_audio(file_stream: BinaryIO, *, audio_format: str = "wav") -> str:
    global _whisper_model
    
    if _dependency_exc_info is not None:
        raise MissingDependencyException(
            "Speech transcription requires 'faster-whisper'."
        ) from _dependency_exc_info[1].with_traceback(_dependency_exc_info[2])

    if _whisper_model is None:
        # Initializing local GPU whisper
        _whisper_model = WhisperModel("base", device="cuda", compute_type="float16")

    # faster-whisper accepts file paths, so we dump the stream to a temp file
    suffix = f".{audio_format}"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_audio:
        temp_audio.write(file_stream.read())
        temp_audio.flush()
        temp_path = temp_audio.name

    try:
        segments, info = _whisper_model.transcribe(temp_path, beam_size=5)
        transcript = " ".join([segment.text for segment in segments])
        return "[No speech detected]" if not transcript.strip() else transcript.strip()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
