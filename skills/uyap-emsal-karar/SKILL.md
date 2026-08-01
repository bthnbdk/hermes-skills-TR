---
name: uyap-emsal-karar
description: "Emsal UYAP — search, download, and merge Turkey's court precedent database (emsal.uyap.gov.tr). Full pipeline: multi-keyword search → collect unique results → download full texts → merge into single TXT."
version: 1.3.0
author: BatuBOT
---

# UYAP Emsal Karar Arama — Search & Scrape Pipeline

**Site:** [emsal.uyap.gov.tr](https://emsal.uyap.gov.tr) — Turkey's national precedent court decision database (~840K BAM decisions).

## CLI Tool

Script at `<calisma_dizini>/emsal_uyap.py` (agent bağımsız — doğrudan python3 ile çalışır)

### Single Commands

```bash
# Simple keyword search
python3 <calisma_dizini>/emsal_uyap.py search "ihale"

# Search with pagination + limit
python3 <calisma_dizini>/emsal_uyap.py search "kira sözleşmesi" --max 20 --page-size 50

# Export to CSV
python3 <calisma_dizini>/emsal_uyap.py search "iş kazası" --max 100 --csv /tmp/is_kazasi.csv

# Export to JSON
python3 <calisma_dizini>/emsal_uyap.py search "tahliye" --max 1000 --json /tmp/tahliye.json

# Advanced search with filters
python3 <calisma_dizini>/emsal_uyap.py advanced "tazminat" \
  --court "İstanbul Bölge Adliye Mahkemesi 13. Hukuk Dairesi" \
  --start-date 01.01.2020 --end-date 31.12.2023 --max 50

# Get full decision text
python3 <calisma_dizini>/emsal_uyap.py get-doc 702706800

# Full pipeline: search + download all matching decisions
python3 <calisma_dizini>/emsal_uyap.py fetch-all "icra hukuk" \
  --output-dir /tmp/kararlar/ --max 50
```

## Multi-Keyword Search + Merge Pipeline

Use when you need to search across multiple keyword combinations, deduplicate, download texts, and merge into one file.

### Step-by-step Pattern

```python
import json, os, time, re, urllib.request, http.cookiejar, glob

OUT = "/tmp/kararlar"
os.makedirs(f"{OUT}/documents", exist_ok=True)

# 1. Define search queries (keywords are OR-matched by the API)
QUERIES = [
    # ("label_for_category", "search_keywords")
    ("01_fatura_yoklugu",     "araç mahrumiyet bedeli fatura"),
    ("02_ispat_yuku",         "ikame araç bedeli ispat yükü"),
    ("03_kiralama_belgesi",   "ikame araç bedeli kiralama belgesi ibraz edilmemesi"),
    ("04_makul_onarim",       "makul onarım süresi araç mahrumiyeti"),
    ("05_zorunlu_ulasim",     "araç mahrumiyet zararı zorunlu ulaşım"),
    ("06_taksi_gideri",       "araç mahrumiyet zararı taksi gideri"),
]

# 2. Search each query (max 15-20 per category is enough for case law research)
all_sources = {}  # id -> {meta, categories}
for label, keyword in QUERIES:
    os.system(f"python3 <calisma_dizini>/emsal_uyap.py search \"{keyword}\" --max 15 --page-size 15 --json {OUT}/{label}.json 2>/dev/null")

# 3. Collect unique document IDs
for f in glob.glob(f"{OUT}/0*.json"):
    with open(f) as fp:
        data = json.load(fp)
    cat = os.path.basename(f).replace('.json','')
    for r in data.get("results", []):
        did = r["id"]
        if did not in all_sources:
            all_sources[did] = {"meta": r, "categories": []}
        if cat not in all_sources[did]["categories"]:
            all_sources[did]["categories"].append(cat)

print(f"Total unique: {len(all_sources)}")

# 4. Download documents (needs cookie jar to handle captcha rate limit)
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Seed session
req = urllib.request.Request("https://emsal.uyap.gov.tr/",
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
with opener.open(req, timeout=15) as resp:
    resp.read()

BASE = "https://emsal.uyap.gov.tr/getDokuman?id="
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
           "Referer": "https://emsal.uyap.gov.tr/"}

downloaded = 0
blocked = []
for did, info in all_sources.items():
    out_path = f"{OUT}/documents/{did}.json"
    if os.path.exists(out_path):
        downloaded += 1
        continue
    time.sleep(1.5)  # 1.5s to avoid captcha trigger
    
    try:
        req = urllib.request.Request(BASE + did, headers=HEADERS)
        with opener.open(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("data") is not None:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            downloaded += 1
        else:
            blocked.append(did)
    except Exception as e:
        blocked.append(did)

# 5. Retry blocked docs with fresh session
if blocked:
    time.sleep(5)
    cj2 = http.cookiejar.CookieJar()
    opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj2))
    req = urllib.request.Request("https://emsal.uyap.gov.tr/", headers=HEADERS)
    with opener2.open(req, timeout=15) as resp:
        resp.read()
    for did in blocked:
        time.sleep(2.5)
        try:
            req = urllib.request.Request(BASE + did, headers=HEADERS)
            with opener2.open(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("data") is not None:
                with open(f"{OUT}/documents/{did}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

# 6. Merge into single TXT file
def clean_text(html):
    if html is None: return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text

lines = []
lines.append("=" * 80)
lines.append("ANA BAŞLIK — EMSAL KARARLAR DERLEMESİ")
lines.append(f"Kaynak: emsal.uyap.gov.tr")
lines.append(f"Toplam: {len(all_sources)} karar")
lines.append("=" * 80)
lines.append("")

for cat_label in sorted(glob.glob(f"{OUT}/0*.json")):
    with open(cat_label) as fp:
        data = json.load(fp)
    cat_name = os.path.basename(cat_label).replace('.json','')
    items = [(did, info) for did, info in all_sources.items() if cat_name in info["categories"]]
    if not items: continue

    lines.append("=" * 80)
    lines.append(f"  {cat_name.upper()}")
    lines.append(f"  {len(items)} karar")
    lines.append("=" * 80)
    lines.append("")

    for i, (did, info) in enumerate(items, 1):
        doc_path = f"{OUT}/documents/{did}.json"
        if not os.path.exists(doc_path): continue
        with open(doc_path) as f:
            doc = json.load(f)
        doc_text = clean_text(doc.get("data", ""))

        lines.append(f"─" * 80)
        lines.append(f"  KARAR {i}  |  ID: {did}  |  Esas: {info['meta'].get('esasNo','?')}")
        lines.append(f"─" * 80)
        lines.append(f"  Mahkeme: {info['meta'].get('daire','?')}")
        lines.append(f"  Tarih: {info['meta'].get('kararTarihi','?')}")
        lines.append(f"  Durum: {info['meta'].get('durum','?')}")
        lines.append(f"  URL: https://emsal.uyap.gov.tr/getDokuman?id={did}")
        lines.append("")
        if len(doc_text) > 4000:
            lines.append(doc_text[:4000])
            lines.append(f"\n  [...devamı {len(doc_text)-4000} karakter]")
        else:
            lines.append(doc_text)
        lines.append("")

with open(f"{OUT}/MERGED_EMSAL_KARARLAR.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
```

### What the Merged File Contains

- **Index** with category names and counts
- Each **decision entry** includes: karar numarası, mahkeme adı, tarih, durum, karar metni (ilk 4000 karakter)
- Full text accessible via the provided URL

## API Reference

### Endpoints

| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| POST | `/aramalist` | Paginated keyword search | JSON `{data, metadata}` |
| POST | `/aramadetaylist` | Paginated advanced search | JSON `{data, metadata}` |
| GET | `/getDokuman?id=N` | Full decision text | JSON `{data: "<html>...", metadata}` |

### Search Response Fields

| Field | Example |
|---|---|
| `id` | `617488800` |
| `daire` | `İstanbul Bölge Adliye Mahkemesi 13. Hukuk Dairesi` |
| `esasNo` | `2019/509` |
| `kararNo` | `2020/1472` |
| `kararTarihi` | `17.12.2020` |
| `durum` | `KESİNLEŞTİ` or `KESİNLEŞMEDİ` |
| `index` | `1` |

### Request Format (Search)

```json
{
  "data": {"aranan": "keyword", "arananKelime": "keyword", "pageSize": 20, "pageNumber": 1}
}
```

### Advanced Search Fields

```json
{
  "arananKelime": "tazminat",
  "birimHukukMah": "İstanbul Bölge Adliye Mahkemesi 13. Hukuk Dairesi",
  "esasYil": "2020",
  "baslangicTarihi": "01.01.2020",
  "bitisTarihi": "31.12.2023",
  "siralama": "1",           // 1=Esas No, 2=Karar No, 3=Karar Tarihi
  "siralamaDirection": "desc"  // desc or asc
}
```

### Search Volume Notes

API does **OR matching** on space-separated keywords. Observed volumes:
- Single word "araç mahrumiyeti": ~780K results
- Combined "araç mahrumiyet bedeli fatura": ~540K results
- Combined "makul onarım süresi araç mahrumiyeti": ~470K results

## Captcha Recovery

The site has a session-level rate limit. After ~40 rapid `getDokuman` calls, the server returns `DisplayCaptcha` errors.

**Recovery pattern:**
1. Create a fresh `http.cookiejar.CookieJar` + `build_opener`
2. Visit homepage `GET /` first to seed JSESSIONID
3. Retry blocked calls at 2-2.5s delay between requests
4. Fresh session yields another ~40-60 docs before rate limit

## XML Export Format

When the user wants individual XML files instead of a merged TXT, convert each JSON document to XML:

```python
import json, os, re

def escape_xml(s):
    if not s: return ''
    for ch, esc in [('&','&amp;'),('<','&lt;'),('>','&gt;'),('"','&quot;'),("'",'&apos;')]:
        s = s.replace(ch, esc)
    return s

for fname in os.listdir('/tmp/kararlar/documents/'):
    if not fname.endswith('.json'): continue
    did = fname.replace('.json','')
    with open(f'/tmp/kararlar/documents/{fname}') as f:
        doc = json.load(f)
    html = doc.get('data','')
    if not html: continue
    
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Extract metadata from HTML
    m = re.search(r'DOSYA\s*NO[^\d]*([\d/]+)', html)
    dosya_no = m.group(1) if m else ''
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<EmsalKarar>
  <DokumanID>{escape_xml(did)}</DokumanID>
  <DosyaNo>{escape_xml(dosya_no)}</DosyaNo>
  <KararMetni>{escape_xml(text)}</KararMetni>
</EmsalKarar>'''
    
    with open(f'/tmp/kararlar/xml/{did}.xml', 'w', encoding='utf-8') as f:
        f.write(xml)
```

Full metadata fields for XML: `Mahkeme`, `Daire`, `MahkemeTuru`, `DosyaNo`, `EsasNo`, `KararNo`, `KararTarihi`, `KararDurumu`, `DavaTuru`, `IlkDereceMahkemesi`, `IlkKararTarihi`, `IlkKararNumarasi`, `KaynakURL`, `KararMetni`.

## Full-Scale Extraction (All 840K Decisions)

Strategy for pulling the entire database — see `references/full-scale-extraction.md` for full details.

### Key Insight: Date-Only Search

`/aramadetaylist` works with **only date range, no keyword**. This lets you enumerate ALL documents systematically by iterating month-by-month.

```python
# Monthly chunking discovers every document ID
for yil in range(2016, 2027):
    for ay in range(1, 13):
        res = advanced_search({
            "baslangicTarihi": f"01.{ay:02d}.{yil}",
            "bitisTarihi": last_day_str,
            "pageSize": 100, "pageNumber": page,
        })
```

### Parallel Download with Session Rotation

- 8 parallel workers, each with its own CookieJar
- Every **38 docs → fresh session** (avoids DisplayCaptcha)
- 1.5s delay between requests
- **~44 hours** for all 840K (8 workers)
- **~13 hours** for Faz 1 (2024-2026, ~250K)

### Recommended: Phased (Kademeli) Approach

```
Faz 1: 2024-2026  (MVP, ~13h)
Faz 2: 2020-2023  (background, ~18h)
Faz 3: 2016-2019  (archive, ~13h)
```

Start with Faz 1, build the MVP, expand later.

## Edge Cases

- Some documents return `data: null` with `DisplayCaptcha` error — use cookie jar recovery
- 429 Too Many Requests — wait 5s then retry with fresh session
- HTML content is ~6-14KB per doc with `<br>` separators, no semantic HTML
- Text extraction via regex (`<[^>]+>`) works well
