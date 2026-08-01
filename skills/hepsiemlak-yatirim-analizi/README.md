# 📈 HepsiEmlak Yatırım Analizi

**Türkiye'nin herhangi bir şehrinde kiralık yatırım potansiyelini analiz eden skill — "Bu evi alıp kiraya versem kârlı mı?" sorusunun cevabı.**

## 🎯 Ne İşe Yarar?

Bir ev satın alıp kiraya vermeyi düşünüyorsunuz. Bu skill, HepsiEmlak'taki ilanları **yatırım gözlüğüyle** analiz eder:

- 💰 **Fiyat analizi** — ilan fiyatı bölge ortalamasına göre uygun mu?
- 📊 **Tahmini kira getirisi** — aylık/yıllık getiri oranı (yield) hesaplar
- 🏥 **Konum skorlaması** — hastane, okul, ulaşım yakınlığı
- 🛏️ **Fiziksel özellikler** — kat, oda sayısı, bina yaşı
- 🤖 **AI kararı** — tüm faktörleri birleştirip "alınabilir / riskli / geç" puanı verir

## ⚙️ Nasıl Çalışır?

1. HepsiEmlak ilanlarını çeker (resmi API)
2. SQLite'da saklar
3. İstenen şehir için isteğe bağlı analiz çalıştırılır
4. Sonuç: her ilan için yatırım skoru + gerekçe açıklaması

## 📥 Kurulum

```bash
# Hermes:
cp -r skills/hepsiemlak-yatirim-analizi ~/.hermes/skills/

# Diğer agent'lar (Claude Code, Codex, Python vb.):
# Skill klasörünü kendi çalışma dizininize kopyalayın, script'leri python3 ile çalıştırın.
```

Hermes'e örnek istek:

> "Eskişehir'de 2+1, 3M TL altı dairelerin kiralık yatırım analizini yap — getirisi en yüksek 5 ilanı listele"

## 🧩 Özellikler

- ✅ Türkiye'nin **her şehri** için çalışır (şehir rehberi: `references/sehir-rehberi.md`)
- ✅ Kira getirisi tahmini
- ✅ Hastane/okul yakınlığı skorlaması
- ✅ SQLite + AI analiz
- ✅ İsteğe bağlı: yatırım izleme (cron ile düzenli rapor)

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar
- `references/sehir-rehberi.md` — şehir bazlı analiz notları
