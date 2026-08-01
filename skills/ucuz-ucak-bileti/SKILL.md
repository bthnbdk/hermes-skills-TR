---
name: ucuz-ucak-bileti
description: "Search cheap flight deals via FlightList.io (Kiwi.com proxy API). Query ANY Turkish airport (IST, SAW, ESB, ADB, AYT, DLM...) with full URL params and JSON response structure documented. City/airport codes for all 81 provinces in references/turkiye-havalimanlari.md."
version: 3.0.0
author: BatuBOT
---

# Ucuz Uçak Bileti (FlightList.io / Kiwi API) — Tüm Türkiye

Search flight deals using the FlightList.io API — a proxy over Kiwi.com's Tequila API. Returns clean JSON with pricing, routes, airlines, and durations. **Türkiye'deki herhangi bir havalimanından çıkış desteklenir** — `fly_from`'a kendi şehrinizin IATA kodunu verin (tam liste: `references/turkiye-havalimanlari.md`).

## Endpoint

```
GET https://www.flightlist.io/api/search.php
```

## URL Parameters

### Origin & Destination

| Param | Example | Meaning |
|-------|---------|---------|
| `fly_from` | `airport:ESB` | Origin — prefix with `airport:` for IATA code, or `city:` for city code. **Türkiye için:** `airport:IST`, `airport:SAW`, `airport:ESB`, `airport:ADB`, `airport:AYT`... (tam liste: `references/turkiye-havalimanlari.md`) |
| `fly_to` | `city:LON` | Destination — same prefix logic. Also accepts comma-separated ISO country codes (e.g. `AT,BE,BG,...`) for area searches |

### Outbound Date Range (when the outbound flight can depart)

| Param | Example | Meaning |
|-------|---------|---------|
| `date_from` | `19/05/2026` | Earliest outbound departure date (DD/MM/YYYY) |
| `date_to` | `17/06/2026` | Latest outbound departure date |

### Return Date Range (when the return flight can depart)

| Param | Example | Meaning |
|-------|---------|---------|
| `return_from` | `18/06/2026` | Earliest return departure date |
| `return_to` | `17/07/2026` | Latest return departure date |

### Stay Duration

| Param | Example | Meaning |
|-------|---------|---------|
| `nights_in_dst_from` | `2` | Minimum nights at destination |
| `nights_in_dst_to` | `2` | Maximum nights (set both equal to fix exact duration) |

### Passengers

| Param | Example | Meaning |
|-------|---------|---------|
| `adults` | `1` | Number of adult passengers |
| `children` | `0` | Number of children |
| `infants` | `0` | Number of infants |

### Cabin & Baggage

| Param | Example | Meaning |
|-------|---------|---------|
| `selected_cabins` | `M` | Cabin class: M=Economy, W=Premium Economy, C=Business, F=First |
| `adult_hand_bag` | `0` | Number of carry-on bags per adult |
| `adult_hold_bag` | `0` | Number of checked bags per adult |

### Filters

| Param | Example | Meaning |
|-------|---------|---------|
| `price_to` | *(empty)* | Max price cap; leave empty for no limit |
| `max_stopovers` | `10` | Max number of stopovers per leg |
| `max_fly_duration` | `60` | Max total flight duration in hours |
| `stopover_from` | `00:00` | Min stopover duration (HH:MM) |
| `stopover_to` | `48:00` | Max stopover duration |
| `dtime_from` | `00:00` | Earliest departure time of day |
| `dtime_to` | `23:59` | Latest departure time of day |
| `enable_vi` | `true` | Enable virtual interlining (self-transfer combos across airlines) |
| `ret_from_diff_city` | `false` | Allow return from a different city than arrival |
| `ret_to_diff_city` | `false` | Allow return to a different city than departure |

### Result Control

| Param | Example | Meaning |
|-------|---------|---------|
| `flight_type` | `return` | `return` for round-trip, `oneway` for one-way |
| `curr` | `TRY` | Currency code for prices (ISO 4217) |
| `limit` | `5` | Number of results to return |
| `sort` | `price` | Sort order: `price`, `quality`, `duration` |

## JSON Response Structure

