---
name: hepsiemlak-arsa-watchdog
description: "Monitor villa plots (villa arsası) with single title deed (tek tapu) on HepsieEmlak for Ankara. Filters by subCategory (Zoned Villa/Residential), max price 2.5M TL. Python stdlib urllib, no external deps."
version: 2.0.0
author: Batu
---

# HepsieEmlak Villa Arsası (Tek Tapu) Watchdog

HepsiEmlak API'sinden Ankara satılık **tek tapulu villa arsalarını** otomatik izleyen sistem.
Sadece imarlı villa ve imarlı konut arsalarını takip eder — tarla, bahçe, ticari arsalar filtrelenir.
SQLite veritabanı, AI puanlama ve Telegram bildirimi ile.

## 🧠 API

**URL:** `https://www.hepsiemlak.com/api/realty-list/ankara-satilik/arsa`

### Parametreler

| Param | Örnek | Açıklama |
|-------|-------|----------|
| `intent` | `satilik` | Satılık |
| `mainCategory` | `arsa` | Arsa kategorisi |
| `pageNo` | `1` | Sayfa |
| `sortField` | `UPDATED_DATE` veya `PRICE` | Sıralama |
| `sortDirection` | `DESC` veya `ASC` | Yön |
| `p32` | `1000000` | Maks fiyat (TL) |
| `counties` | `golbasi` | İlçe filtresi (isteğe bağlı) |

### Response Yapısı (konut ile aynı, farklı olanlar)

| Alan | Arsa'da Farkı |
|------|---------------|
| `mainCategory.name` | `"Arsa"` |
| `subCategory.typeName` | Arsa tipi (⚠️ **İngilizce**): `Zoned - Residential`=İmarlı Konut, `Field`=Tarla, `Garden`=Bahçe, `Zoned - Commercial`=İmarlı Ticari |
| `age` | Her zaman `null` (arsa için anlamsız) |
| `floor` | Her zaman `null` |
| `room`, `livingRoom` | `[0]`, anlamsız |
| `sqm.netSqm` | Her zaman `0` |
| `sqm.grossSqm[0]` | **Arsa büyüklüğü (m²)** ✅ |
| `sqm.price` | **m² fiyatı (TL/m²)** ✅ |
| `detailUrl` | ⚠️ `/en/` prefix'i **VAR** — strip etmeyi unutma! |
| `identificationNo` | Arsa için varsa parsel numarası |

### Filtreleme Parametreleri (test edilmiş)

| Param | Değer | Etki |
|-------|-------|------|
| `p32` | `2500000` | Maks 2.5M TL (villa arsası) |
| `counties` | `golbasi` | Sadece Gölbaşı |
| `sortField` | `UPDATED_DATE` | Güncellenme tarihine göre |
| `sortDirection` | `DESC` | En yeni en üstte |

## 📊 Puanlama Kriterleri (Villa Arsası)

| Kriter | Ağırlık | Açıklama |
|--------|:-------:|----------|
| 💰 **Toplam Fiyat** | 25% | **Bütçe (0-20):** 500K=20, 2.5M=0 · **Piyasa (0-5):** ilçe m² fiyat ortalamasına göre |
| 💵 **m² Fiyatı** | 15% | Düşük m² fiyatı = yüksek puan |
| 📏 **Arsa Büyüklüğü** | 10% | Orta büyüklük (500-2000m²) ideal |
| 🏷️ **Arsa Tipi** | 15% | İmarlı Villa=20, İmarlı Konut=8 (villa arsası odaklı) |
| 📍 **İlçe** | 20% | Tercih edilen ilçeler (Etimesgut, Sincan, Pursaklar vb.) |
| 📸 **Fotoğraf** | 10% | 10+ foto = 10p |
| 🎥 **Video** | 5% | Varsa 5p |

### Arsa Tipi Puanları (Villa Odaklı)

⚠️ Sadece `Zoned - Villa` ve `Zoned - Residential` tipleri gösterilir. Tarla, bahçe, ticari arsalar **otomatik filtrelenir**.

