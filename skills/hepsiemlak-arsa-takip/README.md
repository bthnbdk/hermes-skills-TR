# 🏗️ HepsiEmlak Arsa Takip

**Türkiye'nin herhangi bir şehrinde arsa ilanlarını otomatik takip eden bekçi skill'i — takip edeceğiniz arsa tiplerini siz seçersiniz.**

## 🎯 Ne İşe Yarar?

Arsa yatırımı yapanlar için kritik bilgi: iyi arsalar **çok hızlı tükenir**. Bu skill:

- Seçtiğiniz şehirdeki **arsa ilanlarını** HepsiEmlak'tan çeker
- **Arsa tipi filtresi** tamamen size bağlı: villa arsası, imarlı konut, tarla, bahçe, ticari, imarsız — istediğiniz kombinasyon
- **Tek tapu filtresi** açılıp kapanabilir (sadece müstakil / hisseli dahil)
- **Maksimum fiyat + m² aralığı** filtreleri ile bütçenize uygun ilanları seçer
- Yeni ilanları zamanlanmış görevle bildirir
- **81 ilin tamamı desteklenir** — şehir slug'ı yeterli (bkz. `references/turkiye-sehirleri.csv`)

## ⚙️ Nasıl Çalışır?

- HepsiEmlak'ın resmi API'sini kullanır (Python standart kütüphanesi `urllib`, ek bağımlılık yok)
- Arsa tipi + fiyat + m² + tapu filtreleriyle sorgu oluşturur
- SQLite'da geçmiş tutar → sadece yeni ilanları raporlar
- Cron ile çalışır

## 🏙️ Yapılandırma

| Değişken | Örnek | Açıklama |
|----------|-------|----------|
| `{sehir}` | `ankara`, `istanbul`, `izmir`, `antalya`... | HepsiEmlak URL slug'ı (81 il listesi: `references/turkiye-sehirleri.csv`) |
| `arsa_tipleri` | `["zoned_villa", "zoned_residential"]` | Takip edilecek tipler — **boş = hepsi** |
| `tek_tapu` | `True` / `False` | Sadece müstakil tapu mu? `False` = hisseli dahil |
| `max_price` | `2500000` | Maks fiyat (TL) |
| `min_sqm` / `max_sqm` | `500` / `2000` | Arsa büyüklüğü aralığı |
| `counties` | `golbasi` veya boş | İlçe filtresi |

### Örnek Kullanımlar

| İstek | Yapılandırma |
|-------|-------------|
| "Ankara'da tek tapulu, 2.5M TL altı villa arsası takip et" | `arsa_tipleri=["zoned_villa"]`, `tek_tapu=True`, `max_price=2500000` |
| "İzmir'de imarlı konut + bahçe arsaları, hisseli dahil" | `arsa_tipleri=["zoned_residential","garden"]`, `tek_tapu=False` |
| "Konya'da 1000-5000 m² tarla, 1M TL altı" | `arsa_tipleri=["field"]`, `min_sqm=1000`, `max_sqm=5000` |
| "Antalya'da tüm arsalar" | `arsa_tipleri=[]` (filtre yok) |

## 📥 Kurulum

```bash
cp -r skills/hepsiemlak-arsa-takip ~/.hermes/skills/
```

Hermes'e örnek istek:

> "Ankara'da tek tapulu, 2.5 milyon TL altı villa arsası ilanlarını günde 2 kez kontrol et, yeni çıkanları bildir"
> "İzmir'de 3 milyon TL altı imarlı konut arsalarını takip et, hisseli de olsun"
> "Konya'da tarla ilanlarını izle"

## 🧩 Özellikler

- ✅ Tüm Türkiye — 81 il desteklenir (şehir slug'ı ile)
- ✅ Arsa tipi filtresi tamamen yapılandırılabilir (villa/konut/tarla/bahçe/ticari/imarsız)
- ✅ Tek tapu filtresi aç/kapa
- ✅ Fiyat limiti + m² aralığı
- ✅ İlçe puanları şehir bazlı yapılandırılabilir
- ✅ Sıfır bağımlılık — Python standart kütüphanesi yeterli

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (filtreler, cron ayarı, örnekler)
- `references/turkiye-sehirleri.csv` — 81 ilin HepsiEmlak URL slug'ları
- `references/arsa-puanlama-ornekleri.md` — Ankara, İstanbul, İzmir, Antalya, Bursa, Kocaeli için ilçe puanı önerileri
