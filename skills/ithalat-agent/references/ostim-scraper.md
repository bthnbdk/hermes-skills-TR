# OSTİM Firm Directory Scraper

## Source

**Site:** https://www.ostim.org.tr
**API:** https://ostim.org.tr/api/search/index?q={char}&page=1&pageSize=100
**Detail page:** https://www.ostim.org.tr/firmalar/{slug} (NOT `/firma/{slug}`)

## API Discovery Summary

The old scraper (v1) used HTML parsing on `/firmalar?page=1..7` and found ~42 firms.
The new scraper (v2) uses the hidden JSON API and **333 companies** were discovered.

**Key API findings:**
- `type=1` = companies, `type=2` = products — always filter `type == 1`
- `pageSize=100` max — backend caps at 100 results regardless of what you request
- Character-by-character enumeration (a-z + 0-9) catches ALL companies because every company name starts with a letter or digit
- Deduplication by `slug` handles overlaps between character queries
- Detail page URL is `/firmalar/{slug}`, not `/firma/{slug}` (old pattern was wrong)
- Rate limit: 0.3s between requests; 333 firms scanned in ~200 seconds

## Structure

### /firmalar listing page
- Each entry: `a[href*='/firmalar/']` with combined text: `"Firma Adi312phoneemail@example.com"`
- Extract phone via regex: `r'(?:\+90|0)\s*\d{2,3}\s*\d{3}\s*\d{2}\s*\d{2}'`
- Extract email via regex: `r'[\w.+-]+@[\w-]+\.[\w.-]+'`
- Firm name = text before first phone/email match

### /firmalar/{slug} detail page
- **Website**: text-wide regex for `https?://...`
- **Sectors** (Sektörler): find element containing "sektör" text, read parent's list items
- **Products** (Ürünler): find element containing "ürün" text, read sibling LI elements
- **Description**: first `<p>` with text > 50 chars
- **Contact**: full address text, phone numbers, emails scattered through page

## ERPNext Field Mapping

| OSTİM scrape field | Supplier Research field | Notes |
|---|---|---|
| company name | `supplier_name` | Max 140 chars |
| "Ankara" (hardcoded) | `city` | |
| website URL | `website` | Max 200 chars |
| email | `contact_email` | NOT `email` — that field doesn't exist |
| phone | `phone` | Max 30 chars |
| sectors | `product_category` | Join first 3 with "; " |
| description + products | `notes` | Free-text, max 500 chars |
| — | `verification_status` | Always `"Unverified"` for fresh scrapes |

## Deduplication

- Query all existing Supplier Research records with `fields=["supplier_name", "website"]`
- Check `name_lower in existing_names` and `website_lower in existing_urls`
- No `source` filter available (field doesn't exist in DocType)

## Downstream Chain

Each newly discovered firm creates:
1. Supplier Research record ✅
2. [Research Agent] task per sector (max 2) → UK market analysis
3. [CRM Agent] task → Customer/Contact registration

## Script

`ithalat_ostim_scraper.py` at `~/.hermes/scripts/`
Runs daily at 02:00, max 5 firms per tick. Produces JSON output with `discovered` count.

## Pitfalls

### `html` module name shadowing

When you `import html` for `html.unescape()` AND also store the downloaded HTML in a variable called `html`, the module is overwritten:

```python
import html
# ...
html = download_page()  # ❌ Overwrites the html module
name = html.unescape(raw)  # ❌ AttributeError: 'str' object has no attribute 'unescape'
```

Fix: always name the page-content variable `raw_html` or `page_html`, never `html`.

### Detail page URL is `/firmalar/{slug}`, not `/firma/{slug}`

```python
# ✅ Correct
FIRM_DETAIL_URL = "https://www.ostim.org.tr/firmalar"
resp = get(f"{FIRM_DETAIL_URL}/{slug}")

# ❌ Wrong — returns 404
resp = get(f"https://www.ostim.org.tr/firma/{slug}")
```

### Search API returns products AND companies

The `/api/search/index` endpoint returns mixed results:
- `type=1` = companies (what we want)
- `type=2` = products (no detail page, no contact info)

Always filter: `if item.get("type") == 1: ...`

### Contact info extraction from detail page

The `/firmalar/{slug}` page layout is unstructured HTML. Reliable extraction patterns:

- **Phone**: Search raw HTML for Turkish phone patterns:
  ```python
  r'(?:\+90|0)\s*5\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'  # mobile
  r'(?:\+90|0)\s*[23489]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'  # landline
  ```
- **Email**: `r'[\w.+-]+@[\w-]+\.[\w.-]+'` — first match is usually the correct one
- **Website**: Look for `href="https://...` near "web" or "site" labels. Avoid ostim.org.tr and facebook.com/instagram.com self-links.
- **Sectors/Products**: Regex search for `[Ss]ekt[oö]r` and `[ÜÜ]r[üu]n` nearby text. Fallback: sector keyword detection from company name.

The company name is best extracted from the `<title>` tag (contains `| OSTİM` suffix).

### HTML entity decoding

Company names from the search API may contain HTML entities (e.g. `&#xFC;` for ü). Always decode with `html.unescape()` after extraction — but see the shadowing pitfall above.
