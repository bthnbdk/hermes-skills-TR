---
name: bing-rss-arama
description: "Bing RSS arama — ücretsiz, API anahtarı gerektirmeyen web araması. https://www.bing.com/search?q=KEYWORD&format=rss ile 10 sonuç döner. Haber takibi, fiyat araştırması, keyword monitoring, rakip izleme için ideal. Python stdlib ile parse edilir, her agent ile çalışır."
version: 1.0.0
author: Turkce AI Skillleri Toplulugu
---

# Bing RSS Arama

Ücretsiz, API anahtarı gerektirmeyen web arama yöntemi. Bing'in RSS çıktısı ile herhangi bir anahtar kelime için **son 10 arama sonucunu** (başlık, link, açıklama, tarih) alırsınız.

**Endpoint:**
```
https://www.bing.com/search?q={KEYWORD}&format=rss
```

## 🎯 Ne İşe Yarar?

- 🔍 **Haber takibi** — belirli konularda yeni çıkan haberleri izle
- 🏷️ **Keyword monitoring** — bir ürün/marka hakkında ne konuşuluyor takip et
- 💰 **Fiyat araştırması** — "hepsiemlak ankara kiralık" gibi sorgularla piyasa fikri al
- 🏢 **Rakip izleme** — rakip firma/hizmet hakkında yeni içerikleri yakala
- 📰 **Kurum/kişi takibi** — belli bir kurum adı geçen yeni sayfaları bildir
- 🔗 **Link keşfi** — bir konudaki otorite siteleri/URL'leri topla

## 🧠 API Detayları

| Parametre | Örnek | Açıklama |
|-----------|-------|----------|
| `q` | `hepsiemlak ankara` | Arama sorgusu (boşluklar `+` ile değiştirilir) |
| `format` | `rss` | RSS çıktısı (zorunlu) |
| `first` | `1`, `11`, `21` | İsteğe bağlı — sayfalama (varsayılan ilk 10) |
| `count` | `10` | İsteğe bağlı — sonuç sayısı (genelde 10 sabit) |
| `cc` | `tr` | İsteğe bağlı — ülke kodu (Türkçe sonuçlar için `cc=tr`) |
| `setlang` | `tr` | İsteğe bağlı — dil |

### Response Yapısı (RSS XML)

```xml
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Bing: hepsiemlak ankara</title>
    <item>
      <title>Hepsiemlak | Satılık, Kiralık Ev &amp; Emlak İlanları</title>
      <link>https://www.hepsiemlak.com/</link>
      <description>Hepsiemlak ile aradığınız tüm satılık &amp; kiralık ev...</description>
      <pubDate>Cmt, 01 Ağu 2026 07:40:00 GMT</pubDate>
    </item>
    <!-- toplam 10 item -->
  </channel>
</rss>
```

### Item Alanları

