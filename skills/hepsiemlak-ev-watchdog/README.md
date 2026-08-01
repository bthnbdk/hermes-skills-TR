# 🏠 HepsiEmlak Emlak Watchdog (Tüm Türkiye)

**Türkiye'nin herhangi bir şehri/ilçesinde HepsiEmlak'ta yeni çıkan emlak ilanlarını otomatik takip eden bekçi (watchdog) skill'i.**

## 🎯 Ne İşe Yarar?

HepsiEmlak'ta iyi fiyatlı ilanlar **dakikalar içinde** satılıyor/kiralanıyor. Manuel olarak sayfayı sürekli yenilemek yerine, bu skill:

- Seçtiğiniz şehir/ilçe/mahalle için **yeni ilanları saniyeler içinde** yakalar
- İlanları SQLite veritabanında saklar (tekrar bildirmez)
- Her yeni ilana **AI puanı** verir (fiyat, konum, özelliklere göre)
- Zamanlanmış (cron) görev olarak çalışır, yeni ilanları Telegram'a bildirir

## 🏙️ Şehir Seçimi

Skill ilk olarak Ankara Çankaya için geliştirildi, ancak **tamamen yeniden yapılandırılabilir** — istediğiniz ilçe, mahalle listesi ve filtrelerle çalışır:

| Değişken | Örnek | Açıklama |
|----------|-------|----------|
| `SEHIR` | `ankara`, `istanbul`, `izmir`, `antalya`, `bursa`... | HepsiEmlak şehir slug'ı (81 il desteklenir) |
| `ILCE` | `cankaya`, `konak`, `muratpasa`... veya `""` | İlçe slug'ı — boş = tüm ilçeler |
| `MAX_PRICE` | `8000000` | Maks fiyat (TL) |
| `WORK_LAT/LON` | `39.8897782, 32.8594033` | Mesafe puanı referans noktası (ev/iş yeri) |
| `EXCLUDED` | `{"Ümitköy", ...}` | Hariç tutulacak mahalleler |

## ⚙️ Nasıl Çalışır?

1. HepsiEmlak'ın **resmi API uç noktalarını** kullanır (site kazıma yok — bot korumasına takılmaz)
2. `templates/hepsiemlak-fetch-template.py` şablonu ile ilanları çeker (SEHIR/ILCE değiştir → çalıştır)
3. SQLite'da ilan geçmişi tutar → **sadece yeni ilanları** raporlar
4. `templates/sehir_server.py` + `sehir_harita.html` ile istenirse yerel bir web paneli + harita görselleştirmesi çalıştırır

## 📥 Kurulum

```bash
cp -r skills/hepsiemlak-ev-watchdog ~/.hermes/skills/
```

Ardından Hermes'e şöyle bir istek verin:

> "Çankaya'da 3+1, 4.5M TL altı yeni satılık ilanları takip et — her saat kontrol et, yenileri bildirimbb'ye gönder"
> "İzmir Konak'ta 2+1, 3M TL altı yeni ilanları takip et"
> "Antalya Muratpaşa'da 500 bin TL altı kiralık daireleri izle"

Hermes, filtreleri (ilçe, mahalle, fiyat, oda sayısı, m²) size sorarak cron görevini kurar.

## 🧩 Özellikler

- ✅ Tüm Türkiye için çalışır (şehir/ilçe değiştirilebilir — 81 il)
- ✅ Mahalle bazlı filtreleme
- ✅ SQLite tabanlı — yeniden bildirim yok
- ✅ AI skorlama (fiyat/konum/özellik dengesi)
- ✅ Harita görselleştirme (HTML — şehre göre otomatik uyarlanır)
- ✅ Yatırım izleme entegrasyonu (bkz. `references/yatirim-monitoring.md`)

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar
- `templates/hepsiemlak-fetch-template.py` — ilan çekme şablonu (şehir/ilçe değişkenleri)
- `templates/sehir_server.py` — yerel web paneli (CONFIG sözlüğü ile yapılandırılır)
- `templates/sehir_harita.html` — Leaflet harita frontend (placeholder'lar server'dan doldurulur)
