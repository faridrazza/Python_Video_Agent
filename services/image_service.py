import requests
from typing import List, Dict
import openai

class ImageService:
    def __init__(self, together_api_key: str, openai_api_key: str):
        self.together_api_key = together_api_key
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {together_api_key}",
            "Content-Type": "application/json"
        }

    async def generate_image_prompts(self, transcript: str, num_scenes: int = 10) -> List[str]:
        """Generate image prompts based on transcript sections"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create detailed image generation prompts based on this transcript."},
                    {"role": "user", "content": f"Create {num_scenes} detailed image prompts for this transcript: {transcript}"}
                ]
            )
            
            prompts = response.choices[0].message.content.split("\n")
            return [p.strip() for p in prompts if p.strip()]
            
        except Exception as e:
            raise Exception(f"Prompt generation failed: {str(e)}")

    async def generate_images(self, prompts: List[str]) -> List[bytes]:
        """Generate images using Together AI"""
        images = []
        
        for prompt in prompts:
            try:
                response = requests.post(
                    "https://api.together.xyz/inference",
                    headers=self.headers,
                    json={
                        "model": "stabilityai/stable-diffusion-xl-base-1.0",
                        "prompt": prompt,
                        "negative_prompt": "blurry, low quality, distorted",
                        "width": 1024,
                        "height": 1024,
                        "num_inference_steps": 50
                    }
                )
                response.raise_for_status()
                images.append(response.content)
                
            except Exception as e:
                raise Exception(f"Image generation failed for prompt: {prompt}. Error: {str(e)}")
        
        return images 