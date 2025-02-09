from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Dict, Optional

class PublishingService:
    def __init__(self, youtube_client_id: str, youtube_client_secret: str, youtube_api_key: str):
        self.client_id = youtube_client_id
        self.client_secret = youtube_client_secret
        self.api_key = youtube_api_key
        self.youtube_service = self._setup_youtube()

    def _setup_youtube(self):
        """Setup YouTube API client"""
        try:
            # OAuth flow for upload permissions
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": ["http://localhost:8080"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                ['https://www.googleapis.com/auth/youtube.upload']
            )
            credentials = flow.run_local_server(
                port=8080,
                success_message="Authentication successful! You can close this window."
            )
            return build('youtube', 'v3', credentials=credentials)
        except Exception as e:
            raise Exception(f"YouTube service setup failed: {str(e)}")

    async def upload_to_youtube(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        privacy_status: str = 'private'
    ) -> str:
        """Upload video to YouTube"""
        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }

            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True
            )

            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = request.execute()
            return f"https://youtube.com/watch?v={response['id']}"

        except Exception as e:
            raise Exception(f"YouTube upload failed: {str(e)}") 





#             import requests
# from typing import Dict
#     def __init__(self, youtube_credentials_path: str, instagram_api_key: str):
#         self.youtube_service = self._setup_youtube(youtube_credentials_path)
#         self.instagram_api_key = instagram_api_key
#         self.instagram_base_url = "https://graph.instagram.com/v12.0"
#     def _setup_youtube(self, credentials_path: str):
#         SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
#         flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
#         credentials = flow.run_local_server(port=0)
#         return build('youtube', 'v3', credentials=credentials)
#         tags: list
#                     'privacyStatus': 'private',  # or 'public', 'unlisted'
#             raise Exception(f"YouTube upload failed: {str(e)}")

#     async def upload_to_instagram(
#         self,
#         video_path: str,
#         caption: str
#     ) -> str:
#         """Upload video to Instagram"""
#         try:
#             # First, create container
#             container_response = requests.post(
#                 f"{self.instagram_base_url}/me/media",
#                 params={
#                     "access_token": self.instagram_api_key,
#                     "media_type": "VIDEO",
#                     "video_url": video_path,
#                     "caption": caption
#                 }
#             )
#             container_response.raise_for_status()
#             creation_id = container_response.json()["id"]

#             # Then publish the container
#             publish_response = requests.post(
#                 f"{self.instagram_base_url}/me/media_publish",
#                 params={
#                     "access_token": self.instagram_api_key,
#                     "creation_id": creation_id
#                 }
#             )
#             publish_response.raise_for_status()
            
#             return f"https://instagram.com/p/{publish_response.json()['id']}"

#         except Exception as e:
#             raise Exception(f"Instagram upload failed: {str(e)}") 