# Server Deploy Yo'riqnomasi

## Tez Deploy (Avtomatik Script)

```bash
# 1. Deploy scriptni ishga tushiring
chmod +x deploy.sh
./deploy.sh
```

Script so'raydi:
- Server IP
- Server username (default: root)
- Telegram Bot Token

Hamma narsa avtomatik o'rnatiladi va ishga tushadi!

---

## Qo'lda Deploy (Batafsil)

### 1. Serverga kirish

```bash
ssh root@your_server_ip
# yoki
ssh username@your_server_ip
```

### 2. Docker o'rnatish (agar yo'q bo'lsa)

```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Versiyani tekshirish
docker --version
docker-compose --version
```

### 3. Repository clone qilish

```bash
git clone https://github.com/bahrombekk715-dotcom/instagram-telegram-bot.git
cd instagram-telegram-bot
```

### 4. .env faylini sozlash

```bash
cp .env.example .env
nano .env
```

`.env` fayliga kiriting:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

Saqlash: `Ctrl + O`, `Enter`, Chiqish: `Ctrl + X`

### 5. Bot ishga tushirish

```bash
docker-compose up -d
```

### 6. Status tekshirish

```bash
# Container statusini ko'rish
docker-compose ps

# Loglarni ko'rish
docker-compose logs -f

# Chiqish: Ctrl + C
```

---

## Foydali Buyruqlar

### Bot boshqaruvi

```bash
# To'xtatish
docker-compose down

# Qayta ishga tushirish
docker-compose restart

# Loglarni ko'rish (oxirgi 100 qator)
docker-compose logs --tail=100

# Real-time loglar
docker-compose logs -f

# Yangilash (GitHub'dan pull qilib)
git pull
docker-compose down
docker-compose up -d --build
```

### Xotira va resurslarni tozalash

```bash
# Ishlatilmayotgan Docker imagelarni o'chirish
docker system prune -a

# Faqat containerlarni tozalash
docker container prune
```

### Avtomatik qayta ishga tushirish (reboot'dan keyin)

```bash
# Container'ga restart policy qo'shish
docker update --restart unless-stopped instagram-telegram-bot
```

---

## Muammolarni hal qilish

### Bot ishlamayapti?

```bash
# 1. Container ishlayaptimi?
docker ps

# 2. Loglarni tekshiring
docker-compose logs --tail=50

# 3. Qayta ishga tushiring
docker-compose restart
```

### "Permission denied" xatosi?

```bash
# Docker guruhiga user qo'shish
sudo usermod -aG docker $USER

# Session'ni yangilash
newgrp docker
```

### Port band?

```bash
# Qaysi jarayon port ishlatayotganini ko'rish
sudo netstat -tulpn | grep :3000
```

### .env fayli o'qilmayapti?

```bash
# Fayl mavjudligini tekshirish
ls -la .env

# Fayl tarkibini ko'rish
cat .env

# To'g'ri formatda ekanligini tekshirish (bo'sh joylar, qo'shtirnoqlar yo'q)
```

---

## Xavfsizlik Maslahatlari

### 1. Firewall sozlash

```bash
# UFW ni o'rnatish (Ubuntu/Debian)
sudo apt install ufw

# SSH ruxsat berish (server bilan aloqa uzilmasligi uchun!)
sudo ufw allow 22/tcp

# Firewall yoqish
sudo ufw enable

# Status
sudo ufw status
```

### 2. .env faylini himoyalash

```bash
# Faqat owner o'qiy oladi
chmod 600 .env
```

### 3. SSH kalit bilan kirish (parolsiz)

Lokal kompyuterda:
```bash
# SSH key yaratish
ssh-keygen -t ed25519 -C "your_email@example.com"

# Serverga yuklash
ssh-copy-id root@your_server_ip
```

---

## Monitoring

### Loglarni fayl sifatida saqlash

```bash
# Real-time loglarni faylga yozish
docker-compose logs -f > bot.log &

# Oxirgi loglarni ko'rish
tail -f bot.log
```

### Resurs ishlatilishini ko'rish

```bash
# Container statistikasi
docker stats instagram-telegram-bot
```

---

## Yangilash Jarayoni

Yangi versiya GitHub'ga push qilinganida:

```bash
cd ~/instagram-telegram-bot

# 1. Oxirgi o'zgarishlarni olish
git pull

# 2. Containerni to'xtatish
docker-compose down

# 3. Qayta build va ishga tushirish
docker-compose up -d --build

# 4. Loglarni tekshirish
docker-compose logs -f
```

---

## Backup

### Bot konfiguratsiyasini backup qilish

```bash
# .env faylini nusxalash
cp .env .env.backup

# Butun papkani arxivlash
tar -czf instagram-bot-backup-$(date +%Y%m%d).tar.gz instagram-telegram-bot/
```

---

## Sistemli deploy (Production)

### Systemd service yaratish (optional)

`/etc/systemd/system/instagram-bot.service`:

```ini
[Unit]
Description=Instagram Telegram Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/root/instagram-telegram-bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Faollashtirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable instagram-bot
sudo systemctl start instagram-bot
sudo systemctl status instagram-bot
```

---

## Yordam

Muammo bo'lsa:
1. `docker-compose logs -f` ni tekshiring
2. `.env` fayli to'g'riligini tasdiqlang
3. Bot token faol ekanligini tekshiring [@BotFather](https://t.me/botfather)
4. Server internetga ulanganligini tekshiring: `ping -c 3 google.com`
