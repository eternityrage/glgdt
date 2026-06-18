import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()


def run_pipeline():
    print("\n" + "=" * 60)
    print("STARTING AUTOMATION PIPELINE")
    print("=" * 60 + "\n")

    print("STEP 1: Fetching video from Google Drive...")
    from google_drive_fetch import fetch_one_video_from_drive

    downloaded = fetch_one_video_from_drive(allow_repost=False)

    if not downloaded:
        print("\nNo new videos in Google Drive")
        print("REPOST MODE: Fetching random published video for repost...\n")

        downloaded = fetch_one_video_from_drive(allow_repost=True)

        if not downloaded:
            print("\nNo videos available to post. Pipeline complete.")
            print("Add new videos to Google Drive or check credentials")
            return

        print(f"\nRepost Mode: Using existing video\n")

    print(f"\nStep 1 complete: Video downloaded\n")

    print("STEP 2: Processing video (upscaling + watermark removal)...")
    from process_videos import process_single_video

    processed_video = process_single_video(downloaded)

    if not processed_video or not os.path.exists(processed_video):
        print("\nVideo processing failed!")
        sys.exit(1)

    print("\nStep 2 complete: Video processed\n")

    print("STEP 3: Uploading to social media platforms...")
    print("   Platforms: Instagram, Facebook, Threads, YouTube")
    print("\n" + "=" * 60 + "\n")

    from daily_publisher import main as publish_video
    sys.argv = ["daily_publisher.py", processed_video]
    publish_video()

    print("\n" + "=" * 60)
    print("AUTOMATION PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
