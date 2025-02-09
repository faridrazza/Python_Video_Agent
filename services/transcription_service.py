import whisper
from typing import Dict

class TranscriptionService:
    def __init__(self):
        self.model = whisper.load_model("base")

    async def generate_transcript(self, audio_file_path: str) -> Dict[str, str]:
        """
        Generate transcript from audio file using Whisper AI
        """
        try:
            result = self.model.transcribe(audio_file_path)
            
            return {
                "text": result["text"],
                "segments": result["segments"]
            }
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}") 