# CemilAbi Bot Orkestrası - Mimari Belgesi

## Genel Bakış

Bu proje, Python, AsyncIO ve Redis kullanarak birden fazla botun koordineli çalışmasını sağlayan bir bot orkestrasyonu sistemidir.

## Bileşenler

### 1. CemilAbi (Master Orchestrator)

**Dosya:** `orchestrator/main.py`

**Görevleri:**
- Botların durumunu izlemek (health monitoring)
- Bot komutlarını işlemek
- Stratejik kararlar almak
- Sistem raporu oluşturmak

**Özellikler:**
- Kalp atışı (heartbeat) alma: her 5 saniyede
- Sağlık kontrolü: her 10 saniyede
- Karar verme: her 15 saniyede
- Durum raporu: her 30 saniyede

### 2. BaseBot (Taban Sınıf)

**Dosya:** `orchestrator/bot_base.py`

**Sağladığı:**
- Redis bağlantısı
- Pub/Sub mesajlaşma
- Logger kurulumu
- Kalp atışı mekanizması
- Başlangıç/kapanış döngüsü

**Metotlar:**
- `subscribe(*topics)`: Konulara abone ol
- `receive_message()`: Mesaj al
- `publish(topic, message)`: Mesaj gönder
- `run()`: Ana işlemi çalıştır (override et)

### 3. Bot Uygulamaları

#### DataProcessorBot
**Dosya:** `bots/data_processor_bot.py`
- Veriyi alır
- İşler/dönüştürür
- Sonucu başka bota gönderir

#### ApiCallerBot
**Dosya:** `bots/api_caller_bot.py`
- Dış API'lara istek yapar
- Yanıt alır
- Sonucu işler

#### NotificationBot
**Dosya:** `bots/notification_bot.py`
- Nihai sonuçları bildirir
- Log dosyalarına yazar
- Uyarı gönderir

### 4. Utilities

#### RedisClient
**Dosya:** `utils/redis_client.py`
- Async Redis bağlantı
- Pub/Sub yönetimi
- Singleton pattern

#### Logger
**Dosya:** `utils/logger.py`
- Merkezi logging
- Dosya ve konsol çıkışı
- Rotating file handler

#### Config
**Dosya:** `orchestrator/config.py`
- Merkezi konfigürasyon
- Ortam değişkenleri
- Sabitler

## İletişim Akışı

```
1. Bot başlanır → Kalp atışı gönderir
2. CemilAbi kalp atışını alır → Bot durumunu günceller
3. CemilAbi karar alır → Komut gönderir
4. Bot komutu alır → İş yapar → Sonuç gönderir
5. NotificationBot sonucu alır → Bildirim gönderir
6. CemilAbi rapor oluşturur → Log yazar
```

## Redis Konuları (Topics)

| Konu | Kullanım |
|------|----------|
| `system:health` | Botlar kalp atışı gönderir |
| `orchestrator:commands` | CemilAbi komut gönderir |
| `cemilabi:decision` | CemilAbi kararlarını gönderir |
| `data:input` | Veri girişi |
| `data:processed` | İşlenmiş veri |
| `api:request` | API isteği |
| `api:response` | API yanıtı |
| `data:error` | Hata mesajı |

## Dosya Yapısı

```
cirkin-ordek-yavrusu/
├── orchestrator/           # Master orchestrator
│   ├── __init__.py
│   ├── main.py            # CemilAbi
│   ├── bot_base.py        # BaseBot sınıfı
│   └── config.py          # Konfigürasyon
├── bots/                   # Bot uygulamaları
│   ├── __init__.py
│   ├── data_processor_bot.py
│   ├── api_caller_bot.py
│   └── notification_bot.py
├── utils/                  # Yardımcı modüller
│   ├── __init__.py
│   ├── logger.py
│   └── redis_client.py
├── logs/                   # Log dosyaları (oluşturulur)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── QUICKSTART.md
└── ARCHITECTURE.md
```

## Veri Akışı Örneği

### Senaryo: Veri İşleme Pipeline'ı

```
1. Input Data
   ↓
2. DataProcessorBot
   - Veriyi alır
   - Transform eder
   - Mesaj gönderir: data:processed
   ↓
3. ApiCallerBot
   - data:processed mesajını alır
   - Dış API'yi çağırır
   - Mesaj gönderir: api:response
   ↓
4. NotificationBot
   - api:response mesajını alır
   - Sonucu loglar
   - Bildirim gönderir
   ↓
5. CemilAbi
   - Bütün akışı izler
   - Health check yapar
   - Rapor oluşturur
```

## Asenkron Tasarım

Bütün botlar AsyncIO kullanarak eşzamansız olarak çalışır:

- Bekleme süresi boyunca diğer botlar çalışmaya devam eder
- CPU işi sırasında diğer görevler yapılabilir
- Verimli kaynak kullanımı
- Bağımsız iş parçalanması

## Hata Yönetimi

1. **Bot Hatası**: Bot hata loglar, sonra kapalı kalır
2. **Redis Bağlantı Hatası**: Bot yeniden bağlanmayı dener
3. **Stale Bot**: CemilAbi uyarı verir
4. **Message Timeout**: Bot beklemeden devam eder

## Genişletilebilirlik

### Yeni Bot Ekleme

1. `BaseBot` sınıfından inherit et
2. `run()` metodunu override et
3. `docker-compose.yml`'ye servis ekle
4. `docker compose up --build`

### Yeni Konu Ekleme

```python
# config.py'ye ekle
MY_CUSTOM_TOPIC = "custom:mytopic"

# Bot'ta kullan
await self.subscribe(MY_CUSTOM_TOPIC)
```

### CemilAbi'ye Yeni Karar Ekle

```python
async def _my_custom_logic(self):
    # CemilAbi'ye yeni mantık ekle
    pass
```

## Performans Notları

- **Botlar**: AsyncIO ile C10K (10,000 concurrent connections) destekler
- **Redis**: Alpine image, ~150MB
- **Network**: Local Docker network, minimal overhead
- **CPU**: Single core, ~10% idle state
- **Memory**: ~200MB total usage

## Security Notes

- Production'da Redis şifre olmalı
- Container images security scan yapılmalı
- Network isolation kullanılmalı
- Secret management eklenmeliri

## İleri Özellikler

Gelecekte eklenebilecek:
- Bot yeniden başlatma
- Task kuyruğu (Celery)
- Monitoring (Prometheus)
- Database persistence
- Message encryption
- API gateway
- WebSocket support
