import os
from typing import Dict
import logging
from datetime import datetime

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_temp_directory():
    """Create temporary directory for file processing"""
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir

def generate_unique_id() -> str:
    """Generate a unique ID for each video project"""
    return f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def cleanup_temp_files(directory: str):
    """Clean up temporary files after processing"""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}") 