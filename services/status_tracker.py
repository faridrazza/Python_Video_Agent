from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Dict, List

class StatusTracker:
    def __init__(self, client_email: str, private_key: str, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.service = self._setup_sheets(client_email, private_key)

    def _setup_sheets(self, client_email: str, private_key: str):
        """Setup Google Sheets API client"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": "your-project-id",
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            },
            scopes=SCOPES
        )
        return build('sheets', 'v4', credentials=credentials)

    async def update_status(
        self,
        video_id: str,
        status: Dict[str, str]
    ) -> None:
        """Update video status in Google Sheets"""
        try:
            # Prepare row data
            row_data = [
                video_id,
                status.get('script_status', ''),
                status.get('audio_url', ''),
                status.get('transcript_status', ''),
                status.get('images_status', ''),
                status.get('video_status', ''),
                status.get('youtube_url', ''),
                status.get('creation_date', ''),
                status.get('notes', '')
            ]

            # Append row to sheet
            request = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1',  # Update with your sheet name
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            )
            request.execute()

        except Exception as e:
            raise Exception(f"Status update failed: {str(e)}")

    async def get_status(self, video_id: str) -> Dict[str, str]:
        """Get video status from Google Sheets"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1'  # Update with your sheet name
            ).execute()
            
            rows = result.get('values', [])
            for row in rows:
                if row[0] == video_id:
                    return {
                        'video_id': row[0],
                        'script_status': row[1],
                        'audio_url': row[2],
                        'transcript_status': row[3],
                        'images_status': row[4],
                        'video_status': row[5],
                        'youtube_url': row[6],
                        'creation_date': row[7],
                        'notes': row[8]
                    }
                    
            return None

        except Exception as e:
            raise Exception(f"Status retrieval failed: {str(e)}") 