| API'den gelen (`typeName`) | Türkçe | Puan | Kabul |
|---------------------------|--------|:----:|:-----:|
| `Zoned - Villa` | İmarlı Villa | **20** 🥇 | ✅ Villa arsası |
| `Zoned - Residential` | İmarlı - Konut | 8 | ✅ Villa yapılabilir |
| Diğer | Tarla/Bahçe/Ticari | — | ❌ Filtrelenir |

### İlçe Puanları (gelişim potansiyeline göre güncellenmiş)

| İlçe | Puan | Not |
|------|:----:|-----|
| Etimesgut | **20** 🥇 | 🔊 Metro hattı, hızlı büyüyen bölge |
| Sincan | **18** | 🔊 Metro + gelişen konut alanları |
| Pursaklar | **17** | 🔊 Yeni gelişen bölge |
| Kahramankazan | **16** | 🔊 OSB, sanayi yatırımı |
| Çankaya | 16 | Merkez ama pahalı |
| Yenimahalle | 16 | Metro hattı |
| Gölbaşı | 15 | 🔊 Gelişen, Mogan gölü etkisi |
| Mamak | 14 | 🔄 Kentsel dönüşüm |
| Altındağ | 12 | 🔄 Kentsel dönüşüm |
| Keçiören | 10 | |
| Akyurt | 10 | |
| Çubuk | 8 | |
| Beypazarı | 5 | 🟡 Uzak ilçe |
| Polatlı | 4 | 🟡 Uzak ilçe |
| Ayaş | 4 | 🟡 Uzak ilçe |
| Diğer | 2-3 | 🟡 Uzak ilçe |

## 💡 Ankara Arsa Alırken Bilinmesi Gerekenler

### 📍 Konum & Gelişim

- **Metro hattı uzantıları**: Kızılay–Çayyolu, Batıkent–Sincan gibi hatların güzergahındaki arsalar ciddi değerleniyor
- **Gelişmekte olan ilçeler**: Etimesgut, Sincan, Pursaklar, Kahramankazan son yıllarda hızlı büyüyor
- **Dönüşüm bölgeleri**: Mamak ve Altındağ'da kentsel dönüşüm projeleri var
- **ABB yatırım planları**: Hangi ilçede altyapı, okul, hastane, sanayi bölgesi yapılacağı arsayı direkt etkiler

### 📋 İmar Durumu (En Kritik Kriter)

- **İmarlı / imarsız ayrımı**: İmarsız arsa ucuzdur ama satmak/inşaat yapmak çok zor
- **Kat adedi ve TAKS/KAKS**: Aynı büyüklükte iki parselde biri 3 kat, diğeri 8 kat yapılabiliyorsa değerleri çok farklı
- **Kullanım amacı**: Konut, ticaret, sanayi, tarım — her birinin hukuki çerçevesi farklı
- **İmar planı revizyonu**: Belediye meclisi gündemlerini takip edin

### 🔍 Tapu & Hukuk

- **Tapu türü**: Kat irtifakı, hisseli tapu, müstakil tapu
- **Şerh ve hacizler**: e-Devlet üzerinden sorgulama yapılabilir
- **2/B arazisi**: Eski orman/hazine arazisi statüsündeyse tapu devri kısıtlı olabilir
- **Kamulaştırma riski**: Belediye veya Karayolları güzergahını kontrol edin

### ⚠️ Kırmızı Bayraklar

- Satıcı tapu yerine "sözleşme" ile satmak istiyorsa → kaçın
- Fiyat piyasanın çok altındaysa → hukuki sorun neredeyse kesin
- "İmar çıkacak" vaadi sadece sözlüyse → yazılı teminat isteyin
- Hisseli tapu + çok sayıda hissedar → ileride satmak kabusa dönebilir

### 🛠️ Araştırma Araçları

