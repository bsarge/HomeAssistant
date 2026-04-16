import requests
import time
from bs4 import BeautifulSoup
import os
import subprocess
from urllib.parse import urlparse

# Replace with your Roku's IP address
ROKU_IP = "192.168.1.100"  # Change to your Roku's actual IP
STREAM_PAGE_URL = "https://ascensionlutheran.com/church-service-video-streams/"

# Step 1: Get the YouTube Livestream Link
def get_youtube_live_url():
    response = requests.get(STREAM_PAGE_URL)
    if response.status_code != 200:
        print("Failed to access website.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the first button/link that contains a YouTube URL
    for link in soup.find_all("a", href=True):
        if "youtube.com" in link["href"]:
            url = link["href"]
            parsed_url = urlparse(url)
            video_id = parsed_url.path.split("/")[-1]
            return video_id

    print("No livestream link found.")
    return None

# Step 2: Send commands to Roku to open YouTube
def send_roku_command(command):
    url = f"http://{ROKU_IP}:8060/keypress/{command}"
    requests.post(url)

# Step 3: Automate YouTube Search on Roku
def search_youtube_on_roku(video_title):
    send_roku_command("Home")  # Go to Roku home screen
    time.sleep(2)
    send_roku_command("Launch/837")  # Open YouTube (App ID: 837)
    time.sleep(5)  # Wait for YouTube to open

    # Simulate typing the search term (video title)
    for char in video_title:
        send_roku_command(f"LIT_{char}")  # LIT_ sends text to Roku
        time.sleep(0.2)

    send_roku_command("Enter")  # Press Enter to search
    time.sleep(2)
    send_roku_command("Enter")  # Press Enter again to play the first result


def send_adb_command(channel_id):
    """Send an ADB command to the Android TV through Home Assistant."""
    url = "http://10.0.0.30:8123/api/services/androidtv.adb_command"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2YTE1OTliYTU1MDg0ODYyYmU2NjM0NWIwMGNlMTQyYiIsImlhdCI6MTc0MzAyMDA1NywiZXhwIjoyMDU4MzgwMDU3fQ.kfXEpiehopnl4O_1xYjoEt1Kl022hKk_7ClwBxEcjM8"

    ANDROID_TV_ENTITY =  "media_player.fire_tv_10_0_0_21" # "2a0cb820361bd742567b567cb4c775b9"  "media_player.fire_tv_10_0_0_21"
    ADB_COMMAND = f"am start -a android.intent.action.VIEW -d https://www.youtube.com/watch?v={channel_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "entity_id": f"{ANDROID_TV_ENTITY}",
        "command": f"{ADB_COMMAND}"
    }

    print(f"data: {data}")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("✅ YouTube channel launched successfully!")
    else:
        print(f"❌ Failed to launch YouTube: {response.text}")


# Run the script
latest_video = get_youtube_live_url()
if latest_video:
#    print(f"Playing: {latest_video} on Roku...")
#    search_youtube_on_roku(latest_video)
    # print(f"{latest_video}")
    send_adb_command(latest_video)
else:
    print("No latest video found.")
