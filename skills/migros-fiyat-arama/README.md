# 🛒 Migros Fiyat Arama

**Migros Sanal Market'te ürün ve fiyat araştırması — en iyi fiyatı bul, indirimleri takip et, yemek planı yap.**

## 🎯 Ne İşe Yarar?

Migros Sanal Market'in **resmi REST API'si** üzerinden çalışır (site kazıma yok):

- 🔍 **Ürün arama** — "süzme peynir" veya "çamaşır deterjanı" gibi aramalarda tüm ürünleri, fiyatları, birim fiyatlarını çeker
- 💰 **Fiyat karşılaştırma** — aynı kategorideki ürünlerin kg/litre başına fiyatını hesaplar (en ekonomik seçeneği bulur)
- 🏷️ **İndirim takibi** — kampanyalı ürünleri listeler, indirim oranlarını gösterir
- 🥘 **Yemek planlama** — bütçeye göre haftalık alışveriş listesi + yemek menüsü önerir (bkz. `references/meal-planning.md`)
- 📉 **Maliyet analizi** — aylık market harcaması ve tasarruf fırsatları (bkz. `references/cost-analysis.md`)

## ⚙️ Nasıl Çalışır?

- Migros'un mobil/web uygulamasının kullandığı API uç noktalarını kullanır
- Sorgu parametreleri: kategori, arama terimi, sayfalama
- Yanıt: ürün adı, marka, fiyat, birim fiyat, indirim durumu

## 📥 Kurulum

```bash
cp -r skills/migros-fiyat-arama ~/.hermes/skills/
```

Hermes'e örnek istekler:

> "Migros'ta en ucuz zeytinyağı hangisi? Kg başına fiyatları karşılaştır"
> "Bu hafta Migros'ta indirimde olan kahve ürünlerini listele"
> "500 TL bütçeyle 3 günlük yemek planı + alışveriş listesi çıkar"

## 🧩 Özellikler

- ✅ Resmi API — hızlı ve güvenilir
- ✅ Birim fiyat karşılaştırma (kg/lt başına)
- ✅ İndirim ve kampanya tespiti
- ✅ Yemek planlama + bütçe yönetimi
- ✅ İndirim watchdog deseni (düzenli kontrol)

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (API uç noktaları, parametreler)
- `references/discount-types.md` — indirim türleri
- `references/discount-watchdog.md` — indirim takibi deseni
- `references/meal-planning.md` — yemek planlama
- `references/cost-analysis.md` — maliyet analizi
