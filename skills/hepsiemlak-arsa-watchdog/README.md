# 🏗️ HepsiEmlak Arsa Watchdog

**Türkiye'nin herhangi bir şehrinde tek tapulu (müstakil) villa arsası ilanlarını otomatik takip eden bekçi skill'i.**

## 🎯 Ne İşe Yarar?

Villa arsası (villa arsası/zoned villa) yatırımı yapanlar için kritik bilgi: **tek tapu** ile satılan, imar durumu uygun arsalar çok hızlı tükenir. Bu skill:

- Seçtiğiniz şehirdeki **tek tapulu villa arsası** ilanlarını HepsiEmlak'tan çeker
- Alt kategori filtreleri: İmarlı Villa / Konut (Zoned Villa / Residential)
- **Maksimum fiyat filtresi** (şehre göre ayarlanır) ile bütçenize uygun ilanları seçer
- Yeni ilanları zamanlanmış görevle bildirir
- **81 ilin tamamı desteklenir** — şehir slug'ı yeterli (bkz. `references/turkiye-sehirleri.csv`)

## ⚙️ Nasıl Çalışır?

- HepsiEmlak'ın resmi API'sini kullanır (Python standart kütüphanesi `urllib`, ek bağımlılık yok)
- Alt kategori + fiyat filtresiyle sorgu oluşturur
- SQLite'da geçmiş tutar → sadece yeni ilanları raporlar
- Cron ile çalışır: "İzmir'de 3M TL altı tek tapulu villa arsası çıkarsa bildir"

## 🏙️ Şehir Seçimi

| Değişken | Örnek | Açıklama |
|----------|-------|----------|
| `{sehir}` | `ankara`, `istanbul`, `izmir`, `antalya`... | HepsiEmlak URL slug'ı (81 il listesi: `references/turkiye-sehirleri.csv`) |
| `max_price` | `2500000` | Maks fiyat (TL) — şehre göre ayarlayın |
| `counties` | `golbasi` veya boş | İlçe filtresi (boş = tüm ilçeler) |

## 📥 Kurulum

```bash
cp -r skills/hepsiemlak-arsa-watchdog ~/.hermes/skills/
```

Hermes'e örnek istek:

> "Ankara'da tek tapulu, 2.5 milyon TL altı villa arsası ilanlarını günde 2 kez kontrol et, yeni çıkanları bildir"
> "İzmir'de tek tapulu, 3 milyon TL altı villa arsası ilanlarını takip et"

## 🧩 Özellikler

- ✅ Tüm Türkiye — 81 il desteklenir (şehir slug'ı ile)
- ✅ Tek tapu filtresi (en çok aranan özellik)
- ✅ Alt kategori: İmarlı Villa / Konut
- ✅ Fiyat limiti (TL, şehre göre ayarlanabilir)
- ✅ İlçe puanları şehir bazlı yapılandırılabilir
- ✅ Sıfır bağımlılık — Python standart kütüphanesi yeterli

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (filtreler, cron ayarı, örnekler)
- `references/turkiye-sehirleri.csv` — 81 ilin HepsiEmlak URL slug'ları
- `references/arsa-puanlama-ornekleri.md` — Ankara, İstanbul, İzmir, Antalya, Bursa, Kocaeli için ilçe puanı önerileri
