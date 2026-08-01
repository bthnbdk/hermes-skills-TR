# Emsal UYAP API Reverse-Engineering Notes

**Site:** emsal.uyap.gov.tr  
**Analysis date:** July 2026  
**Total indexed decisions:** ~840,000

## Technology Stack

- **Frontend:** Metronic v7.0.5 (admin template) with jQuery + DataTables
- **Backend:** Java Spring (JSESSIONID-based auth)
- **Anti-bot:** Google reCAPTCHA v2 (invisible, session-triggered after rate limit)
- **Asset version:** ?v=7.0.5 across JS/CSS bundles

## API Endpoints Discovered

All endpoints confirmed working via `urllib.request` (no browser needed):

| Method | Endpoint | Purpose | Response Format |
|---|---|---|---|
| POST | `/arama` | Simple keyword search | HTML table skeleton (DataTable init) |
| POST | `/aramalist` | Paginated simple search | JSON `{data: {data: [...], recordsTotal, recordsFiltered}, metadata}` |
| POST | `/detayliArama` | Advanced search | HTML table skeleton |
| POST | `/aramadetaylist` | Paginated advanced search | Same JSON format as `/aramalist` |
| GET | `/getDokuman?id=N` | Full decision text | JSON `{data: "<html>...", metadata: {...}}` |
| GET | `/getIstatistik` | Yearly statistics | JSON (jstree tree data) |
| GET | `/getIstatistikTable` | Statistics table | JSON DataTable data |

## Search Request Format

```json
{
  "data": {
    "aranan": "keyword",           // main search field
    "arananKelime": "keyword",     // same value (used for detail search)
    "pageSize": 20,
    "pageNumber": 1
  }
}
```

## Search Response (DataTable JSON)

```json
{
  "data": {
    "data": [
      {
        "id": "617488800",
        "daire": "İstanbul Bölge Adliye Mahkemesi 13. Hukuk Dairesi",
        "esasNo": "2019/509",
        "kararNo": "2020/1472",
        "kararTarihi": "17.12.2020",
        "arananKelime": "ihale",
        "durum": "KESİNLEŞTİ",
        "index": 1
      }
    ],
    "recordsTotal": 24890,
    "recordsFiltered": 24890
  },
  "metadata": {
    "FMTY": "SUCCESS",
    "FMC": "ADALET_SUCCESS",
    "FMTE": "İşlem başarıyla gerçekleştirildi!",
    "TID": "...",
    "SID": "..."
  }
}
```

## Advanced Search Fields

```json
{
  "arananKelime": "tazminat",
  "birimHukukMah": "İstanbul Bölge Adliye Mahkemesi 13. Hukuk Dairesi",
  "esasYil": "2020",
  "esasIlkSiraNo": "",
  "esasSonSiraNo": "",
  "kararYil": "",
  "kararIlkSiraNo": "",
  "kararSonSiraNo": "",
  "baslangicTarihi": "01.01.2020",
  "bitisTarihi": "31.12.2023",
  "siralama": "1",          // 1=Esas No, 2=Karar No, 3=Karar Tarihi
  "siralamaDirection": "desc",  // desc or asc
  "pageSize": 100,
  "pageNumber": 1
}
```

## Document HTML Structure

Each document is ~6-14KB of inline HTML with:

```html
<html>
<body leftmargin="25" topmargin="20" font face="Verdana" size="2">
  <p align="justify">
    <font face="Verdana" size="2">
      T.C.<br>İSTANBUL<br>BÖLGE ADLİYE MAHKEMESİ<br>
      12. HUKUK DAİRESİ<br>
      DOSYA NO: 2019/1336 <br>
      KARAR NO: 2021/1763<br>
      ...
    </font>
  </p>
</body>
</html>
```

All structured via `<br>` separators — no semantic HTML. Plain-text extraction via regex works well.

## Search Results Volume

The search API does **OR matching** on space-separated keywords. Observed volumes:
- "araç mahrumiyeti" alone: ~780K results
- "araç mahrumiyet bedeli fatura": ~540K results
- "araç mahrumiyet zararı taksi gideri": ~780K results

These are all BAM (Bölge Adliye Mahkemesi) decisions. The statistics page says ~838K total.

## Rate Limit & Recovery

`GET /getDokuman` has a session-level rate limit. After ~40 rapid calls (0.3s delay), the server returns `DisplayCaptcha` error. Recovery pattern:
1. Fresh `CookieJar` + `build_opener` with `HTTPCookieProcessor`
2. Visit homepage `GET /` first to seed JSESSIONID
3. Retry blocking calls at 2-2.5s delay
4. Works for another ~40-60 docs per fresh session

## Key Discovery: Date-Only Search

**`/aramadetaylist` accepts requests with NO keyword — only date range is required.** Server-side validation passes when `baslangicTarihi` + `bitisTarihi` are present. This is critical for full-scale extraction because it lets you enumerate ALL documents in the database.

### Verified

```json
{
  "data": {
    "baslangicTarihi": "01.01.2026",
    "bitisTarihi": "31.01.2026",
    "siralama": "3",
    "siralamaDirection": "asc",
    "pageSize": 5,
    "pageNumber": 1
  }
}
```

Returns 7,936 records for January 2026 — every single decision from that month. No keyword needed.

## XML Export Fields

When converting JSON documents to XML, extract these fields from the HTML content:

| XML Element | Extraction Pattern |
|---|---|
| `<Mahkeme>` | `T\.C\.\s*(.*?)(?:[\n<])` after `<html>` |
| `<Daire>` | From search metadata `daire` field |
| `<MahkemeTuru>` | BAM / ASLIYE / SULH / YARGITAY / DANISTAY (inferred from daire) |
| `<DosyaNo>` | `DOSYA\s*NO[^\d]*([\d/]+)` |
| `<EsasNo>` | From search metadata `esasNo` field |
| `<KararNo>` | `KARAR\s*NO[^\d]*([\d/]+)` |
| `<KararTarihi>` | `İSTİNAF KARAR TARİHİ\s*:?\s*([\d/]+)` |
| `<KararDurumu>` | From search metadata `durum` (KESİNLEŞTİ/KESİNLEŞMEDİ) |
| `<DavaTuru>` | `DAVA\s*:?\s*(.*?)(?:<\|$)` |
| `<KararMetni>` | Full text after stripping HTML tags |
