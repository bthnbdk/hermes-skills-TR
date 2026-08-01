---
name: migros-market-arama
description: Use when searching products and prices on Migros (Migros Sanal Market). Query their REST API for product search, price comparison, deal hunting, and meal planning.
version: 1.4.0
author: BatuBOT
license: MIT
metadata:
  hermes:
    tags: [migros, market, alışveriş, fiyat, arama, migros-sanalsepet, yemek-planı]
    related_skills: []
references:
  - cost-analysis.md (maliyet analizi şablonu + çıktı formatı + örnek kod)
  - discount-types.md (4 indirim/kampanya tipi detayı)
  - discount-watchdog.md (otomatik indirim takip cron job'u kurulumu)
  - meal-planning.md (haftalık yemek planı + maliyet hesabı şablonu)
---

# Migros Sanal Market Ürün Arama Skill'i

## Overview

Migros Sanal Market'in public REST API'si üzerinden ürün araması, fiyat sorgulaması, karşılaştırma ve yemek planlaması yapar. API herkese açıktır -- herhangi bir auth/API key gerektirmez.

**Base URL:** `https://www.migros.com.tr/rest/search/screens/products`

## API Parametreleri

| Param | Tip | Açıklama | Varsayılan |
|-------|-----|----------|-----------|
| `q` | string | Arama sorgusu (URL-encoded) | zorunlu |
| `page` | int | Sayfa numarası | 1 |
| `size` | int | Sayfa başına ürün sayısı | 30 (max: ?) |

## Response Yapısı

```json
{
  "successful": true,
  "data": {
    "searchInfo": {
      "hitCount": 362,
      "pageCount": 13,
      "storeProductInfos": [ ... ],
      "sortCriteria": "...",
      "aggregationGroups": [ ... ]
    }
  }
}
```

### `storeProductInfos` (ürün array'i) -- her ürün:

| Alan | Tip | Açıklama | Örnek |
|------|-----|----------|-------|
| `id` | int | Ürün ID'si | 20000046040139 |
| `sku` | string | Stok kodu | "46040139" |
| `name` | string | Ürün adı | "Banvit Piliç Bonfile Kg" |
| `brand` | dict | Marka: `{name, id, prettyName}` | `{name: "Banvit", id: 1817}` |
| `regularPrice` | int | Normal fiyat (**kuruş cinsinden!**) | 34995 |
| `shownPrice` | int | Gösterilen fiyat (**kuruş!**) | 34995 |
| `discountRate` | int | İndirim yüzdesi | 0 |
| `unit` | string | Birim türü | "GRAM", "PIECE", "LITER" |
| `unitAmount` | int | Birim miktarı | 1000 (1 kg için), 1 (adet için) |
| `status` | string | Stok durumu | "IN_SALE", "OUT_OF_STOCK" |
| `category` | dict | Kategori: `{id, name, prettyName}` | `{name: "Piliç"}` |
| `categoryAscendants` | array | Hiyerarşik kategori zinciri | `[{name: "Beyaz Et"}, {name: "Et, Tavuk, Balık"}]` |
| `images` | array | Görseller (farklı boyutlarda URL'ler) | `[{urls: {PRODUCT_LIST: "...", PRODUCT_DETAIL: "..."}}]` |

### Fiyat Notu (ÖNEMLİ)

Tüm fiyatlar **kuruş cinsindendir** (int). TL'ye çevirmek için 100'e bölün:
- `regularPrice: 34995` → **349,95 TL**
- `shownPrice: 4995` → **49,95 TL**

### Görsel URL'leri

`images[0].urls` içinde farklı boyutlar:
- `PRODUCT_LIST`: 105x105 (liste/karşılaştırma için)
- `PRODUCT_DETAIL`: 350x350 (detay için)
- `PRODUCT_HD`: 1200x1200 (yüksek çözünürlük)
- `CART`: 60x60 (sepet)

Base domain: `https://images.migrosone.com/sanalmarket/product/<SKU>/`

### Kategoriler / Filtreleme

`aggregationGroups` array'i kategori, marka ve indirim filtrelerini içerir (filtreleme için opsiyonel parametreler mevcut).

### İndirim / Kampanya Yapısı (ÖNEMLİ)

Her ürün 4 farklı indirim/kampanya tipi içerebilir. Detaylar için `references/discount-types.md`:

| Alan | Tip | Açıklama |
|------|-----|----------|
| `discountRate` | int | Doğrudan yüzde indirimi (0 = indirim yok, 47 = %47) |
| `regularPrice` | int | Normal fiyat (indirimsiz, kuruş) |
| `shownPrice` | int | Gösterilen/güncel fiyat (kuruş) |
| `badges` | array | `PRICE_PROMOTED` (sarı etiket), `CROSS_PROMOTED` (çoklu alım), `MIGROSKOP` |
| `groupBadgeMap` | dict | `MARKETING` grubu içinde Migroskop badge detayları (badgeId: 20000000000001) |
| `crmDiscountTags` | array | Sepet indirimleri: "50 TL Sepette 59,9 TL", "2 Öde 1'i Money Hediye" |

**İndirim Tespit Kodları:**

```python
# Doğrudan fiyat indirimi (yüzde)
if p.get('discountRate', 0) > 0:
    print(f"🔥 %{p['discountRate']} indirim")

# Migroskop ürünü
is_migroskop = any(b.get('name') == 'MIGROSKOP' for b in p.get('badges', []))

# Çoklu alım kampanyası
is_cross = any(b.get('name') == 'CROSS_PROMOTED' for b in p.get('badges', []))

# Sepet indirimi
if p.get('crmDiscountTags'):
    for tag in p['crmDiscountTags']:
        print(f"🛒 {tag['tag']}")
```

⚠️ **Not:** Şu an için indirimli ürünlerin listelenmesi API'de doğrudan bir `?discount=true` parametresi yok. En pratik yöntem:
1. Geniş bir sorguyla arama yap (`q=indirim`, `q=kampanya`, vs.)
2. Gelen ürünlerden `discountRate > 0` veya `badges` içerenleri filtrele
3. Sayfalama ile devam et (her sayfada max 30 ürün)

**Migroskop web sayfası:** `https://www.migros.com.tr/migroskop-urunleri-dt-3`
**Tüm indirimliler:** `https://www.migros.com.tr/tum-indirimli-urunler-dt-0`

## Kullanım Şekilleri

### 1. Basit Ürün Arama

```bash
curl -s 'https://www.migros.com.tr/rest/search/screens/products?q=tavuk%20g%C3%B6%C4%9Fs%C3%BC' \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Accept: application/json'
```

### 2. Sayfalı Arama

```bash
curl -s 'https://www.migros.com.tr/rest/search/screens/products?q=s%C3%BCt&page=2&size=20' \
  -H 'User-Agent: Mozilla/5.0' \
  -H 'Accept: application/json'
```

### 3. Fiyat Karşılaştırma (Python script pattern)

```python
import json, subprocess, sys

def migros_search(query: str, page: int = 1, size: int = 20) -> list[dict]:
    """Migros'ta ürün ara, ürün listesi döndür."""
    import urllib.parse
    url = f"https://www.migros.com.tr/rest/search/screens/products?q={urllib.parse.quote(query)}&page={page}&size={size}"
    result = subprocess.run(
        ["curl", "-s", url, "-H", "User-Agent: Mozilla/5.0", "-H", "Accept: application/json"],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return data["data"]["searchInfo"]["storeProductInfos"]

def format_price(kurus: int) -> str:
    """Kuruştan TL formatına çevir."""
    return f"{kurus/100:.2f} TL"

def show_products(products: list[dict]):
    """Ürünleri formatlı göster."""
    for p in products:
        indirim = f" (🔥 %{p['discountRate']} indirim!)" if p.get('discountRate', 0) > 0 else ""
        print(f"• {p['name']}")
        print(f"  Fiyat: {format_price(p['shownPrice'])}{indirim}")
        if p.get('regularPrice') != p.get('shownPrice'):
            print(f"  Normal: {format_price(p['regularPrice'])}")
        print(f"  Marka: {p['brand']['name']}")
        print(f"  SKU: {p['sku']}")
        print()

# Kullanım
urunler = migros_search("tavuk göğsü")
show_products(urunler)
```

## Meal Planning with Migros Prices

Migros API'den güncel fiyatları çekerek haftalık/aylık yemek planı oluşturulabilir.
Detaylar için `references/meal-planning.md`:

- Kullanıcının sağlık profili + beslenme tercihlerine göre özelleştirme
- Her öğünün gramaj bazlı maliyet hesabı
- Haftalık alışveriş listesi çıktısı
- Fiyat referans tablosu (güncel Migros fiyatları)
- Çıktıyı MEDIA: ile dosya olarak gönder (text olarak değil)

### Meal Planning Workflow

1. Kullanıcı bilgilerini topla (yaş, boy, kilo, beslenme tercihleri)
2. Migros API'den temel protein/sebze/meyve/temel gıda fiyatlarını çek
3. Her öğün için gramaj bazlı maliyet hesapla
4. Haftalık plan tablosu + maliyet özeti + alışveriş listesi oluştur
5. Markdown dosyası olarak kaydet ve MEDIA: ile gönder

Pratik referans script: `~/.hermes/scripts/temmuz_yemek_plani.py`

## En Ucuz Ürün Bulma (Cheapest Product Finder)

Kullanıcı "en ucuz fiyat" istediğinde uygulanacak workflow:

### Workflow

1. **Sorguyu geniş tut** — markasız arama yap, tüm sonuçları getir
2. **Stok kontrolü** — `status == "IN_SALE"` olanları filtrele
3. **Keyword filtresi** — ürün adında olması gereken anahtar kelimelerle daralt
4. **Fiyata göre sırala** — `shownPrice` asc sort ile en ucuzu bul
5. **Marka adına dikkat** — Migros markalı ürünler (private label) genelde en ucuzdur
6. **Büyük boy/küçük boy karşılaştırması yap** — bazen büyük boy kg fiyatı daha ucuz olabilir

### Python Pattern

```python
def find_cheapest(products, keywords=None):
    candidates = []
    for p in products:
        if p.get("status") != "IN_SALE":
            continue
        name = p.get("name","").lower()
        if keywords:
            if not all(k.lower() in name for k in keywords):
                continue
        candidates.append(p)
    if not candidates:
        return None
    candidates.sort(key=lambda x: x["shownPrice"])
    return candidates[0]
```

### Per-Unit Cost Hesaplama (ÖNEMLİ)

Sebzeler API'de kg fiyatıyla döner (`unit: "GRAM", unitAmount: 1000`). Kullanıcının adet bazlı istediği miktarları kg'a çevirmek için **tahmini gramaj** kullan:

| Sebze | 1 Adet Yaklaşık | Hesaplama |
|-------|-----------------|-----------|
| Patates orta boy | ~100-150 gr | 3 adet = ~450 gr |
| Kuru Soğan orta | ~120-150 gr | 3-4 adet = ~400 gr |
| Sarımsak baş | ~40-60 gr | 1 baş = ~50 gr |
| Kapya Biber | ~80-120 gr | 2 adet = ~200 gr |
| Sivri Biber | ~40-60 gr | 4 adet = ~200 gr |
| Kabak | ~120-180 gr | 1 adet = ~150 gr |
| Patlıcan (Kemer) | ~120-180 gr | 1 adet = ~150 gr |
| Havuç | ~80-120 gr | 1 adet = ~100 gr |

**Formül:** kg_fiyatı_tl * (adet_sayisi * gram_tek_adet / 1000) — shownPrice kuruş/100 = kg TL

## Output Formatı (Telegram için önerilen)

### 1. Ürün Arama Sonuçları (Kısa Liste)

```
🔍 *[sorgu]* - [adet] ürün bulundu

① *[Ürün Adı]*
💰 [fiyat] TL [🔥 %indirim]
🏷 [marka] · [kategori]
🔗 migros.com.tr/...p-[sku]

② *[Ürün Adı]*
💰 [fiyat] TL
🏷 [marka] · [kategori]
🔗 migros.com.tr/...p-[sku]

📄 Sayfa [x]/[toplam]
```

### 2. Toplu Alışveriş Listesi + Maliyet Analizi

Kullanıcıya toplu listenin maliyetini sunarken:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥩 PROTEİNLER (N kalem)
------------------------------
🥩 Dana Kuşbaşı (X gr) → XXX,XX TL
🥩 Tavuk Göğsü (X gr) → XXX,XX TL
...
Toplam Protein: XXX,XX TL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥦 SEBZELER (N kalem)
------------------------------
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 KİLER (N kalem)
------------------------------
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 TOPLAM (N kalem) → X.XXX,XX TL

📊 ÖĞÜN BAŞI ANALİZ
🍽️ Etli öğün: X
💵 Protein/öğün: XX,XX TL
💵 Günlük ortalama: ~XXX TL/gün

💡 TASARRUF İPUÇLARI
• Private label genelde en ucuz
• Büyük boy alıp bölmek daha ekonomik
```

### 3. En Ucuz Alternatif Gösterimi

```
🟡 [Ürün] SEÇENEKLERİ:
   A) Migros Marka X = XX,XX TL (en ucuz)
   B) Diğer Marka Y   = XX,XX TL
