import os
import re
import time
import shutil
import asyncio
import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Instagram cookies fayli (docker-compose da volume qilib ulanadi)
COOKIES_FILE = Path(os.getenv("COOKIES_FILE", "/app/cookies.txt"))

MAX_FILE_SIZE = 50 * 1024 * 1024  # Telegram bot limiti: 50MB
YTDLP_TIMEOUT = 180  # soniya

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:p|reels?|tv)/[A-Za-z0-9_-]+[^\s]*"
)


def extract_instagram_url(text: str):
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋\n\n"
        "Instagram video yuklab olish botiga xush kelibsiz!\n\n"
        "Menga Instagram post yoki reel linkini yuboring va men sizga videoni yuboraman.\n\n"
        "Misol: https://www.instagram.com/reel/xxxxx/"
    )


def build_error_text(stderr_text: str) -> str:
    low = stderr_text.lower()
    if any(k in low for k in ("login required", "rate-limit", "cookies", "not available")):
        if "private" in low:
            return "❌ Bu post private, yuklab bo'lmaydi."
        return (
            "❌ Instagram so'rovni blokladi (login yoki limit).\n"
            "Birozdan keyin qayta urinib ko'ring."
        )
    if "private" in low:
        return "❌ Bu post private, yuklab bo'lmaydi."
    if "unsupported url" in low or "404" in low or "not found" in low:
        return "❌ Post topilmadi yoki o'chirilgan."
    return "❌ Video yuklab olishda xatolik yuz berdi. Keyinroq qayta urinib ko'ring."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text or ""

    if "instagram.com" not in message_text:
        await update.message.reply_text(
            "❌ Iltimos, Instagram linkini yuboring.\n"
            "Misol: https://www.instagram.com/reel/xxxxx/"
        )
        return

    url = extract_instagram_url(message_text)
    if not url:
        await update.message.reply_text(
            "❌ Noto'g'ri Instagram link. Iltimos, to'g'ri link yuboring."
        )
        return

    status_msg = await update.message.reply_text("⏳ Video yuklab olinmoqda...")

    temp_dir = DOWNLOAD_DIR / f"temp_{update.message.chat_id}_{int(time.time())}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        output_template = str(temp_dir / "video.%(ext)s")

        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--no-playlist",
            "-f", "best[ext=mp4]/best",
            "-o", output_template,
        ]

        # Cookies faylini vaqtinchalik papkaga nusxalaymiz,
        # chunki yt-dlp uni qayta yozishga urinadi (read-only volume muammosi bo'lmasin)
        if COOKIES_FILE.exists():
            cookies_copy = temp_dir / "cookies.txt"
            shutil.copy(COOKIES_FILE, cookies_copy)
            cmd += ["--cookies", str(cookies_copy)]
        else:
            logger.warning("cookies.txt topilmadi, cookies'siz urinilyapti")

        cmd.append(url)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=YTDLP_TIMEOUT
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            logger.error("yt-dlp timeout")
            await status_msg.edit_text("❌ Yuklab olish juda uzoq davom etdi. Qayta urinib ko'ring.")
            return

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            logger.error(f"yt-dlp error: {error_msg}")
            await status_msg.edit_text(build_error_text(error_msg))
            return

        video_files = [
            f for f in temp_dir.glob("video.*") if f.suffix != ".part"
        ]
        if not video_files:
            await status_msg.edit_text("❌ Video topilmadi.")
            return

        video_path = video_files[0]
        file_size = video_path.stat().st_size

        if file_size > MAX_FILE_SIZE:
            await status_msg.edit_text(
                "❌ Video juda katta (50MB dan oshiq), Telegram orqali yuborib bo'lmaydi."
            )
            return

        await status_msg.edit_text("📤 Video yuborilmoqda...")

        with open(video_path, "rb") as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="📹 Instagram Video",
                supports_streaming=True,
                read_timeout=60,
                write_timeout=60,
            )

        await status_msg.delete()

    except Exception as e:
        logger.exception(f"Error: {e}")
        try:
            await status_msg.edit_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        except Exception:
            pass
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    logger.info("Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
