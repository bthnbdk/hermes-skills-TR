---
name: hepsiemlak-cankaya-watchdog
description: "Monitor new property listings on HepsieEmlak for ANY city/district in Turkey. Reusable — configure {sehir}/{ilce} slugs, mahalle list, max price, work coordinates, and cron job for any location. Uses Python stdlib urllib, no external deps. SQLite-backed with AI scoring."
version: 4.0.0
author: Batu
---

# HepsiEmlak Emlak Watchdog (Tüm Türkiye)

HepsiEmlak API'sinden **herhangi bir il/ilçede** satılık konut ilanlarını kontrol eden `no_agent` cron job sistemi. Python stdlib ile çalışır — requests/curl_cffi/Playwright gerektirmez. Şehir seçimi tamamen size bağlı: `SEHIR` ve `ILCE` değişkenlerini değiştirip 5 dakikada yeni bir lokasyonda çalıştırabilirsiniz.

## 🎯 Şehir Yapılandırması (İlk Adım)

| Değişken | Örnek | Açıklama |
|----------|-------|----------|
| `SEHIR` | `ankara`, `istanbul`, `izmir`, `antalya`, `bursa`... | HepsiEmlak şehir slug'ı (81 il: `references/turkiye-sehirleri.csv`) |
| `ILCE` | `cankaya`, `konak`, `muratpasa`... veya `""` | İlçe slug'ı — boş = tüm ilçeler |
| `MAX_PRICE` | `8000000` | Maks fiyat (TL) — şehrin piyasasına göre ayarlayın |
| `WORK_LAT/LON` | `39.8897782, 32.8594033` | Mesafe puanı referans noktası (ev/iş yeri koordinatı) |
| `EXCLUDED` | `{"Ümitköy", ...}` | Hariç tutulacak mahalleler (set) |
| `DB` | `~/.hermes/hepsiemlak.db` | SQLite dosyası — şehir başına ayrı dosya önerilir |

**Tüm 81 il için slug listesi:** arsa-watchdog skill'indeki `references/turkiye-sehirleri.csv` dosyasını da kullanabilirsiniz (aynı slug formatı).

Kurulum örneği — İzmir Konak için:
```
HepsiEmlak İzmir Konak'ta 3+1, 5 milyon TL altı yeni satılık ilanları takip et — her 3 saatte kontrol et
```

## 🧠 API Response Structure (DOĞRULANMIŞ)

Base URL: `https://www.hepsiemlak.com/api/realty-list/{sehir}-satilik`

API normalde HTTP 200 döner. Cloudflare ana sayfayı bloklayabilir ama çoğu durumda API'ye dokunmaz.

### Cloudflare Bypass

**Öncelikli yaklaşım — `curl_cffi` ile (tavsiye edilen):**

```python
from curl_cffi import requests as curl_req
session = curl_req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 ...'})

# Warm up + API aynı session'da
r = session.get(main_url, impersonate='chrome124')
time.sleep(3)
r = session.get(api_url, headers={'Referer': main_url, 'Origin': 'https://www.hepsiemlak.com'}, impersonate='chrome124')
```

**Fallback — `urllib.request` ile (curl_cffi yoksa):**

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}
def req(url, accept, referer=None):
    h = {**HEADERS, "Accept": accept}
    if referer:
        h.update({"Referer": referer, "Origin": "https://www.hepsiemlak.com",
                  "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin"})
    return urllib.request.Request(url, headers=h)

# Step 1: Warm up
r1 = req(main_url, "text/html,...")
with urllib.request.urlopen(r1, context=ctx, timeout=30): pass
time.sleep(2)
# Step 2: API call
r2 = req(api_url, "application/json, text/plain, */*", referer=main_url)
with urllib.request.urlopen(r2, context=ctx, timeout=30) as r:
    data = json.loads(r.read().decode())
