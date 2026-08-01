# ⚖️ Emsal UYAP

**Yargıtay'ın emsal içtihat veritabanından (emsal.uyap.gov.tr) toplu içtihat indirme aracı — hukukçular için.**

## 🎯 Ne İşe Yarar?

Türkiye'de avukatlar ve hukukçular, davalarında **emsal kararlara** (Yargıtay içtihatlarına) ihtiyaç duyar. Bu skill, resmi emsal.uyap.gov.tr portalından içtihatları **otomatik ve toplu** şekilde indirir:

- 🔎 **Çoklu anahtar kelime araması** — bir konu hakkında farklı terimlerle arar (örn. "kira tespit", "tahliye", "kefalet")
- 📚 **Benzersiz sonuç toplama** — tekrarları ayıklar
- 📄 **Tam metin indirme** — her içtihadın tam metnini indirir
- 🗂️ **Birleştirme** — tüm metinleri tek TXT dosyasında toplar (dava dosyası hazırlığı için)

## ⚙️ Nasıl Çalışır?

Emsal UYAP'ın web arayüzünün altındaki arama API'si tersine mühendislikle çözülmüştür (bkz. `references/api-reverse-engineering.md`):

1. Oturum başlat (portalın oturum çerezi deseni)
2. Anahtar kelimelerle arama yap → sonuç listesini al
3. Her sonuç için tam metin iste → indir
4. Tümünü birleştir → TXT çıktı

## 📥 Kurulum

```bash
# Hermes:
cp -r skills/uyap-emsal-karar ~/.hermes/skills/

# Diğer agent'lar (Claude Code, Codex, Python vb.):
# Skill klasörünü kendi çalışma dizininize kopyalayın, script'leri python3 ile çalıştırın.
```

Hermes'e örnek istek:

> "Kira sözleşmesi feshi ile ilgili son 5 yılın Yargıtay emsallerini topla ve tek dosyada birleştir"

## 🧩 Özellikler

- ✅ Resmi devlet portalı (emsal.uyap.gov.tr)
- ✅ Çoklu anahtar kelime + benzersiz sonuç
- ✅ Tam metin indirme
- ✅ Tek dosyada birleştirme
- ✅ Geniş ölçekli çekim deseni (sayfalama, oturum yenileme) — bkz. `references/full-scale-extraction.md`

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (arama, indirme, birleştirme hattı)
- `references/api-reverse-engineering.md` — portal API'sinin çözümü
- `references/full-scale-extraction.md` — büyük ölçekli çekim notları

## ⚠️ Not

Portal, hızlı ardışık isteklerde oturum doğrulaması (reCAPTCHA) isteyebilir. Skill, oturum çerezi deseni ve istek hızlandırma ile bunu aşar (80+ belge / oturum). Yine de **makul hızda** kullanılması önerilir.
