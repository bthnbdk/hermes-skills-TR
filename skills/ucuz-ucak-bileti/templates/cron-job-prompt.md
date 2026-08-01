# Cron Job Prompt Template for Flight Monitoring

Use this template when the user asks to monitor a new route.
Deliver all results to the user's notification channel (örn. telegram:-1003839224584 @bildirimbb).
Always set deliver="telegram:-1003839224584" (veya kullanıcının kendi kanalı).

## Generic Template

Name: "{cityFrom}-{cityTo} Flight Monitor"
Schedule: "7d" (weekly) or "3d" (every 3 days)
Repeat: forever
Skills: ["ucuz-ucak-bileti"]
Deliver: "telegram:-1003839224584"

## Prompt Template

Search for cheap return flights from {cityFrom} ({airportFrom}) to {cityTo} ({airportTo}) for {date_range}.

Requirements: {requirements}

URL: https://www.flightlist.io/api/search.php?fly_from=airport%3A{airportFrom}&fly_to={destinationParam}&date_from={dd}%2F{mm}%2F{yyyy}&date_to={dd}%2F{mm}%2F{yyyy}&return_from={dd}%2F{mm}%2F{yyyy}&return_to={dd}%2F{mm}%2F{yyyy}&nights_in_dst_from={min}&nights_in_dst_to={max}&adults=1&selected_cabins=M&curr=TRY&limit=10&sort=price&max_stopovers={stops}&max_fly_duration={duration}&enable_vi=true&flight_type=return&adult_hand_bag=0&adult_hold_bag=0

Fetch JSON, filter for nightsInDest range. Replace affilid=flightlistflightlistio with affilid=batuhanbudakkk. Convert EUR using fx_rate.

Output format (NO URLs anywhere — no bare URLs, no markdown links):

✈️ {cityFrom} → {cityTo}
  |  {dep_day} {dep_date} – {ret_day} {ret_date}  |  {nights} nights
—————
1️⃣  {price:,d} ₺  (~€{eur})
📅 Out: {dep_day} {dep_date} {dep_time} · {duration}h · {stops_label}
📅 Ret: {ret_day} {ret_date} {ret_time} · {stops_label}
🏷️ {airlines}  |  ⚠️ VI
—————

Only top 5. If no results: output nothing at all (silent skip).

## Türkiye Çıkış Havalimanları

Çıkış noktası seçerken: `references/turkiye-havalimanlari.md` dosyasındaki IATA kodlarını kullanın.
- İstanbul: airport:IST veya airport:SAW veya city:IST (ikisi birden)
- Ankara: airport:ESB · İzmir: airport:ADB · Antalya: airport:AYT (veya city:AYT)
- Muğla: airport:DLM veya airport:BJV · Trabzon: airport:TZX

## Common Configurations

### ESB → London (Direct, 2+ nights, Jul-Oct)
- max_stopovers=0
- nights_in_dst_from=2, nights_in_dst_to=30
- max_fly_duration=60
- Schedule: every 3 days

### ESB → Guatemala City (3 stops, 10-15 nights, Feb-Mar)
- max_stopovers=3
- nights_in_dst_from=10, nights_in_dst_to=15
- max_fly_duration=60 (or omit for long-haul)
- Schedule: weekly

### IST → Anywhere Europe (weekly price scan)
- fly_from=airport:IST, fly_to=europe preset
- max_stopovers=1
- nights_in_dst_from=2, nights_in_dst_to=14
- Schedule: weekly

## Key Rules for the Prompt

1. Replace affilid in deep_links (reference only, do NOT output URLs)
2. NO URLs anywhere in the notification — no bare URLs, no markdown links. They trigger Telegram link previews that break the layout.
3. No intro text, no outro text, no warnings, no commentary — pure flight data only
4. Show ⚠️ VI when virtual_interlining is true
5. Show outbound duration in hours
6. Show stops per direction
7. Use short separator: ————— (5 em-dashes)
8. Header line break: city line on its own, details indented on next line
