# Maliyet Analizi Şablonu

Kullanıcıya bir alışveriş listesinin **en ucuz seçeneklerle** maliyetini sunmak için kullanılır.

## Workflow

1. **Stok kontrolü**: sadece `status == "IN_SALE"` olan ürünler
2. **Keyword filtresi**: ürün adında aranan kelimelerin tümü geçmeli
3. **Fiyat sıralaması**: `shownPrice` ascending → en ucuz ilk sırada
4. **Miktar hesaplama**: 
   - KG birimli ürünler: `kg_fiyati_tl * (adet_sayisi * tahmini_gram / 1000)`
   - PIECE birimli ürünler: direkt `shownPrice / 100`
5. **Kategorilere ayır**: Proteinler / Sebzeler / Kiler / Baharatlar
6. **Öğün başı analiz**: protein/öğün, günlük ortalama
7. **Tasarruf ipuçları ekle**: private label alternatifleri, büyük boy avantajları

## Output Template (Telegram için)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥩 PROTEİNLER (N kalem) = XXX,XX TL
------------------------------
🥩 Dana Kuşbaşı (X gr) → XXX,XX TL — Marka Fiyat/kg
🥩 Tavuk Göğsü (X gr) → XXX,XX TL
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥦 SEBZELER (N kalem) = XXX,XX TL
------------------------------
🥫 Garnitür (X gr)   → XXX,XX TL
🥦 Patates (X gr)    → XXX,XX TL
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 KİLER (N kalem) = XXX,XX TL
------------------------------
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 TOPLAM (N kalem) → X.XXX,XX TL

📊 ÖĞÜN BAŞI ANALİZ
🍽️  Etli öğün: X öğün
💵 Protein/öğün:     XX,XX TL
💵 Günlük ortalama:  ~XXX TL/gün

💡 TASARRUF İPUÇLARI
• ...
```

## Örnek Kod (Python)

```python
def adet_maliyeti_hesapla(shownPrice_kurus, adet_sayisi, gram_tek_adet=100):
    """Kg fiyatı (kuruş) + adet bilgisinden toplam TL maliyet."""
    kg_fiyati_tl = shownPrice_kurus / 100
    toplam_kg = adet_sayisi * gram_tek_adet / 1000
    return kg_fiyati_tl * toplam_kg

def kategori_ozeti(items: list, category_name: str):
    """items = [(isim, fiyat_tl), ...] formatında listeyi özetle."""
    toplam = sum(f for _, f in items)
    return toplam

def ogun_analizi(protein_toplam, gun_sayisi=7):
    """Protein maliyetinin öğün başına ve günlük ortalamasını hesapla."""
    etli_ogun = 5  # kullanıcının listesine göre
    return {
        "protein_per_meal": protein_toplam / etli_ogun,
        "daily_avg": protein_toplam / gun_sayisi,
    }
```
