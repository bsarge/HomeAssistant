import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
import os
import subprocess
from urllib.parse import urlparse
import requests

async def get_youtube_id():
    STREAM_PAGE_URL = "https://ascensionlutheran.com/church-service-video-streams/"

    async with aiohttp.ClientSession() as session:
            async with session.get(STREAM_PAGE_URL) as resp:
                page = await resp.text()
                soup = BeautifulSoup(page, "html.parser")

    # response = requests.get(STREAM_PAGE_URL)
    # if response.status_code != 200:
    #     print("Failed to access website.")
    #     return None

    # soup = BeautifulSoup(response.text, "html.parser")

    # Find the first button/link that contains a YouTube URL
    video_id = None
    for link in soup.find_all("a", href=True):
        if "youtube.com" in link["href"]:
            url = link["href"]
            parsed_url = urlparse(url)
            video_id = parsed_url.path.split("/")[-1]
            break

    return video_id


# http://192.168.1.100:8060/launch/837?contentID=zn2RqCQxVd4&MediaType=live

async def lauch_youtube(video_id):
    # http://10.0.0.37:8060/launch/837?contentID=zn2RqCQxVd4
    # video_id = "eG7yj9CSkqo"
    roku_url = f"http://10.0.0.4:8060/launch/837?contentID={video_id}" #&MediaType=live

    async with aiohttp.ClientSession() as session:
            await session.post(roku_url)


async def test_with_alexa_message(video_id):
    url = "http://10.0.0.30:8123/api/services/notify/alexa_media"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwYmY1ZjA4ODM1NTc0Y2VhOTZkMDYwMGRmN2NiNmFlZSIsImlhdCI6MTc0MzAyMzAzMSwiZXhwIjoyMDU4MzgzMDMxfQ.N1tFBvXmFYDi53TmYVR8hHGTk_f6VN0DTCl35DuIabo"

    ALEXA_ENTITY = "media_player.gloria_s_echo"
    message = f"video id is {video_id}"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "message": message,
        "target": ALEXA_ENTITY,
        "data": {"type": "tts"},  # Text-to-Speech
    }
    async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as resp:
                # Print response
                if resp.status == 200:
                    print("Message sent successfully!")
                else:
                    print(f"Failed to send message: {resp.text}")

@service
async def play_church_on_roku():
    id = await get_youtube_id()
    if (id):
        await lauch_youtube(id)
        # await test_with_alexa_message(id)
    else:
        print("did not find video")

def is_event_loop_running():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


if is_event_loop_running():
    play_church_on_roku()
else:
    asyncio.run(play_church_on_roku())
