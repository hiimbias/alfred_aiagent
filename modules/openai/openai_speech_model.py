import os
import tempfile
from loguru import logger
from openai import OpenAI
from core.interfaces import BaseSpeechModel
from typing import Optional, Literal
from core._types import NamedByteIO


class OpenAISpeechModel(BaseSpeechModel):
    def __init__(self,
                    client: OpenAI,
                    voice: Optional[Literal["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]] = "alloy",
                    stt_model: Optional[str] = "whisper-1",
                    *args,
                    **kwargs):

        self._client = client
        self.voice = voice
        self.stt_model = stt_model
        
    def _transcribe(self, file_obj, file_name=None):
        if file_name and isinstance(file_obj, bytes):
            buffer = NamedByteIO(file_obj, name=file_name)
            
        response = self._client.audio.transcriptions.create(
            model = self.stt_model,
            file = buffer,
        )
        
        return response.text 
    
    def speech_to_text(self, audio_data: bytes) -> str:
        pass
    
    def text_to_speech(self, message: str, response_format: Optional[str] = "wav") -> bytes:
        response = self._client.audio.speech.create(
            model = "tts-1",
            voice = self.voice,
            input = message,
            response_format = response_format,
        )
        
        return response.content