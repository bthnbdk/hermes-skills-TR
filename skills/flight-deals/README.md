# ✈️ Flight Deals (Tüm Türkiye)

**Türkiye'deki herhangi bir havalimanından çıkışlı ucuz uçuş fırsatlarını otomatik arayan skill — FlightList.io (Kiwi.com proxy) API'si ile.**

## 🎯 Ne İşe Yarar?

Türkiye'den yurt dışına **ucuz uçak bileti** fırsatlarını yakalamak için:

- 🔍 **Fırsat arama** — seçtiğiniz havalimanından (İstanbul IST/SAW, Ankara ESB, İzmir ADB, Antalya AYT, Muğla DLM/BJV, Trabzon TZX...) hedef bölgelere ucuz gidiş-dönüş fırsatları
- 📅 **Tarih esnekliği** — belirli tarih aralıklarında en ucuz günleri bulur
- 💰 **Fiyat karşılaştırma** — rotaları ve fiyatları JSON olarak çeker
- ⏰ **Zamanlanmış takip** — cron ile düzenli kontrol, fırsat çıkınca bildirir

## 🏙️ Çıkış Havalimanı Seçimi

Tüm Türkiye havalimanları IATA kodları: `references/turkiye-havalimanlari.md`

| Şehir | IATA | Not |
|-------|:---:|-----|
| İstanbul | `IST` / `SAW` | `city:IST` ikisini birden kapsar |
| Ankara | `ESB` | Başkent |
| İzmir | `ADB` | Ege hub'ı |
| Antalya | `AYT` | `city:AYT` = AYT + GZP |
| Muğla | `DLM` / `BJV` | Dalaman / Bodrum |
| Trabzon | `TZX` | Karadeniz |

## ⚙️ Nasıl Çalışır?

FlightList.io (Kiwi.com'un proxy API'si) üzerinden çalışır — JS tabanlı uçuş sitelerini kazımak yerine doğrudan API sorgusu yapar:

```
GET https://www.flightlist.io/api/search.php?fly_from=airport:ESB&fly_to=city:LON&...
```

- Tam URL parametreleri ve JSON yanıt yapısı `references/` dosyalarında dokümante edilmiştir
- Bölge ön ayarları: `references/region-presets.csv` (Avrupa, Asya vb. hedef grupları)

## 📥 Kurulum

```bash
cp -r skills/flight-deals ~/.hermes/skills/
```

Hermes'e örnek istek:

> "Önümüzdeki 3 ayda İstanbul'dan Avrupa'ya en ucuz 10 uçuş fırsatını listele"
> "Her pazartesi ESB çıkışlı uçuş fırsatlarını kontrol et, 200€ altı olursa bildir"
> "İzmir'den Schengen bölgesine haftalık ucuz uçuş taraması yap"

## 🧩 Özellikler

- ✅ Tüm Türkiye — 81 ilin havalimanı IATA kodları dahil
- ✅ Kiwi.com proxy API — resmi veri, kazıma yok
- ✅ Bölge ön ayarları (preset)
- ✅ Cron örüntüsü hazır (`templates/cron-job-prompt.md`)

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (URL parametreleri, örnekler)
- `references/turkiye-havalimanlari.md` — tüm Türkiye havalimanları IATA kodları
- `references/example-response.json` — örnek yanıt
- `references/full-api-response-reference.md` — tam API yanıt referansı
- `references/region-presets.csv` — bölge ön ayarları
- `templates/cron-job-prompt.md` — zamanlanmış görev şablonu

## ⚠️ Not

FlightList.io ücretsiz bir proxy servisidir; kullanım kotaları olabilir. Alternatif API'ler için `flight-search-api` skill'ine bakılabilir (Kiwi/Teqblaze/Skyscanner/Amadeus).