→ **A SEÇENEĞİ** kullanıldı
```

## Watchdog / Otomatik İndirim Takibi

Migros'ta belirli kategorilerdeki ürünler indirime girdiğinde otomatik bildirim almak için bir **no_agent=True watchdog script** + **cron job** kombinasyonu kullanılır.

### Mimari

```
cron job (no_agent=True) → script stdout → Telegram kanalı
    │                              │
    │                              └─ boşsa = sessiz (yeni yok)
    │
    └─ her tick'te çalışır
       ~/.hermes/scripts/migros_indirim_watchdog.py
```

Script, Migros API'sini tarar, önceki çalıştırmadaki indirim durumuyla karşılaştırır, sadece **yeni çıkan** indirimleri raporlar.

### State Yönetimi

- **State file:** `~/.hermes/migros_discount_state.json`
- Her ürün için: discountRate, migroskop durumu, cross_promoted durumu, son görülme zamanı
- 7 gün görülmeyen ürünler otomatik temizlenir (state şişmesin)
- İlk çalıştırmada tüm ürünler "yeni" görünür — state dolduktan sonra gerçek yenilikler bildirilir

### Script Oluşturma

Referans script: `~/.hermes/scripts/migros_indirim_watchdog.py`

Script template:
```python
#!/usr/bin/env python3
import json, os, subprocess, sys
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.hermes/migros_discount_state.json")

