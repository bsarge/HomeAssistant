import subprocess
import sys

if len(sys.argv) > 1:
    youtube_url = sys.argv[1]
    print(f"url is {youtube_url}")
else:
    print("video id argument missing")
    exit()

send_firetv_command(youtube_url):
    FIRETV_IP = "10.0.0.21"  # Update this
    # Connect to Fire TV (if not already connected)
    subprocess.run(["adb", "connect", FIRETV_IP])
    YOUTUBE_INTENT = f"am start -a android.intent.action.VIEW \
                    -d \"{youtube_url}\""
    subprocess.run(["adb", "shell", YOUTUBE_INTENT])

# Open YouTube video
# YOUTUBE_VIDEO_ID = "Dc6wcbcgI3E"
# YOUTUBE_INTENT = f"am start -a android.intent.action.VIEW \
#                 -d \"https://www.youtube.com/watch?v={video_id}\""




print("YouTube video should be playing on Fire TV.")
