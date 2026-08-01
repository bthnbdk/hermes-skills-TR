# Migros İndirim / Kampanya Tipleri

API'de her üründe bulunan indirim ve kampanya alanları:

## 1. Doğrudan Fiyat İndirimi (discountRate)

```json
{
  "regularPrice": 34995,    // Normal fiyat: 349,95 TL
  "shownPrice": 23995,      // İndirimli fiyat: 239,95 TL
  "discountRate": 31        // %31 indirim
}
```

- `regularPrice` ile `shownPrice` farklıysa üründe indirim var
- `discountRate` yüzdeli indirimi gösterir (0 = indirim yok)
- `badges` array'inde `name: "PRICE_PROMOTED"` ile eşleşir
- Örnek badge: `{"name": "PRICE_PROMOTED", "value": "169,95 TL"}` (sarı etiket)

## 2. Çapraz Promosyon / Çoklu Alım (CROSS_PROMOTED)

```json
{"name": "CROSS_PROMOTED", "value": "2 Al 1 Öde", "colorCodes": ["#808284", "#ffffff"]}
```

- Sepette çoklu alım kampanyaları
- Değerler: "2 Al 1 Öde", "3 Al 2 Öde", vb.
- Doğrudan fiyat indirimi DEĞİL, sepette uygulanır

## 3. Migroskop Ürünleri (MIGROSKOP)

```json
{
  "name": "MIGROSKOP",
  "value": "MİGROSKOP",
  "colorCodes": ["#FFF8E5", "#4B4C4E"]
}
```

- `groupBadgeMap.MARKETING` içinde badgeId: 20000000000001
- badgeId: 20000000000001 (MIGROSKOP)
- Migroskop logosu: `https://images.migrosone.com/sanalmarket/assets/logos/migroskop_logo.svg`
- Hafif sarı arka planlı badge (`#FFF8E5`)

## 4. CRM / Sepet İndirimleri (crmDiscountTags)

```json
{"type": "CRM_DISCOUNT", "tag": "50 TL Sepette 59,9 TL"}
{"type": "CRM_DISCOUNT", "tag": "2 Öde 1'i Money Hediye"}
```

- Sepete eklenince otomatik uygulanan indirimler
- Para indirimi, money kampanyası, hediye ürün gibi tipler
- Fiyat üzerinde görünmez, sepette uygulanır

## Özet: İndirim Tespit Yöntemleri

| İndirim Tipi | Tespit Yöntemi | Sepette mi? |
|-------------|----------------|-------------|
| Yüzde indirim | `discountRate > 0` veya `regularPrice != shownPrice` | Hayır |
| Çoklu alım | `badges[].name == "CROSS_PROMOTED"` | Evet |
| Migroskop | `badges[].name == "MIGROSKOP"` veya `badges[].badgeId == 20000000000001` | Hayır |
| Sepet indirimi | `crmDiscountTags.length > 0` | Evet |
