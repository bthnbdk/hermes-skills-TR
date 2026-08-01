---
name: hepsiemlak-arsa-takip
description: "Monitor land/plot (arsa) listings on HepsiEmlak for ANY city in Turkey. Fully configurable: {sehir} slug, arsa tipleri (villa/konut/tarla/bahçe/ticari/imarsız), tek tapu filtresi açık/kapalı, max price, min/max m², counties. Python stdlib urllib, no external deps."
version: 4.0.0
author: Turkce AI Skillleri Toplulugu
---

# 🏗️ HepsiEmlak Arsa Takip — Tüm Türkiye (Tam Yapılandırılabilir)

HepsiEmlak API'sinden herhangi bir şehirde satılık **arsa ilanlarını** otomatik izleyen sistem.
**Ne izleyeceğiniz tamamen size bağlı**: sadece tek tapulu villa arsası, sadece tarla, imarlı konut + bahçe kombinasyonu, hepsi birden — hepsi mümkün.
SQLite veritabanı, AI puanlama ve Telegram bildirimi ile.

## 🎯 Yapılandırma (İlk Adım — Her Şey Değiştirilebilir)

| Değişken | Örnek | Açıklama |
|----------|-------|----------|
| `{sehir}` | `ankara`, `istanbul`, `izmir`, `antalya`, `bursa`... | HepsiEmlak URL slug'ı (Türkçe karakterler ASCII'ye çevrilir: `çankırı` → `cankiri`) |
| `{SEHIR_ADI}` | `Ankara`, `İstanbul`... | Bildirimlerde görünen şehir adı |
| `arsa_tipleri` | `["zoned_villa", "zoned_residential"]` | Takip edilecek arsa tipleri (aşağıdaki tablo) — **boş = hepsi** |
| `tek_tapu` | `True` veya `False` | Sadece tek tapulu (müstakil) arsalar mı? `False` = hisseli dahil |
| `max_price` | `2500000` | Maks fiyat (TL) — şehre göre ayarlayın |
| `min_sqm` / `max_sqm` | `500` / `2000` | Arsa büyüklüğü aralığı (boş = sınırsız) |
| `counties` | `golbasi` veya boş | İlçe filtresi (boş = tüm ilçeler) |
| `preferred_counties` | `["etimesgut", "sincan"]` | Puanlama'da tercih edilen ilçeler |

**Tüm 81 il için slug listesi:** `references/turkiye-sehirleri.csv` (HepsiEmlak URL formatında)

### 🏷️ Arsa Tipleri (API `subCategory.typeName`)

| API'den gelen (`typeName`) | Türkçe | Varsayılan puan | Varsayılan kabul |
|---------------------------|--------|:----:|:-----:|
| `Zoned - Villa` | İmarlı Villa | **20** 🥇 | ✅ |
| `Zoned - Residential` | İmarlı - Konut | 8 | ✅ |
| `Field` | Tarla | 5 | ❌ (kapalı) |
| `Garden` | Bahçe | 6 | ❌ (kapalı) |
| `Zoned - Commercial` | İmarlı - Ticari | 10 | ❌ (kapalı) |
| `Unzoned` / diğer | İmarsız / Diğer | 3 | ❌ (kapalı) |

> 💡 **`arsa_tipleri` listesiyle hangilerinin takip edileceğini seçin.** Boş bırakılırsa API'den gelen tüm tipler izlenir (filtre yok). Puanlar da ihtiyaca göre değiştirilebilir — örn. tarla yatırımı yapan biri `Field`'a 20 puan verebilir.

Kurulum örnekleri:
```
# Sadece tek tapulu villa arsası (varsayılan):
HepsiEmlak İzmir'de tek tapulu, 3 milyon TL altı villa arsası ilanlarını günde 2 kez kontrol et

# İmarlı konut + bahçe, hisseli dahil:
HepsiEmlak Bursa'da imarlı konut ve bahçe arsalarını 2 milyon TL altı takip et, hisseli tapu da olsun

# Tarla yatırımı:
HepsiEmlak Konya'da 1000-5000 m² tarla ilanlarını 1 milyon TL altı izle

# Her şey (filtre yok):
HepsiEmlak Antalya'da tüm arsa ilanlarını takip et
```

## 🧠 API

**URL:** `https://www.hepsiemlak.com/api/realty-list/{sehir}-satilik/arsa`

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

