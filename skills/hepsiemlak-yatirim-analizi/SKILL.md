---
name: hepsiemlak-yatirim-analizi
description: "Analyze HepsiEmlak listings for rental investment potential across ANY city in Turkey. Scoring: price, rental yield estimate, hospital/school proximity, floor, room type. Uses SQLite + AI analysis for on-demand queries."
version: 1.0.0
author: Batu
---

# HepsiEmlak Konut Yatırım Analizörü

HepsiEmlak API'sinden herhangi bir şehirde 1.000.000 - 1.500.000 TL bandında küçük daireleri (1+0, 1+1, 2+1) bulup kira yatırımı potansiyeline göre skorlar.

## 🎯 Yatırım Stratejisi

- **Bütçe:** 1.000.000 - 1.500.000 TL (kredi ile)
- **Hedef:** Küçük daireler (1+0, 1+1, 2+1)
- **Amaç:** Satın al → kirala → pasif gelir
- **Lokasyon:** Gelişmekte olan şehirler, hastane/okul yakını
- **Kredi:** Krediye uygun (availableForLoanStatus=APPLICABLE)

### 🗺️ Öncelikli Şehirler (Batu seçimi)

| Şehir | Slug | Potansiyel | Gerekçe |
|-------|------|:----------:|---------|
| 🥇 **Kırıkkale** | `kirikkale` | 18 | Ankara'ya yakın, sanayi, makul fiyatlar |
| 🥇 **Eskişehir** | `eskisehir` | 20 | Öğrenci şehri, sürekli kira talebi |
| 🥇 **Bolu** | `bolu` | 17 | Öğrenci + doğa, yükselen trend |
| 🥇 **Sakarya** | `sakarya` | 18 | İstanbul-Ankara arası, gelişen sanayi |

> ⚠️ Şehir slug'larında Türkçe karakter olmaz: `eskişehir` → `eskisehir`, `kırıkkale` → `kirikkale`

## ⚙️ Gereksinimler

```bash
# curl_cffi gerekli (Cloudflare bypass)
pip install curl_cffi
```

