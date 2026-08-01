# Research Agent — Turkish Topic Extraction & Multi-Source Search

## Topic Extraction Strategy (v2)

The research agent extracts search topics from task subjects/descriptions. Priority:

1. **Subject (preferred)** — Strip `[Research Agent]` prefix, remove trailing Turkish research verbs
2. **Description (fallback)** — First sentence, strip trailing verbs
3. **Default** — `"product research"`

### Turkish Research Verb Stripping

Strip these from the end of the extracted topic:

```
araştırması, araştır, bul, bulun, fiyat araştırması, pazar araştırması, market research, analysis
```

### Turkish→English Translation Map

Used for search queries. Add to the map when new products are researched.

| Turkish | English |
|---------|---------|
| organik | organic |
| zeytinyağı / zeytinyagi | olive oil |
| bal | honey |
| kuru meyve | dried fruit |
| kuruyemiş | nuts |
| bakliyat | pulses |
| baharat | spices |
| reçel | jam |
| salça | tomato paste |
| makarna | pasta |
| erişte | noodles |
| domates | tomato |
| üzüm | grape |
| incir | fig |
| kayısı | apricot |
| pazar / pazarı / pazari | market |
| fiyat | price |
| talep | demand |

### Location Context Stripping

Before translating, remove UK location context from the search term:
- `uk`, `uk'de`, `uk'da`, `ukde`, `ukda` (any apostrophe variant)
- Leftover apostrophes from partial matches

## Multi-Source Search Pipeline

```
topic → search_ddg("topic site:amazon.co.uk")
     → search_ddg("topic site:ebay.co.uk")
     → search_ddg("topic site:etsy.com/uk")
     → Wikipedia (reliable fallback)
     → analyze_demand_signal() + generate_market_summary()
     → Opportunity Case (go/no-go score 0-100)
```

### DuckDuckGo HTML Endpoint

Uses `https://html.duckduckgo.com/html/` (POST, parameter `q`). The non-JS endpoint returns parseable HTML with `.result` elements (for `site:` queries) or flat link lists (for general queries).

**Rate limiting:** Returns status 202 (empty page) when rate-limited. Handler retries once with rotated User-Agent. If still 202, falls back to Wikipedia results.

### Market Analysis Scoring

| Signal | Points |
|--------|--------|
| 3+ listings found | 25 |
| Price between £3 and £200 | 25 |
| 2+ unique seller domains | 20 |
| Low competition (≤3 domains) | 20 |
| Medium competition (4-6 domains) | 10 |
| Wikipedia context available | 15 (fallback minimum) |

## Go/No-Go Score

- **0-30:** Limited data — needs further research
- **31-60:** Moderate opportunity — worth supplier investigation
- **61-100:** Strong signal — create Opportunity Case, route to Supplier Agent

## Opportunity Case Field Mapping

| Source Field | Opportunity Case Field |
|-------------|----------------------|
| `title` | Product name |
| Market summary | `uk_demand_signals` (Text) |
| Price range | `competitor_prices` (Text) |
| Avg price | `estimated_sales_price` (Currency) |
| Score 0-100 | `go_no_go_score` (Float) |
| Product category | `product_category` (Data) |
| Source URLs | `source_links` (Text) |
| Next step | `recommended_next_step` (Text) |
| Always | `status: "New"` |
