# 🇹🇷 Hermes Skills TR

**Türkiye'den Hermes Agent kullananlar için özel hazırlanmış skill koleksiyonu.**

[Hermes Agent](https://hermes-agent.nousresearch.com/docs), kişisel AI asistanınızdır — Telegram, e-posta ve yerel dosyalarınızla çalışır, sizin yerinize görevleri otomatikleştirir. Bu repodaki skill'ler, Hermes'in **Türkiye'ye özel** veri kaynaklarıyla (HepsiEmlak, Migros, UYAP, Biletinial, Türk havalimanları vb.) çalışmasını sağlar.

## 📦 Neler Var?

| Skill | Kategori | Ne Yapar? |
|---|---|---|
| [hepsiemlak-ev-takip](skills/hepsiemlak-ev-takip/README.md) | 🏠 Emlak | HepsiEmlak'ta yeni ilanları otomatik takip et (81 il, şehir/ilçe seçilebilir) |
| [hepsiemlak-arsa-takip](skills/hepsiemlak-arsa-takip/README.md) | 🏗️ Emlak | Herhangi bir şehirde arsa ilanlarını takip et (tip/tapu/fiyat filtreleri yapılandırılabilir) |
| [hepsiemlak-yatirim-analizi](skills/hepsiemlak-yatirim-analizi/README.md) | 📈 Emlak | Kiralık yatırım analizi: fiyat, kira getirisi, konum skorlaması |
| [migros-fiyat-arama](skills/migros-fiyat-arama/README.md) | 🛒 Market | Migros Sanal Market'te ürün ve fiyat araştırması |
| [biletinial-etkinlik](skills/biletinial-etkinlik/README.md) | 🎟️ Etkinlik | 84 şehirdeki konser/tiyatro/atölye etkinliklerini çek |
| [uyap-emsal-karar](skills/uyap-emsal-karar/README.md) | ⚖️ Hukuk | Yargıtay emsal içtihatlarını toplu indir (emsal.uyap.gov.tr) |
| [ucuz-ucak-bileti](skills/ucuz-ucak-bileti/README.md) | ✈️ Seyahat | Tüm Türkiye havalimanlarından ucuz uçuş fırsatlarını ara |

## 🚀 Kurulum

1. **Hermes Agent'ı kurun** (yoksa): [dokümantasyon](https://hermes-agent.nousresearch.com/docs)
2. **Skill'leri indirin:**

```bash
git clone https://github.com/bthnbdk/hermes-skills-TR.git
```

3. **İstediğiniz skill'i Hermes'in skill klasörüne kopyalayın:**

```bash
cp -r hermes-skills-TR/skills/hepsiemlak-ev-takip ~/.hermes/skills/
# veya tümünü:
cp -r hermes-skills-TR/skills/* ~/.hermes/skills/
```

4. **Hermes'i yeniden başlatın** (veya yeni oturum açın) — skill'ler otomatik yüklenir.

5. Her skill'in README'sindeki **kurulum ve kullanım** talimatlarını izleyin. Çoğu skill cron görevi (zamanlanmış otomatik çalıştırma) ile birlikte kullanılır.

## 🏙️ Şehir Bazlı Skill'ler

Aşağıdaki skill'ler **tüm Türkiye'de** çalışacak şekilde tasarlanmıştır — şehri siz seçersiniz:

| Skill | Nasıl Yapılandırılır? |
|---|---|
| hepsiemlak-ev-takip | `SEHIR` + `ILCE` slug'larını değiştirin (örn. `istanbul` + `kadikoy`) |
| hepsiemlak-arsa-takip | `{sehir}` slug'ı + `arsa_tipleri` + `tek_tapu` (örn. `izmir` + villa/konut + hisseli dahil) |
| ucuz-ucak-bileti | `fly_from=airport:{IATA}` (örn. `airport:IST`, `airport:ADB`) |

81 ilin HepsiEmlak slug listesi: `skills/hepsiemlak-arsa-takip/references/turkiye-sehirleri.csv`
Türkiye havalimanları IATA kodları: `skills/ucuz-ucak-bileti/references/turkiye-havalimanlari.md`

## 🛠️ Gereksinimler

- Python 3.10+ (çoğu skill sadece standart kütüphane kullanır, ek kurulum gerekmez)
- Hermes Agent (Telegram entegrasyonu önerilir — bildirimler için)
- Bazı skill'ler ücretsiz/üyelikli servislere erişim gerektirir (örn. HepsiEmlak, Migros)

## 📄 Lisans

Bu repodaki skill'ler kişisel kullanım içindir. İlgili servislerin (HepsiEmlak, Migros, UYAP, Biletinial vb.) kullanım koşullarına uymanız gerekir. Skill'ler, resmi API'ler ve kamuya açık uç noktalar üzerinden çalışır; site içi kazıma yöntemleri kullanmaz.

## 🤝 Katkı

Türkiye'ye özel yeni bir skill eklemek veya mevcutları geliştirmek isterseniz PR açabilirsiniz. Skill'lerin **açıklamaları Türkçe** olmalıdır.
