import os
import requests
from pathlib import Path
from dotenv import load_dotenv

def upload_to_tiktok(video_path, description):
    print(f"Uploading {video_path} to TikTok with description: {description}")
    return {"status": "success", "platform": "tiktok"}
