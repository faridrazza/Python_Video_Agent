import asyncio
from config.config import APIConfig
from main import VideoCreationOrchestrator

async def main():
    try:
        # Initialize config and validate
        config = APIConfig()
        config.validate()
        
        # Create orchestrator
        orchestrator = VideoCreationOrchestrator(config)
        
        # Create and publish video
        result = await orchestrator.create_and_publish_video(
            topic="Your video topic",
            format_type="educational",  # or "entertainment"
            duration=5  # duration in minutes
        )
        
        print("Video creation completed!")
        print(f"YouTube URL: {result.get('youtube_url')}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 