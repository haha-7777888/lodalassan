#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# This file is part of < https://github.com/TheAloneTeam/AloneMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/AloneMusic/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
import random
import re
from typing import Union

import aiohttp
import yt_dlp
from py_yt import VideosSearch
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, InlineKeyboardMarkup

from AloneMusic import LOGGER, app
from AloneMusic.utils.database import is_thumb_on
from AloneMusic.utils.formatters import time_to_seconds

YOUR_API_URL = None
FALLBACK_API_URL = "https://shrutibots.site"


async def load_api_url():
    global YOUR_API_URL
    logger = LOGGER("AloneMusic.platforms.Youtube.py")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://pastebin.com/raw/rLsBhAQa",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    YOUR_API_URL = content.strip()
                    logger.info("API URL loaded successfully")
                else:
                    YOUR_API_URL = FALLBACK_API_URL
                    logger.info("Using fallback API URL")
    except Exception:
        YOUR_API_URL = FALLBACK_API_URL
        logger.info("Using fallback API URL")


try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(load_api_url())
    else:
        loop.run_until_complete(load_api_url())
except RuntimeError:
    pass


def _normalize_youtube_url(link: str) -> str:
    """Accept a YouTube URL or video ID and return a canonical watch URL."""
    value = str(link or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    return f"https://www.youtube.com/watch?v={value}"


def _download_with_yt_dlp(link: str, video: bool = False):
    """Synchronous yt-dlp fallback, executed in a worker thread."""
    import glob

    url = _normalize_youtube_url(link)
    if not url:
        return None

    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "outtmpl": os.path.join(download_dir, "%(id)s.%(ext)s"),
        "overwrites": False,
        "retries": 2,
        "fragment_retries": 2,
        "socket_timeout": 30,
    }
    if video:
        options["format"] = "best[height<=720][ext=mp4]/best[ext=mp4]/best"
        options["merge_output_format"] = "mp4"
    else:
        options["format"] = "bestaudio/best"
        options["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = (info or {}).get("id")
            candidates = []
            if video_id:
                candidates.extend(glob.glob(os.path.join(download_dir, f"{video_id}.*")))
            # yt-dlp may return a final path even if the postprocessor changed the extension.
            prepared = ydl.prepare_filename(info) if info else None
            if prepared:
                candidates.extend([
                    prepared,
                    os.path.splitext(prepared)[0] + ".mp3",
                    os.path.splitext(prepared)[0] + ".mp4",
                    os.path.splitext(prepared)[0] + ".mkv",
                    os.path.splitext(prepared)[0] + ".webm",
                ])
            for candidate in dict.fromkeys(candidates):
                if candidate and os.path.isfile(candidate) and os.path.getsize(candidate) > 0:
                    if not video or os.path.splitext(candidate)[1].lower() in {
                        ".mp4", ".mkv", ".webm", ".mov"
                    }:
                        return candidate
    except Exception as exc:
        LOGGER("AloneMusic.platforms.Youtube.py").warning(
            f"yt-dlp fallback failed: {type(exc).__name__}: {exc}"
        )
    return None


async def download_song(link: str) -> str:
    global YOUR_API_URL

    value = str(link or "").strip()
    if not value:
        return None

    if not YOUR_API_URL:
        await load_api_url()
    if not YOUR_API_URL:
        YOUR_API_URL = FALLBACK_API_URL

    # Keep the configured download API as the first choice.
    video_id = value.split("v=")[-1].split("&")[0] if "v=" in value else value.rstrip("/").split("/")[-1]
    if not video_id or len(video_id) < 3:
        return None

    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    file_path = os.path.join(download_dir, f"{video_id}.mp3")
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{YOUR_API_URL}/download",
                params={"url": video_id, "type": "audio"},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("download_token")
                    if token:
                        async with session.get(
                            f"{YOUR_API_URL}/stream/{video_id}?type=audio",
                            headers={"X-Download-Token": token},
                            timeout=aiohttp.ClientTimeout(total=300),
                        ) as file_response:
                            if file_response.status == 200:
                                with open(file_path, "wb") as output:
                                    async for chunk in file_response.content.iter_chunked(16384):
                                        output.write(chunk)
                                if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                                    return file_path
    except Exception as exc:
        LOGGER("AloneMusic.platforms.Youtube.py").warning(
            f"Primary audio downloader failed: {type(exc).__name__}: {exc}"
        )

    return await asyncio.to_thread(_download_with_yt_dlp, _normalize_youtube_url(value), False)


async def download_video(link: str) -> str:
    global YOUR_API_URL

    value = str(link or "").strip()
    if not value:
        return None

    if not YOUR_API_URL:
        await load_api_url()
    if not YOUR_API_URL:
        YOUR_API_URL = FALLBACK_API_URL

    video_id = value.split("v=")[-1].split("&")[0] if "v=" in value else value.rstrip("/").split("/")[-1]
    if not video_id or len(video_id) < 3:
        return None

    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    file_path = os.path.join(download_dir, f"{video_id}.mp4")
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{YOUR_API_URL}/download",
                params={"url": video_id, "type": "video"},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("download_token")
                    if token:
                        async with session.get(
                            f"{YOUR_API_URL}/stream/{video_id}?type=video",
                            headers={"X-Download-Token": token},
                            timeout=aiohttp.ClientTimeout(total=600),
                        ) as file_response:
                            if file_response.status == 200:
                                with open(file_path, "wb") as output:
                                    async for chunk in file_response.content.iter_chunked(16384):
                                        output.write(chunk)
                                if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                                    return file_path
    except Exception as exc:
        LOGGER("AloneMusic.platforms.Youtube.py").warning(
            f"Primary video downloader failed: {type(exc).__name__}: {exc}"
        )

    return await asyncio.to_thread(_download_with_yt_dlp, _normalize_youtube_url(value), True)


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        title, duration_min, duration_sec, thumbnail, vidid = None, None, 0, None, None
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        title = None
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        duration = None
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        thumbnail = None
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            else:
                return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        playlist = await Playlist.get(link)
        if playlist:
            videos = []
            for video in playlist["videos"][:limit]:
                try:
                    duration = video.get("duration")
                    if duration:
                        duration_sec = int(time_to_seconds(duration))
                    else:
                        duration_sec = 0
                    videos.append(
                        {
                            "vidid": video["id"],
                            "title": video.get("title", "Unknown"),
                            "duration_min": duration,
                            "duration_sec": duration_sec,
                            "thumbnail": (
                                video.get("thumbnails", [{}])[0]
                                .get("url", "")
                                .split("?")[0]
                                if video.get("thumbnails")
                                else ""
                            ),
                        }
                    )
                except:
                    continue
            return videos
        return None

    async def get_related_videos(self, vidid: str):
        # Priority: Completely random category search for maximum variety as requested.
        # This breaks title-based looping.
        categories = [
            "Latest Hindi Songs",
            "Top Bollywood Hits",
            "Punjabi Mashup",
            "Lo-fi Hindi",
            "Indian Pop Songs",
            "New English Songs",
            "Top Global Hits",
            "Retro Bollywood Hits",
            "Indie India Music",
            "Trending Music India",
        ]
        try:
            query = random.choice(categories)
            results = VideosSearch(query, limit=20)
            related = []
            for result in (await results.next())["result"]:
                if result["id"] != vidid:
                    related.append(result["id"])
            if related:
                return related
        except:
            pass

        # Fallback 1: Using YouTube Radio Mix (RD Mix)
        url = f"https://www.youtube.com/watch?v={vidid}&list=RD{vidid}"
        ydl_opts = {
            "quiet": True,
            "extract_flat": "in_playlist",
            "playlist_items": "2-10",
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )
                if "entries" in info:
                    ids = [
                        e["id"]
                        for e in info["entries"]
                        if e.get("id") and e["id"] != vidid
                    ]
                    if ids:
                        return ids
        except:
            pass

        # Final Fallback: Search by title if broad search and RD mix fail
        title = await self.title(vidid, True)
        if title:
            try:
                results = VideosSearch(f"{title} related songs", limit=6)
                related = []
                for result in (await results.next())["result"]:
                    if result["id"] != vidid:
                        related.append(result["id"])
                if related:
                    return related
            except:
                pass
        return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        title, duration_min, vidid, yturl, thumbnail = None, None, None, None, None
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except:
                    continue
        return formats_available, link

    async def slider(
        self, link: str, query_type: int, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        if mystic:
            try:
                from strings import get_string
                from AloneMusic.utils.database import get_lang
                language = await get_lang(mystic.chat.id)
                _ = get_string(language)
                try:
                    await mystic.edit_caption(caption=_["call_7"])
                except Exception:
                    try:
                        await mystic.edit_text(text=_["call_7"])
                    except Exception:
                        pass
            except Exception:
                pass

        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True
            else:
                return None, False
        except Exception:
            return None, False
