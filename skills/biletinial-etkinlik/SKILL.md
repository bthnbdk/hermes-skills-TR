---
name: biletinial-etkinlik
description: "Biletinial etkinlik API'si — şehir bazlı konser/tiyatro/atölye/etkinlik listesi çekme. cityId haritası (84 şehir), sayfalama, rate limit, cron örüntüsü. Sade curl ile çalışır, auth yok."
version: 1.0.0
author: Turkce AI Skillleri Toplulugu
---

# Biletinial Etkinlik

Biletinial (biletinial.com) — Türkiye geneli etkinlik bileti platformu. Şehir bazlı etkinlik listesini **sade curl ile, auth/cookie olmadan** JSON olarak verir. Konser, tiyatro, atölye, festival takibi için ideal.

## Endpoint

```
GET https://biletinial.com/GetAllEventsByCity?cityId={id}&langId=1&countryId=3&langCode=tr&pageNumber={n}&pageSize=20&initial=true
```

**Zorunlu header'lar:**
```
Accept: application/json
Referer: https://www.biletinial.com/
```

**⚠️ Kritik: `-L` (redirect follow) ŞART** — bazı cityId'ler 301 ile `/tr-tr/GetAllEventsByCity?...` path'ine yönlenir. `-L` olmazsa HTML döner, JSON parse patlar.

## Parametreler

| Param | Değer | Açıklama |
|---|---|---|
| cityId | 1-147 | Şehir ID (harita: `references/cityId-haritasi.csv`) |
| langId | 1 | Sabit |
| countryId | 3 | Türkiye |
| langCode | tr | Sabit |
| pageNumber | 1..N | Sayfa (20'şer) |
| pageSize | 20 | Sayfa boyutu |
| initial | true | İlk yükleme işareti |

## Yanıt Yapısı

```json
{
  "Data": [ { "etkinlikId": 72595, "etkinlik": "Temel Dikiş Atölyesi",
             "seanceId": 18388821, "mekanId": 37996, "mekan": "Boutich İncek",
             "tip": "Eğitim", "tipForUrl": "egitim", "pic": "/Uploads/...jpg",
             "url": "temel-dikis-atolyesi", "SeanceDate": "2026-08-02T11:00:00Z",
             "tarih": "02 Ağustos 2026 Pazar", "saat": "11:00",
             "KoltukKontrol": 10, "SaleStatus": 0 } ],
  "HasMore": true,
  "TypeOptions": [ {"Name": "...", "Count": N} ],
  "VenueOptions": [...],
  "DateOptions": [...]
}
```

- `Data` — etkinlik listesi (max 20/sayfa)
- `HasMore` — true ise `pageNumber+1` ile devam et
- `TypeOptions` / `VenueOptions` / `DateOptions` — filtre seçenekleri (kategori, mekan, tarih)

## Rate Limit

**İstekler arası ~1.5-2 saniye bırak.** Hızlı art arda istekte API `Data: []` (boş) döner — etkinliği olmayan şehirden ayırt etmek için aynı şehri 2sn sonra tekrar dene. 84 şehir taraması ~3 dk sürer.

## cityId Haritası

Tam 84 şehir haritası: `references/cityId-haritasi.csv` (cityId, plaka, şehir, slug, ilk_sayfa_etkinlik, hasMore).

**Önemli şehirler:**
- İstanbul (Tümü)=147, İstanbul Avrupa=5, İstanbul Anadolu=77
- Ankara=3, İzmir=24, Bursa=11, Eskişehir=19, Adana=12, Antalya=23, Konya=13, Kocaeli=20, Gaziantep=9, Mersin=85, Muğla=4, Denizli=14, Aydın=29, Balıkesir=25
- Kıbrıs=55 (plaka 0)

Ağustos 2026 taraması: 84 şehirden **67'sinde etkinlik var**; Rize, Gümüşhane, Muş, Hakkari gibi 17 şehir boş (`Data: []`, 200 döner — hata değil).

## Kullanım Örnekleri

```bash
# Ankara etkinlikleri (ilk sayfa)
curl -sL --max-time 20 \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0" \
  -H "Accept: application/json" -H "Referer: https://www.biletinial.com/" \
  "https://biletinial.com/GetAllEventsByCity?cityId=3&langId=1&countryId=3&langCode=tr&pageNumber=1&pageSize=20&initial=true"
```

```python
# Çok şehirli tarama (rate limit uyumlu)
import json, subprocess, time

def get_events(city_id, page=1):
    url = (f"https://biletinial.com/GetAllEventsByCity?cityId={city_id}"
           f"&langId=1&countryId=3&langCode=tr&pageNumber={page}&pageSize=20&initial=true")
    subprocess.run(["curl","-sL","-o","/tmp/bi.json","--max-time","15",
                    "-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "-H","Accept: application/json",
                    "-H","Referer: https://www.biletinial.com/", url],
                   capture_output=True, timeout=25)
    return json.load(open('/tmp/bi.json'))

# Tüm sayfaları topla
def collect_city(city_id):
    events, page = [], 1
    while True:
        d = get_events(city_id, page)
        events += d.get('Data', [])
        if not d.get('HasMore'): break
        page += 1
        time.sleep(1.6)
    return events
```

## Cron Örüntüsü (haftalık etkinlik özeti)

```bash
# Haftalık Ankara etkinlik özeti: her pazartesi 09:00
0 9 * * 1  python3 /path/to/biletinial_digest.py --cities 3,147,24
```

Script mantığı: şehirleri dolaş (1.6sn arayla) → etkinlikleri topla → `tarih + mekan + tip` ile özetle → bildirim kanalına gönder. Etkinlik yoksa **sessiz kal** (watchdog deseni).

## Pitfalls

1. **`-L` unutma** — 301 redirect bazı şehirlerde JSON'u HTML'e çevirir
2. **Rate limit** — 1.5sn altında boş sonuç; 84 şehir taramasını tek seferde yapma, böl
3. **`Data: []` ≠ hata** — şehrin etkinliği olmayabilir; 200 dönüyor
4. **Etkinlik detayı yok** — `GetEventDetail`, `GetAllEvents`, `GetSeances`, `GetAllVenues` tahminleri 302→404. Sadece `GetAllEventsByCity` mevcut; detay için site HTML'ine (`/{sehir-slug}/{etkinlik-url}`) düş
5. **Şehir adı alanı** — `Data[].cityId` her zaman 0 döner; şehri istekteki cityId'den takip et

## Referanslar

- `references/cityId-haritasi.csv` — 84 şehir cityId eşlemesi + etkinlik sayıları (Ağustos 2026)
- İlgili: web-scraping skill → `references/turkiye-top-site-api-map.md` (Türkiye site API haritası)