```

**⚠️ Rate limit uyarısı:** Hızlı ardışık istekler (saniyeler içinde 10+ farklı şehir sorgusu) Cloudflare'i tetikler ve IP geçici bloklanır (~30dk-1saat). Normal cron trafiği (3 saatte bir) sorunsuzdur. Test yaparken her istek arasında en az 3sn bekleyin.

### Request Hazırlığı

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

def req(url, accept, referer=None):
    h = {**HEADERS, "Accept": accept}
    if referer:
        h.update({"Referer": referer, "Origin": "https://www.hepsiemlak.com",
                  "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin"})
    return urllib.request.Request(url, headers=h)
```

Önce ana sayfayı ziyaret et (Cloudflare cookies warmup), 2sn bekle, sonra API'yi çağır:

```python
# Step 1: Warm up
r1 = req("https://www.hepsiemlak.com/{sehir}-satilik", "text/html,...")
with urllib.request.urlopen(r1, context=ctx, timeout=30): pass
time.sleep(2)
# Step 2: API call
r2 = req(API_URL, "application/json, text/plain, */*", referer=MAIN_URL)
with urllib.request.urlopen(r2, context=ctx, timeout=30) as r:
    data = json.loads(r.read().decode())
```

### Response Key'leri

| Key | Tip | Açıklama |
|-----|-----|----------|
| `totalElements` | int | Toplam ilan sayısı (filtrelenmiş) |
| `page` | int | Mevcut sayfa (1-indexed) |
| `size` | int | Sayfa başına ilan **(24 — pageSize=50 çalışmaz)** |
| `totalPages` | int | Toplam sayfa sayısı |
| `realtyList` | array | İlan listesi (❌ `data` değil) |

### Her İlan (`realtyList[]`) — Kritik Alanlar

| Alan | Tip | Açıklama | Eski (yanlış) ad |
|------|-----|----------|-------------------|
| `id` | int | İlan ID'si (PK) | ✅ |
| `price` | float | Fiyat | ✅ |
| `room` | array[int] | Oda: `[3]` | ❌ `roomCount` |
| `livingRoom` | array[int] | Salon: `[1]` | ❌ |
| `roomAndLivingRoom` | array[str] | Direk `["3+1"]` — tercih edilir | ✅ |
| `sqm` | object | `{"netSqm":55,"grossSqm":[55]}` | ❌ `squareMeters` |
| `district` | object | `{"name":"Küçükesat"}` | ❌ `neighborhoodName` |
| `detailUrl` | string | `en/ankara-.../daire/123-456` (⚠️ `/en/` strip et!) | ❌ `slug` |
| `floor` | object | `{"name":"3. Floor"}` | ✅ |
| `age` | int | Bina yaşı (0=yeni) | ✅ |
| `images` | array | Fotoğraf URL listesi | ✅ |
| `imageUrl` | string | Kapak fotoğrafı | ✅ |
| `videoUrl` | string | Video turu (varsa) | ✅ |
| `mapLocation` | object | `{"lat":...,"lon":...}` | ✅ |
| `createDate` | string | Yayın başlangıcı | ✅ |
| `advertiseOwner` | string | `"Emlakçıdan"` veya `"Sahibinden"` | ✅ |
| `sellerType` | string | `"Kurumsal"` veya `"Şahsi"` | ✅ |
| `whatsappNumber` | object | İletişim WhatsApp | ✅ |
| `onlineVisit` | bool | Online gezilebilir | ✅ |
| `stale` | bool | Bayat ilan mı? | ✅ |

**Tüm 64 field** `raw_data` JSON sütununda saklanır — API'deki her alan korunur.

### Parse Edilirken Dikkat Edilmesi Gerekenler

**Oda:** `roomAndLivingRoom` tercih edilir (`["3+1"]`), yoksa `room=[3]` + `livingRoom=[1]` birleştir.

**m²:** `sqm.grossSqm` array'in ilk elemanı Brüt, `sqm.netSqm` Net. Her ikisi de opsiyonel.

**Detay linki:** API `/en/` prefix'i ile döner. Strip edilmezse site İngilizce açılır:
```python
detail = i.get("detailUrl", "")
if detail.startswith("en/"):
    detail = detail[3:]
full_url = f"https://www.hepsiemlak.com/{detail}"
```

**Koordinat:** `mapLocation.lat` / `mapLocation.lon`. Emlakçılar yanlış işaretleyebilir → mahalle referansı kullan (aşağıya bak).

