# CemilAbi Bot Orkestrası

Bu proje, birden fazla botun birlikte çalıştığı bir bot orkestrasyon sistemi için başlangıç altyapısıdır.

Ana yöneten botun adı: CemilAbi

## Mimari

- CemilAbi: ana orkestratör, botları izler, karar verir, komut dağıtır
- DataProcessorBot: veriyi işler
- ApiCallerBot: dış API çağrıları yapar
- NotificationBot: sonuçları bildirir
- Redis: botlar arası iletişim katmanı
- Docker Compose: tüm sistemi tek komutla çalıştırır

## Teknoloji Stack

- Python 3.11
- AsyncIO
- Redis
- Docker Compose

## Proje Yapısı

```text
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── bots/
│   ├── __init__.py
│   ├── api_caller_bot.py
│   ├── data_processor_bot.py
│   └── notification_bot.py
├── orchestrator/
│   ├── __init__.py
│   ├── bot_base.py
│   ├── config.py
│   └── main.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── redis_client.py
└── logs/
```

## Çalıştırma

İlk olarak bağımlılıkları kur:

```bash
pip install -r requirements.txt
```

Ardından Docker ile çalıştır:

```bash
docker compose up --build
```

Logları takip etmek için:

```bash
docker compose logs -f
```

## Durdurma

```bash
docker compose down
```

## Notlar

Bu proje bir başlangıç/örnek yapı sunar. Gerçek üretim ortamında şu eklemeler gerekir:

- bot yeniden başlatma stratejisi
- görev kuyruğu ve retry mekanizması
- güvenlik/kimlik doğrulama katmanı
- prometheus / grafana izleme
- daha sağlam hata yönetimi
- persistans ve veri tabanı entegrasyonu

## CemilAbi Nedir?

CemilAbi, tüm botların merkezindeki master yöneticidir. Botların durumunu izler, komut gönderir, karar üretir ve sistem durumu hakkında rapor tutar.

## Hızlı Başlangıç Test Akışı

1. Redis çalışsın
2. CemilAbi başlasın
3. DataProcessorBot bağlansın
4. ApiCallerBot bağlansın
5. NotificationBot bağlansın
6. botlar Redis üzerinden mesaj alışverişi yapsın

Bu akış, bot orkestrasyon için temel örnektir.
