# Full FlightList.io API Response Reference

## Top-Level Fields
```json
{
  "search_id": "uuid",         // Unique ID for this search
  "currency": "TRY",           // Currency of prices
  "fx_rate": 52.846912,        // FX rate: TRY per EUR
  "data": [...],               // Array of itinerary objects
  "_results": 5                // Total results returned
}
```

## Each Itinerary Object (data[])

```json
{
  "id": "leg1_0|leg2_0|...",        // Pipe-separated leg IDs
  "flyFrom": "ESB",                  // Origin IATA airport
  "flyTo": "STN",                    // Destination IATA airport
  "cityFrom": "Ankara",
  "cityCodeFrom": "ANK",             // City code (may differ from airport)
  "cityTo": "London",
  "cityCodeTo": "LON",
  "countryFrom": {"code": "TR", "name": "Turkey"},
  "countryTo": {"code": "GB", "name": "United Kingdom"},

  "local_departure": "2026-06-17T09:55:00.000Z",  // Outbound departure (local time, ISO8601) — Z suffix is MISLEADING, this is local time
  "utc_departure": "2026-06-17T06:55:00.000Z",     // Same in UTC
  "local_arrival": "2026-06-17T15:40:00.000Z",     // Final arrival (local time) — of LAST OUTBOUND LEG, not return arrival
  "utc_arrival": "2026-06-17T14:40:00.000Z",

  "nightsInDest": 2,            // Nights spent at destination

  "price": 10700,               // Total price in requested currency
  "conversion": {
    "EUR": 202.47,              // Price in EUR
    "TRY": 10700                // Price in TRY
  },
  "fare": {
    "adults": 10700,            // Fare breakdown by pax type
    "children": 0,
    "infants": 0
  },
  "bags_price": {
    "1": 127.65                 // Price to add 1 checked bag — ALWAYS IN EUR, regardless of curr param
  },

  "quality": 316.47,            // Internal quality score (lower = better)
  "distance": 2818.28,          // Great-circle distance in km

  "duration": {
    "departure": 27900,         // Outbound journey duration in SECONDS
    "return": 14400,            // Return journey duration in seconds
    "total": 42300              // Combined total in seconds
  },

  "airlines": ["W6", "FR", "VF"],   // All airlines involved (IATA codes)
  "availability": {"seats": 5},      // Seats available (null = unknown)
  "pnr_count": 3,                    // Number of separate bookings required
  "virtual_interlining": true,       // If true: self-transfer, NOT protected
  "has_airport_change": false,       // Whether pax must change airports mid-trip
  "technical_stops": 0,
  "throw_away_ticketing": false,
  "hidden_city_ticketing": false,

  "deep_link": "https://www.kiwi.com/deep?...",   // Direct booking URL — replace affilid before presenting
  "booking_token": "...",                          // Token for booking API (Kiwi)
  "facilitated_booking_available": false,          // Whether Kiwi handles booking directly

  "route": [...]   // Array of individual flight segments
}
```

## Each Segment in route[]

```json
{
  "id": "segment_id",
  "combination_id": "...",
  "flyFrom": "ESB",
  "flyTo": "BUD",
  "cityFrom": "Ankara",
  "cityTo": "Budapest",
  "local_departure": "2026-06-17T09:55:00.000Z",
  "utc_departure": "2026-06-17T06:55:00.000Z",
  "local_arrival": "2026-06-17T11:25:00.000Z",
  "utc_arrival": "2026-06-17T09:25:00.000Z",
  "airline": "W6",              // Operating airline IATA code
  "flight_no": 2488,            // Flight number
  "operating_carrier": "",      // Actual operator if different from ticketing airline
  "fare_basis": "VLTCLR",       // Fare basis code
  "fare_classes": "M",          // Booking class
  "return": 0,                  // 0 = outbound leg, 1 = return leg
  "bags_recheck_required": false,  // Pax must collect and re-check bags
  "vi_connection": false,          // This connection is virtual interlining
  "guarantee": false               // Kiwi guarantees rebooking if missed
}
```

## Key Gotchas (from real usage)

1. **virtual_interlining: true** + **pnr_count > 1** = self-assembled itinerary, NOT protected by airlines
2. **bags_price in EUR** — always convert via `fx_rate`: `bags_price_TRY = bags_price_EUR * fx_rate`
3. **Timestamps say Z but are local** — use `utc_*` fields for actual UTC
4. **nightsInDest** is the canonical field for stay duration — don't calculate from route times unless necessary
5. **deep_link** is a ready-to-use booking URL — just open in browser, no further API needed
