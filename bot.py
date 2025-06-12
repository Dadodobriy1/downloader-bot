# -*- coding: utf-8 -*-
import asyncio
import re
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from yt_dlp import YoutubeDL

API_TOKEN = os.getenv("7353528532:AAHFKC7JcAujOSdHJ3BOk1NJ9nRwLU5-PB8")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 YouTube, TikTok yoki Instagram link yuboring. Men video yuklab beraman.")

@dp.message(F.text)
async def download(message: Message):
    url = message.text.strip()

    if not re.match(r"https?://(www\.)?(youtube\.com|youtu\.be|tiktok\.com|instagram\.com)", url):
        await message.answer("❌ Noto'g'ri link. Faqat YouTube, TikTok yoki Instagram link yuboring.")
        return

    await message.answer("⏳ Yuklab olinmoqda, iltimos kuting...")

    try:
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'noplaylist': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        video = FSInputFile(file_path)
        await message.reply_video(video=video, caption="✅ Video yuklab olindi!")
        os.remove(file_path)

    except Exception as e:
        await message.answer("❌ Yuklab bo'lmadi. Linkda xatolik bo'lishi mumkin.")
        print("Xatolik:", e)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
