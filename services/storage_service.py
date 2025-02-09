from google.cloud import storage
from google.cloud.storage import Bucket, Blob
import os
from typing import Optional

class StorageService:
    def __init__(self, credentials_path: str):
        self.client = storage.Client.from_service_account_json(credentials_path)
        
    def upload_file(self, bucket_name: str, source_file_path: str, destination_blob_name: str) -> str:
        """
        Upload a file to GCS and return its public URL
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            blob.upload_from_filename(source_file_path)
            
            # Make the blob publicly accessible
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            raise Exception(f"File upload failed: {str(e)}")
    
    def download_file(self, bucket_name: str, source_blob_name: str, destination_file_path: str) -> None:
        """
        Download a file from GCS
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            
            blob.download_to_filename(destination_file_path)
            
        except Exception as e:
            raise Exception(f"File download failed: {str(e)}") 