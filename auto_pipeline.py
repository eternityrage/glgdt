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

    print("STEP 1.5: Fetching audio track from Google Drive...")
    from google_drive_fetch import fetch_one_audio_from_drive

    audio_track = fetch_one_audio_from_drive()
    if audio_track:
        print(f"Audio track ready: {os.path.basename(audio_track)}\n")
    else:
        print("No audio track fetched - will keep original video audio (if any).\n")

    print("STEP 2: Processing video (upscaling + watermark removal + audio overlay)...")
    from process_videos import process_single_video

    processed_video = process_single_video(downloaded, audio_track)

    if not processed_video or not os.path.exists(processed_video):
        print("\nVideo processing failed!")
        sys.exit(1)

    print("\nStep 2 complete: Video processed\n")

    print("STEP 2b: Verifying video resolution...")
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        processed_video
    ]
    import subprocess
    try:
        res = subprocess.check_output(cmd_probe).decode("utf-8").strip()
        pw, ph = map(int, res.split("x"))
        if pw != 1080 or ph != 1920:
            print(f"⚠️  WARNING: Processed video is {pw}x{ph}, expected 1080x1920")
            print(f"   Videos may appear stretched on Facebook/Instagram")
        else:
            print(f"✅ Resolution verified: {pw}x{ph} (correct)")
    except Exception as e:
        print(f"⚠️  Could not verify resolution: {e}")
    print("")

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