```json
{
  "search_id": "uuid",
  "currency": "TRY",
  "fx_rate": 52.84,
  "data": [
    {
      "id": "flight_id_0",
      "flyFrom": "ESB",
      "flyTo": "STN",
      "cityFrom": "Ankara",
      "cityCodeFrom": "ANK",
      "cityTo": "London",
      "cityCodeTo": "LON",
      "countryFrom": { "code": "TR", "name": "Turkey" },
      "countryTo": { "code": "GB", "name": "United Kingdom" },
      "local_departure": "2026-07-10T08:25:00.000Z",
      "local_arrival": "2026-07-10T10:50:00.000Z",
      "price": 10401,
      "conversion": { "EUR": 196.84, "TRY": 10401 },
      "duration": { "departure": 15900, "return": 0, "total": 15900 },
      "quality": 119.89,
      "distance": 2818.28,
      "airlines": ["VF"],
      "bags_price": { "1": 42.5 },
      "baglimit": { "hand_weight": 8, "hold_weight": 20 },
      "route": [
        {
          "flyFrom": "ESB",
          "flyTo": "STN",
          "cityFrom": "Ankara",
          "cityTo": "London",
          "local_departure": "2026-07-10T08:25:00.000Z",
          "local_arrival": "2026-07-10T10:50:00.000Z",
          "airline": "VF",
          "flight_no": 531,
          "return": 0,
          "vehicle_type": "aircraft"
        },
        {
          "flyFrom": "STN",
          "flyTo": "ESB",
          "local_departure": "2026-08-30T16:35:00.000Z",
          "local_arrival": "2026-08-30T22:35:00.000Z",
          "airline": "VF",
          "flight_no": 532,
          "return": 1,
          "vehicle_type": "aircraft"
        }
      ],
      "booking_token": "long_token_string",
      "deep_link": "https://www.kiwi.com/deep?affilid=flightlistflightlistio&..."
    }
  ]
}
```

## Key Fields & Calculations

| Field | Description |
|-------|-------------|
| `price` | Total price in requested currency |
| `duration.total` | Total flying time in **seconds** (÷3600 for hours) |
| `local_departure` | Departure time of **first leg** of entire trip |
| `local_arrival` | Arrival time of **last outbound leg** (NOT the return!) |
| `nightsInDest` | Nights spent at destination (direct from API) |
| `duration.departure` | Outbound journey duration in **seconds** |
| `duration.return` | Return journey duration in **seconds** |
| `virtual_interlining` | `true` = self-transfer, NOT protected (higher risk) |
| `pnr_count` | Number of separate bookings required |
| `has_airport_change` | Whether you must switch airports mid-trip |

### Calculating Stay Duration (Nights at Destination)

**Use `nightsInDest` directly** from the API — no need to calculate from route times.

If you do need to calculate manually:
1. Find the **last outbound leg** — last `route[]` item where `return=0`
2. Find the **first return leg** — first `route[]` item where `return=1`
3. **Stay = first_return_leg.local_departure − last_outbound_leg.local_arrival** (in days)

### Route Array Structure

```
route[0]: return=0 → first outbound leg
route[1]: return=0 → second outbound leg (if 1 stop)
...
route[n]: return=1 → first return leg
route[n+1]: return=1 → second return leg (if 1 stop on return)
```

The `return` field in each route item tells you which direction it belongs to.

## Key Fields

- **`airlines[]`** — Airline IATA codes: `VF`=AJet, `TK`=Turkish Airlines, `W6`=Wizz Air, `PC`=Pegasus
- **`deep_link`** — URL to book on Kiwi.com. **Always replace affiliate param**: change `affilid=flightlistflightlistio` to `affilid=batuhanbudakkk` before presenting. Use regex: `affilid=flightlistflightlistio` → `affilid=batuhanbudakkk`
- **`booking_token`** — Token for booking via Kiwi API
- **`route[].return`** — `0` for outbound, `1` for return leg

## 🚨 Critical Gotchas

1. **Virtual Interlining** (`virtual_interlining: true`) — Self-assembled itineraries combining multiple airline tickets. Cheaper but riskier: missed connections are NOT protected by airlines. `pnr_count > 1` means multiple separate tickets.

2. **Bag Recheck** (`bags_recheck_required: true`) — Passenger must collect luggage and re-check at that layover. Always surface this to the user.

3. **Duration in Seconds** — Divide by 3600 for hours: `27900s = 7h 45m`.

4. **bags_price is in EUR** (NOT the requested currency!). Use `fx_rate` to convert: `bags_price_TRY = bags_price_EUR × fx_rate`.

5. **Timestamps: Z suffix is MISLEADING** — `local_departure` / `local_arrival` end in `Z` but are actually local time. Use `utc_*` for true UTC. Display local times with their timezone context.

6. **City vs Airport Codes** — `cityCodeFrom/To` (e.g. `LON`, `ANK`) are metro areas. `flyFrom/flyTo` (e.g. `LHR`, `STN`, `ESB`) are specific airports.

