from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", 32076000))
        self.API_HASH = getenv("API_HASH", "22adb8c3d3f905d09fe41cf4ae805b71")

        self.BOT_TOKEN = getenv("BOT_TOKEN", "9160938427:AAGrX0KSGSThbx3wh1ibGHUrFVCS6CjvavY")
        self.MONGO_URL = getenv("MONGO_URL", "mongodb+srv://public:abishnoimf@cluster0.rqk6ihd.mongodb.net/?retryWrites=true&w=majority")

        self.LOGGER_ID = int(getenv("LOGGER_ID", -1003150808065))
        self.OWNER_ID = int(getenv("OWNER_ID", 8516736963))

        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", 60)) * 60
        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", 20))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", 20))

        self.SESSION1 = getenv("SESSION", "BAIgI4sAqBGlPQAYu39MR0OcmFCRj-x9i9ggs7IxaEnDi4tco-A-oUW8aSC7hLXkaqEAtp88RaxlANlEFBKFqoUTY2WO6hkwF1AegXtaKqVJl9MIi-k72bSG4GDT1dKwuaexTJ4sb6-icn3HT0uAfDVZQTQKcT9lyYTg2TMoZXAO3A2Z_3mCtHXjZBerUglQdJxJR9FchqcOA-DvFklYyqe08k3EHL0FROtnLFgCmmauPXm5Uo3WHKGF4M4Gkcl1mbuvhD1N1ycDCcWXZx5c51lh42rEukTQKA2S6QMARWxXNnNCQPNk5gVHKJDCZrtnsJl9Zg1WABQs1D-BzYMMepVKfrbpgQAAAAIJ678XAA")
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/Senpai_Updates")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/THE_DRAGON_SUPPORT")

        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "False").lower() == "true"
        self.AUTO_END: bool = getenv("AUTO_END", "False").lower() == "true"

        self.THUMB_GEN: bool = getenv("THUMB_GEN", "False").lower() == "true"
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "False").lower() == "true"

        self.LANG_CODE = getenv("LANG_CODE", "en")

        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "https://batbin.me/logomancy").split(" ")
            if url and "batbin.me" in url
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/z4tco8.jpg")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/unu7ar.jpg")

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
