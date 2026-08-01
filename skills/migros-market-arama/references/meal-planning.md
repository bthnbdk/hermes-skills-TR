# Migros Fiyatlarıyla Haftalık Yemek Planı Oluşturma

## Use Case

Kullanıcının sağlık profili (yaş, kilo, boy, aktivite) + beslenme tercihlerine
(kahvaltı yok, ekmek yok, günde 2 öğün, makarna sever, yazın karpuz) göre
Migros API'den güncel fiyatlarla bir haftalık/aylık yemek planı çıkar.

## Workflow

### Adım 1: Kullanıcı Bilgilerini Topla

- Yaş, boy, kilo → günlük kalori ihtiyacı (~2000-2400 kcal)
- Öğün sayısı (genelde 2: öğle + akşam)
- Diyet kısıtları (ekmek yok, kahvaltı yok, vs.)
- Tercihler (makarna sever, karpuz sever, zeytinyağı kullanır)
- Bulaşık/süre toleransı (az pişirme, az bulaşık)
- Hazır yemek toleransı (bazı günler hazır alabilir)

### Adım 2: Migros API'den Fiyatları Çek

Her kategori için en ucuz ürünü bul (genelde Migros marka tercih edilir):

```
🥩 Protein: tavuk göğsü, yumurta, ton balığı, mercimek, nohut, beyaz peynir
🥦 Sebze: domates, salatalık, soğan, biber, kabak, ıspanak, patates, marul
🍉 Meyve: karpuz (çekirdeksiz), elma, limon
🫒 Temel: zeytinyağı, makarna, bulgur, salça, yoğurt
```

### Adım 3: API Response'ları İşle

Her API sorgusunda en ucuz seçeneği seç:

```python
def migros_search(query):
    import subprocess, json, urllib.parse
    url = f"https://www.migros.com.tr/rest/search/screens/products?q={urllib.parse.quote(query)}&page=1&size=3"
    result = subprocess.run(
        ["curl", "-s", url, "-H", "User-Agent: Mozilla/5.0"],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    return data["data"]["searchInfo"]["storeProductInfos"]
```

Fiyatlar **kuruş cinsinden** — TL'ye dönüştürmek için `/100`.

### Adım 4: Maliyet Hesabı

Her öğünün malzeme maliyetini hesapla:

```python
def item(gram, price_per_kg):
    return gram / 1000 * price_per_kg

def adet(n, adet_fiyat):
    return n * adet_fiyat

# Örnek: Tavuk göğsü 200g
# prices["tavuk_gogs"] = 329.95 TL/kg
# cost = item(200, 329.95) = 65.99 TL
```

### Adım 5: Haftalık Plan Şablonu

Her gün için 2 öğün (öğle + akşam) planla:

| Gün | Öğle (işte) | Akşam (evde) |
|-----|------------|-------------|
| Pzt | Ton balıklı salata (hazırlık yok) | Tavuk sote + salata (15dk, 1 tava) |
| Sal | Mercimek çorbası (termos) | Fırın köfte + patates (25dk fırın) |
| Çar | Haşlanmış yumurta + peynir | 🍝 Makarna günü |
| Per | Nohut + yoğurt | Ispanaklı yumurta (10dk tek tava) |
| Cum | Hazır yemek / artanlar | Bulgur pilavı + cacık + karpuz |
| Cmt | — | Karpuz + peynir + ceviz (hafif, hiç pişmez) |
| Pzr | — | Fırın patates + yumurta |

### Adım 6: Çıktı Formatı

Planı markdown tablosu + maliyet özeti + alışveriş listesi olarak kaydet
ve dosyayı MEDIA: yoluyla gönder (text olarak değil).

## Fiyat Referansı (Temmuz 2026)

| Ürün | Migros Fiyatı | Birim |
|------|--------------|-------|
| Tavuk göğsü bonfile (Banvit) | 329.95 TL | kg |
| Tavuk but (Uzman Kasap) | 109.95 TL | kg |
| Yumurta (10'lu) | 111.95 TL | adet |
| Ton balığı (Migros 2x160g) | 121.95 TL | paket |
| Dana kıyma (Uzm Ks 400g) | 298.95 TL | 400g |
| Kırmızı mercimek (Migros) | 74.95 TL | kg |
| Nohut (Migros) | 62.95 TL | kg |
| Beyaz peynir (Migros) | 265.90 TL | kg |
| Yoğurt (Migros süzme 900g) | 135.50 TL | 900g |
| Süt (Migros UHT 1L) | 49.95 TL | L |
| Zeytinyağı (Migros sızma 1L) | 278.00 TL | L |
| Makarna (Migros 500g) | 17.95 TL | 500g |
| Bulgur (Migros 1kg) | 34.95 TL | kg |
| Domates salçası (Migros 830g) | 49.00 TL | 830g |
| Domates (taze kg) | 39.95 TL | kg |
| Soğan kuru (kg) | 23.90 TL | kg |
| Patates (kg) | 42.95 TL | kg |
| Karpuz çekirdeksiz (kg) | 27.95 TL | kg |
| Muz (kg) | 119.95 TL | kg |

## Pitfall'lar

1. **Sebze-meyve fiyatları mevsimseldir** — Karpuz yazın ucuz, kışın pahalı.
   Mevsimine göre plan yap (yaz: kabak, domates, karpuz; kış: lahana, kereviz, portakal).
2. **Migros API taze sebze/meyve için zayıf** — "salatalık taze" sorgusu bazen
   turşu veya başka ürün döndürür. Alternatif sorgular dene ("salatalık kg",
   "Bahçıvan salatalık") veya piyasa fiyatı kullan.
3. **Bazı ürünler Migros marka değil** — Tavuk göğsünde Banvit en ucuz,
   Migros marka yok. Kıyma için Uzman Kasap tek seçenek.
4. **Kıyma çok pahalı (~750 TL/kg)** — Haftada 1 kez kullan, diğer günler
   tavuk but (110 TL/kg) veya bakliyatla değiştir.
5. **API rate limit** — Sorgular arası 0.3 saniye bekle. 20+ sorguda
   gecikme olursa toplu çekim yap.
6. **Fiyatlar zamanla değişir** — Bu referanstaki fiyatlar Temmuz 2026'ya
   aittir. Yeni bir plan yaparken API'den taze fiyat çek.
