# Migros İndirim Watchdog — Zamanlanmış Görev

`migros_indirim_watchdog.py` isimli Python script'i ile 10 kategorideki yeni indirimleri otomatik takip eder. Agent bağımsız — herhangi bir zamanlayıcıyla çalışır.

## Kurulum

Script'i bir çalışma dizinine kopyalayın, ardından zamanlayıcıya bağlayın:

```bash
# Seçenek A — Sistem cron:
0 9,18 * * * cd <calisma_dizini> && python3 migros_indirim_watchdog.py >> watchdog.log 2>&1

# Seçenek B — Hermes:
cronjob action=create \
  name="migros-indirim-watchdog" \
  schedule="0 9,18 * * *" \
  script="migros_indirim_watchdog.py" \
  no_agent=true \
  deliver="<KANAL>"
```

- Script stdout'u direkt bildirim kanalına gider
- Çıktı BOŞSA sessiz — yeni indirim yok demektir
- Hermes'te `deliver` parametresi hedef kanala göre ayarlanır

## Kapsanan Kategoriler (10 adet)

| Kategori | Sorgular |
|----------|----------|
| 🥩 Et | tavuk göğsü, kıyma, bonfile, kuşbaşı, tavuk but, kuzu, dana et, köfte, hindi |
| 🥛 Süt Ürünleri | süt, yoğurt, peynir, tereyağ, kefir, ayran, labne, krema |
| 🫒 Zeytinyağı | zeytinyağı, riviera, sızma |
| 🧴 Şampuan | şampuan, saç kremi |
| 🦷 Diş Macunu | diş macunu, ağız bakım |
| 🧻 Kağıt Havlu | kağıt havlu |
| 🧻 Tuvalet Kağıdı | tuvalet kağıdı |
| 💧 Islak Havlu | ıslak havlu, silme bezi |
| 🍱 Hazır Yemek | hazır yemek, pratik yemek, donuk yemek |
| 🧂 Gıda | makarna, pirinç, mercimek, konserve, salça |

## Hariç Tutulan Ürünler

Pet ürünleri (köpek maması, kedi maması, kum, akvaryum vb.) tüm kategorilerden filtrelenir — `EXCLUDED_KEYWORDS` listesi ile.

## Tespit Edilen İndirim Türleri

- 🔥 Yüzde indirim (`discountRate > 0`)
- 🌟 Migroskop (`badges.name == "MIGROSKOP"`)
- 🎯 Çoklu alım (`badges.name == "CROSS_PROMOTED"`)
- 🛒 Sepet indirimi (`crmDiscountTags`)

## Durum Takibi

- `<calisma_dizini>/migros_discount_state.json` — state dosyası
- Her ürünün önceki discountRate/Migroskop/CROSS_PROMOTED/CRM durumunu hatırlar
- Sadece **yeni çıkan** veya **artış gösteren** indirimleri bildirir
- 7 gün görülmeyen ürünler temizlenir (state şişmesin)
