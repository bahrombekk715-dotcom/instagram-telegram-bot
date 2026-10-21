import os
import logging
import re
import subprocess
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def is_instagram_url(url: str) -> bool:
    patterns = [
        r'instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_-]+',
        r'instagram\.com/reels?/[A-Za-z0-9_-]+',
    ]
    return any(re.search(pattern, url) for pattern in patterns)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋\n\n"
        "Instagram video yuklab olish botiga xush kelibsiz!\n\n"
        "Menga Instagram post yoki reel linkini yuboring va men sizga videoni yuboraman.\n\n"
        "Misol: https://www.instagram.com/reel/xxxxx/"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    if 'instagram.com' not in message_text:
        await update.message.reply_text(
            "❌ Iltimos, Instagram linkini yuboring.\n"
            "Misol: https://www.instagram.com/reel/xxxxx/"
        )
        return

    if not is_instagram_url(message_text):
        await update.message.reply_text("❌ Noto'g'ri Instagram link. Iltimos, to'g'ri link yuboring.")
        return

    status_msg = await update.message.reply_text("⏳ Video yuklab olinmoqda...")

    import time
    import shutil

    temp_dir = DOWNLOAD_DIR / f"temp_{int(time.time())}"
    temp_dir.mkdir(exist_ok=True)

    try:
        # yt-dlp orqali video yuklab olish
        output_template = str(temp_dir / "video.%(ext)s")

        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--no-check-certificate",
            "-f", "best",
            "-o", output_template,
            message_text.strip()
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='ignore')
            logger.error(f"yt-dlp error: {error_msg}")
            await status_msg.edit_text(
                "❌ Video yuklab olishda xatolik yuz berdi.\n"
                "Bu post private yoki o'chirilgan bo'lishi mumkin."
            )
            shutil.rmtree(temp_dir, ignore_errors=True)
            return

        # Yuklab olingan videoni topish
        video_files = list(temp_dir.glob("video.*"))

        if not video_files:
            await status_msg.edit_text("❌ Video topilmadi.")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return

        video_path = video_files[0]
        file_size = video_path.stat().st_size

        # Telegram fayl hajmi limiti: 50MB
        if file_size > 50 * 1024 * 1024:
            await status_msg.edit_text("❌ Video juda katta (50MB dan oshiq). Kichikroq video yuboring.")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return

        await status_msg.edit_text("📤 Video yuborilmoqda...")

        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="📹 Instagram Video",
                supports_streaming=True,
                read_timeout=60,
                write_timeout=60
            )

        await status_msg.delete()
        shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        shutil.rmtree(temp_dir, ignore_errors=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    logger.info("Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
