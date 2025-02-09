import requests
import json
from typing import Optional

class AudioService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }

    async def generate_audio(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
        """
        Generate audio from text using Eleven Labs API
        Default voice_id is "Rachel" - you can change this to any voice ID from Eleven Labs
        """
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return response.content

        except Exception as e:
            raise Exception(f"Audio generation failed: {str(e)}") 