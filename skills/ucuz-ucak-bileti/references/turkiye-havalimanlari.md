# ✈️ Türkiye Havalimanları — IATA Kodları

FlightList.io API'sinde `fly_from=airport:{IATA}` olarak kullanılır.
Şehir bazlı arama için `city:{CITY_CODE}` da kullanılabilir (örn. `city:IST` → İstanbul metropolü).

## Büyük Havalimanları (Uluslararası)

| IATA | Havalimanı | Şehir | Not |
|:---:|---|---|---|
| IST | İstanbul Havalimanı | İstanbul | Ana uluslararası hub |
| SAW | Sabiha Gökçen | İstanbul | Asya yakası, LCC merkezi |
| ESB | Esenboğa | Ankara | Başkent |
| ADB | Adnan Menderes | İzmir | Ege hub'ı |
| AYT | Antalya | Antalya | Turizm devi |
| DLM | Dalaman | Muğla | Turizm |
| BJV | Milas-Bodrum | Muğla | Turizm |
| TZX | Trabzon | Trabzon | Karadeniz |
| ADA | Şakirpaşa | Adana | Çukurova |
| GZT | Oğuzeli | Gaziantep | Güneydoğu |
| ASR | Erkilet | Kayseri | İç Anadolu |
| VAN | Ferit Melen | Van | Doğu |
| ERZ | Erzurum | Erzurum | Doğu Anadolu |
| DIY | Diyarbakır | Diyarbakır | Güneydoğu |
| SZF | Çarşamba | Samsun | Karadeniz |
| GZP | Gazipaşa-Alanya | Antalya | Turizm |

## Orta Ölçekli Havalimanları

| IATA | Havalimanı | Şehir |
|:---:|---|---|
| HTY | Hatay | Hatay |
| KYA | Konya | Konya |
| MLX | Malatya | Malatya |
| EZS | Elazığ | Elazığ |
| DNZ | Çardak | Denizli |
| NAV | Kapadokya | Nevşehir |
| YEI | Yenişehir | Bursa |
| ISE | Süleyman Demirel | Isparta |
| KCO | Cengiz Topel | Kocaeli |
| OGU | Ordu-Giresun | Ordu |
| RZV | Rize-Artvin | Rize |
| KSY | Kars | Kars |
| VAS | Sivas | Sivas |
| KCM | Kahramanmaraş | Kahramanmaraş |
| SFQ | Şanlıurfa GAP | Şanlıurfa |
| NKT | Şırnak | Şırnak |
| AJI | Ağrı | Ağrı |
| IGD | Iğdır | Iğdır |
| MSR | Muş | Muş |
| BGG | Bingöl | Bingöl |
| MQM | Mardin | Mardin |
| BAL | Batman | Batman |
| SXZ | Siirt | Siirt |
| YKO | Hakkari-Yüksekova | Hakkari |

## Küçük / Bölgesel Havalimanları

| IATA | Havalimanı | Şehir |
|:---:|---|---|
| USQ | Uşak | Uşak |
| ONQ | Çaycuma | Zonguldak |
| KFS | Kastamonu | Kastamonu |
| TEQ | Çorlu | Tekirdağ |
| CKZ | Çanakkale | Çanakkale |
| BZI | Koca Seyit | Balıkesir |
| EDO | Edremit Körfez | Balıkesir |
| ADF | Adıyaman | Adıyaman |
| GKD | Gökçeada | Çanakkale |
| YLJ | Ahlat | Bitlis |
| MQJ | Balıkesir Merkez | Balıkesir |

## Popüler Şehir Kodları (city: prefix)

| CITY_CODE | Şehir | Kapsadığı Havalimanları |
|:---:|---|---|
| IST | İstanbul | IST + SAW |
| ANK | Ankara | ESB |
| IZM | İzmir | ADB |
| AYT | Antalya | AYT + GZP |
| BJV | Bodrum/Muğla | BJV + DLM |
| TZX | Trabzon | TZX |

## Örnek Kullanımlar

```
# İstanbul'dan Londra'ya
fly_from=airport:IST&fly_to=city:LON

# İzmir'den Avrupa'nın herhangi bir yerine
fly_from=airport:ADB&fly_to=AT,BE,BG,...

# Antalya'dan (city kodu — AYT + GZP dahil) Orta Doğu'ya
fly_from=city:AYT&fly_to=AE,BH,EG,...

# Ankara'dan direkt uçuşlar
fly_from=airport:ESB&max_stopovers=0
```
