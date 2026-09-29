# CemilAbi Bot Orkestrası - Hızlı Başlangıç

## 📋 Gereksinimler

- Docker
- Docker Compose
- Python 3.11+ (lokal geliştirme için)

## 🚀 Başlangıç - 3 Adım

### Adım 1: Docker ile Başlat

```bash
cd cirkin-ordek-yavrusu
docker compose up --build
```

Bu komut:
- Redis başlatacak
- CemilAbi'yi çalıştıracak
- Tüm botları ayağa kaldıracak

### Adım 2: Logları İzle

Başka bir terminal penceresinde:

```bash
docker compose logs -f
```

Beklediğin şeyler:
- ✅ "👔 CemilAbi initialized - The Boss is here!"
- ✅ "💚 CemilAbi: DataProcessorBot checked in"
- ✅ "💚 CemilAbi: ApiCallerBot checked in"
- ✅ "💚 CemilAbi: NotificationBot checked in"

### Adım 3: Sistem Durumunu Kontrol Et

```bash
# Çalışan servisleri gör
docker compose ps

# Redis'in canlı olduğunu doğrula
docker compose exec redis redis-cli ping
# Cevap: PONG
```

## 🛑 Durdurma

```bash
docker compose down
```

## 🔧 Lokal Geliştirme

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Ortam değişkenlerini ayarla
cp .env.example .env

# Redis'i lokal çalıştır (Docker olmadan)
# Sistem Python'da çalışacak
python -m orchestrator.main
```

## 📊 Sistem Mimarisi

```
┌─────────────────────────────┐
│      CemilAbi (Boss)        │
│   (Master Orchestrator)     │
└──────────────┬──────────────┘
               │
      ┌────────┼────────┐
      │        │        │
   ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
   │Data │ │ API │ │Notice│
   │Proc │ │Call │ │Bot  │
   └──┬──┘ └──┬──┘ └──┬──┘
      │       │       │
      └───────┼───────┘
              │
         ┌────▼────┐
         │  Redis  │
         │ (Pub/Sub│
         └─────────┘
```

## 📝 Log Dosyaları

```
logs/
├── cemilabi.log          # CemilAbi ana logları
├── dataprocessorbot.log  # DataProcessorBot logları
├── apicallerbot.log      # ApiCallerBot logları
└── notificationbot.log   # NotificationBot logları
```

## 🐛 Sorun Giderme

### Redis bağlanamıyorum

```bash
# Redis container'ının çalışıp çalışmadığını kontrol et
docker compose ps redis

# Redis loglarını gör
docker compose logs redis
```

### Botlar bağlanmıyor

```bash
# Tüm logları gör
docker compose logs

# Belirli bir bot'un loglarını gör
docker compose logs bot-processor
```

### Port zaten kullanımda

```bash
# 6379 portunu kullananlara bak
lsof -i :6379

# Varsa öldür
kill -9 <PID>
```

## 📚 Yeni Bot Ekleme

1. `bots/my_new_bot.py` dosyası oluştur:

```python
from orchestrator.bot_base import BaseBot

class MyNewBot(BaseBot):
    async def run(self):
        await self.subscribe("my_topic")
        while self.is_running:
            message = await self.receive_message(timeout=5)
            if message:
                # İş yap
                await self.publish("result_topic", result)
```

2. `docker-compose.yml` dosyasına bot ekle:

```yaml
my-bot:
  build: .
  container_name: bot-mynewbot
  depends_on:
    redis:
      condition: service_healthy
  environment:
    - REDIS_HOST=redis
    - REDIS_PORT=6379
  command: python -m bots.my_new_bot
  networks:
    - bot-network
```

3. Tekrar çalıştır:

```bash
docker compose up --build
```

## ✅ Çalışır Kontrol Listesi

- [ ] Docker Compose kurulu
- [ ] `docker compose up --build` başarıyla çalışıyor
- [ ] Redis PONG veriyor
- [ ] CemilAbi başlamış
- [ ] Bütün botlar bağlanmış
- [ ] Loglar akışını gösteriyor
- [ ] `docker compose down` komut çalışıyor

## 💡 İpuçları

- Logları renkli görmek için: `docker compose logs -f --colors`
- Belirli servislerin loglarını görmek için: `docker compose logs -f orchestrator`
- Real-time izlemek için: `watch -n 1 'docker compose ps'`

## 🆘 Yardım

Her zaman repo'yu kontrol et veya issue açabilirsin.
