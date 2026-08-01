# Bing RSS Arama

**Ücretsiz, API anahtarı gerektirmeyen web araması — Bing'in RSS çıktısıyla herhangi bir anahtar kelime için son 10 sonucu alın.**

## 🎯 Ne İşe Yarar?

- 🔍 **Haber takibi** — belirli konularda yeni çıkan haberleri izle
- 🏷️ **Keyword monitoring** — bir ürün/marka hakkında ne konuşuluyor takip et
- 💰 **Fiyat araştırması** — "hepsiemlak ankara kiralık" gibi sorgularla piyasa fikri al
- 🏢 **Rakip izleme** — rakip firma/hizmet hakkında yeni içerikleri yakala
- 📰 **Kurum/kişi takibi** — belli bir kurum adı geçen yeni sayfaları bildir

## ⚙️ Nasıl Çalışır?

Tek bir URL ile — API anahtarı, kayıt veya ücret yok:

```
https://www.bing.com/search?q=hepsiemlak+ankara&format=rss
```

Bing, RSS XML olarak son 10 sonucu döndürür: başlık, link, açıklama, yayın tarihi. Python stdlib ile parse edilir — ek bağımlılık yok.

**Agent bağımsız:** curl veya `urllib` ile her ortamda çalışır; sistem cron, Hermes, Claude Code, Codex veya GitHub Actions'a bağlanabilir.

## 📥 Kurulum

```bash
# Hermes:
cp -r skills/bing-rss-arama ~/.hermes/skills/

# Diğer agent'lar (Claude Code, Codex, Python vb.):
# Skill klasörünü kendi çalışma dizininize kopyalayın, script'leri python3 ile çalıştırın.
```

Hermes'e örnek istek:

> "Bing'de 'istanbul deprem yönetmeliği' için her 6 saatte bir yeni sonuçları ara, yenileri kanalıma gönder"
> "'migros indirim' hakkında son haberleri listele"

## 🧩 Özellikler

- ✅ Ücretsiz — API anahtarı gerekmez
- ✅ 10 sonuç / sorgu (sayfalama destekli)
- ✅ Türkçe sorgu ve sonuç desteği
- ✅ Agent bağımsız — her ortamda çalışır
- ✅ Watchdog deseni hazır (state tutan script örneği)

## ⚠️ Not

Bing RSS sonuçları resmi olarak **kişisel, ticari olmayan** kullanım içindir. Büyük ölçekli/ticari kullanım için Bing Web Search API gereklidir.

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar (API detayları, parse örnekleri, watchdog)
- `references/bing-rss-format.md` — RSS XML format detayları
