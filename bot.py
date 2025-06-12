# -*- coding: utf-8 -*-
import asyncio
import json
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters.command import Command
from aiogram.types import Message, FSInputFile
from yt_dlp import YoutubeDL

API_TOKEN = "7353528532:AAHFKC7JcAujOSdHJ3BOk1NJ9nRwLU5-PB8"  # <<<<< Bu yerga o‘z bot tokeningizni yozing

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

USER_DB = "users.json"

# Foydalanuvchilarni fayldan o‘qish
def load_users():
    try:
        with open(USER_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Foydalanuvchilarni faylga yozish
def save_users(users):
    with open(USER_DB, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

users = load_users()

# Har bir foydalanuvchi uchun limitni tekshirish
def check_and_update_limit(user_id):
    today = datetime.now().date().isoformat()
    user_data = users.get(str(user_id), {"downloads": 0, "last_reset": today, "premium": False})

    if user_data["last_reset"] != today:
        user_data["downloads"] = 0
        user_data["last_reset"] = today

    if not user_data.get("premium", False) and user_data["downloads"] >= 2:
        return False, user_data

    user_data["downloads"] += 1
    users[str(user_id)] = user_data
    save_users(users)
    return True, user_data

# /start buyrug‘iga javob
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(f"👋 Salom, {message.from_user.first_name}!\n"
                         f"🎥 Video yuklash uchun YouTube, TikTok yoki Instagram link yuboring.")

# Linkni qabul qilib, video yuklash
@dp.message(F.text)
async def download_handler(message: Message):
    user_id = message.from_user.id
    allowed, user_data = check_and_update_limit(user_id)

    if not allowed:
        await message.answer("🚫 Siz bugun 2 ta videoni yuklab bo'ldingiz.\nPremium uchun admin bilan bog'laning.")
        return

    url = message.text.strip()

    if not re.match(r"https?://(www\.)?(youtube\.com|youtu\.be|tiktok\.com|instagram\.com)", url):
        await message.answer("⚠️ Noto'g'ri link. Faqat YouTube, TikTok yoki Instagram link yuboring.")
        return

    await message.answer("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            "format": "mp4",
            "outtmpl": "video.%(ext)s",
            "quiet": True,
            "noplaylist": True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        video_file = FSInputFile(file_path)
        await message.answer_video(video=video_file, caption="✅ Video tayyor!")

    except Exception as e:
        await message.answer("❌ Yuklab bo'lmadi. Linkda xatolik bo'lishi mumkin.")
        print("Xatolik:", e)

# Botni ishga tushurish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
