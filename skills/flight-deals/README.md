# ✈️ Flight Deals

**Ankara (ESB) çıkışlı ucuz uçuş fırsatlarını otomatik arayan skill — FlightList.io (Kiwi.com proxy) API'si ile.**

## 🎯 Ne İşe Yarar?

Türkiye'den (özellikle Ankara'dan) yurt dışına **ucuz uçak bileti** fırsatlarını yakalamak için:

- 🔍 **Fırsat arama** — Ankara (ESB) çıkışlı, hedef bölgelere (Avrupa, Asya, Orta Doğu...) ucuz gidiş-dönüş fırsatları
- 📅 **Tarih esnekliği** — belirli tarih aralıklarında en ucuz günleri bulur
- 💰 **Fiyat karşılaştırma** — rotaları ve fiyatları JSON olarak çeker
- ⏰ **Zamanlanmış takip** — cron ile düzenli kontrol, fırsat çıkınca bildirir

## ⚙️ Nasıl Çalışır?

FlightList.io (Kiwi.com'un proxy API'si) üzerinden çalışır — JS tabanlı uçuş sitelerini kazımak yerine doğrudan API sorgusu yapar:

```
GET https://api.flightlist.io/...?flyFrom=ESB&to=...&dateFrom=...&dateTo=...
```

- Tam URL parametreleri ve JSON yanıt yapısı `references/` dosyalarında dokümante edilmiştir
- Bölge ön ayarları: `references/region-presets.csv` (Avrupa, Asya vb. hedef grupları)

## 📥 Kurulum

```bash
cp -r skills/flight-deals ~/.hermes/skills/
```

Hermes'e örnek istek:

> "Önümüzdeki 3 ayda Ankara'dan Avrupa'ya en ucuz 10 uçuş fırsatını listele"
> "Her pazartesi ESB çıkışlı uçuş fırsatlarını kontrol et, 200€ altı olursa bildir"

## 🧩 Özellikler

- ✅ Ankara (ESB) merkezli — Türkiye kullanıcıları için
- ✅ Kiwi.com proxy API — resmi veri, kazıma yok
- ✅ Bölge ön ayarları (preset)
- ✅ Cron örüntüsü hazır (`templates/cron-job-prompt.md`)

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (URL parametreleri, örnekler)
- `references/example-response.json` — örnek yanıt
- `references/full-api-response-reference.md` — tam API yanıt referansı
- `references/region-presets.csv` — bölge ön ayarları
- `templates/cron-job-prompt.md` — zamanlanmış görev şablonu

## ⚠️ Not

FlightList.io ücretsiz bir proxy servisidir; kullanım kotaları olabilir. Alternatif API'ler için `flight-search-api` skill'ine bakılabilir (Kiwi/Teqblaze/Skyscanner/Amadeus).