## 📂 Skill Files

| Dosya | Açıklama |
|-------|----------|
| `references/api-response-reference.md` | Gerçek API response örneği + tüm 64 field |
| `references/github-backup.md` | GitHub yedekleme detayları |
| `references/yatirim-monitoring.md` | Yatırımlık daire takibi + OSM/kire analizi |
| `references/web-visualization.md` | Leaflet+Chart.js web arayüzü detayları: API endpoints, 4 tab, trend/bargains, weekly report |
| `templates/hepsiemlak-fetch-template.py` | Yeni lokasyon için kopyalanabilir script şablonu (SEHIR/ILCE değişkenleri) |
| `templates/sehir_server.py` | Leaflet+OSM harita backend — **CONFIG sözlüğü ile her şehre uyarlanır** |
| `templates/sehir_harita.html` | Leaflet.js frontend — `__SEHIR_ADI__`/`__WORK_LAT__`/`__WORK_LON__` placeholder'ları server tarafından doldurulur |
| `scripts/hepsiemlak_fetch.py` | Canlı script — örnek Çankaya konut (`~/.hermes/scripts/` altında) |
| `scripts/haftalik_piyasa_raporu.py` | Haftalık pazar raporu scripti (cron job, her Pazartesi 09:00) |

## 🤖 Cron Job Kurulumu (no_agent mode)

**⛔ Kritik: Script yolu kısıtlaması**
- Script `~/.hermes/scripts/` altında OLMALI
- `script=` parametresine **sadece dosya adı** ver (örn: `hepsiemlak_fetch.py`)
- **Hata:** `Blocked: script path resolves outside the scripts directory` → dosyayı `~/.hermes/scripts/` altına taşı
- `workdir=` ayarlanmalı (örn: `/home/batu/.hermes`)

Komut:
```
cronjob(action='create', name='HepsiEmlak {SEHIR} {ILCE}', script='hepsiemlak_fetch.py',
        no_agent=True, schedule='0 */3 * * *',
        deliver='telegram:-1003839224584', workdir='/home/batu/.hermes')
```

### ⛔ ZORUNLU: Çıktı Formatı Kuralı

**no_agent script'leri ASLA** collection loop'u sırasında debug/progress satırı (`HTTP 200`, `X ilan | 0 yeni`) print etmemelidir. Console'a yazılan her şey Telegram'a gider — kullanıcı sadece **final zengin formatlı** sonucu görmeli.

Kural:
1. Loop içindeki tüm `print()` çağrılarını **kaldır** (warmup, API çağrısı, döngü ilerlemesi)
2. Hataları `print()` ile değil, `sys.exit(2)` ile bildir (cron hata olarak kaydeder)
3. Yeni ilanlar varsa → `format_item()` pattern'i ile zengin çıktı
4. Yeni ilan **yoksa** → tamamen sessiz (hiçbir şey print etme)
5. Mevcut script'ler arasında format tutarlılığı: **hepsiemlak_fetch.py** referans alınır

**Batu'nun net talebi:** "Bunu böyle verme. Doğrudan analiz edip ver. Aynen Ankara'daki ev arama bildirimi gibi"

### Örnek Job (her şehir için farklı script + job oluşturun)

| Özellik | Değer |
|---------|-------|
| Script | `hepsiemlak_fetch.py` (kendi şehriniz için kopyalayın: `hepsiemlak_izmir_fetch.py` vb.) |
| Schedule | `0 */3 * * *` (her 3 saat) |
| Mode | `no_agent: true` |
| Deliver | `telegram:-1003839224584` (kendi kanalınız) |
| Workdir | `/home/batu/.hermes` |

### Haftalık Rapor Job

| Özellik | Değer |
|---------|-------|
| Script | `haftalik_piyasa_raporu.py` |
| Schedule | `0 9 * * 1` (Pazartesi 09:00) |
| Mode | `no_agent: true` |
| Deliver | `telegram:-1003839224584` |
| Workdir | `/home/batu/.hermes` |

### Parametre Açıklamaları

