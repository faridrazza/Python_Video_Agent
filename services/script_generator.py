import openai
from typing import Dict, Optional

class ScriptGenerator:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        
    async def generate_script(self, topic: str, format_type: str, duration: int) -> Dict[str, str]:
        """
        Generate a video script using ChatGPT
        
        Args:
            topic: Main topic of the video
            format_type: Type of video (educational, entertainment, etc.)
            duration: Approximate duration in minutes
            
        Returns:
            Dict containing script and metadata
        """
        prompt = f"""Create a {duration}-minute video script about {topic}.
        Format: {format_type}
        Include:
        1. Introduction
        2. Main content
        3. Conclusion
        4. Natural transitions
        Also provide timestamps for each section."""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional video script writer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            script = response.choices[0].message.content
            
            # Generate title and description
            metadata = await self._generate_metadata(script)
            
            return {
                "script": script,
                "title": metadata["title"],
                "description": metadata["description"]
            }
            
        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")
    
    async def _generate_metadata(self, script: str) -> Dict[str, str]:
        """Generate video title and description based on the script"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Generate an engaging title and description for this video script."},
                    {"role": "user", "content": script}
                ]
            )
            
            metadata = response.choices[0].message.content
            # Parse the response to extract title and description
            # Assuming the response is formatted as "Title: xxx\nDescription: yyy"
            lines = metadata.split("\n")
            title = lines[0].replace("Title: ", "")
            description = "\n".join(lines[1:]).replace("Description: ", "")
            
            return {
                "title": title,
                "description": description
            }
            
        except Exception as e:
            raise Exception(f"Metadata generation failed: {str(e)}") 