### Tek Tapu (Müstakil) Tespiti

API'de `tek tapu` alanı doğrudan yok — aşağıdaki sinyallerle çıkarım yapılır:

| Sinyal | Anlamı |
|--------|--------|
| `title` veya `description` içinde "tek tapu", "müstakil tapu", "tek parsel" | ✅ Tek tapu |
| `identificationNo` dolu | Parsel numarası var (genelde tek tapu) |
| `title` içinde "hisseli", "hisse" | ❌ Hisseli tapu |
| Başlıkta "ifraz", "tevhit" | Parsel işlemi var — dikkat |

```python
TEK_TAPU_KEYWORDS = ["tek tapu", "müstakil tapu", "tek parsel", "tam tapu"]
HISSELI_KEYWORDS = ["hisseli", "hisse"]

def tek_tapu_mu(item) -> bool:
    text = (item.get("title", "") + " " + item.get("description", "")).lower()
    if any(k in text for k in HISSELI_KEYWORDS):
        return False
    if item.get("identificationNo"):
        return True
    return any(k in text for k in TEK_TAPU_KEYWORDS)
```

> ⚠️ **Önemli:** `tek_tapu=True` ise sadece kesin tek tapu sinyali olanlar gösterilir. `tek_tapu=False` ise bu filtre hiç uygulanmaz. Belirsiz durumlarda `title`/`description`'ı kullanıcıya gösterip karar bırakılabilir.

### Filtreleme Parametreleri (test edilmiş)

| Param | Değer | Etki |
|-------|-------|------|
| `p32` | `2500000` | Maks 2.5M TL |
| `counties` | `golbasi` | Sadece Gölbaşı |
| `sortField` | `UPDATED_DATE` | Güncellenme tarihine göre |
| `sortDirection` | `DESC` | En yeni en üstte |

## 📊 Puanlama Kriterleri (Yapılandırılabilir)

| Kriter | Ağırlık | Açıklama |
|--------|:-------:|----------|
| 💰 **Toplam Fiyat** | 25% | **Bütçe (0-20):** şehre göre alt/üst sınır ayarlanır · **Piyasa (0-5):** ilçe m² fiyat ortalamasına göre |
| 💵 **m² Fiyatı** | 15% | Düşük m² fiyatı = yüksek puan |
| 📏 **Arsa Büyüklüğü** | 10% | İdeal aralık yapılandırılır (varsayılan 500-2000m²; tarla için 2000-10000m² olabilir) |
| 🏷️ **Arsa Tipi** | 15% | `arsa_tipleri` tablosundaki puanlar — ihtiyaca göre değiştirin |
| 📍 **İlçe** | 20% | Tercih edilen ilçeler — **şehre göre yapılandırılır** |
| 📸 **Fotoğraf** | 10% | 10+ foto = 10p |
| 🎥 **Video** | 5% | Varsa 5p |

### İlçe Puanları — Şehir Bazlı Yapılandırma

İlçe puanları **şehre göre değişir**. Genel kural:
- Metro/raylı sistem hattı olan ilçeler: yüksek puan (16-20)
- Hızlı gelişen yeni konut alanları: 14-18
- Kentsel dönüşüm bölgeleri: 10-14
- Merkez ama pahalı ilçeler: 12-16
- Uzak/kırsal ilçeler: 2-8

**Örnek — Ankara (varsayılan):**

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

> 💡 Yeni şehir için: `preferred_counties` listesini o şehrin gelişen ilçeleriyle doldurun. Puanlar aynı mantıkla atanır — yerel emlak trendlerini araştırıp güncelleyin.

## 💡 Arsa Alırken Bilinmesi Gerekenler (Türkiye Geneli)

### 📍 Konum & Gelişim