Script `curl_cffi` kullanır (`urllib` yetersiz kalır — Cloudflare API'yi bloklayabilir).

## 🧠 API Kullanımı

Base URL: `https://www.hepsiemlak.com/api/realty-list/{sehir}-satilik`

`{sehir}` = şehir slug'ı (İngilizce, küçük harf, özel karakterler URL encoded):
- ankara, istanbul, izmir, bursa, antalya, adana, konya, gaziantep, eskişehir (⚠️ ş→s), mersin (❌ 403), trabzon, samsun, kayseri, kocaeli...

### Filtre parametreleri

| Param | Değer | Açıklama |
|-------|-------|----------|
| `p32` | `1500000` | Maks fiyat (1.5M TL) |
| `p31` | `1000000` | Min fiyat (1M TL) |
| `availableForLoanStatus` | `APPLICABLE` | Krediye uygun |
| `intent` | `satilik` | Satılık |
| `mainCategory` | `konut` | Konut |
| `sortField` | `UPDATED_DATE` | Sıralama |
| `pageNo` | `1` | Sayfa |
| `pageSize` | `50` | (API 24 override eder) |

## 📊 Yatırım Puanlaması (0-100)

| Kriter | Ağırlık | Açıklama |
|--------|:-------:|----------|
| 💰 **Fiyat** | 25 | 1M=25p, 1.5M=0p |
| 🛏️ **Oda Tipi** | 20 | 1+0=20, 1+1=18, 2+1=12 |
| 📍 **Şehir Potansiyeli** | 20 | Gelişen şehirler yüksek puan |
| 🏢 **Kat** | 10 | Bodrum=0, üst kat=10 |
| 📸 **İlan Kalitesi** | 10 | Foto+video kalitesi |
| 🏗️ **Bina Yaşı** | 10 | 0-10 yaş=10, 30+=0 |
| ⏳ **Yayın Süresi** | 5 | Yeni ilan = fırsat |

### Şehir Potansiyeli Puanları

| Şehir | Puan | Gerekçe |
|-------|:----:|---------|
| Ankara | 20 | Başkent, istikrarlı kira |
| İstanbul | 20 | En yüksek talep |
| İzmir | 18 | Büyükşehir, göç alıyor |
| Bursa | 17 | Sanayi + göç |
| Antalya | 17 | Turizm + yabancı talep |
| Eskişehir | 16 | Öğrenci şehri, üniversite |
| Konya | 14 | Organize sanayi |
| Gaziantep | 14 | Güneydoğu'nun merkezi |
| Adana | 13 | Büyükşehir, sanayi |
| Kayseri | 13 | Gelişen sanayi |
| Samsun | 12 | Karadeniz'in merkezi |
| Trabzon | 11 | Karadeniz, artan talep |
| Kocaeli | 12 | Sanayi, İstanbul'a yakın |
| Diğer | 10 | |

## 🏥 Çevresel Analiz (OSM ile)

Bu analiz **talep üzerine** çalışır — kullanıcı "yatırımlık analiz yap" dediğinde AI tetikler.

### Sorgulanan Kriterler

| Kriter | Menzil | Puan Katkısı |
|--------|:------:|:------------:|
| 🏥 Hastane | 1km | +10 |
| 🏫 Okul | 500m | +8 |
| 🚌 Toplu Taşıma (otobüs/dolmuş durağı) | 500m | +8 |
| 🏛️ Üniversite | 2km | +10 (öğrenci = kira garantisi!) |
| 🏪 Market/Supermarket | 500m | +5 |
| 🌳 Park/Yeşil Alan | 500m | +3 |

### ⚠️ OSM Rate Limit (Kritik)

OSM Nominatim API'ye en fazla **1 request/saniye** gönderilebilir. Her ilan için 5 kategori sorgusu:
- Hastane (1km) → 1sn
- Okul (500m) → 1sn
- Durak (500m) → 1sn
- Üniversite (2km) → 1sn
- Market (500m) → 1sn
= **~6sn/ilan**. 15 ilan = ~90sn.

**execute_code içinde 300sn timeout limiti var** — en fazla 10-12 ilan sorgulanabilir. 15+ ilan için terminal'de arka planda çalıştır.

### AI Analiz Workflow'u

Kullanıcı "yatırımlık analiz yap" dediğinde:

```python
import subprocess, json, time, sqlite3

MAPS = os.path.expanduser("<maps_client.py yolu — maps skill'i kuruluysa kullanılır>")
DB = os.path.expanduser("~/hepsiemlak_yatirim.db")  # kendi çalışma dizininiz

# 1. DB'den sadece mantıklı ilanları çek (1+0, 1+1, 2+1, Stüdyo, <200m²)
conn = sqlite3.connect(DB)
rows = conn.execute("""
    SELECT id, city, county, district, price, room_type, gross_sqm,
           lat, lon, detail_url
    FROM listings
    WHERE room_type IN ('1+0','1+1','2+1','Stüdyo')
      AND (gross_sqm IS NULL OR gross_sqm < 200)
      AND price BETWEEN 800000 AND 1500000
    ORDER BY price ASC
    LIMIT 12
""").fetchall()

# 2. Her ilan için OSM sorgula (subprocess.run ile JSON parse)
for r in rows:
    lat, lon = r['lat'], r['lon']
    if not lat or not lon: continue
    
    for cat, rad in [("hospital",1000),("school",500),("bus_stop",500),
                      ("university",2000),("supermarket",500)]:
        cmd = ["python3", MAPS, "nearby", str(lat), str(lon), cat, "--radius", str(rad)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        count = data.get("count", 0)  # ← sayı burada
        # veya results listesinden distance_m oku
        time.sleep(1.1)  # Nominatim rate limit

# 3. Kira tahmini + skorla + göster
```

### Örnek Çıktı

```
🏠 **Yatırım Fırsatı #1 — Eskişehir** (toplam: 94/100)

**1,250,000 TL** · Tepebaşı · 1+1 · 55m² · 3. Kat
📍 Şehir: 20/20 · 💰 Fiyat: 18/25 · 🛏️ Oda: 18/20
🏥 Hastaneye 400m (+10) · 🏫 Okula 200m (+8) · 🚌 Durağa 150m (+8)
🏛️ Anadolu Üniversitesi'ne 1.2km (+10)
📊 Tahmini kira: 8,000-10,000 TL/ay (getiri: %7.7-9.6)
🔗 link

🏠 **Yatırım Fırsatı #2 — Kırıkkale** (toplam: 82/100)

**950,000 TL** · Merkez · 2+1 · 75m² · 2. Kat
📍 Şehir: 18/20 · 💰 Fiyat: 22/25 · 🛏️ Oda: 12/20
🏥 Hastaneye 800m (+10) · 🚌 Durağa 300m (+8)
📊 Tahmini kira: 6,000-7,500 TL/ay (getiri: %7.6-9.5)
🔗 link
```

### Kira Getirisi Tahmini

Şehir bazında yaklaşık kira çarpanları (güncel piyasa):

| Şehir | 1+0 Kira | 1+1 Kira | 2+1 Kira |
|-------|:--------:|:--------:|:--------:|
| Eskişehir | 6-8K | 8-12K | 12-15K |
| Kırıkkale | 4-5K | 5-7K | 7-9K |
| Sakarya | 5-7K | 7-10K | 10-13K |
| Bolu | 4-6K | 6-8K | 8-11K |

**Yıllık getiri = (Aylık Kira × 12) / Satın Alma Fiyatı**

Hedef: **%7+ yıllık getiri** (Türkiye'de ideal kira getirisi %5-8 arasıdır)

### Nasıl Kullanılır

```
→ "yatırımlık analiz yap"
→ "Eskişehir'deki ilanları hastane yakınlığına göre sırala"
→ "Kırıkkale'de en iyi 5 yatırımlık daire"
→ "okula yakın 1+1'leri göster"
```

## 🗄️ Veritabanı

Her şehir için ayrı DB veya tek DB'de şehir sütunu:

**Dosya:** `~/hepsiemlak_yatirim.db` (kendi çalışma dizininizde)

```sql
CREATE TABLE listings (
    id TEXT PRIMARY KEY,
    city TEXT NOT NULL,
    county TEXT,
    district TEXT,
    price INTEGER,
    score INTEGER,
    room_type TEXT,
    gross_sqm REAL,
    floor_name TEXT,
    building_age INTEGER,
    lat REAL, lon REAL,
    detail_url TEXT,
    title TEXT,
    photo_count INTEGER,
    has_video INTEGER,
    kredi_uygun INTEGER,
    raw_data TEXT,
    first_seen TEXT,
    last_seen TEXT
);
```

## 🚀 Kullanım

### Toplu şehir taraması

```bash
# Tek seferlik: gelişen şehirleri tara
python3 <calisma_dizini>/hepsiemlak_yatirim_tara.py

# Şehir listesi: istanbul,ankara,izmir,bursa,antalya,eskişehir...
```

### AI analizi (talep üzerine)

Kullanıcı "yatırımlık daire bul" dediğinde:
1. Skill'i yükle
2. DB'deki verileri AI'ya ver
3. Hastane/okul yakınlığını OSM'den sorgula
4. Yatırım skoruna göre sırala
5. Sonuçları göster

## 📝 Çıktı Formatı

```
🏠 **Yatırım Fırsatı — Bursa** (skor: 82/100)

**1,250,000 TL** · Osmangazi · 1+1 · 65m² · 4. Kat
📍 Şehir potansiyeli: Bursa 🥇
💰 Fiyat aralıkta · 🏢 İyi kat · 🏗️ 8 yaş
🏥 Hastaneye 800m · 🏫 Okula 400m
📊 Tahmini kira: 8,000-10,000 TL/ay (getiri: %7.7)
🔗 link
```

## 🔗 İlgili Skill'ler

- `hepsiemlak-ev-takip` — konut takibi (bireysel kullanım)
- `maps` — OpenStreetMap POI sorgulama (hastane/okul için)
