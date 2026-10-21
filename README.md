# Instagram Video Downloader Telegram Bot

Instagram videolarini yuklab olish uchun Telegram bot.

## Xususiyatlar

- Instagram post va reel videolarini yuklab olish
- Docker bilan oson deploy qilish
- O'zbek tilida interfeyz
- Avtomatik xato boshqaruvi

## O'rnatish

### 1. Bot tokenini olish

1. Telegram'da [@BotFather](https://t.me/botfather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting
4. Bot username'ini kiriting (masalan: `my_instagram_bot`)
5. Sizga bot token beriladi

### 2. Konfiguratsiya

`.env.example` faylini `.env` ga nusxalang va bot tokenini kiriting:

```bash
cp .env.example .env
```

`.env` faylini tahrirlang:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 3. Docker bilan ishga tushirish

```bash
# Build va run
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f

# To'xtatish
docker-compose down
```

### 4. Docker'siz ishga tushirish (optional)

```bash
# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# Paketlarni o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish
export TELEGRAM_BOT_TOKEN="your_token_here"
python bot.py
```

## Foydalanish

1. Botni Telegram'da toping
2. `/start` buyrug'ini yuboring
3. Instagram video linkini yuboring:
   - Post: `https://www.instagram.com/p/xxxxx/`
   - Reel: `https://www.instagram.com/reel/xxxxx/`
4. Bot videoni yuklab oladi va sizga yuboradi

## Serverga deploy qilish

### Ubuntu/Debian serverda

```bash
# Repositoriyani clone qiling
git clone <repo-url>
cd instagram-telegram-bot

# .env faylini sozlang
cp .env.example .env
nano .env  # tokenni kiriting

# Docker va Docker Compose o'rnating (agar yo'q bo'lsa)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Botni ishga tushiring
docker-compose up -d

# Avtomatik qayta ishga tushirish uchun (reboot'dan keyin)
docker update --restart unless-stopped instagram-telegram-bot
```

### Loglarni tekshirish

```bash
docker-compose logs -f instagram-bot
```

### Yangilash

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Muammolarni hal qilish

### Bot javob bermayapti
```bash
docker-compose logs -f
```

### Container to'xtab qolgan
```bash
docker-compose restart
```

### Private postlarni yuklab olmayapti
Bot faqat public postlarni yuklab oladi. Private accountlarning videolarini yuklab olish uchun Instagram login kerak bo'ladi.

## Texnologiyalar

- Python 3.11
- python-telegram-bot 21.0
- instaloader 4.11
- Docker & Docker Compose

## Litsenziya

MIT
