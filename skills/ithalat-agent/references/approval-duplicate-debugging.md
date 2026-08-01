# Approval Email Storm — Debugging Chain (June 2025)

## Symptom

~100 emails with subject `[Onay Gerekli] go_no_go_decision - <id>` arrived in batuhan@budak.net inbox on 2026-06-25. Same decision IDs appeared 2-4 times each. All from "Approval Manager" <budaknetmail+approvals@gmail.com>.

## Discovery Chain

### 1. Identify source account

```bash
# Check which inbox has the flood
himalaya envelope list --account budaknet -s 100 -p 1 2>&1 | grep -c "Onay Gerekli"
# → 92 on page 1 alone
```

### 2. Read one email to identify sender

```
From: Approval Manager <budaknetmail@gmail.com>
Subject: [Onay Gerekli] go_no_go_decision - 9u0se4espu
Ne: go_no_go_decision
Risk Seviyesi: High
Finansal Etki: £0.00
Guven Skoru: 0.0
Tavsiye: Founder decision required
```

Key observation: `None tarafindan` (requested_by is null), £0.00 financial impact, 0.0 confidence — all suppliers have no pricing data so they all hit "High risk → founder approval required".

### 3. Find the email-sending code

The email body matches `ithalat_founder_notifier.py`'s `send_approval_request()` function, which calls `send_agent_email()` with `agent_name="Approval Manager"`, `plus_tag="approvals"`.

### 4. Trace the pipeline chain

```
ithalat-trade-readiness (8-59/30, no_agent=True)
    ↓ creates [Approval Manager] Go/No-Go: {title} Tasks
ithalat-agent-approval (5-59/5, no_agent=True)
    ↓ finds Open tasks, creates Approval Request records
ithalat-founder-notifier (every 60m, no_agent=True)
    ↓ finds Pending Approval Requests, sends email
```

### 5. Root cause: cascading `limit=50` dedup failures

**Bug A — `ithalat_trade_readiness.py` line ~305:**
```python
existing_approval_tasks = erp.get_list("Task",
    filters=[["subject", "like", f"%Go/No-Go: {title[:40]}%"]],
    fields=["name", "status"])
# NO explicit limit → default 50. If >50 tasks exist, misses some → re-creates
```

**Bug B — `ithalat_founder_notifier.py` line ~94:**
```python
notifications = erp.get_list("Founder Email Notification",
    filters=[["notification_type", "=", "approval_request"]],
    fields=["related_document"])
# NO explicit limit → default 50. If >50 sent, re-sends older ones
```

Both use `ERPNext.get_list()` which defaults to `limit=50`. Beyond 50 records, dedup silently fails.

### 6. Timeline

- Trade readiness ran every 30m → created new tasks each time (dedup missed due to limit)
- Approval agent ran every 5m → created new Approval Requests for each new task
- Founder notifier ran every 60m → sent emails for each unseen Approval Request
- Compound effect over ~17 hours of June 25 → ~100 emails

### 7. Fix (Applied 2026-06-26)

Both scripts patched with `limit=10000` on dedup queries. Additionally, `ithalat_trade_readiness.py` now updates Opportunity Case status to `"Pending Approval"` after creating a Go/No-Go task — this is the double-safety layer.

The duplicate inbox messages (104 emails) were marked as read. No stale Approval Requests remain in Pending-from-email-storm state.

### Additional Bug: "None tarafindan" — Wrong field name in Approval Request creation

**Bug C — `ithalat_agent_approval.py`:**
```python
# BAD — uses wrong field name
erp.create("Approval Request", {
    "requested_by": "Trade Readiness",   # ← THIS FIELD DOES NOT EXIST
    ...
})
```

The ERPNext `Approval Request` DocType stores the requester in `requested_by_agent`. Using `requested_by` creates the record but leaves the field empty, causing the email to display `None tarafindan`.

**Fix:**
```python
# GOOD — matches the DocType field name
erp.create("Approval Request", {
    "requested_by_agent": "Trade Readiness",
    ...
})
```

Or better, use the helper method:
```python
erp.create_approval(
    requested_by="Trade Readiness",
    action_type="go_no_go_decision",
    recommendation="Founder decision required",
    risk_score="High"
)
```

**Lesson:** When creating DocType records directly with `erp.create()`, verify field names against the DocType or the helper method. The `erp.create_approval()` helper exists specifically to get these field names right — prefer it over raw `erp.create("Approval Request", ...)` when possible.

### Prevention Checklist

```bash
# Count how many duplicate emails
himalaya envelope list --account budaknet -s 200 -p 1 2>&1 | grep "Onay Gerekli" | sort

# Delete them via IMAP or mark as read
# For Approval Requests in ERPNext: change status of all Pending go_no_go ones
# to "Cancelled" if they have no financial data (£0.00, score 0.0)
```

When adding a new mechanical agent script that creates records and checks for existing ones:

- [ ] Does the dedup query pass an explicit `limit` parameter?
- [ ] Does the dedup query use the right fields for matching (e.g., `related_document` not `name`)?
- [ ] Is the upstream script (that creates the input records) also properly bounded?
- [ ] After processing, does the source record get its status updated so it won't be picked up again?
