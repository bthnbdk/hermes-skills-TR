# Yatırımlık Daire Takibi

## Genel Bakış

HepsiEmlak'tan yatırım amaçlı küçük daireleri tarar. 4 şehir: Kırıkkale, Eskişehir, Bolu, Sakarya. Fiyat aralığı: 800K-1.5M TL. Krediye uygun (`availableForLoanStatus=APPLICABLE`).

## Script: `hepsiemlak_yatirim_tara.py`

**Cron:** Her gün 15:00 (`0 15 * * *`)
**DB:** `~/.hermes/hepsiemlak_yatirim.db`
**API:** `curl_cffi` ile Cloudflare bypass

## Puanlama Kriterleri

| Kriter | Max | Açıklama |
|--------|:---:|----------|
| 💰 Fiyat | 25 | 800K=25p, 1.5M=0p |
| 🏙️ Şehir | 20 | Eskişehir=20, Kırıkkale/Sakarya=18, Bolu=17 |
| 🛏️ Oda | 20 | 1+0=20, 1+1=18, 2+1=12, 3+1=5 |
| 🏢 Kat | 10 | Bodrum=0 → 4.Kat=10 |
| 🏗️ Yaş | 10 | 0-10yaş=10, 11-20=7, 20+=3, bilinmiyor=5 |
| 📸 Fotoğraf | 10 | 10+=10p |
| 🎥 Video | 5 | Varsa 5p |

## Pattern: `format_item(sehir, p)`

```python
def format_item(sehir, p):
    sqm = str(int(p['sqm'])) if p['sqm'] and p['sqm'] != '?' else '?'
    bar = "🟩" * (p['score'] // 10) + "⬜" * (10 - p['score'] // 10)
    video = " 🎥" if p.get("has_video") else ""
    floor_short = (p.get("floor","") or "").replace("Floor","K")...
    age_str = f"🏗️{p['age']}" if isinstance(p.get('age'), int) else ""
    highlights = [...]
    return "\n".join(lines)
```

## Çıktı Formatı

```
🏠 **Yeni Yatırımlık Daireler** (sana göre sıralı 📊)

**66** 🟩🟩🟩🟩🟩🟩⬜⬜⬜⬜
**1,250,000 TL** · Sakarya · Karasu · 2+1 · 85m²
1. K · 🏗️0
✅ 🛏️2+1 ideal · 🏗️Yeni bina (0-10 yaş) · 📸Bol fotoğraf
🔗 https://hepsiemlak.com/...
```

## Yatırım Analizi İş Akışı (OSM + Kira Getirisi)

Batu yatırım analizi istediğinde aşağıdaki adımlar uygulanır:

1. **OSM çevre sorgusu**: Her ilan için hava mesafesindeki (500m-2km) hastane, okul, durak, üniversite, AVM/market sayısını OSM API ile çek
2. **Kira getirisi tahmini**: Şehir + oda sayısı bazında ortalama kira değerini hesapla
3. **Skorla sırala**: OSM skoru + kira getirisi %'sini puanla birlikte göster
4. **Linkleri ayrıca göster**: Her ilanın linkini ayrı bir satırda ver

## Parametreler

| Param | Değer |
|-------|-------|
| `intent` | `satilik` |
| `mainCategory` | `konut` |
| `availableForLoanStatus` | `APPLICABLE` |
| `p31` | `800000` (min fiyat) |
| `p32` | `1500000` (max fiyat) |
| `sortField` | `UPDATED_DATE` |
