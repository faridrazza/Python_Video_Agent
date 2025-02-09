import asyncio
import os
from typing import Dict, List
from config.config import APIConfig
from services.script_generator import ScriptGenerator
from services.audio_service import AudioService
from services.storage_service import StorageService
from services.image_service import ImageService
from services.video_service import VideoService
from services.transcription_service import TranscriptionService
from services.publishing_service import PublishingService
from services.status_tracker import StatusTracker
from utils.helpers import setup_logging, create_temp_directory, generate_unique_id, cleanup_temp_files

logger = setup_logging()

class VideoCreationOrchestrator:
    def __init__(self, config: APIConfig):
        self.config = config
        self.temp_dir = create_temp_directory()
        
        # Initialize services
        self.script_generator = ScriptGenerator(config.OPENAI_API_KEY)
        self.audio_service = AudioService(config.ELEVEN_LABS_API_KEY)
        self.storage_service = StorageService(
            config.GCS_CLIENT_EMAIL,
            config.GCS_PRIVATE_KEY
        )
        self.image_service = ImageService(
            config.TOGETHER_AI_API_KEY,
            config.OPENAI_API_KEY
        )
        self.video_service = VideoService(config.STABILITY_AI_API_KEY)
        self.transcription_service = TranscriptionService(config.OPENAI_API_KEY)
        self.publishing_service = PublishingService(
            config.YOUTUBE_CLIENT_ID,
            config.YOUTUBE_CLIENT_SECRET,
            config.YOUTUBE_API_KEY
        )
        self.status_tracker = StatusTracker(
            config.GCS_CLIENT_EMAIL,
            config.GCS_PRIVATE_KEY,
            config.GOOGLE_SHEET_ID
        )

    async def create_and_publish_video(
        self,
        topic: str,
        format_type: str,
        duration: int
    ) -> Dict[str, str]:
        """
        Orchestrate the entire video creation and publishing process
        """
        video_id = generate_unique_id()
        status = {}
        
        try:
            # 1. Generate Script
            logger.info(f"Generating script for video {video_id}")
            script_data = await self.script_generator.generate_script(topic, format_type, duration)
            status['script_status'] = 'completed'
            await self.status_tracker.update_status(video_id, status)

            # 2. Generate Audio
            logger.info("Generating audio from script")
            audio_content = await self.audio_service.generate_audio(script_data['script'])
            audio_path = os.path.join(self.temp_dir, f"{video_id}_audio.mp3")
            with open(audio_path, 'wb') as f:
                f.write(audio_content)
            
            # Upload audio to GCS
            audio_url = self.storage_service.upload_file(
                self.config.AUDIO_BUCKET,
                audio_path,
                f"{video_id}/audio.mp3"
            )
            status['audio_url'] = audio_url
            await self.status_tracker.update_status(video_id, status)

            # 3. Generate Transcript
            logger.info("Generating transcript")
            transcript_data = await self.transcription_service.generate_transcript(audio_path)
            status['transcript_status'] = 'completed'
            await self.status_tracker.update_status(video_id, status)

            # 4. Generate Images
            logger.info("Generating images")
            image_prompts = await self.image_service.generate_image_prompts(
                transcript_data['text']
            )
            images = await self.image_service.generate_images(image_prompts)
            
            # Save and upload images
            image_paths = []
            for idx, image in enumerate(images):
                image_path = os.path.join(self.temp_dir, f"{video_id}_image_{idx}.png")
                with open(image_path, 'wb') as f:
                    f.write(image)
                image_paths.append(image_path)
                
                self.storage_service.upload_file(
                    self.config.IMAGE_BUCKET,
                    image_path,
                    f"{video_id}/images/image_{idx}.png"
                )
            
            status['images_status'] = 'completed'
            await self.status_tracker.update_status(video_id, status)

            # 5. Generate Videos from Images
            logger.info("Generating videos from images")
            videos = await self.video_service.generate_videos_from_images(images)
            
            # Save videos
            video_paths = []
            for idx, video in enumerate(videos):
                video_path = os.path.join(self.temp_dir, f"{video_id}_video_{idx}.mp4")
                with open(video_path, 'wb') as f:
                    f.write(video)
                video_paths.append(video_path)

            # 6. Assemble Final Video
            logger.info("Assembling final video")
            final_video_path = os.path.join(self.temp_dir, f"{video_id}_final.mp4")
            await self.video_service.assemble_final_video(
                video_paths,
                audio_path,
                transcript_data['text'],
                final_video_path
            )
            
            # Upload final video to GCS
            final_video_url = self.storage_service.upload_file(
                self.config.VIDEO_BUCKET,
                final_video_path,
                f"{video_id}/final_video.mp4"
            )
            status['video_status'] = 'completed'
            await self.status_tracker.update_status(video_id, status)

            # 7. Publish to Platforms
            logger.info("Publishing video to platforms")
            youtube_url = await self.publishing_service.upload_to_youtube(
                final_video_path,
                script_data['title'],
                script_data['description'],
                []  # Add tags if needed
            )
            status['youtube_url'] = youtube_url
            
            # 8. Final Status Update
            status['creation_date'] = datetime.now().isoformat()
            status['notes'] = 'Successfully completed'
            await self.status_tracker.update_status(video_id, status)

            # Cleanup
            cleanup_temp_files(self.temp_dir)
            
            return status

        except Exception as e:
            logger.error(f"Error in video creation process: {str(e)}")
            status['notes'] = f"Error: {str(e)}"
            await self.status_tracker.update_status(video_id, status)
            cleanup_temp_files(self.temp_dir)
            raise

# Example usage
async def main():
    try:
        # Load and validate configuration
        config = APIConfig()
        config.validate()
        
        orchestrator = VideoCreationOrchestrator(config)
        
        status = await orchestrator.create_and_publish_video(
            topic="The Partition of India -What Really Happened in 1947",
            format_type="The Partition of India -What Really Happened in 1947",
            duration=30
        )
        print("Video creation completed successfully!")
        print("Status:", status)
        
    except ValueError as e:
        print(f"Configuration Error: {str(e)}")
    except Exception as e:
        print(f"Error creating video: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 