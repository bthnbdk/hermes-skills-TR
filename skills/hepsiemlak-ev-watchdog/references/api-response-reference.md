# HepsiEmlak API Full Response Reference

Doğrulanmış endpoint: `https://www.hepsiemlak.com/api/realty-list/{sehir}-satilik`
Örnek: `https://www.hepsiemlak.com/api/realty-list/ankara-satilik?counties=cankaya&sortDirection=DESC&sortField=UPDATED_DATE&intent=satilik&mainCategory=konut&availableForLoanStatus=APPLICABLE&p32=6500000&pageNo=1&pageSize=50`

> ⚠️ `pageSize=50` parametresi çalışmaz — API her zaman 24 ilan döndürür.

## Top-Level Structure

```json
{
  "heading": "Çankaya House For Sale",
  "metaTag": {
    "title": "Çankaya Satılık Ev Fiyatları ve İlanları",
    "description": "Çankaya satılık ev fiyatlarını ve detaylarını incelemek için Hepsiemlak'ı ziyaret edin..."
  },
  "totalElements": 2389,
  "page": 1,
  "size": 24,
  "totalPages": 100,
  "realtyList": [ ... ]
}
```

## Single Listing (realtyList[0])

Gerçek API yanıtından alınmıştır (25 May 2026):

```json
{
  "id": 45847239,
  "adDataType": null,
  "age": 30,
  "city": {"id": 6, "name": "Ankara", "tier": 1},
  "country": null,
  "county": {"id": 1231, "name": "Çankaya", "tier": 1},
  "createDate": "2026-01-01T10:36:50.163+00:00",
  "updatedDate": "2026-05-25T03:55:43.890Z",
  "listingUpdatedDate": "2026-05-25T03:55:43.870Z",
  "startDate": "2026-05-22T04:26:58.867+00:00",
  "currency": "TL",
  "date": "2026-01-01T10:21:00.000+00:00",
  "district": {"id": 28773, "name": "Ön Cebeci", "tier": 1},
  "subCategory": {"id": 1, "name": "Daire"},
  "mainCategory": {"id": 1, "name": "Konut"},
  "floor": {"currentFloor": 3, "totalFloor": 5, "isGround": false, ...},
  "images": [...],
  "imageUrl": "https://i.hepsiemlak.com/.../thumb/...jpg",
  "listingId": "113450-1510",
  "owner": null,
  "firmUser": {...},
  "firm": {...},
  "contact": {...},
  "price": 5275000.0,
  "useContactInfo": true,
  "room": [3],
  "livingRoom": [1],
  "roomAndLivingRoom": ["3+1"],
  "sellerType": "fromOwner",
  "sqm": {
    "netSqm": 110.0,
    "grossSqm": [138.0],
    "price": 0.0
  },
  "title": "138 Square Meters Apartment For Sale in Çankaya, Ankara",
  "category": {...},
  "detailUrl": "en/ankara-cankaya-on-cebeci-satilik/daire/113450-1510",
  "detailDescription": "...",
  "star": 0,
  "dormitory": 0,
  "tagProducts": [],
  "featuringProducts": [],
  "projeland": null,
  "highestPrice": null,
  "lowestPrice": null,
  "mapLocation": {...},
  "populated": false,
  "videoUrl": null,
  "advertiseOwner": null,
  "stale": false,
  "whatsAppNumber": null,
  "image360Count": 0,
  "onlineVisit": false,
  "hasBranded": false,
  "hasUpdateBooster": false,
  "hasFirmBrandedUser": false,
  "firmBrandedUser": null,
  "advertiseCategoryTitle": "Satılık Daire",
  "bedCount": 0,
  "guestCount": 0,
  "period": null,
  "identificationNo": null,
  "permitDocumentOwner": null,
  "apartmentsOnFloor": 1,
  "realtyIsShared": false,
  "cplStatus": null,
  "flatReceivedForLand": null,
  "energyDocumentNo": null
}
```

## Key Extraction Patterns (Doğrulanmış)

| Hedef | Kod | Açıklama |
|-------|-----|----------|
| ID | `i["id"]` | int, benzersiz |
| Fiyat | `i["price"]` | float, TL cinsinden |
| Mahalle | `i["district"]["name"]` | string, Türkçe (örn: "Küçükesat") |
| Oda | `i["room"][0]` + `i["livingRoom"][0]` | array'den ilk eleman |
| Brüt m² | `i["sqm"]["grossSqm"][0]` | array'den ilk eleman |
| Net m² | `i["sqm"]["netSqm"]` | float |
| Detay URL | `i["detailUrl"]` | `/en/` prefix'ini strip et! |
| Güncelleme | `i["updatedDate"]` | ISO 8601 timestamp |
| Başlık | `i["title"]` | İngilizce (API'den öyle geliyor) |
| İlan türü | `i["advertiseCategoryTitle"]` | "Satılık Daire" gibi |
| Kat | `i["floor"]["currentFloor"]` / `i["floor"]["totalFloor"]` | int |
| İlçe | `i["county"]["name"]` | "Çankaya" |
| Görsel | `i["imageUrl"]` | thumbnail URL |
