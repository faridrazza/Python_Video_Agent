import requests
import time
from typing import List, Dict
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

class VideoService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.stability.ai/v2beta/image-to-video"

    async def generate_videos_from_images(self, image_files: List[bytes], duration_per_clip: int = 5) -> List[bytes]:
        """Generate videos from images using Stability AI"""
        videos = []
        
        for image in image_files:
            try:
                response = requests.post(
                    f"{self.base_url}",
                    headers=self.headers,
                    json={
                        "image": image,
                        "motion_bucket_id": 127,  # Controls motion intensity
                        "duration": duration_per_clip
                    }
                )
                response.raise_for_status()
                generation_id = response.json()["id"]

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
        transcript: Dict[str, any],
        output_path: str,
        transition_duration: float = 0.5
    ) -> str:
        """
        Assemble final video with audio, transitions, and synchronized captions
        """
        try:
            # 1. Load and process video clips
            video_clips = []
            for video_path in video_files:
                clip = VideoFileClip(video_path)
                # Add fade in/out transitions
                clip = clip.fadein(transition_duration).fadeout(transition_duration)
                video_clips.append(clip)
            
            # 2. Concatenate video clips with transitions
            final_video = mp.concatenate_videoclips(
                video_clips, 
                method="compose",
                transition=mp.VideoFileClip("crossfade", duration=transition_duration)
            )
            
            # 3. Process audio
            audio = AudioFileClip(audio_file)
            
            # 4. Adjust video duration to match audio if needed
            if final_video.duration != audio.duration:
                final_video = final_video.set_duration(audio.duration)
            
            # 5. Add audio to video
            final_video = final_video.set_audio(audio)
            
            # 6. Process captions from transcript segments
            subtitles = self._create_subtitles_from_transcript(
                transcript["segments"],
                final_video.size
            )
            
            # 7. Composite video with subtitles
            final = CompositeVideoClip([
                final_video,
                subtitles.set_position(('center', 'bottom'))
            ])
            
            # 8. Write final video with appropriate settings
            final.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                threads=4,
                preset='medium'
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Video assembly failed: {str(e)}")

    def _create_subtitles_from_transcript(
        self,
        segments: List[Dict],
        video_size: tuple
    ) -> SubtitlesClip:
        """Create synchronized subtitles from transcript segments"""
        subs = []
        for segment in segments:
            start = segment['start']
            end = segment['end']
            text = segment['text']
            
            txt_clip = TextClip(
                text,
                font='Arial',
                fontsize=24,
                color='white',
                bg_color='black',
                size=(video_size[0] * 0.8, None),
                method='caption'
            )
            
            subs.append(((start, end), txt_clip))
        
        return SubtitlesClip(subs) 