| Param | Anlamı |
|-------|--------|
| `counties` | İlçe adı (İngilizce: cankaya, konak, muratpasa) |
| `intent` | `satilik` veya `kiralik` |
| `mainCategory` | `konut` veya `isyeri` |
| `availableForLoanStatus` | `APPLICABLE` (krediye uygun) |
| `p32` | Maks fiyat (TL) |
| `sortField` | `UPDATED_DATE` veya `PRICE` |
| `pageSize` | **Çalışmaz!** API her zaman 24 döndürür |

## 🗄️ SQLite Veritabanı

**Dosya:** `~/.hermes/hepsiemlak_{sehir}_{ilce}.db` (örn: `hepsiemlak_izmir_konak.db` — her lokasyon için ayrı dosya önerilir)

### Tablolar

**`listings`** — Her ilanın güncel durumu

| Alan | Kaynak |
|------|--------|
| `id` (PK) | API `id` |
| `first_seen`, `last_seen` | Otomatik |
| `price`, `score`, `room`, `neighborhood` | API + hesaplanan |
| `gross_sqm`, `net_sqm` | API `sqm.grossSqm[0]`, `sqm.netSqm` |
| `detail_url` | API `detailUrl` (/en/ stripped) |
| `title`, `city_name`, `county_name` | API |
| `listing_id`, `image_url`, `whatsapp` | API |
| `map_lat`, `map_lon` | API `mapLocation` |
| `seller_type`, `advertise_owner` | API |
| `floor_name`, `age`, `online_visit` | API |
| **`raw_data`** | **API'den gelen TÜM JSON (64 field)** |

**`price_history`** — Fiyat değişim geçmişi (`listing_id`, `seen_at`, `price`, `lowest_price`)

**`scan_log`** — Her cron çalışmasının kaydı (`scanned_at`, `api_total`, `new_items`, `price_changes`)

### Örnek Sorgular

```sql
-- Mahalle bazında ortalama fiyat
SELECT neighborhood, COUNT(*), ROUND(AVG(price/1000000),1) as avg_m
FROM listings GROUP BY neighborhood ORDER BY avg_m DESC;

-- En ucuz 3+1
SELECT price, neighborhood, detail_url FROM listings
WHERE room = '3+1' ORDER BY price LIMIT 5;

-- Fiyat düşen ilanlar (pazarlık fırsatı)
SELECT l.neighborhood, l.price as current, ph.price as old
FROM listings l JOIN price_history ph ON ph.listing_id = l.id
WHERE ph.price > l.price ORDER BY ph.seen_at DESC;

-- AI analizi (tüm raw_data ile)
SELECT id, raw_data FROM listings;
```

## ⭐ Puanlama Sistemi (0-100)

### Kriterler ve Ağırlıklar

| # | Kriter | Ağırlık | Formül |
|---|--------|:-------:|--------|
| 1 | 💰 Fiyat | 0-20 | **Bütçe (0-15):** şehre göre alt/üst sınır ayarlanır · **Piyasa (0-5):** mahalle m² fiyat ortalamasına göre |
| 2 | 📍 Mesafe | 0-30 | 0km=30p, 5km=0p, **mahalle referansı** |
| 3 | 🏢 Kat | 0-12 | Bodrum=0, 8+Kat=12 |
| 4 | 🛏️ Oda | 0-12 | 3+1=12, 2+1=8, 1+1=2 |
| 5 | 🏗️ Yaş | 0-8 | 0yaş=8, 50+yaş=0 |
| 6 | 📸 Fotoğraf | 0-10 | 20+=10, 5-=0 |
| 7 | 🎥 Video | 0-5 | Varsa +5 |
| 8 | ⏳ İlan Yaşı | 0-3 | 1-7gün=3, 90+gün=0 |

### Kat Puanları (floor.name)

