# Web Görselleştirme Arayüzü — Referans

## Architecture

```
cankaya_server.py  (HTTP server, Python stdlib)
  ├── / → cankaya_harita.html (Leaflet.js + Chart.js frontend)
  ├── /api/stats              → SQLite aggregate
  ├── /api/neighborhoods      → GROUP BY neighborhood (with distance_km)
  ├── /api/listings/all       → all listings (client-side filter/sort)
  ├── /api/trend              → daily avg price from price_history
  └── /api/bargains           → listings with price drops (joined: price_history × listings)
```

Built with Python stdlib — no Flask, no npm. Chart.js v4 + Leaflet v1.9 from CDN. Single-threaded, fine for single-user local use on port 8200.

## Server (`cankaya_server.py`)

### Key Implementation Details

**Haversine distance** for work-to-listing distance:
```python
WORK_LAT, WORK_LON = 39.8897782, 32.8594033  # referans noktası (örnek: iş yeri, Çankaya)
```

### SQLite Queries

**Trend (daily price aggregation):**
```sql
SELECT DATE(ph.seen_at) as day,
       ROUND(AVG(ph.price),0) as avg_price,
       COUNT(DISTINCT ph.listing_id) as listings_count,
       ROUND(AVG(ph.price / NULLIF(l.gross_sqm, 0)), 0) as avg_ppm
FROM price_history ph
JOIN listings l ON l.id = ph.listing_id
GROUP BY DATE(ph.seen_at)
ORDER BY day
```

**Bargains (price drops):**
```sql
SELECT ph.listing_id as id, l.neighborhood, l.room, l.price as current_price,
       l.gross_sqm, l.score, l.map_lat, l.map_lon, l.detail_url,
       MIN(ph.price) as lowest_price, MAX(ph.price) as highest_price,
       MIN(ph.seen_at) as first_seen, MAX(ph.seen_at) as last_seen,
       COUNT(ph.id) as price_changes
FROM price_history ph
JOIN listings l ON l.id = ph.listing_id
GROUP BY ph.listing_id
HAVING lowest_price < highest_price AND l.price <= highest_price * 0.97
ORDER BY (highest_price - l.price) DESC
LIMIT 50
```
Note: price_history has columns (id, listing_id, seen_at, price, lowest_price). No gross_sqm — need JOIN.

### Route Handling
Custom `SimpleHTTPRequestHandler` subclass:
- Uses a dict-based dispatch (cleaner than if/elif chain)
- `path == '' or path == '/'` → serve HTML (critical: rstrip('/') on `/` gives `''`)
- `/api/*` → JSON responses
- All other paths → `super().do_GET()`

### JSON Serialization
```python
json.dumps(data, default=str, ensure_ascii=False)
```
The `default=str` handles datetime and other non-serializable types from SQLite.

## Frontend (`cankaya_harita.html`)

### CDN Dependencies
```html
<!-- Map -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<!-- Charts -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.2.0/dist/chartjs-plugin-zoom.min.js"></script>
```

### Map Setup
```javascript
const map = L.map('map', {center: [WORK.lat, WORK.lng], zoom: 13});
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 18, attribution: 'Tiles © Esri'
}).addTo(map);
```

Always use Esri World Topo Map (terrain), not default OSM. Kullanıcı sade, doğal görünüm tercih eder.

### Color Scale (price per m²)
```javascript
function ppmColor(p) {
  if (!p || p < 40000) return '#2e7d32';    // green
  if (p < 50000) return '#689f38';           // light green
  if (p < 60000) return '#f57c00';           // orange
  if (p < 70000) return '#d32f2f';           // red
  return '#b71c1c';                          // dark red
}
```

### Circle Size (by listing count)
```javascript
function rFromCnt(c) { return Math.max(8, Math.min(32, c * 0.35)); }
```
No text labels on circles. Hover tooltip only. Karmaşa yaratma.

### Format Helpers
```javascript
function fmtP(p) { return p ? Number(p).toLocaleString('tr-TR') + ' TL' : '—'; }
function fmtS(p) { return p ? (p/1e6).toFixed(1) + 'M' : '—'; }
function fmtKm(d) { return d ? d.toFixed(1) + 'km' : '—'; }
```

### Four Tab System

**Tab 1 — Mahalleler:** Aggregate neighborhood view. Colored circles on map (color=ppm, size=count). Sidebar list with price, sqm, count, score, distance, score bar. Click → zoom + popup.

