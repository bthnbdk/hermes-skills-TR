# ERPNext HTML Reports for Remote Viewing

When the user is on a different machine and can't access `http://localhost:8080`, generate a self-contained HTML file from ERPNext data and deliver it via Telegram's `MEDIA:` path.

## Pattern

1. Query ERPNext via `ithalat_erpnext_api.py` for all records
2. Build a dark-themed static HTML page with tables + cards
3. Save to Windows Desktop: `/mnt/c/Users/batu/Desktop/<filename>.html`
4. Deliver via Telegram by including `MEDIA:/mnt/c/Users/batu/Desktop/<filename>.html` in the send_message body or the final response

## Example: Opportunity Case + Supplier Research Report

```python
import sys, os, json, datetime
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from ithalat_erpnext_api import ERPNext

erp = ERPNext()

# Fetch data
opps = erp.get_list('Opportunity Case', fields=['*'], limit=200)
opps.sort(key=lambda o: float(o.get('go_no_go_score', 0) or 0), reverse=True)

supps = erp.get_list('Supplier Research',
    fields=['name','supplier_name','product_category','creation','city',
            'website','contact_email','phone','verification_status','notes'],
    limit=200)

# Build HTML — dark theme, sortable by score, sticky headers
html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>İthalat Agent — Product List</title>
<style>
  body { font-family: -apple-system, sans-serif; background: #0f1117; color: #e1e4e8; padding: 24px; }
  h1 { color: #f0f6fc; }
  table { width: 100%; border-collapse: collapse; background: #161b22; border: 1px solid #30363d; }
  th { background: #1c2128; color: #8b949e; padding: 10px 12px; border-bottom: 1px solid #30363d; position: sticky; top: 0; }
  td { padding: 8px 12px; border-bottom: 1px solid #21262d; }
  .score-high { background: #1b3a2d; color: #3fb950; }
  .score-mid { background: #3d2e14; color: #d29922; }
  .score-low { background: #3d1f1a; color: #f85149; }
</style>
</head>
<body>
<h1>📦 İthalat Agent — Opportunity Cases</h1>
<p>''' + str(len(opps)) + ''' records</p>
<table><thead><tr><th>Score</th><th>Title</th><th>Status</th></tr></thead><tbody>
'''

for o in opps:
    score = o.get('go_no_go_score', 0) or 0
    cls = 'score-high' if score >= 50 else 'score-mid' if score >= 30 else 'score-low'
    html += f'<tr><td><span class="{cls}">{score}</span></td>'
    html += f'<td>{(o.get("title") or "?")[:80]}</td>'
    html += f'<td>{o.get("status","?")}</td></tr>'

html += '''</tbody></table></body></html>'''

# Save to Windows Desktop
desktop = '/mnt/c/Users/batu/Desktop/ithalat_report.html'
with open(desktop, 'w') as f:
    f.write(html)
print(f"✅ {desktop}")
```

## Delivery

After generating the file, send it via Telegram:

```python
# In Hermes response, include:
# MEDIA:/mnt/c/Users/batu/Desktop/ithalat_report.html
```

Or use `send_message`:
```
send_message(target="telegram", message="Report ready MEDIA:/mnt/c/Users/batu/Desktop/ithalat_report.html")
```

## Pitfalls
- Frontend container may be crash-looping — run pitfall #32 recovery first
- `ERPNext()` login may `ConnectionResetError` if container just started — retry with 5s delay
- Supplier Research `get_list()` with unknown field names returns HTTP 417 — use only known fields from the DocType schema
- File path must be absolute — relative paths don't resolve for MEDIA delivery
