# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
import time
from pathlib import Path

from py_yt import Playlist, VideosSearch

from anony import logger
from anony.helpers import Track, utils


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.iregex = re.compile(
            r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)"
            r"(?!/(watch\?v=[A-Za-z0-9_-]{11}|shorts/[A-Za-z0-9_-]{11}"
            r"|playlist\?list=PL[A-Za-z0-9_-]+|[A-Za-z0-9_-]{11}))\S*"
        )

    def get_cookies(self):
        if not self.checked:
            if os.path.exists(self.cookie_dir):
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(f"{self.cookie_dir}/{file}")
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        os.makedirs(self.cookie_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            for url in urls:
                name = url.split("/")[-1]
                link = "https://batbin.me/raw/" + name
                async with session.get(link) as resp:
                    resp.raise_for_status()
                    with open(f"{self.cookie_dir}/{name}.txt", "wb") as fw:
                        fw.write(await resp.read())
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def invalid(self, url: str) -> bool:
        return bool(re.match(self.iregex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
        except Exception:
            return None
        if results and results["result"]:
            data = results["result"][0]
            duration = data.get("duration") or "00:00"
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=duration,
                duration_sec=utils.to_seconds(duration),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        return None

    async def autoplay(self, video_id: str, history: set[str], video: bool = False) -> Track | None:
        try:
            def _extract_mix():
                opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "extract_flat": True,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "playlistend": 15,
                }
                if cookie := self.get_cookies():
                    opts["cookiefile"] = cookie
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(
                        f"{self.base}{video_id}&list=RD{video_id}", download=False
                    )

            info = await asyncio.to_thread(_extract_mix)
        except Exception:
            return None

        entries = info.get("entries") if info else None
        if not entries:
            return None

        for entry in entries:
            item_id = entry.get("id")
            duration_sec = int(entry.get("duration") or 0)
            if not item_id or item_id == video_id or item_id in history or not duration_sec:
                continue

            return Track(
                id=item_id,
                channel_name=entry.get("uploader") or "",
                duration=time.strftime("%M:%S", time.gmtime(duration_sec)),
                duration_sec=duration_sec,
                title=entry.get("title", "")[:25],
                thumbnail=(entry.get("thumbnail") or "").split("?")[0],
                url=self.base + item_id,
                view_count=str(entry.get("view_count", "")),
                video=video,
            )
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                duration = data.get("duration") or "00:00"
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=duration,
                    duration_sec=utils.to_seconds(duration),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception:
            pass
        return tracks
async def download(self, video_id: str, video: bool = False) -> str | None:
        url = self.base + video_id
        os.makedirs("downloads", exist_ok=True)

        for existing in Path("downloads").glob(f"{video_id}.*"):
            if video and existing.suffix == ".mp4":
                return str(existing)
            if not video and existing.suffix in {".webm", ".m4a", ".opus", ".mp3", ".mp4"}:
                return str(existing)

        cookie = self.get_cookies()

        attempts = [
            # Attempt 1: TV / Web Safari with cookies
            {
                "cookiefile": cookie,
                "extractor_args": {"youtube": {"player_client": ["tv", "web_safari", "mweb"]}},
            },
            # Attempt 2: Android / iOS WITHOUT cookies (mobile clients reject browser cookies)
            {
                "extractor_args": {"youtube": {"player_client": ["android", "ios"]}},
            },
        ] if cookie else [
            {
                "extractor_args": {"youtube": {"player_client": ["tv", "android", "ios"]}},
            }
        ]

        def _download():
            for extra_opts in attempts:
                ydl_opts = {
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "quiet": True,
                    "noplaylist": True,
                    "geo_bypass": True,
                    "no_warnings": True,
                    "overwrites": False,
                    "nocheckcertificate": True,
                    "remote_components": ["ejs:github"],
                    **extra_opts,
                }
                if video:
                    ydl_opts["format"] = "bestvideo[height<=?720]+bestaudio/best[height<=?720]/best"
                    ydl_opts["merge_output_format"] = "mp4"
                else:
                    ydl_opts["format"] = "bestaudio/best"

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=True)
                        if info:
                            downloaded = ydl.prepare_filename(info)
                            if Path(downloaded).exists():
                                return downloaded
                    except Exception as ex:
                        logger.warning("Download attempt failed: %s", ex)
                        continue

                for file in Path("downloads").glob(f"{video_id}.*"):
                    if file.exists():
                        return str(file)
            return None

        return await asyncio.to_thread(_download)
