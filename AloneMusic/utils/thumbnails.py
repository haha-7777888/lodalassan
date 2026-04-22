#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# This file is part of < https://github.com/TheAloneTeam/AloneMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/AloneMusic/blob/master/LICENSE >
#
# All rights reserved.

import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight), Image.LANCZOS)

async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub(r"\W+", " ", title).title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")

        # Configuration
        GLOW_COLOR = "#ff0099"  
        BORDER_COLOR = "#FF1493"  
        
        # Background Processing
        image1 = changeImageSize(1280, 720, youtube)
        # REMOVED: image1 = image1.filter(ImageFilter.GaussianBlur(20)) <-- This was the "spoiler" blur
        image1 = ImageEnhance.Brightness(image1).enhance(0.6) # Slightly brighter background

        thumb_width, thumb_height = 840, 460
        youtube_thumb = youtube.resize((thumb_width, thumb_height), Image.LANCZOS)

        # Create Rounded Corner Mask
        mask = Image.new("L", (thumb_width, thumb_height), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([(0, 0), (thumb_width, thumb_height)], radius=25, fill=255)
        youtube_thumb.putalpha(mask)

        center_x, center_y_img = 640, 300
        thumb_x = center_x - (thumb_width // 2)
        thumb_y = center_y_img - (thumb_height // 2)
        thumb_x2, thumb_y2 = thumb_x + thumb_width, thumb_y + thumb_height

        # Aesthetic Glow Effect
        glow_layer = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        draw_glow = ImageDraw.Draw(glow_layer)
        draw_glow.rounded_rectangle(
            [(thumb_x - 15, thumb_y - 15), (thumb_x2 + 15, thumb_y2 + 15)],
            radius=35, fill=GLOW_COLOR
        )
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(25))
        image1.paste(glow_layer, (0, 0), glow_layer)

        # Border
        border_layer = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        draw_border = ImageDraw.Draw(border_layer)
        draw_border.rounded_rectangle(
            [(thumb_x - 5, thumb_y - 5), (thumb_x2 + 5, thumb_y2 + 5)],
            radius=30, fill=BORDER_COLOR
        )
        image1.paste(border_layer, (0, 0), border_layer)
        image1.paste(youtube_thumb, (thumb_x, thumb_y), youtube_thumb)

        draw = ImageDraw.Draw(image1)
        try:
            font_title = ImageFont.truetype("AloneMusic/assets/font.ttf", 45)
            font_details = ImageFont.truetype("AloneMusic/assets/font2.ttf", 30)
        except:
            font_title = ImageFont.load_default()
            font_details = ImageFont.load_default()

        # Title Rendering
        if len(title) > 40:
            title = title[:40] + "..."
        
        # Center the text
        w_title = draw.textbbox((0, 0), title, font=font_title)[2]
        text_y_pos = thumb_y2 + 50
        
        draw.text(((1280 - w_title) / 2, text_y_pos), title, fill="white", font=font_title, stroke_width=2, stroke_fill="black")

        # Stats Rendering
        stats_text = f"⚡ {views} Views  |  🕒 {duration}  |  🎸 @aashikmusicbot"
        w_stats = draw.textbbox((0, 0), stats_text, font=font_details)[2]
        draw.text(((1280 - w_stats) / 2, text_y_pos + 65), stats_text, fill=BORDER_COLOR, font=font_details, stroke_width=1, stroke_fill="black")

        # Clean and Save
        if os.path.exists(f"cache/thumb{videoid}.png"):
            os.remove(f"cache/thumb{videoid}.png")

        file_name = f"cache/{videoid}.png"
        image1.save(file_name)
        return file_name

    except Exception as e:
        print(f"Error generating thumb: {e}")
        return YOUTUBE_IMG_URL

async def get_qthumb(vidid):
    try:
        url = f"https://www.youtube.com/watch?v={vidid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
