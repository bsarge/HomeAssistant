# Overview

The goal of this project was to provide a way for my mother, who is 94 and blind, to listen to the church's service from her home. The service is streamed every Sunday morning using a live YouTube channel. The URL changes each week so I was not able to use a simple Alexa routine to start YouTube with a static URL. I initially setup a laptop with a link to the page with the live YouTube channel but she found it difficult to use. I came up with a solution that lets her say "Alexa Start Church" which turns on her TV and sends a command to her Roku to open YouTube and play the live stream.

# The journey

When I found Mike Grant's Haaska Home Assistant integration with Alexa I realized I could write a custom Alexa skill that calls Home Assistant. I wrote a python script that scrapes the church's website for the URL and sends a command to Roku to start the video. Once that was working it was just a matter of getting the Haaska integration to trigger the script. This was accomplished by using an input_boolean and an automation triggered when the intput_boolean was turned on and executes the python script.

# Design summary

- A custom AWS Alexa skill calls the Home Assistant server.
- The HA Haaska integration turns on an input_boolean which generates an event.
- Automation triggerend on the event executes a python script.
- The scrpt:
  - Scrapes the church's website for the YouTube URL
  - Parses the vidio ID from the URL
  - Turns on Roku
  - Launches YouTube with the church's live vidio ID.


# Automation
| Component                   |  Trigger                 | Action                        | Dependencies |
| --------------------------- | ------------------------ | ----------------------------- | ------------ |
| Alexa Smart Home Skill      | say "Alexa Start Church" | Trigger AWS Smart Home Lambda | Alexa        |
| AWS Alexa Smart Home Lambda | Alexa Smart Home Skill   | Call HA Alexa Integration     | AWS          |
| HA Alexa integration        | AWS Lambda call          | input_boolean.turn_on         | HA           |
| Start Church On Roku        | event Turn On Boolean    | See play_church_on_ruku.py    | Python       |
| Roku                        | Python code              | Turn on & start video         | YouTube      |

# Activity Log Example

1. Start Church on Roku turned on triggered by action Input boolean: Turn on input boolean
2. Amazon Alexa sent command Alexa.PowerController/TurnOn for Start Church on Roku triggered by action 3. 3. Input boolean: Turn on input boolean
4. Start Church on Roku turned off triggered by automation Trigger Church Video on Roku triggered by state of Start Church on Roku
5. Trigger Church Video on Roku triggered by action Input boolean: Turn on input boolean
6. Roku turned on
7. Roku changed to Playing

# Implementation

This is a recommended approach to implementing "Start Church". It builds and tests each componenet step=by=step. 

## 1. Install PyScript on Home Assistant
https://github.com/custom-components/pyscript

## 2. play_church_on_ruku.py
This python script scrapes the Axcention Lutheran Church website for the youtube video ID.
It starts YouTube on Roku and plays the vido. Test using scripts.yaml

```
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
    roku_url = f"http://10.0.0.4:8060/launch/837?contentID={video_id}" 

    async with aiohttp.ClientSession() as session:
            await session.post(roku_url)


@service
async def play_church_on_roku():
    id = await get_youtube_id()
    if (id):
        await lauch_youtube(id)
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

```
## 3. scripts.yaml
Use this script to test the python code

```
start_church:
  alias: "Start Church Script"
  sequence:
    - service: pyscript.play_church_on_roku
```

## 4. Helper Switch
Add Helper Switch and "Trigger Church Video on Roku" to Automation.yaml. Test by manually turning switch on and off. I recommend using the UI to create the switch.
The switch is available in Helpers, can be added to a Dashboard and can be manually turned on for testing.

![alt text](image.png)

If you prefer using YAML use the following.
Use either the UI or YAML, Do not add both!

```
input_boolean:
  start_church_on_roku:
    name: Start Church On Roku
    icon: mdi:toggle-switch
```

## 5. Automation.yaml
This automation is triggered when input_boolean.start_church_on_roku is turned on. 
It executes yscript.play_church_on_roku and turns input_boolean.start_church_on_roku off. 
Test by turning Helper switch on and off (input_boolean.start_church_on_roku)

```
- id: '1743079221742'
  alias: Trigger Church Video on Roku
  description: 'When switch is turned on execute script and turn the switch off'
  triggers:
  - entity_id:
    - input_boolean.start_church_on_roku
    to: 'on'
    trigger: state
  actions:
  - action: pyscript.play_church_on_roku
    data: {}
  - delay: 00:00:05
  - action: input_boolean.turn_off
    metadata: {}
    data: {}
    target:
      entity_id: input_boolean.start_church_on_roku
```

## 6. Amazon Alexa Smart Home Skill (Haaska)
Carefully follow these instructions to setup the AWS Smart Home skill using Haaska.
I recommend using the Simple Method rather than building from source but either should work.
settingup haaska: https://github.com/mike-grant/haaska/wiki

## 7. Configuration.yaml
In the previous step you should have added alexa: smart_home to the Configuration.yaml file. Now add the entity input_boolean.start_church_on_roku, it is turned on by default.


```
alexa:
  smart_home:
    client_id: https://pitangui.amazon.com/
    client_secret: {client secret}
    filter:
      include_entities:
        - input_boolean.start_church_on_roku
```