- **Metro/raylı sistem uzantıları**: Hattın güzergahındaki arsalar ciddi değerleniyor — her şehirde hangi ilçelerden geçtiğini kontrol edin
- **Gelişmekte olan ilçeler**: OSB, üniversite, hastane, organize sanayi yatırımı alan ilçeler hızlı büyüyor
- **Dönüşüm bölgeleri**: Büyükşehirlerde kentsel dönüşüm projeleri olan bölgeler
- **Belediye yatırım planları**: Hangi ilçede altyapı, okul, hastane, sanayi bölgesi yapılacağı arsayı direkt etkiler

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
| Belediye CBS portalı | Nazım imar planları (her şehrin kendi CBS'si) |
| Sahibinden / Hepsiemlak | Piyasa fiyat takibi |
| AFAD | Heyelan/risk haritaları |

## 🗄️ SQLite Veritabanı

**Dosya:** `~/hepsiemlak_arsa_{sehir}.db` (örn: `hepsiemlak_arsa_istanbul.db`)

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
    tek_tapu INTEGER,          -- 1/0 (çıkarım)
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

## ⏰ Zamanlanmış Görev Kurulumu (Agent Bağımsız)

Script bağımsız Python'dur — herhangi bir zamanlayıcıyla çalışır:

```bash
# Seçenek A — Sistem cron (her ortamda):
0 */3 * * * cd <calisma_dizini> && python3 hepsiemlak_arsa_fetch.py >> arsa.log 2>&1

# Seçenek B — Hermes:
cronjob(
    action='create',
    name='HepsiEmlak {SEHIR} Arsa ({TIpler})',
    script='hepsiemlak_arsa_fetch.py',
    no_agent=True,
    schedule='0 */3 * * *',  # her 3 saatte
    deliver='<KANAL>',
    workdir='<WORKDIR>'
)

# Seçenek C — Doğrudan:
python3 hepsiemlak_arsa_fetch.py
```

## 📝 Çıktı Formatı

```
🏡 **Yeni Arsa İlanı — {SEHIR}**
📅 27.05.2026 15:00  |  📊 500 ilan içinden 3 uygun
🔑 Filtre: {arsa_tipleri} · {tek_tapu: "tek tapu" | "hisseli dahil"} · ≤{max_price} TL

**76** 🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜
**2,100,000 TL** · Gölbaşı · İkizce · 850m² · 2,470 TL/m²
Zoned - Villa · 🏡Villa arsası · Tek tapu ✅ · 💰Uygun fiyat · 📊Piyasanın altında
🔊 Gelişen bölge, Mogan gölü etkisi
🔗 link
```

Tip etiketleri:
- `Zoned - Villa` → 🏡Villa arsası
- `Zoned - Residential` → 🏠Konut arsası
- `Field` → 🌾Tarla
- `Garden` → 🌳Bahçe
- `Zoned - Commercial` → 🏢Ticari arsa
- Diğer/İmarsız → 📄İmarsız/Diğer

### Fiyat Puanı Detayı (0-25)

Fiyat skoru iki bileşenden oluşur: **Bütçe (0-20)** + **Piyasa kıyası (0-5)**.

```python
# Bütçe: alt sınır ve üst sınır şehre göre ayarlanır (örn. Ankara: 500K-2.5M)
budget_score = max(0, min(20, 20 - (price - MIN_PRICE) / ((MAX_PRICE - MIN_PRICE) / 20)))

# Piyasa: ilçe m² ortalamasına göre
AVG(CAST(price AS REAL) / NULLIF(gross_sqm, 0)) GROUP BY county
diff_pct = (price_per_sqm - avg_pps) / avg_pps * 100
# %15+ altında=5p | %5-15 altı=4p | ±%5=3p | %5-15 üstü=2p | %15-30 üstü=1p | %30+üstü=0p
```

Çıktı highlight'ları: `📊Piyasanın altında` (piyasa ≥4) · `📊%X ucuz` (fark < -%10) · `Tek tapu ✅` (tek_tapu=True ise)

## ⚠️ Filtreleme

- `detailUrl` Türkçe — `/en/` prefix'i YOK
- `age` ve `floor` null — puanlamada yok
- `room` anlamsız — `[0]` gelir
- `sqm.price` = m² fiyatı (TL/m²) — önemli kriter
- `sqm.grossSqm[0]` = arsa büyüklüğü
- `identificationNo` = parsel numarası (varsa)
- `tek_tapu=True` ise sadece kesin tek tapu sinyali olanlar; `False` ise filtre yok

## 📂 Skill Files

| Dosya | Açıklama |
|-------|----------|
| `SKILL.md` | Ana talimatlar (bu dosya) |
| `references/turkiye-sehirleri.csv` | 81 ilin HepsiEmlak URL slug'ları |
| `references/arsa-puanlama-ornekleri.md` | Farklı şehirler için ilçe puanı örnekleri |
