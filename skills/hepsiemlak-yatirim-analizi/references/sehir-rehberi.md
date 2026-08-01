# Yatırım Şehirleri Veritabanı

Kullanıcının yatırım stratejisi için seçilmiş şehirler, slug'ları ve puanlama gerekçeleri.

## Mevcut Hedef Şehirler

| Şehir | Slug | Puan | Neden? |
|-------|------|:----:|--------|
| Eskişehir | `eskisehir` | 20 | Öğrenci şehri (Anadolu Üni + ESTÜ), sürekli kira talebi, Ankara'ya 1.5 saat |
| Kırıkkale | `kirikkale` | 18 | Ankara'ya 50km, sanayi bölgesi, düşük giriş fiyatları, YHT hattı |
| Sakarya | `sakarya` | 18 | İstanbul-Ankara arası, büyüyen sanayi, üniversite (SAÜ), lojistik avantajı |
| Bolu | `bolu` | 17 | Öğrenci şehri (İzzet Baysal), doğa turizmi, Ankara-İstanbul otoyolu üzeri |

## Genişletilmiş Şehir Listesi (gelecekte eklenebilir)

| Şehir | Slug | Puan | Potansiyel |
|-------|------|:----:|------------|
| Ankara | `ankara` | 20 | Başkent, istikrarlı |
| İstanbul | `istanbul` | 20 | En yüksek talep, yüksek fiyat |
| İzmir | `izmir` | 18 | Büyükşehir, göç alıyor |
| Bursa | `bursa` | 17 | Sanayi + göç |
| Antalya | `antalya` | 17 | Turizm + yabancı talep |
| Konya | `konya` | 14 | OSB, tarım sanayi |
| Gaziantep | `gaziantep` | 14 | Güneydoğu merkezi |
| Adana | `adana` | 13 | Büyükşehir, sanayi |
| Kayseri | `kayseri` | 13 | Gelişen sanayi |
| Samsun | `samsun` | 12 | Karadeniz merkezi |
| Kocaeli | `kocaeli` | 12 | Sanayi, İstanbul yakını |
| Trabzon | `trabzon` | 11 | Artan talep, kısıtlı arsa |

## API Test Sonuçları (25 May 2026)

API'ye `{slug}-satilik` + `&p31=800000&p32=1500000` filtresiyle sorgulama:

| Şehir | Toplam İlan | Durum |
|-------|:-----------:|:-----:|
| Kırıkkale | 26 | ✅ |
| Eskişehir | — | ⚠️ encoding sorunu (ş→s) |
| Bolu | — | ✅ |
| Sakarya | — | ✅ |

## Slug Kuralları

- Küçük harf, İngilizce karakterler
- `ş` → `s`, `ı` → `i`, `ğ` → `g`, `ü` → `u`, `ö` → `o`, `ç` → `c`
- Örn: `Eskişehir` → `eskisehir`, `Kırıkkale` → `kirikkale`
- İstisnalar: `mersin` ❌ 403 döndü (farklı slug olabilir)