# Hariç tutulacak ürün adı anahtar kelimeleri (pet maması vs.)
EXCLUDED_KEYWORDS = ["köpek", "kedi", "kitten", "puppy", "kum", "pet", "akvaryum"]

def is_excluded(product_name):
    name_lower = product_name.lower()
    return any(kw in name_lower for kw in EXCLUDED_KEYWORDS)

CATEGORIES = {
    "🥩 Et":           ["tavuk göğsü", "kıyma", "bonfile", "kuşbaşı", "tavuk but", "kuzu", "dana et", "köfte", "hindi"],
    "🥛 Süt Ürünleri":  ["süt", "yoğurt", "peynir", "tereyağ", "kefir", "ayran", "labne", "krema"],
    "🫒 Zeytinyağı":    ["zeytinyağı", "riviera", "sızma"],
    "🧴 Şampuan":       ["şampuan", "saç kremi"],
    "🦷 Diş Macunu":    ["diş macunu", "ağız bakım"],
    "🧻 Kağıt Havlu":   ["kağıt havlu"],
    "🧻 Tuvalet Kağıdı": ["tuvalet kağıdı"],
    "💧 Islak Havlu":   ["ıslak havlu", "silme bezi"],
    "🍱 Hazır Yemek":   ["hazır yemek", "pratik yemek", "donuk yemek"],
    "🧂 Gıda":          ["makarna", "pirinç", "mercimek", "konserve", "salça"],
}