**Tab 2 — İlanlar:** Individual listing browser. Sort dropdown (score, price↑↓, distance, sqm, age). Room chip filters (1+1, 2+1, 3+1, 4+1 — multiple selectable). Search by neighborhood/room/price. First 60 results shown as small markers on map. Click → zoom to listing + popup with hepsiemlak link.

**Tab 3 — Piyasa:** Three analysis panels:
1. **Trend Chart** (line): daily avg price (M TL) + avg m² price (bin TL) over time. Uses Chart.js with zoom plugin (pan, wheel zoom, drag zoom on x-axis).
2. **Scatter Plot**: price vs distance — each point is a neighborhood. Size = listings count, color = m² price. Hover shows: neighborhood, price, distance, sqm, ppm, count, score. Zoom enabled.
3. **Comparison Table**: all neighborhoods sortable by any column (click header). Best values highlighted green. Columns: neighborhood, count, avg price, m² price, sqm, score, distance, age.

**Tab 4 — Fırsatlar:** Bargain hunter. Lists listings from `/api/bargains` where price dropped. Each item shows: green drop badge (%↓), drop amount, old price, sqm, distance, score, hepsiemlak link. Green circles on map (larger radius=6). Click → popup with drop details.

### Chart Configuration (Chart.js v4)

**Trend chart:** Two datasets (price + ppm) on same y-axis, line+fill, tension=0.3, pointRadius=2. Zoom plugin: pan and drag-to-zoom on x-axis enabled.

**Scatter chart:** Single dataset with `pointRadius` varying by count. No legend. Custom tooltip shows neighborhood details. Zoom: pan+drag on xy.

### Key Design Patterns

1. **All data loaded once** — `loadData()` fetches neighborhoods, all listings, trend, bargains, and stats in parallel via `Promise.all`. Filtering/sorting is instant client-side.
2. **Tab switching** — on switch: clear listing markers, re-render map circles (for mahalle/ilan tabs), or clear all map layers (for piyasa/fırsat tabs).
3. **Map layer management** — two persistent layer groups: `circleGroup` (neighborhood circles) and `listingMarkers` (individual listing dots). Cleared and rebuilt on tab switch.
4. **No cluster labels** — removed in v2. Iteration: v1 had text labels → kullanıcı "çok karışık" dedi → simplified to circles-only with hover tooltips.
5. **Room filter as chips** — `.room-chip` elements with `.active` toggle. Maintains `activeRooms` Set. All active by default.

## Weekly Report (`scripts/haftalik_piyasa_raporu.py`)

A scheduled job that runs every Monday 09:00. Fetches all 5 APIs and compiles a notification-formatted market report. Works with any scheduler (system cron, Hermes, CI).

**Content:**
- Summary stats (total listings, neighborhoods, avg/min/max price, sqm, score)
- Price trend (21-day change with direction arrow 📈📉)
- Cheapest & most expensive neighborhoods by m²
- Most active neighborhoods (by listing count)
- Top 5 bargains (biggest price drops)
- Best value neighborhoods (score / (ppm × distance) heuristic)

**Scheduling:**
```bash
# System cron:
0 9 * * 1 cd <calisma_dizini> && python3 haftalik_piyasa_raporu.py

# Hermes:
cronjob(action='create', name='Haftalık {SEHIR} Konut Raporu',
        script='haftalik_piyasa_raporu.py', no_agent=True,
        schedule='0 9 * * 1', deliver='<KANAL>',
        workdir='<WORKDIR>')
```

## Server Management

```bash
# Start (background)
cd <calisma_dizini> && nohup python3 sehir_server.py &

# Stop
pkill -f sehir_server.py

# Or find PID on port
lsof -ti:8200 | xargs kill -9
```

⚠️ When restarting after code changes: always `fuser -k 8200/tcp` first to ensure old process is gone. The background `&` + `pkill` pattern sometimes misses the old PID.

## Files

| File | Path | Purpose |
|------|------|---------|
| Server | `<calisma_dizini>/sehir_server.py` | HTTP server, all API endpoints |
| Frontend | `<calisma_dizini>/sehir_harita.html` | Leaflet + Chart.js UI (4 tabs) |
| Report script | `<calisma_dizini>/haftalik_piyasa_raporu.py` | Weekly market report |
| Database | `<calisma_dizini>/hepsiemlak.db` | listings, price_history, scan_log |