| Alan | Açıklama |
|------|----------|
| `title` | Sonuç başlığı (HTML entity'ler olabilir: `&amp;` → `&`) |
| `link` | Hedef URL |
| `description` | Kısa açıklama / snippet (HTML içerebilir — strip et) |
| `pubDate` | Yayın tarihi (RFC 822 formatı, Türkçe ay adları olabilir: `Cmt, 01 Ağu 2026`) |

## 🚀 Kullanım

### Seçenek A — curl + Python parse (her ortamda)

```bash
curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36" \
  "https://www.bing.com/search?q=hepsiemlak+ankara&format=rss" -o sonuclar.xml
```

```python
import re, html, urllib.request, urllib.parse

def bing_rss(sorgu, first=1):
    url = "https://www.bing.com/search?q=" + urllib.parse.quote_plus(sorgu) + "&format=rss&first=" + str(first)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36"
    })
    xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    sonuclar = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        def al(tag):
            m = re.search(rf"<{tag}>(.*?)</{tag}>", item, re.S)
            return html.unescape(m.group(1)).strip() if m else ""
        sonuclar.append({"title": al("title"), "link": al("link"),
                         "description": al("description"), "pubDate": al("pubDate")})
    return sonuclar

for s in bing_rss("hepsiemlak ankara kiralık"):
    print(f"📰 {s['title']}\n🔗 {s['link']}\n📅 {s['pubDate']}\n")
```

### Seçenek B — Doğrudan XML okuma (xpath olmadan)

`xml.etree.ElementTree` de kullanılabilir ama Bing'in Türkçe ay adları (`Cmt, 01 Ağu`) RFC 822 parse'ında sorun çıkarabilir — regex yaklaşımı daha güvenli.

## ⏰ Zamanlanmış Görev (Watchdog)

Yeni sonuçları bildirmek için state tutan script + zamanlayıcı:

```python
#!/usr/bin/env python3
# bing_watchdog.py — örn. "Yeni İstanbul deprem yönetmeliği haberleri"
import json, os, sys

SORGU = "istanbul deprem yönetmeliği"
STATE_FILE = os.path.expanduser("~/bing_watchdog_state.json")

# ... bing_rss() fonksiyonu yukarıdaki gibi ...

yeni = []
state = json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {"gorulen": []}
for s in bing_rss(SORGU):
    if s["link"] not in state["gorulen"]:
        yeni.append(s)
state["gorulen"] = [s["link"] for s in bing_rss(SORGU)]
json.dump(state, open(STATE_FILE, "w"))

if yeni:
    for s in yeni[:5]:
        print(f"📰 {s['title']}\n🔗 {s['link']}\n📅 {s['pubDate']}")
    # Boş çıktı = sessiz (yeni yok) — bildirim kanalına hiçbir şey gitmez
```

```bash
# Sistem cron (her 6 saatte):
0 */6 * * * cd <calisma_dizini> && python3 bing_watchdog.py >> bing.log 2>&1

# Hermes:
cronjob(action='create', name='Bing {SORGU} Takibi',
        script='bing_watchdog.py', no_agent=True,
        schedule='0 */6 * * *', deliver='<KANAL>',
        workdir='<WORKDIR>')
```

## 🚨 Gotchas

1. **User-Agent zorunlu** — isteksiz UA ile Bing 403 dönebilir. Tarayıcı UA'sı kullan.
2. **Rate limit** — saniyeler içinde çok fazla istek atarsanız IP geçici engellenebilir. İstekler arasında en az 2-3sn bekleyin.
3. **Sadece 10 sonuç** — RSS formatında Bing genelde ilk 10 sonucu döndürür. `first=11`, `first=21` ile sayfalayın.
4. **Türkçe tarih formatı** — `pubDate` RFC 822 ama Türkçe ay/gün kısaltmaları içerebilir (`Cmt`, `Ağu`). `email.utils.parsedate` bunları çözemeyebilir — tarihi string olarak kullanın veya kendiniz parse edin.
5. **Ticari kullanım kısıtı** — Bing RSS sonuçları resmi olarak kişisel, ticari olmayan kullanım içindir (XML içinde Microsoft'un telif notu vardır). Büyük ölçekli/ticari kullanım için Bing Web Search API gereklidir.
6. **HTML entity'ler** — `&amp;`, `&#39;` gibi entity'ler `html.unescape()` ile temizlenmeli.
7. **Description HTML içerir** — snippet'te `<b>` gibi etiketler olabilir, regex ile strip edin.
8. **Türkçe karakterler** — `q` parametresinde Türkçe karakterler URL-encode edilmeli (`urllib.parse.quote_plus`).

## 🔍 Örnek Sorgular

| Amaç | Sorgu |
|------|-------|
| Emlak piyasası | `hepsiemlak ankara kiralık daire` |
| Hukuk | `yargıtay kararı kira tespit davası` |
| Alışveriş | `migros indirim bu hafta` |
| Teknoloji | `türkiye yapay zeka yatırımı` |
| Siyaset | `meclis gündemi bu hafta` |
| Sağlık | `sağlık bakanlığı yeni genelge` |

## 📂 Skill Files

| Dosya | Açıklama |
|-------|----------|
| `SKILL.md` | Ana talimatlar (bu dosya) |
| `references/bing-rss-format.md` | RSS XML format detayları + parse örnekleri |
