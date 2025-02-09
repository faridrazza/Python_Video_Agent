import openai
from typing import Dict

class TranscriptionService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    async def generate_transcript(self, audio_file_path: str) -> Dict[str, str]:
        """
        Generate transcript from audio file using Whisper API
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await openai.Audio.atranscribe(
                    "whisper-1",
                    audio_file,
                    response_format="verbose_json"
                )
            
            return {
                "text": transcript["text"],
                "segments": transcript["segments"]
            }
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}") 