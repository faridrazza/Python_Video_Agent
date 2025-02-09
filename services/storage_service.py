from google.cloud import storage
from google.cloud.storage import Bucket, Blob
import os
from typing import Optional
from google.oauth2 import service_account
import json
from datetime import datetime, timedelta

class StorageService:
    def __init__(self, client_email: str, private_key: str):
        """Initialize storage service with credentials"""
        try:
            credentials = service_account.Credentials.from_service_account_info({
                "type": "service_account",
                "project_id": "your-project-id",  # Your project ID
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            })
            self.client = storage.Client(
                project="educationalai-446710",  # Your project ID
                credentials=credentials
            )
        except Exception as e:
            raise Exception(f"Storage service initialization failed: {str(e)}")

    def upload_file(self, bucket_name: str, source_file_path: str, destination_blob_name: str) -> str:
        """Upload a file to GCS and return its signed URL"""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            # Upload the file
            blob.upload_from_filename(source_file_path)
            
            # Generate a signed URL that expires in 7 days
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            
            print(f"File {source_file_path} uploaded to {bucket_name}/{destination_blob_name}")
            return url
            
        except Exception as e:
            raise Exception(f"File upload failed: {str(e)}")

    def download_file(self, bucket_name: str, source_blob_name: str, destination_file_path: str) -> None:
        """Download a file from GCS"""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            
            # Download the file
            blob.download_to_filename(destination_file_path)
            print(f"File {source_blob_name} downloaded to {destination_file_path}")
            
        except Exception as e:
            raise Exception(f"File download failed: {str(e)}")

    def check_bucket_access(self, bucket_name: str) -> bool:
        """Verify access to the bucket"""
        try:
            bucket = self.client.bucket(bucket_name)
            return bucket.exists()
        except Exception as e:
            print(f"Bucket access check failed: {str(e)}")
            return False 