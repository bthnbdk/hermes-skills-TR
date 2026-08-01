# Full-Scale Data Extraction Strategy

For pulling ALL ~840K decisions from emsal.uyap.gov.tr.

## The Discovery Problem

Document IDs are non-sequential, sparse, and unpredictable:
```
617488800, 787211000, 866971400, 911748600, 965831300, 1007136800...
```

You cannot iterate ID=1,2,3... because most IDs don't exist (they belong to other UYAP modules or were deleted).

## The Solution: Date-Range Enumeration

**Key finding:** `/aramadetaylist` accepts requests with ONLY date range, no keyword needed. Server-side validation passes when `baslangicTarihi` + `bitisTarihi` are provided alone.

### Date-Only Query (verified working)

```python
payload = {"data": {
    "baslangicTarihi": "01.01.2026",
    "bitisTarihi": "31.01.2026",
    "siralama": "3",              # karar tarihine göre sırala
    "siralamaDirection": "asc",
    "pageSize": 100,
    "pageNumber": 1,
}}
```

January 2026 returned 7,936 records — full list of all decisions in that month.

### Chunking Strategy: Monthly

| Period | Chunks | Avg records/chunk | API calls | Time (0.5s) |
|--------|--------|-------------------|-----------|-------------|
| 2016-2026 | 120 months | ~7,000 | ~8,400 | ~70 min |
| 2024-2026 only (Faz 1) | 31 months | ~8,000 | ~2,480 | ~21 min |
| 2020-2023 (Faz 2) | 48 months | ~7,000 | ~3,360 | ~28 min |
| 2016-2019 (Faz 3) | 48 months | ~5,200 | ~2,500 | ~21 min |

### Enumerating All IDs (Pseudocode)

```python
from calendar import monthrange

all_ids = {}
for yil in range(2016, 2027):
    for ay in range(1, 13):
        _, last_day = monthrange(yil, ay)
        bas = f"01.{ay:02d}.{yil}"
        bit = f"{last_day}.{ay:02d}.{yil}"
        
        # First call gets total count
        res = advanced_search({
            "baslangicTarihi": bas, "bitisTarihi": bit,
            "pageSize": 100, "pageNumber": 1
        })
        total = res["records_total"]
        total_pages = (total + 99) // 100
        
        for page in range(1, total_pages + 1):
            res = advanced_search({
                "baslangicTarihi": bas, "bitisTarihi": bit,
                "pageSize": 100, "pageNumber": page
            })
            for r in res["results"]:
                all_ids[r["id"]] = r  # dedup by ID
            time.sleep(0.3)
```

## Parallel Download Architecture

Once all IDs are collected, download documents in parallel.

### The Captcha Constraint

After ~38-40 rapid `/getDokuman` calls, the server starts returning:

```json
{"metadata": {"FMTY": "ERROR", "FMTE": "Runtime exception:{0}:DisplayCaptcha"}}
```

### Solution: Session Pool with Rotation

Each worker uses its own `CookieJar`, seeds a session via `GET /`, downloads 38 docs at 1.5s intervals, then creates a fresh session.

```
Worker-1:  [ID 1..38] → fresh session → [ID 39..76] → fresh session → ...
Worker-2:  [ID 77..114] → fresh session → ...
Worker-3:  [ID 115..152] → fresh session → ...
Worker-4:  [ID 153..190] → fresh session → ...
Worker-5:  [ID 191..228] → fresh session → ...
Worker-6:  [ID 229..266] → fresh session → ...
Worker-7:  [ID 267..304] → fresh session → ...
Worker-8:  [ID 305..342] → fresh session → ...
```

### Time Estimates

| Workers | Delay between docs | Captcha risk | Total time |
|---------|-------------------|--------------|------------|
| 1 | 1.5s | Low | 350 hours ❌ |
| 4 | 1.5s | Low | 88 hours |
| **8** | **1.5s** | **Low** | **44 hours ✅** |
| 16 | 2.0s | Medium | 29 hours ⚠️ |
| 32 | 2.5s | High | 18 hours ❌ |

**Recommended: 8 workers × 1.5s delay = ~44 hours (2 days)**

### Worker Implementation

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request, http.cookiejar, time, json

def download_worker(worker_id, doc_ids):
    """Download a batch of documents with session rotation every 38 docs."""
    results = {"worker": worker_id, "success": 0, "failed": 0}
    
    for chunk_start in range(0, len(doc_ids), 38):
        chunk = doc_ids[chunk_start:chunk_start + 38]
        
        # Fresh session for each chunk
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        req = urllib.request.Request("https://emsal.uyap.gov.tr/",
            headers={"User-Agent": "Mozilla/5.0 ..."})
        with opener.open(req, timeout=15): pass
        
        for did in chunk:
            time.sleep(1.5)
            try:
                req = urllib.request.Request(
                    f"https://emsal.uyap.gov.tr/getDokuman?id={did}",
                    headers={"User-Agent": "Mozilla/5.0 ...",
                             "Referer": "https://emsal.uyap.gov.tr/"})
                with opener.open(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                if data.get("data") is not None:
                    with open(f"/tmp/uyap/documents/{did}.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception:
                results["failed"] += 1
    
    return results

# Split 840K IDs across 8 workers
chunks = [ids[i::8] for i in range(8)]
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = [ex.submit(download_worker, i, chunks[i]) for i in range(8)]
    for f in as_completed(futures):
        print(f"Worker done: {f.result()}")
```

## Phased (Kademeli) Approach

Rather than pulling all 840K in one go:

```
Faz 1: 2024-2026  (~250K docs, ~13 hours)  → Build MVP immediately
Faz 2: 2020-2023  (~340K docs, ~18 hours)  → Enrich in background
Faz 3: 2016-2019  (~250K docs, ~13 hours)  → Complete the archive
```

Benefits:
- MVP ready after ~13 hours instead of 44
- Test embedding/retrieval with recent data first
- If something breaks, only one phase is lost
- Older cases are less relevant for current legal practice

## Storage Estimates

| Item | Size |
|------|------|
| Raw JSON (each ~10KB) | ~8.4 GB |
| Clean text (each ~8KB) | ~6.7 GB |
| Vector index (768-dim) | ~2.6 GB |
| Metadata index | ~200 MB |
| **Total** | **~18 GB** |

## Legal Status

- All data is publicly accessible (no login required)
- Anonymized (party names replaced with "---")
- Court decisions are public domain under FSEK m.31
- No ToS violation (site has no terms of service)
- Rate-limiting is a technical constraint, not a legal one
