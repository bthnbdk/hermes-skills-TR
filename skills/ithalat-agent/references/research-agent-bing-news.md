# Bing News RSS — Reliable No-API-Key Web Search

Bing News RSS (`https://www.bing.com/news/search?q=KEYWORD&format=rss`) is a **reliable, zero-cost search source** for the Research Agent. No API key, no registration, no rate-limit issues (unlike DuckDuckGo which returns 202 under load).

## When to Use

- **Primary fallback** when DDG/Amazon/eBay return empty results
- **Market trend signals** — Bing News returns recent articles with dates, giving a pulse on market activity
- **UK-specific queries** — with proper locale headers, returns English results relevant to the UK market
- **Price discovery** — article titles/descriptions sometimes contain £ prices

## Implementation

```python
def search_bing_news(query, max_results=5):
    import urllib.request, urllib.parse
    import xml.etree.ElementTree as ET
    
    url = f"https://www.bing.com/news/search?q={urllib.parse.quote(query)}&format=rss"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-GB,en;q=0.9"  # CRITICAL: en-GB locale or Bing returns Turkish results
    })
    resp = urllib.request.urlopen(req, timeout=10)
    xml_data = resp.read().decode("utf-8", errors="replace")
    
    root = ET.fromstring(xml_data)
    results = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        desc = re.sub(r'<[^>]+>', '', (item.findtext("description") or ""))[:400]
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        
        if not title or len(title) < 5:
            continue
        
        results.append({
            "title": title[:120], "snippet": desc[:300],
            "url": link[:500], "source": "bing_news", "date": pub_date[:25]
        })
        if len(results) >= max_results:
            break
    
    return results
```

## Critical Notes

1. **Locale header is required** — Without `Accept-Language: en-GB,en;q=0.9`, Bing returns Turkish content from bing.com.tr. Always set this when searching for UK market data.

2. **RSS structure** — Standard RSS 2.0: `<rss>` → `<channel>` → `<item>`*. Items have `title`, `description`, `link`, `pubDate`, and a namespaced `{https://www.bing.com/...}Source` element. Use `root.iter("item")` to find items.

3. **URLs are redirects** — `link` points to `http://www.bing.com/news/apiclick.aspx?ref=FexRss&...` with the real URL encoded in query params. For display purposes the raw link works; for follow-up extraction you may need to parse the redirect URL.

4. **No price signal guarantee** — Bing News articles are editorial/news content, not product listings. Price extraction (`re.search(r'[£$€]\s*([\d,]+\.?\d*)', ...)`) may return null — this is expected, fall back to Amazon/eBay for pricing.

5. **Integration in process_task()** — Add after Etsy search, include `bing` in `all_results` and the log action:
   ```python
   all_results = amazon + ebay + etsy + bing
   # ...
   output_summary += f" Bing:{len(bing)}"
   ```

## Comparison to DuckDuckGo

| Aspect | DuckDuckGo HTML | Bing News RSS |
|--------|----------------|---------------|
| API key needed | No | No |
| Rate limits | 202 under load | Rare |
| Locale control | Limited | Full (`Accept-Language`) |
| Product listings | Yes | Rare (news only) |
| Price extraction | Yes (titles) | Occasional |
| Speed | Slower (HTML parsing) | Fast (XML parse) |
| Reliability | Medium | High |
