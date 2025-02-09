import os
from dataclasses import dataclass, field
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    # AI Service Keys
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    ELEVEN_LABS_API_KEY: str = os.getenv('ELEVEN_LABS_API_KEY')
    TOGETHER_AI_API_KEY: str = os.getenv('TOGETHER_AI_API_KEY')
    STABILITY_AI_API_KEY: str = os.getenv('STABILITY_AI_API_KEY')
    
    # Google Cloud & YouTube
    GCS_CLIENT_EMAIL: str = os.getenv('GCS_CLIENT_EMAIL')
    GCS_PRIVATE_KEY: str = os.getenv('GCS_PRIVATE_KEY')
    GCS_PROJECT_ID: str = os.getenv('GCS_PROJECT_ID')
    YOUTUBE_API_KEY: str = os.getenv('YOUTUBE_API_KEY')  # For fetching YouTube data
    YOUTUBE_CLIENT_ID: str = os.getenv('YOUTUBE_CLIENT_ID')  # For uploading videos
    YOUTUBE_CLIENT_SECRET: str = os.getenv('YOUTUBE_CLIENT_SECRET')  # For uploading videos
    
    # GCS bucket names
    AUDIO_BUCKET: str = os.getenv('GCS_AUDIO_BUCKET', 'ai-video-audio-files')
    IMAGE_BUCKET: str = os.getenv('GCS_IMAGE_BUCKET', 'ai-video-image-files')
    VIDEO_BUCKET: str = os.getenv('GCS_VIDEO_BUCKET', 'ai-video-final-files')
    
    # Google Sheets
    GOOGLE_SHEET_ID: str = os.getenv('GOOGLE_SHEET_ID')
    
    # API endpoints
    STABILITY_AI_ENDPOINT: str = "https://api.stability.ai/v2beta/image-to-video"
    
    # Other configurations
    SUPPORTED_VIDEO_FORMATS: Dict[str, str] = field(
        default_factory=lambda: {"youtube": "mp4"}
    )

    @classmethod
    def validate(cls) -> None:
        """Validate that all required environment variables are set"""
        required_vars = [
            'OPENAI_API_KEY',
            'ELEVEN_LABS_API_KEY',
            'TOGETHER_AI_API_KEY',
            'STABILITY_AI_API_KEY',
            'GCS_CLIENT_EMAIL',
            'GCS_PRIVATE_KEY',
            'GCS_PROJECT_ID',
            'YOUTUBE_CLIENT_ID',
            'YOUTUBE_CLIENT_SECRET',
            'YOUTUBE_API_KEY',
            'GOOGLE_SHEET_ID'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file."
            ) 