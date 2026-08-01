#!/usr/bin/env python3
"""
HepsiEmlak Emlak İlan Cron Script (Template)
=============================================
Kullanım: Bu şablonu kopyala, aşağıdaki 3 değişkeni güncelle, cron job oluştur.

DEĞİŞTİRİLMESİ GEREKENLER:
  API_URL    → şehir/ilçe adını güncelle
  MAIN_URL   → şehir/ilçe adını güncelle
  EXCLUDED   → hariç mahalleleri düzenle
  DATA_FILE  → her job için farklı olmalı!
  HISTORY_FILE → her job için farklı olmalı!
"""
import json, os, ssl, sys, time, urllib.error, urllib.request
from datetime import datetime

# ===== KONFİGÜRASYON =====
# 🔧 İstediğiniz şehir/ilçe için değiştirin:
#   SEHIR → HepsiEmlak şehir slug'ı (ankara, istanbul, izmir, antalya, bursa...)
#           81 il listesi: skills/hepsiemlak-arsa-watchdog/references/turkiye-sehirleri.csv
#   ILCE  → ilçe slug'ı (cankaya, konak, muratpasa...) — boş bırakılırsa tüm ilçeler
#   p32   → maks fiyat (TL) — şehrin piyasasına göre ayarlayın
#   EXCLUDED → hariç tutulacak mahalleler (kendi şehrinize göre düzenleyin)
SEHIR = "ankara"     # ← şehrinizi yazın
ILCE = "cankaya"     # ← ilçenizi yazın (veya "")
MAX_PRICE = 8000000  # ← maks fiyat (TL)
API_URL = f"https://www.hepsiemlak.com/api/realty-list/{SEHIR}-satilik?counties={ILCE}&sortDirection=DESC&sortField=UPDATED_DATE&intent=satilik&mainCategory=konut&availableForLoanStatus=APPLICABLE&p32={MAX_PRICE}&pageNo=1&pageSize=50"
MAIN_URL = f"https://www.hepsiemlak.com/{SEHIR}-satilik"
DATA_FILE = os.path.expanduser(f"~/.hermes/hepsiemlak_{SEHIR}_{ILCE or 'tumu'}.json")
HISTORY_FILE = os.path.expanduser(f"~/.hermes/hepsiemlak_{SEHIR}_{ILCE or 'tumu'}_history.jsonl")

# Hariç tutulan mahalleler (örnek — Ankara Çankaya için)
EXCLUDED = {
    "Ümitköy", "Çayyolu", "Alacaatlı", "Karapınar", "Bayraktar",
    "Yukarı Dikmen", "Mutlukent", "Prof. Dr. Ahmet Taner Kışlalı",
    "100. Yıl", "Hilal"
}
# ===== KONFİGÜRASYON SONU =====

# TLS
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

def req(url, accept, referer=None):
    h = {**HEADERS, "Accept": accept}
    if referer:
        h.update({"Referer": referer, "Origin": "https://www.hepsiemlak.com",
                  "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin"})
    return urllib.request.Request(url, headers=h)

# Step 1: Warm up Cloudflare cookies
try:
    r1 = req(MAIN_URL, "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    with urllib.request.urlopen(r1, context=ctx, timeout=30) as r:
        r.read()
except:
    pass

time.sleep(2)

# Step 2: API call
try:
    r2 = req(API_URL, "application/json, text/plain, */*", referer=MAIN_URL)
    with urllib.request.urlopen(r2, context=ctx, timeout=30) as r:
        data = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")[:500]
    print(f"API_ERROR: HTTP {e.code} | {body}", file=sys.stderr)
    sys.exit(2)
except Exception as e:
    print(f"API_ERROR: {e}", file=sys.stderr)
    sys.exit(2)

items = data.get("realtyList", [])
if not items:
    print("API'den hiç ilan dönmedi. totalElements:", data.get("totalElements", "?"))
    sys.exit(0)

parsed = []
for i in items:
    district_obj = i.get("district") or {}
    mah = (district_obj.get("name") or "").strip()
    if mah in EXCLUDED:
        continue

    room_arr = i.get("room") or []
    lr_arr = i.get("livingRoom") or []
    room_count = str(room_arr[0]) if room_arr else "?"
    lr_count = str(lr_arr[0]) if lr_arr else "0"
    room_str = f"{room_count}+{lr_count}"

    sqm_obj = i.get("sqm") or {}
    gross_sqm_list = sqm_obj.get("grossSqm") or []
    gross_sqm = str(int(gross_sqm_list[0])) if gross_sqm_list else ""
    net_sqm = str(int(sqm_obj.get("netSqm", 0))) if sqm_obj.get("netSqm") else ""

    pid = str(i.get("id") or "")
    price = i.get("price") or 0
    detail_url = i.get("detailUrl") or ""
    if detail_url.startswith("en/"):
        detail_url = detail_url[3:]
    full_url = f"https://www.hepsiemlak.com/{detail_url}" if detail_url else f"https://www.hepsiemlak.com/ilan/{pid}"
    updated = i.get("updatedDate", "")
    title = i.get("title", "")

    parsed.append({
        "id": pid,
        "price": int(price) if price else 0,
        "currency": i.get("currency") or "TL",
        "neighborhood": mah,
        "room": room_str,
        "grossSqm": gross_sqm,
        "netSqm": net_sqm,
        "date": updated,
        "url": full_url,
        "title": title
    })

os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Compare with previous run
old_ids = set()
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE) as f:
            old = json.load(f)
        old_ids = {x.get("id", "") for x in old if x.get("id")}
    except:
        pass

current_ids = {x["id"] for x in parsed if x["id"]}
new_items = [x for x in parsed if x["id"] and x["id"] not in old_ids]

# Save current snapshot
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)

# Append new listings to historical archive
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
now_iso = datetime.now().isoformat()
with open(HISTORY_FILE, "a", encoding="utf-8") as f:
    for item in new_items:
        record = {"first_seen": now_iso, "data": item}
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

ts = datetime.now().strftime("%d.%m.%Y %H:%M")

if not old_ids:
    # First run — show all
    print(f"🏠 **HepsiEmlak {ILCE.capitalize()} Satılık — İlk Kontrol**")
    print(f"📅 {ts}")
    print(f"📊 Toplam: **{len(parsed)} ilan**")
    print()
    if not parsed:
        print("❌ Filtrelere uygun ilan bulunamadı.")
    else:
        for p in parsed:
            sqm = p['grossSqm'] or p['netSqm'] or '?'
            print(f"**{p['price']:,} TL** | {p['neighborhood']} | {p['room']} | {sqm} m² | [Link]({p['url']})")
elif new_items:
    print(f"🆕 **Yeni İlanlar — {ILCE.capitalize()} Satılık**")
    print(f"📅 {ts}")
    print(f"📊 **{len(new_items)} yeni ilan** (toplam: {len(parsed)})")
    print()
    for p in new_items:
        sqm = p['grossSqm'] or p['netSqm'] or '?'
        print(f"**{p['price']:,} TL** | {p['neighborhood']} | {p['room']} | {sqm} m² | [Link]({p['url']})")
else:
    # No new listings — silent
    pass