| `floor.name` | Puan | Açıklama |
|-------------|:----:|----------|
| `Underground 1` | **0** ❌ | Bodrum |
| `Partially Basement` | 1 | Yarı bodrum |
| `Garden Floor` | 3 | Bahçe katı |
| `Ground Floor` | 4 → 5 | Giriş katı |
| `Raised Ground Floor` | 6 → 7 | Yükseltilmiş giriş |
| `1. Floor` | 6 → 8 | |
| `2. Floor` | 8 → 10 | |
| `3. Floor` | 9 → 11 | |
| `4. Floor` | 10 → 12 | |
| `5.–8. Floor` | 10–15 | Üst kat = yüksek puan |

> Not: Eski 0-15 skalasından 0-12'ye indirgenmiştir (`round(eski * 12/15)`).

### ⚠️ Konum Güvenliği (Yanlış Koordinat Koruması)

Emlakçılar ilanın koordinatını yanlış işaretleyebiliyor (örn. Gökkuşağı ilanını Atakule yakını göstermek). Çözüm:

1. **Mahalle referans koordinatı**: DB'de o mahalledeki tüm ilanların ortalama `(lat, lon)`'u
2. Mesafe skoru **her zaman mahalle referansına** göre hesaplanır — bireysel ilan koordinatı değil
3. İlanın koordinatı, mahalle referansından 1.5km+ saparsa → `⚠️` uyarısı

Python'da:
```python
ref_key = mah.replace("İ", "i").upper()
ref = neighborhood_refs.get(ref_key)  # DB'den AVG(map_lat), AVG(map_lon)
if ref:
    dist = haversine_km(WORK_LAT, WORK_LON, ref[0], ref[1])
```

### İş Yeri / Referans Koordinatı

```python
WORK_LAT, WORK_LON = 39.8897782, 32.8594033  # ← kendi eviniz/iş yeriniz ile değiştirin
```

Haversine formülü ile km cinsinden mesafe.

### Çıktı Formatı (Temiz — Telegram)

Sade, okunabilir, emoji overload yok:

```
**64** 🟩🟩🟩🟩🟩🟩⬜⬜⬜⬜ 🎥
**6,975,000 TL** · Harbiye · 3+1 · 135m² · 📍1.9km
2. K · 🏗️26 · 📅4g
✅ 🛏️3+1 ideal · 📸Bol fotoğraf · 🎥Video var
🔗 https://hepsiemlak.com/...

**46** 🟩🟩🟩🟩⬜⬜⬜⬜⬜⬜
**7,500,000 TL** · Barbaros · 2+1 · 60m² · 📍1.8km
Bahçe K · 🏗️3 · 📅1014g
✅ 🏗️Yeni bina · ⛔ Bahçe katı
🔗 https://hepsiemlak.com/...
```

