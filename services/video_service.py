import requests
import time
from typing import List, Dict
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

class VideoService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.stability.ai/v2beta/image-to-video"

    async def generate_videos_from_images(self, image_files: List[bytes]) -> List[bytes]:
        """Generate videos from images using Stability AI"""
        videos = []
        
        for image in image_files:
            try:
                # Initialize video generation
                response = requests.post(
                    f"{self.base_url}",
                    headers=self.headers,
                    files={"image": image}
                )
                response.raise_for_status()
                generation_id = response.json()["id"]

                # Poll for completion
                video_bytes = await self._poll_generation(generation_id)
                videos.append(video_bytes)

            except Exception as e:
                raise Exception(f"Video generation failed: {str(e)}")

        return videos

    async def _poll_generation(self, generation_id: str, max_attempts: int = 60) -> bytes:
        """Poll for video generation completion"""
        attempts = 0
        while attempts < max_attempts:
            try:
                response = requests.get(
                    f"{self.base_url}/result/{generation_id}",
                    headers=self.headers
                )
                
                if response.status_code == 202:
                    # Still processing
                    time.sleep(5)
                    attempts += 1
                    continue
                    
                response.raise_for_status()
                return response.content

            except Exception as e:
                if attempts == max_attempts - 1:
                    raise Exception(f"Video generation polling failed: {str(e)}")
                time.sleep(5)
                attempts += 1

    async def assemble_final_video(
        self,
        video_files: List[str],
        audio_file: str,
        transcript: str,
        output_path: str
    ) -> str:
        """Assemble final video with audio and captions"""
        try:
            # Load video clips
            video_clips = [VideoFileClip(v) for v in video_files]
            
            # Concatenate video clips
            final_video = mp.concatenate_videoclips(video_clips)
            
            # Add audio
            audio = AudioFileClip(audio_file)
            final_video = final_video.set_audio(audio)
            
            # Add captions
            txt_clip = TextClip(
                transcript, 
                fontsize=24, 
                color='white',
                bg_color='black',
                size=(final_video.w, None),
                method='caption'
            )
            txt_clip = txt_clip.set_position(('center', 'bottom'))
            
            # Composite video with captions
            final = CompositeVideoClip([final_video, txt_clip])
            
            # Write final video
            final.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Video assembly failed: {str(e)}") 