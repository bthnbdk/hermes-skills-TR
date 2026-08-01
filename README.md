# 🇹🇷 Türkçe AI Skillleri

**Türkiye'ye özel, her AI agent ile çalışan hazır skill koleksiyonu.**

Bu repodaki skill'ler; emlak takibi, market fiyatları, hukuk içtihatları, etkinlikler ve ucuz uçuş gibi **Türkiye'ye özel veri kaynaklarıyla** çalışır. **Agent bağımsızdır** — Hermes Agent, Claude Code, Codex, Cursor veya düz Python ile kullanılabilir.

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

### Hermes Agent kullanıyorsanız

1. **Skill'leri indirin:**

```bash
git clone https://github.com/bthnbdk/turkce-ai-skillleri.git
```

2. **İstediğiniz skill'i Hermes'in skill klasörüne kopyalayın:**

```bash
cp -r turkce-ai-skillleri/skills/hepsiemlak-ev-takip ~/.hermes/skills/
# veya tümünü:
cp -r turkce-ai-skillleri/skills/* ~/.hermes/skills/
```

3. **Hermes'i yeniden başlatın** (veya yeni oturum açın) — skill'ler otomatik yüklenir.

### Başka bir agent / ortam kullanıyorsanız (Claude Code, Codex, Cursor, Python...)

Skill'ler **agent bağımsızdır** — Hermes'e özel API gerektirmez:

1. Repo'yu indirin, istediğiniz skill klasörünü kendi çalışma dizininize kopyalayın
2. `templates/` içindeki script'leri `python3` ile doğrudan çalıştırın (bağımlılık yok — Python stdlib yeterli)
3. Zamanlama için sistem cron / GitHub Actions / herhangi bir zamanlayıcı kullanın:

```bash
0 */3 * * * cd <calisma_dizini> && python3 hepsiemlak_fetch.py
```

4. Bildirim hedefini kendi kanalınıza göre ayarlayın (Telegram bot, e-posta, Slack webhook...)

> ℹ️ `~/.hermes/skills/` yolları yalnızca Hermes kurulumu içindir; diğer ortamlarda skill klasörünü kendi dizininize kopyalamanız yeterli.

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

## ⚠️ Sorumluluk Reddi (Disclaimer)

- Bu repodaki skill'ler **bilgilendirme ve otomasyon amaçlıdır**; yatırım, hukuki veya mali tavsiye niteliği taşımaz.
- Skill'ler, ilgili servislerin (HepsiEmlak, Migros, UYAP, Biletinial, FlightList.io vb.) resmi API'leri ve kamuya açık uç noktaları üzerinden çalışır. Bu servislerin **kullanım koşullarını ihlal etmeyecek** şekilde, makul sıklıkta ve hacimde kullanılması sizin sorumluluğunuzdadır.
- İlgili servisler API'lerini değiştirebilir, erişimi kısıtlayabilir veya kapatabilir; bu durumda skill'lerin çalışmayı durdurması olağandır.
- Skill'lerin kullanımından doğabilecek **doğrudan veya dolaylı hiçbir zarardan, veri kaybından, mali kayıptan veya hukuki sonuçtan repo sahibi sorumlu değildir.** Skill'leri kendi sorumluluğunuzda kullanırsınız.
- Otomatik görevler (cron) yapılandırırken bildirim kanallarını, fiyat eşiklerini ve çalışma sıklığını kendi ihtiyacınıza göre doğrulayın.

## 📄 Lisans

Bu repodaki skill'ler kişisel kullanım içindir. İlgili servislerin (HepsiEmlak, Migros, UYAP, Biletinial vb.) kullanım koşullarına uymanız gerekir. Skill'ler, resmi API'ler ve kamuya açık uç noktalar üzerinden çalışır; site içi kazıma yöntemleri kullanmaz.

## 🤝 Katkı

Türkiye'ye özel yeni bir skill eklemek veya mevcutları geliştirmek isterseniz PR açabilirsiniz. Skill'lerin **açıklamaları Türkçe** olmalıdır.
