# Bing RSS Format Detayları

## Tam XML Örneği (Gerçek)

```xml
<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0">
  <channel>
    <title>Bing: hepsiemlak ankara</title>
    <link>http://www.bing.com:80/search?q=hepsiemlak+ankara</link>
    <description>Arama sonuçları</description>
    <image>
      <url>http://www.bing.com:80/s/a/rsslogo.gif</url>
      <title>hepsiemlak ankara</title>
      <link>http://www.bing.com:80/search?q=hepsiemlak+ankara</link>
    </image>
    <copyright>Telif Hakkı © 2026 Microsoft. Tüm hakları saklıdır. Bu XML sonuçları, Bing sonuçlarını kişisel, ticari olmayan kullanımınız için bir RSS toplayıcısında görüntüleme dışında, hiçbir şekilde veya hiçbir amaçla kullanılamaz, yeniden üretilemez veya iletilemez...</copyright>
    <item>
      <title>Hepsiemlak | Satılık, Kiralık Ev &amp; Emlak İlanları</title>
      <link>https://www.hepsiemlak.com/</link>
      <description>Hepsiemlak ile aradığınız tüm satılık &amp; kiralık ev, daire, ofis ve emlak ilanlarına hem sahibinden hem de emla...</description>
      <pubDate>Cmt, 01 Ağu 2026 07:40:00 GMT</pubDate>
    </item>
    <!-- 10 item'a kadar -->
  </channel>
</rss>
```

## URL Parametreleri

| Param | Örnek | Açıklama |
|-------|-------|----------|
| `q` | `hepsiemlak+ankara` | Sorgu — `+` veya `%20` ile boşluk |
| `format` | `rss` | Zorunlu — RSS çıktısı |
| `first` | `1`, `11`, `21` | Sayfalama başlangıcı (varsayılan 1) |
| `count` | `10` | Sonuç sayısı (Bing genelde 10 sabit döndürür) |
| `cc` | `tr` | Ülke kodu (Türkçe sonuçlar için `cc=tr`) |
| `setlang` | `tr` | Arayüz dili |
| `mkt` | `tr-TR` | Pazar kodu |

## Parse Örneği — ElementTree (Türkçe tarih sorunu var)

```python
import xml.etree.ElementTree as ET

tree = ET.parse("sonuclar.xml")
for item in tree.findall(".//item"):
    title = item.findtext("title")
    link = item.findtext("link")
    print(title, link)
```

⚠️ `pubDate`'i `email.utils.parsedate_to_datetime` ile parse etmeye çalışmayın — Türkçe gün/ay kısaltmaları (`Cmt`, `Ağu`) RFC 822 parse'ında hata verir. Tarihi string olarak gösterin veya kendi Türkçe→İngilizce çeviri tablonuzu yazın:

```python
TR_GUNLER = {"Pzt": "Mon", "Sal": "Tue", "Çar": "Wed", "Per": "Thu", "Cum": "Fri", "Cmt": "Sat", "Paz": "Sun"}
TR_AYLAR = {"Oca": "Jan", "Şub": "Feb", "Mar": "Mar", "Nis": "Apr", "May": "May", "Haz": "Jun",
            "Tem": "Jul", "Ağu": "Aug", "Eyl": "Sep", "Eki": "Oct", "Kas": "Nov", "Ara": "Dec"}

def tr_tarih_parse(pubdate):
    for tr, en in {**TR_GUNLER, **TR_AYLAR}.items():
        pubdate = pubdate.replace(tr, en)
    return pubdate  # artık parsedate ile çözülebilir
```

## Rate Limit Davranışı

- Normal kullanım (dakikada 1-2 istek): sorunsuz
- Hızlı ardışık istekler (10+ / saniye): IP geçici engellenebilir (403 veya boş sonuç)
- Çözüm: istekler arasında 2-3sn bekle, sorgu sayısını sınırla
- Cron kullanımı (saatte 1-4 kez): hiç sorun yaşanmaz

## Gerçek Sorgu Örnekleri + Beklenen Sonuç Sayısı

| Sorgu | Sonuç |
|-------|-------|
| `hepsiemlak ankara` | 10 item — hepsiemlak.com sayfaları |
| `migros indirim` | 10 item — migros.com.tr + haber siteleri |
| `yargıtay kararı kira` | 10 item — hukuk siteleri, karar portalları |
| `ucuz uçak bileti` | 10 item — havayolu/acente siteleri |