def search(query):
    import urllib.parse
    url = f"https://www.migros.com.tr/rest/search/screens/products?q={urllib.parse.quote(query)}&page=1&size=30"
    result = subprocess.run(
        ["curl", "-s", url, "-H", "User-Agent: Mozilla/5.0", "-H", "Accept: application/json"],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    return data["data"]["searchInfo"]["storeProductInfos"]

def has_any_discount(p):
    """Ürünün herhangi bir indirimi var mı?"""
    if p.get("discountRate", 0) > 0:
        return True, "PRICE_PROMOTED"
    if any(b.get("name") == "MIGROSKOP" for b in p.get("badges", [])):
        return True, "MIGROSKOP"
    if any(b.get("name") == "CROSS_PROMOTED" for b in p.get("badges", [])):
        return True, "CROSS_PROMOTED"
    if p.get("crmDiscountTags"):
        return True, "CRM_DISCOUNT"
    return False, None

# ... load_state, save_state, main fonksiyonları
```

### Cron Job Kurulumu

```bash
cronjob action=create \
  schedule="0 9,18 * * *" \
  name="migros-indirim-watchdog" \
  script=migros_indirim_watchdog.py \
  no_agent=True \
  deliver="telegram:-1003839224584"
```

Anahtar noktalar:
- `no_agent=True` → LLM çalışmaz, sadece script çıktısı gider. Sıfır token maliyeti.
- Script stdout boşsa → sessiz (yeni indirim yok). Doluyken → mesaj kanala gider.
- Script `discountRate`, badge'ler ve crmDiscountTags dahil tüm indirim tiplerini kontrol eder.
- Önceki state ile karşılaştırma yaparak sadece **yeni** indirimleri bildirir.

### Kategori Seçimi İçin İpuçları

- Spesifik sorgular kullan: "tavuk göğsü" (tek başına "et" değil — çok geniş)
- Her kategori için 5-10 sorgu yeterli (API her sorguda 30 ürün getirir)
- Hazır yemek için "hazır yemek", "pratik yemek", "donuk yemek" sorguları kapsar
- "ıslak havlu" gibi alt kategoriler ayrı sorgulanmalı
- Marka adları doğrudan sorgulanabilir ama pet markaları (Gurmepack) karma sonuç döndürebilir — `EXCLUDED_KEYWORDS` ile filtrele

## Common Pitfalls

1. **Fiyatları 100'e bölmeyi unutma!** API tüm fiyatları kuruş (int) olarak döndürür. TL göstermek için `/100` yap.

2. **`tavuk göğsü` tatlı da döndürür.** "Tavuk göğsü" hem et ürünü hem de bir tatlı ismi. Kategori filtresi veya "bonfile" gibi spesifik terimlerle daralt.

3. **Görsel URL'leri null olabilir.** Her üründe images array'i dolu olmayabilir, null check yap.

4. **Sayfa sayısı `pageCount` ile kontrol edilir.** `hitCount / size` değil, API'nin döndürdüğü pageCount kullan.

5. **`status` alanı stok durumu.** `"IN_SALE"` = satışta, `"OUT_OF_STOCK"` = stokta yok. Tükendi ürünleri filtrele.

6. **Ürün detay API'si (productId ile) çalışmıyor.** Detay endpoint'i 404 döndürüyor. Sadece arama/search endpoint'i kullanılabilir. Ürün sayfası URL'i: `https://www.migros.com.tr/<brand-prettyName>-p-<sku>` (prettyName brand'dan veya ürün adından çıkarılır -- garanti değil).

7. **İndirim listeleme endpoint'i yok.** API'de `?discount=true` veya `?campaignType=DISCOUNT` gibi bir parametre çalışmıyor. İndirimli ürünleri bulmak için geniş sorgu (`q=indirim` → ~5776 sonuç) + istemci taraflı `discountRate > 0` filtresi kullanılır.

8. **Listing sayfaları Angular SPA.** `tum-indirimli-urunler-dt-0` ve `migroskop-urunleri-dt-3` Angular component'leri. SSR state'i sadece meta bilgisi içerir, ürünler client-side yüklenir. JS bundle'ları minified olduğu için API URL'i reverse-engineer etmek zordur.

9. **Watchdog state'i ilk çalışmada dolar.** İlk tick'te tüm ürünler "yeni" görünür ve büyük bir mesaj gelir. State oluştuktan sonraki tick'ler sadece gerçek yenilikleri bildirir. Kullanıcıya bu açıklanmalı veya script önceden bir kere çalıştırılıp state hazırlanmalı.

10. **Pet/hayvan ürünlerini hariç tut.** Watchdog script'inde `EXCLUDED_KEYWORDS` listesi ve `is_excluded()` fonksiyonu ile köpek maması, kedi maması, kum, akvaryum vb. ürünleri ana döngüde `if is_excluded(p.get("name","")): continue` ile filtrele. Yoksa marka bazlı sorgular (örn. Gurmepack) yanlışlıkla pet ürünü de döndürebilir.

11. **Taze sebze/meyve sorguları zordur.** "salatalık taze" bazen turşu döndürür, "limon" bazen limonata. Alternatif sorgular dene veya piyasa fiyatı kullan. En güvenilir: migros markalı ürünler (kuru gıda, süt ürünleri, konserve).

12. **Kıyma çok pahalıdır (~750 TL/kg).** Haftalık planda kıymayı sınırla, tavuk but (110 TL/kg) veya bakliyatla değiştir.

13. **API aynı sorguya farklı sonuçlar döndürebilir.** Aynı `q` parametresiyle ardışık çağrılar farklı ürünler döndürebilir (ör: "kültür mantarı" ilk seferde 37 TL'lik ürün, ikincide 93 TL'lik ürün döndürdü). Bunun sebebi API'nin arkasındaki arama/sıralama motorunun deterministik olmaması. **Çözüm:** `size` parametresini yüksek tut (10+), tüm sonuçları çek, `find_cheapest()` ile en ucuzu bul — ilk sonuca güvenme.

## Verification Checklist

- [ ] API response JSON parse edilebiliyor
- [ ] Fiyatlar kuruş -> TL dönüşümü doğru
- [ ] Sayfalama çalışıyor (page parametresi)
- [ ] Boş sonuç ve hata durumları handle ediliyor
- [ ] Stokta olmayan ürünler filtreleniyor (opsiyonel)
- [ ] Meal planning: fiyatlar güncel, gramaj hesabı doğru, çıktı MEDIA: ile dosya