| Platform | Ne İşe Yarar |
|----------|-------------|
| [Tapu e-Hizmetler](https://www.tkgm.gov.tr) | Tapu sorgulama, imar durumu |
| [Parselsorgu.com](https://parselsorgu.com) | Ücretsiz imar + parsel sorgulama |
| Endeksa / Reidin | Fiyat trend analizi |
| [Ankara İBB CBS](https://cbs.ankara.bel.tr) | Belediye nazım imar planları |
| Sahibinden / Hepsiemlak | Piyasa fiyat takibi |
| AFAD | Heyelan/risk haritaları (Keçiören, Çankaya yamaçları)

## 🗄️ SQLite Veritabanı

**Dosya:** `~/.hermes/hepsiemlak_arsa.db`

### Tablolar

```sql
CREATE TABLE listings (
    id TEXT PRIMARY KEY,
    first_seen TEXT, last_seen TEXT,
    price INTEGER, score INTEGER,
    subcategory TEXT,          -- "İmarlı - Konut", "Tarla" vb.
    county TEXT,               -- ilçe
    neighborhood TEXT,         -- mahalle
    gross_sqm REAL,            -- arsa büyüklüğü (m²)
    price_per_sqm REAL,        -- m² fiyatı
    detail_url TEXT,
    title TEXT,
    image_url TEXT,
    map_lat REAL, map_lon REAL,
    seller_type TEXT,
    advertise_owner TEXT,
    listing_age_days INTEGER,
    image_count INTEGER,
    has_video INTEGER,
    identification_no TEXT,    -- parsel no
    raw_data TEXT              -- tüm API JSON
);

CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id TEXT REFERENCES listings(id),
    seen_at TEXT, price INTEGER, lowest_price INTEGER
);

CREATE TABLE scan_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scanned_at TEXT, api_total INTEGER,
    items_fetched INTEGER, items_parsed INTEGER,
    new_items INTEGER, price_changes INTEGER
);
```

## 🚀 Cron Job Kurulumu

```python
cronjob(
    action='create',
    name='HepsiEmlak Ankara Villa Arsasi (Tek Tapu)',
    script='hepsiemlak_arsa_fetch.py',
    no_agent=True,
    schedule='0 */3 * * *',  # her 3 saatte
    deliver='telegram:-1003839224584',
    workdir='/home/batu/.hermes'
)
```

## 📝 Çıktı Formatı

```
🏡 **Yeni Villa Arsası (Tek Tapu) — Ankara**
📅 27.05.2026 15:00  |  📊 500 ilan içinden 3 villa arsası uygun
🔑 Sadece tek tapulu, imarlı villa arsaları

**76** 🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜
**2,100,000 TL** · Gölbaşı · İkizce · 850m² · 2,470 TL/m²
Zoned - Villa · 🏡Villa arsası · Tek tapu ✅ · 💰Uygun fiyat · 📊Piyasanın altında
🔊 Gelişen bölge, Mogan gölü etkisi
🔗 link
```

### Fiyat Puanı Detayı (0-25)

Fiyat skoru iki bileşenden oluşur: **Bütçe (0-20)** + **Piyasa kıyası (0-5)**.

```python
# Bütçe: 500K=20p, 2.5M=0p
budget_score = max(0, min(20, 20 - (price - 500_000) / 100_000))

# Piyasa: ilçe m² ortalamasına göre
AVG(CAST(price AS REAL) / NULLIF(gross_sqm, 0)) GROUP BY county
diff_pct = (price_per_sqm - avg_pps) / avg_pps * 100
# %15+ altında=5p | %5-15 altı=4p | ±%5=3p | %5-15 üstü=2p | %15-30 üstü=1p | %30+üstü=0p
```

Çıktı highlight'ları: `📊Piyasanın altında` (piyasa ≥4) · `📊%X ucuz` (fark < -%10) · `🏡Villa arsası · Tek tapu ✅`

## ⚠️ Filtreleme

- `detailUrl` Türkçe — `/en/` prefix'i YOK
- `age` ve `floor` null — puanlamada yok
- `room` anlamsız — `[0]` gelir
- `sqm.price` = m² fiyatı (TL/m²) — önemli kriter
- `sqm.grossSqm[0]` = arsa büyüklüğü
- `identificationNo` = parsel numarası (varsa)
