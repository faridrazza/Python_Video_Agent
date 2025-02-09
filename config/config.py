from dataclasses import dataclass
from typing import Dict

@dataclass
class APIConfig:
    OPENAI_API_KEY: str
    ELEVEN_LABS_API_KEY: str
    TOGETHER_AI_API_KEY: str
    STABILITY_AI_API_KEY: str
    GCS_CREDENTIALS_PATH: str
    YOUTUBE_API_KEY: str
    INSTAGRAM_API_KEY: str
    
    # GCS bucket names
    AUDIO_BUCKET: str = "ai-video-audio-files"
    IMAGE_BUCKET: str = "ai-video-image-files"
    VIDEO_BUCKET: str = "ai-video-final-files"
    
    # API endpoints
    STABILITY_AI_ENDPOINT: str = "https://api.stability.ai/v2beta/image-to-video"
    
    # Other configurations
    SUPPORTED_VIDEO_FORMATS: Dict[str, str] = {
        "youtube": "mp4",
        "instagram": "mp4"
    } 