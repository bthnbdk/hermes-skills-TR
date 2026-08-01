# 🎟️ Biletinial Etkinlik

**Biletinial (biletinial.com) üzerinden Türkiye geneli etkinlikleri çekin — konser, tiyatro, atölye, festival. 84 şehir için çalışır.**

## 🎯 Ne İşe Yarar?

Biletinial, Türkiye'nin en büyük etkinlik bileti platformlarından biridir. Bu skill, platformun **herkese açık JSON API'sini** kullanarak şehir bazlı etkinlik listelerini çeker — **kayıt, giriş, API anahtarı gerekmez**.

- 🎤 **Konser takibi** — sevdiğiniz sanatçıların yeni konserleri
- 🎭 **Tiyatro/etkinlik keşfi** — şehrinizde ne var ne yok
- 🏙️ **Çok şehirli tarama** — 84 şehrin tamamı tek skill'le taranabilir
- ⏰ **Zamanlanmış bildirim** — "Ankara'da bu hafta çıkan yeni etkinlikler" özeti

## ⚙️ Nasıl Çalışır?

Tek bir uç nokta yeterli:

```
GET https://biletinial.com/GetAllEventsByCity?cityId={id}&langId=1&countryId=3&langCode=tr&pageNumber={n}&pageSize=20&initial=true
```

- Her şehrin bir `cityId`'si var (örn. Ankara=3, İstanbul=147, İzmir=24) — tam 84 şehir haritası `references/cityId-haritasi.csv` dosyasında
- Yanıt: etkinlik adı, mekan, tarih+saat, kategori, resim, bilet durumu
- Sayfalama: `pageNumber` + `HasMore` bayrağı
- **Not:** İstekler arası ~1.5-2 saniye bekleyin (hız sınırı); `-L` (redirect takibi) şart

## 📥 Kurulum

```bash
cp -r skills/biletinial-etkinlik ~/.hermes/skills/
```

Hermes'e örnek istekler:

> "Ankara'da bu ayki konserleri listele"
> "İstanbul + İzmir + Ankara'daki yeni etkinlikleri haftalık özetle ve bildir"

## 🧩 Özellikler

- ✅ Auth yok, anahtar yok — sade curl yeterli
- ✅ 84 şehir cityId haritası hazır
- ✅ Etkinlik tipi (kategori), mekan ve tarih filtreleri
- ✅ Cron örüntüsü: haftalık etkinlik özeti bildirimi

## 📄 Dosyalar

- `SKILL.md` — endpoint, parametreler, yanıt yapısı, örnekler, pitfall'lar
- `references/cityId-haritasi.csv` — 84 şehir eşlemesi + etkinlik sayıları

## ⚠️ Not

Ağustos 2026 taramasında 84 şehirden **67'sinde etkinlik** bulunuyor. Etkinliği olmayan şehirler boş liste döner (hata değil).