7. **deep_link is a Ready-to-Use Booking URL** — Just open in browser. No further API calls needed.

8. **max_fly_duration silently kills results on long-haul** — A `max_fly_duration=60` (60 hours) can return 0 results even when valid flights exist. Reason: on routes with 3 stopovers, a single one-way can already take 27-34 hours, and a round trip easily exceeds 60h total. For intercontinental routes with 2–3 stopovers, either omit `max_fly_duration` entirely or set it to `120`+. The API returns `_results: 0` with no error message, making this easy to misdiagnose as "no flights available."

9. **Return search (`flight_type=return`) fails for complex VI routes** — When searching routes that require virtual interlining (3+ separate tickets) in BOTH directions, the combined return search may return 0 results even though both one-way directions have plenty of options individually. This is a Kiwi API limitation, not a genuine "no flights" signal. The workaround: search two one-way legs separately and combine manually (see "Return Search Failure Workaround" below).

## Important Search Patterns

### For Multi-Night Stays (Return Flights)

Set **non-overlapping** date ranges to ensure proper stay:
- `date_from` / `date_to` — when you depart
- `return_from` / `return_to` — when you return (should be ≥2 days after `date_from`)
- `nights_in_dst_from` / `nights_in_dst_to` — set both to same value for exact stay

### For "Anywhere" or Area Searches

Use comma-separated ISO country codes in `fly_to`:
```
fly_to=AT,BE,BG,...  (Schengen zone)
fly_to=AF,AL,DZ,...  (all countries — "anywhere")
```

Exclude countries by removing their codes from the list.

### For Price Monitoring (Cron Jobs)

Use `limit=5` to minimize API calls and token burn. Monitor one-way or return prices and alert when below user's threshold.

See `templates/cron-job-prompt.md` for reusable prompt template. Key rules:
- Always set `deliver="telegram:-1003839224584"` for Batu's notification channel
- Schedule format: `3d` (every 3 days) or `7d` (weekly)
- Use the compact emoji format in "Presentation Format for Notifications" section
- **No URLs anywhere** — no markdown links, no bare URLs. They trigger Telegram link previews.

### Return Search Failure Workaround (Complex VI Routes)

When `flight_type=return` returns 0 results but individual one-way searches work, the Kiwi API may be failing due to route complexity (virtual interlining in both directions, 3+ stopovers, obscure city pairs like Ankara→Guatemala City). Workaround:

1. **Search two one-way legs separately** with `flight_type=oneway`:
   - Outbound: `fly_from=airport:{FROM}&fly_to=airport:{TO}&date_from=...&date_to=...`
   - Return: `fly_from=airport:{TO}&fly_to=airport:{FROM}&date_from=...&date_to=...`
2. **Parse both JSON responses**, build arrays of outbound/inbound flights with arrival/departure datetimes
3. **Combine manually**: iterate every outbound × inbound pair, compute `stay_nights = (inbound_departure - outbound_arrival).days`, filter by desired range
4. **Sum prices** for total round-trip cost
5. **⚠️ Important**: Since these are separate searches, deep_links for outbound and return are independent — present both links to the user so they can book each leg via Kiwi separately
6. **⚠️ Risk**: Each direction is its own booking (3 PNRs outbound + 3 PNRs inbound = up to 6 separate tickets). Missed connections anywhere in the chain are completely unprotected.

## 📦 GitHub Yedekleme

Bu skill GitHub'da yedeklenir:
- TR koleksiyonu: https://github.com/bthnbdk/hermes-skills-TR
- Ana koleksiyon: https://github.com/bthnbdk/hermes-skills

Güncelleme için:
```bash
cd ~/hermes-skills
cp -r ~/.hermes/skills/travel/ucuz-ucak-bileti/* skills/travel/ucuz-ucak-bileti/
git add -A && git commit -m "update ucuz-ucak-bileti" && git push
```

## Preset Country Lists

Full JSON schema reference: see `references/full-api-response-reference.md`
Region presets: saved in `references/region-presets.csv`. Key presets:

