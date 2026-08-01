# 🏠 HepsiEmlak Cankaya Watchdog

**Türkiye'nin herhangi bir şehri/ilçesinde HepsiEmlak'ta yeni çıkan emlak ilanlarını otomatik takip eden bekçi (watchdog) skill'i.**

## 🎯 Ne İşe Yarar?

HepsiEmlak'ta iyi fiyatlı ilanlar **dakikalar içinde** satılıyor/kiralanıyor. Manuel olarak sayfayı sürekli yenilemek yerine, bu skill:

- Seçtiğiniz şehir/ilçe/mahalle için **yeni ilanları saniyeler içinde** yakalar
- İlanları SQLite veritabanında saklar (tekrar bildirmez)
- Her yeni ilana **AI puanı** verir (fiyat, konum, özelliklere göre)
- Zamanlanmış (cron) görev olarak çalışır, yeni ilanları Telegram'a bildirir

## 🏙️ Neden Cankaya?

Skill ilk olarak Ankara Çankaya için geliştirildi (en yoğun emlak piyasası olan ilçelerden biri), ancak **tamamen yeniden yapılandırılabilir** — istediğiniz ilçe, mahalle listesi ve filtrelerle çalışır.

## ⚙️ Nasıl Çalışır?

1. HepsiEmlak'ın **resmi API uç noktalarını** kullanır (site kazıma yok — bot korumasına takılmaz)
2. `templates/hepsiemlak-fetch-template.py` şablonu ile ilanları çeker
3. SQLite'da ilan geçmişi tutar → **sadece yeni ilanları** raporlar
4. `templates/cankaya_server.py` ile istenirse yerel bir web paneli + harita görselleştirmesi çalıştırır

## 📥 Kurulum

```bash
cp -r skills/hepsiemlak-cankaya-watchdog ~/.hermes/skills/
```

Ardından Hermes'e şöyle bir istek verin:

> "Çankaya'da 3+1, 4.5M TL altı yeni satılık ilanları takip et — her saat kontrol et, yenileri bildirimbb'ye gönder"

Hermes, filtreleri (ilçe, mahalle, fiyat, oda sayısı, m²) size sorarak cron görevini kurar.

## 🧩 Özellikler

- ✅ Tüm Türkiye için çalışır (şehir/ilçe değiştirilebilir)
- ✅ Mahalle bazlı filtreleme
- ✅ SQLite tabanlı — yeniden bildirim yok
- ✅ AI skorlama (fiyat/konum/özellik dengesi)
- ✅ Harita görselleştirme (HTML)
- ✅ Yatırım izleme entegrasyonu (bkz. `references/yatirim-monitoring.md`)

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar
- `templates/hepsiemlak-fetch-template.py` — ilan çekme şablonu
- `templates/cankaya_server.py` — yerel web paneli
- `templates/cankaya_harita.html` — harita görselleştirme
- `references/` — API yanıt referansı, görselleştirme, GitHub yedekleme, yatırım izleme notları
