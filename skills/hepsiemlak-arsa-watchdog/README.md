# 🏗️ HepsiEmlak Arsa Watchdog

**Ankara'da tek tapulu (müstakil) villa arsası ilanlarını otomatik takip eden bekçi skill'i.**

## 🎯 Ne İşe Yarar?

Villa arsası (villa arsası/zoned villa) yatırımı yapanlar için kritik bilgi: **tek tapu** ile satılan, imar durumu uygun arsalar çok hızlı tükenir. Bu skill:

- Ankara'daki **tek tapulu villa arsası** ilanlarını HepsiEmlak'tan çeker
- Alt kategori filtreleri: İmarlı Villa / Konut (Zoned Villa / Residential)
- **Maksimum fiyat filtresi** (örn. 2.5M TL) ile bütçenize uygun ilanları seçer
- Yeni ilanları zamanlanmış görevle bildirir

## ⚙️ Nasıl Çalışır?

- HepsiEmlak'ın resmi API'sini kullanır (Python standart kütüphanesi `urllib`, ek bağımlılık yok)
- Alt kategori + fiyat filtresiyle sorgu oluşturur
- SQLite'da geçmiş tutar → sadece yeni ilanları raporlar
- Cron ile çalışır: "Ankara'da 2.5M TL altı tek tapulu villa arsası çıkarsa bildir"

## 📥 Kurulum

```bash
cp -r skills/hepsiemlak-arsa-watchdog ~/.hermes/skills/
```

Hermes'e örnek istek:

> "Ankara'da tek tapulu, 2.5 milyon TL altı villa arsası ilanlarını günde 2 kez kontrol et, yeni çıkanları bildir"

## 🧩 Özellikler

- ✅ Tek tapu filtresi (en çok aranan özellik)
- ✅ Alt kategori: İmarlı Villa / Konut
- ✅ Fiyat limiti (TL)
- ✅ Sıfır bağımlılık — Python standart kütüphanesi yeterli

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (filtreler, cron ayarı, örnekler)