| Preset Name | Region |
|-------------|--------|
| `schengen` | Schengen Area (29 countries) |
| `europe` | Wider Europe |
| `scandinavia` | DK, FI, IS, NO, SE |
| `balkans` | AL, BA, BG, HR, ME, MK, RS, SI, XK |
| `north-america` | CA, MX, US |
| `latin-america` | MX + Central + South America + Caribbean |
| `south-america` | AR, BO, BR, CL, CO, EC, etc. |
| `north-africa` | DZ, EG, LY, MA, SD, TN |
| `middle-east` | AE, BH, EG, IQ, IR, JO, etc. |
| `south-asia` | AF, BD, BT, IN, LK, MV, NP, PK |
| `southeast-asia` | BN, ID, KH, LA, MM, MY, PH, SG, TH, TL, VN |
| `east-asia` | CN, HK, JP, KR, MN, TW |
| `cheap-from-tr` | AT, DE, HU, GB, RO, NL, PL, IT, BG (Türkiye'den ucuz rotalar örneği) |
| `anywhere` | All 195 countries |

## Türkiye Havalimanları

Tüm Türkiye havalimanları IATA kodları ve şehir kodları: `references/turkiye-havalimanlari.md`

Popüler çıkış noktaları:
- **İstanbul:** `airport:IST` (ana hub) veya `airport:SAW` (Sabiha Gökçen) veya `city:IST` (ikisi birden)
- **Ankara:** `airport:ESB`
- **İzmir:** `airport:ADB`
- **Antalya:** `airport:AYT` veya `city:AYT` (AYT + GZP)
- **Muğla:** `airport:DLM` (Dalaman) veya `airport:BJV` (Bodrum)
- **Trabzon:** `airport:TZX`

## Known Cheap Destinations from Turkey (Örnek — Ankara Çıkışlı Tek Yön)

| # | Destination | Price | Direct | Airline |
|---|------------|------:|:------:|:-------:|
| 1 | Budapest 🇭🇺 | 1,536 ₺ | ✅ | Wizz Air |
| 2 | Bucharest 🇷🇴 | 3,196 ₺ | ✅ | AJet |
| 3 | Tirana 🇦🇱 | 3,196 ₺ | ✅ | AJet |
| 4–15 | Various European cities | 3,650–5,332 ₺ | ✅ | AJet/Pegasus/SunExpress |

> 💡 Bu liste örnektir — çıkış havalimanına göre değişir. İstanbul (IST/SAW) ve İzmir (ADB) çıkışlı rotalar genelde daha fazla ve daha ucuz seçenek sunar. Kendi şehriniz için her zaman canlı arama yapın.

## Steps to Search

1. Construct URL with desired params (`fly_from`, `fly_to`, dates, `flight_type`, `limit`, `sort`)
2. `curl -s "https://www.flightlist.io/api/search.php?..."` → save to JSON file
3. Parse JSON, iterate `data[]`
4. **If `_results: 0`**: check if `max_fly_duration` is set too low for long-haul routes, or try `flight_type=oneway` separately for each direction (see "Return Search Failure Workaround" above)
5. For return flights: calculate actual stay from route array (last `return=0` leg arrival → first `return=1` leg departure)
6. Replace `affilid=flightlistflightlistio` with `affilid=batuhanbudakkk` in all deep_links
7. Present sorted by price (cheapest first) with clickable links

## Presentation Format for Notifications

When sending flight deal notifications to Batu's channel, use this exact format. **No intro text, no outro text, no warnings, no commentary** — just the raw flight data. **NO bare URLs, NO markdown links** — they trigger Telegram link previews that break the layout.

**Exact format (copy this verbatim):**
```
✈️ {cityFrom} → {cityTo}
  |  {dep_day} {dep_date} – {ret_day} {ret_date}  |  {nights} nights
—————
1️⃣  {price:,d} ₺  (~€{eur_price:,.0f})
📅 Out: {day} {date} {time} · {duration}h · {stops_label}
📅 Ret: {day} {date} {time} · {stops_label}
🏷️ {airlines}  {⚠️ VI}
—————
2️⃣  ...
```

**Rules:**
- NO intro/outro text or warnings of any kind
- NO URLs, NO `[Book →](url)` markdown links — removed entirely
- Only show `⚠️ VI` if `virtual_interlining` is true (preceded by `  |  `)
- Header line break: `✈️ {cityFrom} → {cityTo}` on its own line, then `  |  ...` on the next line (indented 2 spaces)
- Separator: `—————` (5 em-dashes, cleaner than box drawing chars)
- Price line: `N️⃣  {price:,d} ₺  (~€{eur_price:,.0f})`
- Outbound: `📅 Out: {day} {date} {time} · {duration}h · {stops_label}`
- Return: `📅 Ret: {day} {date} {time} · {stops_label}`
- `direct` for 0 stops, `N stops` otherwise
- Duration in hours: `duration.departure / 3600`
- EUR price: `conversion.EUR` (use `fx_rate` as fallback)
- Only top 5 results
- If no results: nothing at all — silently skip
