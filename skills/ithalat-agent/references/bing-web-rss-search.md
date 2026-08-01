# Bing Web RSS Search (no API key)

## Technique

Bing provides RSS format for BOTH web search and news search — no API key needed.

### Web Search (any query)

```
https://www.bing.com/search?q={url_encoded_query}&format=rss
```

Returns standard RSS XML with `<item>` elements containing `<title>`, `<link>`, `<description>`.

- **Link is DIRECT** (not wrapped in Bing redirect like DDG)
- **10 items per query** — reliable, consistent
- **Turkish characters** work when URL-encoded
- **Status 200** consistently (unlike DDG which returns 202 under rate limits)
- **Accept-Language** header controls result locale — use `tr-TR,tr;q=0.9` for Turkish results, `en-GB,en;q=0.9` for English

### News Search

```
https://www.bing.com/news/search?q={url_encoded_query}&format=rss
```

Same RSS format, but items include a `<pubDate>` field and the source is in a namespaced `<News:Source>` element.

### Implementation

```python
def search_bing_web(query, max_results=10):
    import urllib.request, urllib.parse, xml.etree.ElementTree as ET

    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&format=rss"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"
    })
    resp = urllib.request.urlopen(req, timeout=15)
    root = ET.fromstring(resp.read().decode("utf-8", errors="replace"))

    results = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = item.findtext("description", "").strip()
        # Items with no clean title are skipped
        if not title or len(title) < 5: continue
        results.append({"title": title[:200], "snippet": desc[:400], "url": link[:500]})
        if len(results) >= max_results: break
    return results
```

### When to use vs DDG

| Scenario | Use |
|----------|-----|
| Need Turkish-language results | Bing with `tr-TR` Accept-Language |
| DDG returning 202 (rate-limited) | Bing (rarely rate-limited) |
| Need clean direct URLs | Bing (DDG URLs wrapped in redirect) |
| Site-specific search (`site:domain.com`) | Both work, Bing more reliable |
| Need price/product listings | Amazon/eBay direct scraping (not via Bing) |
