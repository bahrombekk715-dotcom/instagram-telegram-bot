#!/bin/bash

# Instagram Telegram Bot - Server Deploy Script

set -e

echo "🚀 Instagram Telegram Bot - Deploy boshlandi..."

# 1. Serverga ulanish ma'lumotlari
read -p "Server IP manzili: " SERVER_IP
read -p "Server username (default: root): " SERVER_USER
SERVER_USER=${SERVER_USER:-root}

echo ""
echo "📦 Repository yuklanmoqda..."

# 2. Serverdagi papkani tozalash va yangilash
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    # Eski papkani o'chirish
    rm -rf ~/instagram-telegram-bot

    # Repository clone qilish
    git clone https://github.com/bahrombekk715-dotcom/instagram-telegram-bot.git ~/instagram-telegram-bot
    cd ~/instagram-telegram-bot

    echo "✅ Repository yuklandi"
ENDSSH

echo ""
read -p "Telegram Bot Token kiriting: " BOT_TOKEN

# 3. .env faylini yaratish
ssh ${SERVER_USER}@${SERVER_IP} << ENDSSH
    cd ~/instagram-telegram-bot
    echo "TELEGRAM_BOT_TOKEN=${BOT_TOKEN}" > .env
    echo "✅ .env fayli yaratildi"
ENDSSH

echo ""
echo "🐳 Docker tekshirilmoqda..."

# 4. Docker o'rnatilganligini tekshirish
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    if ! command -v docker &> /dev/null; then
        echo "Docker topilmadi. O'rnatilmoqda..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        echo "✅ Docker o'rnatildi"
    else
        echo "✅ Docker allaqachon o'rnatilgan"
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo "Docker Compose o'rnatilmoqda..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo "✅ Docker Compose o'rnatildi"
    else
        echo "✅ Docker Compose allaqachon o'rnatilgan"
    fi
ENDSSH

echo ""
echo "🏗️ Bot ishga tushirilmoqda..."

# 5. Bot ishga tushirish
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    cd ~/instagram-telegram-bot

    # Eski containerni to'xtatish
    docker-compose down 2>/dev/null || true

    # Yangi containerni ishga tushirish
    docker-compose up -d --build

    echo ""
    echo "✅ Bot muvaffaqiyatli ishga tushirildi!"
    echo ""
    echo "📊 Status:"
    docker-compose ps

    echo ""
    echo "📝 Loglarni ko'rish: docker-compose logs -f"
    echo "⏹️  To'xtatish: docker-compose down"
    echo "🔄 Qayta ishga tushirish: docker-compose restart"
ENDSSH

echo ""
echo "🎉 Deploy yakunlandi!"
echo ""
echo "Botni Telegram'da sinab ko'ring!"
