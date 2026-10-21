import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader
import asyncio
from pathlib import Path

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

loader = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    post_metadata_txt_pattern=''
)

def extract_shortcode(url: str) -> str:
    patterns = [
        r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)',
        r'instagram\.com/reels?/([A-Za-z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

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

    shortcode = extract_shortcode(message_text)

    if not shortcode:
        await update.message.reply_text("❌ Noto'g'ri Instagram link. Iltimos, to'g'ri link yuboring.")
        return

    status_msg = await update.message.reply_text("⏳ Video yuklab olinmoqda...")

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if not post.is_video:
            await status_msg.edit_text("❌ Bu post video emas. Faqat videolarni yuklab olishim mumkin.")
            return

        video_path = None

        await asyncio.to_thread(
            loader.download_post,
            post,
            target=str(DOWNLOAD_DIR / shortcode)
        )

        for file in DOWNLOAD_DIR.glob(f"{shortcode}/*.mp4"):
            video_path = file
            break

        if not video_path or not video_path.exists():
            await status_msg.edit_text("❌ Video topilmadi.")
            return

        await status_msg.edit_text("📤 Video yuborilmoqda...")

        caption = f"📹 Instagram Video\n"
        if post.caption:
            caption += f"\n{post.caption[:200]}{'...' if len(post.caption) > 200 else ''}"

        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=caption,
                supports_streaming=True
            )

        await status_msg.delete()

        import shutil
        shutil.rmtree(DOWNLOAD_DIR / shortcode, ignore_errors=True)

    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Instaloader error: {e}")
        await status_msg.edit_text(
            "❌ Video yuklab olishda xatolik yuz berdi.\n"
            "Bu post private yoki o'chirilgan bo'lishi mumkin."
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

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