Format kuralları:
- Progress bar: `🟩` * (score//10) + `⬜` * (10 - score//10)
- 🎥 sadece video varsa
- ⚠️ sadece şüpheli koordinat varsa
- ✅ satırında **max 3** highlight
- 🔗 ham URL (markdown link değil — Telegram preview'i engellemek için)

Highlight kuralları:
- `b['fiyat'] >= 12` → 💰İyi fiyat
- `b['piyasa'] >= 4` → 📊Piyasanın altında
- `b['piyasa_fark'] < -10` → 📊%X ucuz (piyasaya göre yüzde)
- `b['mesafe'] >= 20` → 📍Yürüme mesafesi
- `b['oda'] >= 10` → 🛏️3+1 ideal
- `b['oda'] <= 3` → 🛏️1+1 küçük
- `b['yas'] >= 6` → 🏗️Yeni bina
- `b['kat'] <= 2` → 🏢Bodrum/Bahçe katı ⛔
- `b['foto'] >= 7` → 📸Bol fotoğraf
- `b['video'] >= 5` → 🎥Video var
- `listing_age_days <= 7` → ✨Yeni ilan

### Fiyat Puanı Detayı (0-20)

Fiyat skoru iki bileşenden oluşur: **Bütçe (0-15)** + **Piyasa kıyası (0-5)**.

```python
# Bütçe: alt/üst sınır şehre göre (örn. 2M=15p, 6.5M=0p)
budget_score = max(0, min(15, 15 - (price - MIN_PRICE) / ((MAX_PRICE - MIN_PRICE) / 15)))

# Piyasa: mahalle m² ortalamasına göre
AVG(CAST(price AS REAL) / NULLIF(gross_sqm, 0)) GROUP BY neighborhood
diff_pct = (listing_pps - avg_pps) / avg_pps * 100
# %15+ altında=5p | %5-15 altı=4p | ±%5=3p | %5-15 üstü=2p | %15-30 üstü=1p | %30+üstü=0p
```

Kat kısaltmaları: `Floor` → `K`, `Underground` → `Bodrum`, `Garden` → `Bahçe`, `Ground` → `Giriş`, `Raised` → `Yükseltilmiş`

## 🗺️ Mahalle Filtreleri (Örnek — Ankara Çankaya)

**Hariç (dış mahalleler):** Ümitköy, Çayyolu, Alacaatlı, Karapınar, Bayraktar, Yukarı Dikmen, Mutlukent, Prof. Dr. Ahmet Taner Kışlalı, 100. Yıl, Hilal

**Merkez mahalleler:** Küçükesat, Mürsel Uluç, Gökkuşağı, İlkadım, Birlik, Ertuğrulgazi, Keklik Pınarı, Tınaztepe, Kırkkonaklar, Fidanlık, Muhsin Ertuğrul, İleri, Bahçelievler, Kızılay, Maltepe, Kültür, Yıldızevler, Gaziosmanpaşa, Çankaya, Huzur, Ayrancı, Çamlıtepe, Aşıkpaşa, Çiğdem, Ön Cebeci, Seyranbağları, Eti, Barbaros, Naci Çakır, Şehit Cevdet Özdemir, Yukarı Bahçelievler, Harbiye, Öveçler

> 💡 **Yeni şehir için:** `EXCLUDED` set'ine o şehrin uzak/dış mahallelerini, `preferred_neighborhoods` listesine merkez/tercih edilen mahallelerini yazın. Mahalle adlarını ilk çalıştırmada API response'undan alabilirsiniz (ilk taramada `district.name`'leri toplayın).

## 🌐 Web Görselleştirme Arayüzü (Leaflet + Chart.js)

**Server:** `templates/sehir_server.py` — Python stdlib ``http.server`` (Flask gerekmez). **CONFIG sözlüğünü kendi şehrinize göre düzenleyin** (SEHIR_ADI, ILCE, WORK_LAT/LON, DB, PORT).
**Frontend:** `templates/sehir_harita.html` — Leaflet.js + Esri World Topo Map + Chart.js. `__SEHIR_ADI__`, `__WORK_LAT__`, `__WORK_LON__` placeholder'ları server tarafından otomatik doldurulur.
**Rapor:** `~/.hermes/scripts/haftalik_piyasa_raporu.py` — no_agent cron job.

### Başlatma
```bash
cp templates/sehir_server.py templates/sehir_harita.html ~/.hermes/
cd ~/.hermes && python3 sehir_server.py &   # port CONFIG'den (varsayılan 8200)
```
Arka planda: terminal `background=true` ile çalıştır. Yeniden başlatırken `fuser -k 8200/tcp` ile eski PID'i öldür.

### API Endpoints (SQLite'ten canlı veri)

| Endpoint | Dönüş | Açıklama |
|----------|-------|----------|
| `/` | HTML | Ana sayfa (Leaflet harita + 4 tab) |
| `/api/stats` | JSON | Genel istatistik (toplam, ortalama fiyat/m²/puan, şehir adı) |
| `/api/neighborhoods` | JSON | Mahalleler: ortalama fiyat, m², puan, koordinat, referansa uzaklık, yaş, yeni bina % |
| `/api/listings/all` | JSON | Tüm ilanlar (client-side filter/sort) |
| `/api/trend` | JSON | Günlük fiyat trendi (price_history'den) |
| `/api/bargains` | JSON | Fiyat düşen ilanlar (price_history × listings JOIN) |

### Harita Tasarımı (Batu tercihleri)

- **Tile:** Esri World Topo Map (terrain). OpenStreetMap varsayılanı değil. Sade, doğal.
- **Mahalle daireleri:** Renkli yarı-saydam circle marker. **İsim etiketi yok** — sadece hover tooltip. Karmaşa olmamalı.
- **Renk skalası:** m² fiyatı: yeşil (<40K) → turuncu (50-60K) → kırmızı (70K+).
- **Daire büyüklüğü:** İlan sayısına göre (8-32px radius).
- **Referans noktası:** Mavi nokta + "📍 Referans" tooltip.

### 4 Tab Sistemi

| Tab | İçerik |
|-----|--------|
| **Mahalleler** | Genel bakış. Renkli daireler + sidebar liste. Tıkla → zoom + popup (fiyat, min/max, m², mesafe, puan, yaş) |
| **İlanlar** | Sort (puan/fiyat/mesafe/m²/yaş) + oda filtresi (chip: 1+1/2+1/3+1/4+1) + arama. İlk 60 ilan haritada işaretli. Popup'ta hepsiemlak linki |
| **Piyasa** | 3 analiz: (1) Trend grafiği — günlük fiyat + m² trendi (Chart.js, zoom destekli). (2) Scatter — fiyat vs mesafe, her nokta mahalle. (3) Karşılaştırma tablosu — tüm mahalleler, sütun başlığına tıkla sırala. En iyi değerler yeşil |
| **Fırsatlar** | Fiyat düşmüş ilanlar. ▼% etiketi, düşüş miktarı, eski fiyat. Haritada yeşil daireler. Popup'ta düşüş detayı + link |

### Haftalık Rapor Cron Job

```bash
cronjob(action='create', name='Haftalık {SEHIR} Konut Raporu',
        script='haftalik_piyasa_raporu.py', no_agent=True,
        schedule='0 9 * * 1', deliver='telegram:-1003839224584',
        workdir='/home/batu/.hermes')
```

Pazartesi 09:00'da kanala otomatik rapor: özet, trend, en ucuz/pahalı mahalleler, en hareketli mahalleler, haftanın fırsatları, en iyi değer mahalleler.

### ⚠️ Pitfalls

- `parsed.path.rstrip('/')` yapınca ana sayfa `path=''` olur, `'/'` değil — koşulda ikisini de kontrol et (`path == '/' or path == ''`)
- `send_html()` HTML dosyasını `__file__`'ın yanında arar — script ve HTML aynı dizinde olmalı
- `json.dumps(..., default=str)` — price_history'de datetime string'leri var, `default=str` olmazsa serialization hatası
- Trend SQL: `price_history` tablosunda `gross_sqm` yok — JOIN lazım (`JOIN listings l ON l.id = ph.listing_id`)
- Chart.js zoom plugin: `ChartZoom` register etmeyi unutma (`Chart.register(ChartZoom)`)
- Taşınabilir — başka şehir/lokasyon için: `sehir_server.py` CONFIG'ini düzenle (SEHIR_ADI, WORK_LAT/WORK_LON), template'i kopyalayıp yeniden adlandır

## 📦 GitHub Yedekleme

Bu skill GitHub'da yedeklenir: https://github.com/bthnbdk/hermes-skills

Güncelleme yapınca:
```bash
cd ~/hermes-skills
cp -r ~/.hermes/skills/devops/hepsiemlak-cankaya-watchdog/* skills/devops/hepsiemlak-cankaya-watchdog/
cp ~/.hermes/scripts/hepsiemlak_fetch.py scripts/
git add -A && git commit -m "update" && git push
```

Detay: `references/github-backup.md`

## ⚠️ Known Issues

- `pageSize=50` **çalışmaz** — API her sayfada 24 ilan döndürür (sunucu overrides)
- Mahalle adları API'de Türkçe orijinal haliyle — normalize gerekmez
- `availableForLoanStatus=APPLICABLE` sunucu tarafı filtre — response'ta dönmez
- Cloudflare ana sayfayı 403'ler ama API'ye dokunmaz — urllib yeterli
- Eksik koordinat (null) olan ilanlar mesafe puanı alamaz → 0 puan
- Script `~/.hermes/scripts/` dışındaysa cron: `Blocked: script path resolves outside the scripts directory` — taşı ve `script=` parametresinde sadece dosya adı kullan
