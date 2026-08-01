---
name: ithalat-agent
description: "AI-native import company OS for Turkey-to-UK trade. Manages ERPNext, Gmail, virtual agents, approval rules, and trade readiness workflows."
version: 4.3.0
author: batubot
metadata:
  hermes:
    tags: [import, trade, Turkey, UK, erpnext, gmail, erp, crm]
prerequisites:
  commands: [docker, curl, python3]
  scripts: [ithalat_erpnext_api.py]
---

# İthalat Agent — AI-Native Import Company OS (v3)

AI-native işletim sistemi: Türkiye'den tedarik, UK'ye satış. ERPNext source of truth, Gmail communication layer, Hermes Agent runtime.

## Architecture (Hybrid: Mechanical + LLM Agents)

```\nFounder (batuhan@budak.net) ──email/CC──┐\n          ↑ email bildirimleri           │\n          │    (Approval Manager,        │\n          │     Reporting Agent,         v\n          │     System Health)    ┌──────────────┐\n          │                       │ Agent Mailbox │\n          │                       │budaknetmail@ │\n          │                       └──────┬───────┘\n          │                              │\n          │                     ┌────────┴────────┐\n          │                     │ Gmail Monitor   │\n          │                     │ (1m, mechanical)│\n          │                     └────────┬────────┘\n          │                              │ email → Task\n          │                              v\n          │                     ┌────────────────────┐\n          │                     │     ERPNext         │\n          │                     │  (localhost:8080)   │\n          │                     │  Tasks, DocTypes,   │\n          │                     │  Action Logs        │\n          │                     └──┬──┬──┬──┬──┬──┬──┘\n          │                        │  │  │  │  │  │\n┌─────────┴─────────┐    ┌────────┘  │  │  │  └──────────┐\n│ LLM Agents        │    │ Mechanical Agents              │\n│ (no_agent=False)  │    │ (no_agent=True)                │\n├───────────────────┤    ├────────────────────────────────┤\n│ Supplier Discovery│    │ Orchestrator (2m) ←→ Agent Bus│\n│ (60m)             │    │ CRM (3m)               ↕      │\n├───────────────────┤    │ Supplier (3m)          ↕      │\n│ LLM Research      │    │ Pricing (3m)           ↕      │\n│ (30m)             │    │ Research Mech (5m)     ↕      │\n├───────────────────┤    │ Approval Mgr (5m)             │\n│ LLM Orchestrator  │    │ Reporting (5m)                │\n│ (6h)              │    │ Trade Readiness (30m)         │\n└───────────────────┘    │ Notifier / Health (1h/5m)      │\n                         │ OSTİM Scraper (02:00)         │\n                         └────────────────────────────────┘\n                                     ↕ ↕ ↕\n                          ┌────────────────────┐\n                          │  Agent Message Bus │\n                          │  (SQLite, 7-day)   │\n                          │  Research→Supplier │\n                          │  Supplier→CRM      │\n                          │  CRM→Research      │\n                          └────────────────────┘\n```

**Mechanical agents** = regex/if-else Python scripts (no_agent=True). Fast, cheap, predictable. Handle routine CRUD and fast-repeating operations.

**LLM agents** = self-contained prompts executed by Hermes Agent (no_agent=False). Use web_search, terminal, file tools. Handle research, discovery, prioritization, and strategic decisions. Each has the `ithalat-agent` skill loaded for context. Output delivered to founder's Telegram.

### Agent Email Identity

All outbound emails use a shared `send_agent_email()` function in `ithalat_erpnext_api.py`. Each script sets a unique display name and plus-address so the founder sees which agent sent the email.

```python
from ithalat_erpnext_api import send_agent_email

send_agent_email(
    to="batuhan@budak.net",
    subject="[Onay Gerekli] ...",
    body="...",
    agent_name="Approval Manager",
    plus_tag="approvals",
    app_password=APP_PASSWORD
)
```

Agent identity mapping:

| Script / Prompt | From Name | From Address | Use Case |
|--------|-----------|-------------|----------|
| `founder_notifier` | Approval Manager | `budaknetmail+approvals` | Approval requests |
| `approval_orchestrator` | Approval Manager | `budaknetmail+approvals` | Approval pipeline |
| `agent_orchestrator.py` (mech) | Agent Orchestrator | `budaknetmail+approvals` | Grant alerts, chain routing |
| `daily_report` | Reporting Agent | `budaknetmail+reports` | Daily digest |
| `health_checker` | System Health | `budaknetmail+system` | Health alerts |
| `ithalat-llm-research` prompt | Research Agent | `budaknetmail+research` | UK market research findings |
| `ithalat-llm-orchestrator` prompt | System Orchestrator | `budaknetmail+orchestrator` | System coordination |
| `ithalat-supplier-discovery` prompt | Supplier Discovery | `budaknetmail+suppliers` | New supplier findings |

Gmail plus-addresses in the From header work because SPF/DKIM align on `gmail.com` domain (same as the authenticated SMTP account). The `+tag` enables founder-side inbox filtering rules.

## Agent Message Bus (Inter-Agent Communication)

Introduced v4.2.0. Agents communicate directly via a SQLite-based message bus at `~/.hermes/data/agent_bus.db`. This supplements (does not replace) the ERPNext Task-based chaining — agents still create Tasks, but ALSO send structured messages for real-time awareness.

**Module:** `ithalat_agent_bus.py` — import `AgentMessageBus` class.

```python
from ithalat_agent_bus import AgentMessageBus
bus = AgentMessageBus()

# Send a command to another agent
bus.send(from_agent="Research Agent", to_agent="Supplier Agent",
         subject="Find suppliers for: Olive Oil",
         body="UK market analysis done. Price range £8-£15. Score 65/100.",
         msg_type="command",
         related_doctype="Opportunity Case", related_docname="OC-0001")

# Read unread messages
for msg in bus.get_messages("Supplier Agent", limit=5):
    bus.mark_processed(msg["id"])
```

### Message Types

| Type | Direction | Meaning |
|------|-----------|---------|
| `command` | A → B | "Do this task" |
| `result` | A → B | "Completed X, here's what I found" |
| `question` | A → B | "What do you think?" |
| `answer` | B → A | Reply to a question (same thread) |
| `notification` | Any | FYI, no action needed |

### Chained Operations Flow

```
Research Agent ──command──→ Supplier Agent ──result──→ CRM Agent ──result──→ Research Agent
      │                              ↑
      └──command──→ Pricing Agent ───┘
                         ↓
                   Trade Readiness → Approval
```

**Chain 1 — Research → Supplier → CRM → Research (loop):**
1. Research Agent completes analysis → sends **command** to Supplier + Pricing Agents
2. **Agent Orchestrator** (2m tick) reads unread messages → converts commands into ERPNext Tasks → replies with task names
3. **Supplier Agent** processes task → sends **result** to CRM Agent
4. **CRM Agent** processes task → sends **result** to Research Agent → loop complete

**Chain 2 — Pricing → Trade Readiness → Approval:**
Pricing Agent completes margin analysis → could send **result** to Trade Readiness for grant matching and approval.

### Agent Orchestrator as Message Hub

The orchestrator (`ithalat_agent_orchestrator.py`) was rewritten from a simple task router into an inter-agent communication hub. Uses a `MESSAGE_HANDLERS` dict keyed by (from_agent, msg_type) to dispatch messages. Handlers:

- Research → Supplier command → creates `[Supplier Agent]` task
- Research → Pricing command → creates `[Pricing Agent]` task
- Supplier → CRM result → creates `[CRM Agent]` task
- CRM → Research result → completes loop
- Trade Readiness grant match → email alert to founder
- Any agent question → system status answer

### Why Tasks AND Messages?

Tasks = durable work queue (survives crashes, visible in Desk UI). Messages = awareness layer (immediate chaining, context passing, question/answer threads). Both are needed.

See `references/agent-message-bus.md` for full API reference, DB schema, and performance notes.

## Agent Execution Pipeline

New email → Gmail Monitor → Task created → Orchestrator routes → Specialist executes → ERPNext updated

```
Email gelir ──→ Gmail Monitor ──→ Task oluşur ──→ Orchestrator ──→ [CRM Agent]
                  (1 dk)                              (2 dk)        [Pricing Agent]
                                                                   [Supplier Agent]
                                                                   [Research Agent]
                                                                   [Approval Mgr]
                                                                   [Reporting]
```

## Agent Scripts (deployed at ~/.hermes/scripts/)

| Script | Cron | Agent | Purpose |
|--------|------|-------|---------|
| `ithalat_gmail_monitor.py` | **every 1m** | Email Gateway | Read UNSEEN, classify, create Task + ThreadSummary + FounderInstruction. Parse founder approval replies |
| `ithalat_agent_orchestrator.py` | **every 2m** | Orchestrator (Hub) | NOW ALSO reads Agent Bus messages and routes inter-agent communication (Research→Supplier, Research→Pricing, Supplier→CRM, CRM→Research loop). Answers coordination questions. See `references/agent-message-bus.md` |
| `ithalat_agent_crm.py` | **every 3m** | CRM | Create/update Customer & Contact records. Parse company names, contact info from task descriptions |
| `ithalat_agent_supplier.py` | **every 3m** | Supplier | Create Supplier & Supplier Research records. Parse product/city/contact info |
| `ithalat_agent_pricing.py` | **every 3m** | Pricing | Extract pricing data (cost/target/MOQ) from task text. Create Pricing Analysis records with margin calculations |
| `ithalat_agent_research.py` | **every 5m** | Research | Multi-source market research: Amazon UK, eBay UK, Etsy UK + Wikipedia. Turkish→English topic extraction. Go/no-go scoring. **Chains downstream:** creates `[Supplier Agent]` + `[Pricing Agent]` tasks for scores ≥30. **Per-task 60s SIGALRM timeout + DDG timeout 6s (no retry)** — primary fix is DDG timeout reduction (6s instead of 12s) and removing retry; SIGALRM is safety net. **Max 1 task per tick** (2×60s hits 120s cron limit). See pitfall 17 for SIGALRM+requests incompatibility |
| `ithalat_agent_approval.py` | **every 5m** | Approval Manager | Track pending Approval Requests. Log approval pipeline state |
| `ithalat_agent_reporting.py` | **every 5m** | Reporting | Generate ad-hoc activity summaries. Create Daily Executive Report records |
| `ithalat_founder_notifier.py` | every 1h | (infra) | Email pending approvals to founder. Looks up related Opportunity Case (title, category, status) to enrich subject line with company/product name instead of raw action code |
| `ithalat_approval_orchestrator.py` | every 30m | (infra) | Draft → approval → send pipeline |
| `ithalat_daily_report.py` | 09:00 daily | (infra) | Daily digest email to founder |
| `ithalat_health_checker.py` | every 5m | (infra) | System health (ERPNext/Gmail/Docker/disk) |
| `ithalat_trade_readiness.py` | **8-59/30** | Trade Readiness | Evaluates New Opportunity Cases. Creates **3 records**: Import Readiness Record, TR Export Readiness Record, Supplier Export Flow Record. Matches grants (score≥40) and creates go/no-go approval tasks (score≥50). See `references/trade-readiness-grant-matching.md` for grant logic and scoring |
| `ithalat_ostim_scraper.py` | **0 2 * * *** | OSTİM Scraper v2 | Uses `api/search/index` with a-z + 0-9 character enumeration. 333 unique firms discovered (type=1 filter). For each new firm (max 5/tick): creates Supplier Research record + [Research Agent] UK market task + [CRM Agent] contact registration task. See `references/ostim-scraper.md` |
| `ithalat_backup.sh` | **0 3 * * *** | Backup | Dumps ERPNext MariaDB + site config via `bench --site frontend backup`, archives to ~/.hermes/backups/, 7-day retention |

## Agent Cron Jobs (18 total — 15 mechanical + 3 LLM-powered)

### Mechanical (no_agent=True) — 15 adet

| Job ID | Schedule | Script | Agent |
|--------|----------|--------|-------|
| e44d0e668b5a | **every 1m** | gmail_monitor.py | Email Gateway |
| **4833e767c073** | **1-59/2** | agent_orchestrator.py | Orchestrator |
| **56be7268d5aa** | **2-59/3** | agent_crm.py | CRM |
| **dadff5dd16f3** | **3-59/3** | agent_supplier.py | Supplier |
| **fe9914cde987** | **4-59/3** | agent_pricing.py | Pricing |
| **4135d4f00215** | **6-59/5** | agent_research.py | Research |
| **cefbaa72b519** | **5-59/5** | agent_approval.py | Approval Manager |
| **11c4d4d85535** | **7-59/5** | agent_reporting.py | Reporting |
| 98f8731fbfd9 | every 1h | founder_notifier.py | (infra) |
| 1929d042f053 | every 30m | approval_orchestrator.py | (infra) |
| 7387c8cf1d84 | 09:00 daily | daily_report.py | (infra) |
| 92573794f55b | every 5m | health_checker.py | (infra) |
| **c6e97fa91765** | **8-59/30** | trade_readiness.py | Trade Readiness |
| **0ed6cb64349b** | **0 2 * * *** | ostim_scraper.py | OSTİM Scraper |
| **1a949abc7e3f** | **0 3 * * *** | backup.sh | Daily Backup |

All mechanical cron jobs use `no_agent=true` (script-only, no LLM overhead). Also note: backup and ostim-scraper use `deliver=local` (output saved to ~/.hermes/cron/output/, not sent to user).

### LLM-Powered (no_agent=False) — 3 adet

| Job ID | Schedule | Agent | Görevi | Toolsets |
|--------|----------|-------|--------|----------|
| `dbca4b16afee` | **every 60m** | Supplier Discovery | Bing ile OSTİM/İvedik firmalarını keşfet, website scrape et, Supplier Research + [Research Agent] task zincirle. See `references/bing-web-rss-search.md` for search technique | terminal, file, web |
| `bf7288b60ce7` | **every 30m** | LLM Research | [Research Agent] task'lerini işle, UK pazar araştırması yap, Opportunity Case + downstream task oluştur. Bing News trend taraması. See `references/bing-web-rss-search.md` | terminal, file, web |
| `4a9020fc52ba` | **0 */6 * * *** | LLM Orchestrator | Sistem genel durumu, açık task kontrolü, önceliklendirme, bekleyen onay hatırlatması | terminal, file, web |

These agents receive a self-contained prompt (with `ithalat-agent` skill loaded) and use Hermes tools (terminal, web_search, file) to execute research, scraping, and ERPNext operations. They use the DeepSeek Flash model (cheap, fast).

**Delivery:** All LLM agents use `deliver=local` — their LLM response is saved to a local file, NOT sent to Telegram. Instead, the prompt instructs them to email the founder via `send_agent_email()` when they find something worth reporting. If nothing was found, they stay completely silent (no email, no Telegram). This keeps the founder's inbox clean while ensuring important findings arrive by email with the correct agent identity (+suppliers, +research, +approvals).

**Prompt authoring:** See `references/llm-agent-prompt-guide.md` for the prompt template, tool patterns, token budget, and error handling conventions used across all LLM agents.

### Agent Workflow Detail

**Example: "BlueCo firmasına fiyat teklifi hazırla"**

```
1. 15:00  Founder email gelir                                   → Gmail Monitor
2. 15:01  Monitor: "explicit_founder_instruction" tespit eder    → Gmail Monitor
          Task oluşturur: [Orchestrator Agent] BlueCo teklif
3. 15:02  Orchestrator: "Pricing Agent" yönlendirir              → Orchestrator
          Pricing task oluşturur
4. 15:03  Pricing Agent: task'ı okur, fiyat-ları parse eder     → Pricing Agent
          Pricing Analysis kaydı oluşturur
          Task "Completed" yapar
5. 15:04  Tüm task'lar temizlenir. Her şey ERPNext'te kayıtlı.
```

**Example: "Müşteri şikayeti" (gelen email)**

```
1. Gmail Monitor → intent=complaint → Task: [CRM Agent] Müşteri şikayeti
2. Orchestrator → CRM Agent (2 dk sonra)
3. CRM Agent → yeni Customer/Contact kaydı oluşturur → Task completed
```

**Example: Opportunity Discovery Chain (auto-triggered)**

```
1. [Research Agent] task arrives (from monitor or manual)
2. Research Agent: Amazon UK + eBay UK + Etsy UK + Bing News RSS + Wikipedia search
3. Creates Opportunity Case (with go/no-go score 0-100)
4. If score ≥30: auto-creates two downstream tasks:
   → [Supplier Agent] Find suppliers for {product}
   → [Pricing Agent] Price analysis for {product}
5. Supplier Agent (3 dk sonra): creates Supplier Research + Supplier records
6. Pricing Agent (next tick): creates Pricing Analysis with margin calc
7. Trade Readiness (8-59/30): creates Import Readiness + TR Export Readiness + Supplier Export Flow
8. If score ≥40: Trade Readiness matches grants → Grant Application records created
9. If score ≥50: Trade Readiness creates [Approval Manager] Go/No-Go task for founder decision

**Example: OSTİM Directory Discovery Chain (02:00 daily — v2 API approach)**\n\n```txt\n1. ithalat_ostim_scraper.py scans API: /api/search/index with a-z+0-9 single-char queries\n   → 333 unique companies discovered (type=1 filter, /firmalar/{slug} detail pages)\n2. For each NEW firm (max 5/tick):\n   → Supplier Research record (city=Ankara, product_category=parsed from sector fallback)\n   → [Research Agent] UK market analysis for {company}\n   → [CRM Agent] Create contact: {company}\n3. Mechanical agents pick up these tasks on next tick:\n   CRM (3m) → creates Customer + Contact from task description\n   Research (5m) → processes market analysis → Opportunity Case\n   Trade Readiness (30m) → Import/TR/Supplier Export Flow + grants\n```

### Quickly Viewing İthalat Data from CLI

When ERPNext web UI (http://localhost:8080) is unavailable or you just want a fast table dump, query the API directly:

```bash
# All Opportunity Cases sorted by score
python3 -c "
import sys, os, json
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from ithalat_erpnext_api import ERPNext
erp = ERPNext()
opps = erp.get_list('Opportunity Case', fields=['name','title','go_no_go_score','status'], limit=100)
for o in sorted(opps, key=lambda x: float(x.get('go_no_go_score',0) or 0), reverse=True):
    print(f\"{str(o.get('go_no_go_score','?')):>4} | {str(o.get('status','?')):12s} | {o.get('title','?')[:70]}\")
"

# All Supplier Research — product_category list
python3 -c "
import sys, os, json
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from ithalat_erpnext_api import ERPNext
erp = ERPNext()
for s in erp.get_list('Supplier Research', fields=['supplier_name','product_category','name'], limit=100):
    print(f\"  {s.get('name','?'):20s} | {s.get('product_category','?'):15s} | {s.get('supplier_name','?')[:55]}\")
"

# Count by status
python3 -c "
import sys, os
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from ithalat_erpnext_api import ERPNext
from collections import Counter
erp = ERPNext()
statuses = [o.get('status','?') for o in erp.get_list('Opportunity Case', fields=['status'], limit=500)]
for s, c in Counter(statuses).most_common():
    print(f'  {s:20s} → {c} adet')
"

# Last 10 Agent Action Logs
python3 -c "
import sys, os, json
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from ithalat_erpnext_api import ERPNext
erp = ERPNext()
logs = erp.get_list('Agent Action Log', fields=['agent_name','action_type','creation'], limit=10)
for l in reversed(logs):
    print(f\"  {str(l.get('creation','?'))[:16]:16s} | {l.get('agent_name','?'):20s} | {l.get('action_type','?')}\")
"

# Filter by score threshold
python3 -c "
import sys, os
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from ithalat_erpnext_api import ERPNext
erp = ERPNext()
good = [o for o in erp.get_list('Opportunity Case', fields=['title','go_no_go_score','status'], limit=500)
        if float(o.get('go_no_go_score',0) or 0) >= 40]
for o in sorted(good, key=lambda x: float(x.get('go_no_go_score',0)), reverse=True):
    print(f\"  Skor {str(o.get('go_no_go_score','?')):>4} | {str(o.get('status','?')):12s} | {o.get('title','?')[:65]}\")
"
```

**ERPNext UI'den görmek için:** http://localhost:8080 → Awesome Bar'a `Opportunity Case` veya `Supplier Research` yaz → List View açılır. Filtre eklemek için **+ Filter** butonu → `go_no_go_score` → `Greater Than` → `30` gibi.

### Silent Operation

All agent scripts are SILENT when there's nothing to do:
- No output = no notification to user
- Only print JSON when they actually process tasks
- Boş çalışmalardan bildirim gelmez

## 19 Custom DocTypes (ERPNext CRM module)

| DocType | Purpose |
|---------|---------|
| Agent Profile | Virtual agent identity (key, name, mailbox, purpose, status) |
| Agent Permission | Per-agent read/write/delete per DocType |
| Agent Action Log | Every action: agent_name, action_type, input/output_summary, related doctype, risk_level, model_used |
| Approval Request | Founder approval workflow: action_type, risk_score, financial_impact, recommendation, approval_status |
| Opportunity Case | Market opportunity: title, demand signals, competitor prices, landed cost, margin, go/no-go score |
| Supplier Research | Turkish supplier discovery: name, city, website, verification_status, risk |
| Email Thread Summary | Every processed email: thread_id, sender, plus_tag, routing_reason, intent, urgency |
| Founder Instruction | Parsed founder commands: raw text, parsed_intent, recognized_entities, assigned_agent, status |
| Pricing Analysis | Cost/margin calculations: landed_cost, gross_margin, discount_tolerance, recommendation |
| Risk Event | Tracked risks: risk_type, severity, description, mitigation_action, status |
| Daily Executive Report | Daily summary: new_opportunities, supplier/customer activity, pending_approvals, risks |
| External Email Draft | Outbound email pipeline: agent, recipient, body draft, approval_required, approval_request, send_status |
| Founder Email Notification | Emails sent to founder: type, urgency, summary, decision_options, founder_reply_status |
| Import Readiness Record | Turkey→UK trade readiness: commodity_code, tariff_check, compliance, incoterms, risk_score |
| Supplier Export Flow Record | Per-supplier export readiness: documentation, customs_broker, incoterms |
| TR Export Readiness Record | Turkey entity readiness: exporter_union, customs_agent, required_documents |
| Grant Opportunity Record | Known grant programs: support_program, eligibility, deadline, advisor_review_required |
| Grant Application Record | Active applications: grant_opportunity, application_status, deadline |
| Grant Expense Mapping Record | Expense-to-grant mapping: expense_type, eligible_for_support, support_percentage |

## Gmail Email Routing (ithalat_gmail_monitor.py v2)

**Routing Priority:**
1. Explicit founder instruction (Turkish command patterns: *bul, ara, hazırla, kontrol et*)
2. Email intent/entities (keyword-based: pricing, supplier, logistics, order, approval)
3. ERPNext thread context (future: link to existing tasks/customers)
4. Attachments / quoted history
5. Plus-address tag (`budaknetmail+pricing@gmail.com` → Pricing Agent)
6. CC to agent ops mailbox

**Routing Output (logged to ERPNext):**
- `agent_mailbox_detected`: budaknetmail@gmail.com
- `plus_tag_detected`: pricing, suppliers, etc. (or null)
- `final_route`: Orchestrator Agent / Pricing Agent / Supplier Agent / CRM Agent / Approval Manager Agent
- `routing_reason`: explicit_founder_instruction / founder_cc_plus_tag_pricing / email_intent_pricing / etc.
- `confidence_score`: 0.3–0.95
- `external_reply_allowed`: false (always — CC never authorizes reply)

**Actions per email:**
1. Create Email Thread Summary (with all routing metadata)
2. Create Agent Action Log (agent="Email Gateway", action="email_processed")
3. If from founder: Create Founder Instruction record (assigned_agent = routed agent)
4. Create ERPNext Task (subject="[Routed Agent] Original subject", body includes full routing chain)

## Approval Lifecycle Principle

**"Ask once, wait forever."** — When the system requests founder approval, it sends exactly ONE email per Approval Request. After that, it enters silent-wait mode:

1. **No re-sends** — The `ithalat_founder_notifier.py` dedup check (via Founder Email Notification records) prevents re-sending the same approval.
2. **No auto-proceed** — The system never proceeds without founder approval. Pending approvals stay Pending until the founder replies.
3. **No task re-creation** — After `ithalat_trade_readiness.py` creates a Go/No-Go task, it updates the Opportunity Case status to "Pending Approval" so subsequent ticks don't re-process it.
4. **No escalation spam** — No automatic escalation timer. The LLM Orchestrator (6h) reports pending approvals in its digest but never re-emails.
5. **Context in subject** — The notifier looks up the related Opportunity Case to include company/product name and score in the email subject, so the founder can identify the decision without opening the email.

This is intentional: the founder gets ONE clear notification per decision, then works through approvals at their own pace.

## Approval Rules (enforced by ithalat_approval_orchestrator.py)

> **DocType field reference:** See `references/approval-doctype-select-options.md` for valid values of `approval_status`, `risk_score`, `send_status`, and other Select fields. Using invalid values causes HTTP 417 errors.

| Action | Risk | Auto? | Notes |
|--------|------|-------|-------|
| CRM note/kayıt oluşturma | Low | ✅ Otomatik | |
| Duplicate merge | Medium | ❌ Kurucu onayı | |
| External email draft | Medium | ✅ Otomatik | Sadece taslak. Gönderme ayrı onay |
| External email send | Medium | ❌ Kurucu onayı | MVP politikası |
| Customer discount <3% | Medium | ❌ Onay gerekli | MVP'de zorunlu |
| Customer discount 3-7% | High | ❌ Kurucu onayı | |
| Customer discount >7% | High | ❌ Gerekçe + onay | |
| Yeni tedarikçi outreach | Medium | ❌ Taslak serbest, gönderme onaylı | |
| Sample order | High | ❌ Kurucu onayı | |
| Ödeme | Critical | ❌ Ajan yürütemez | |
| Sözleşme/hukuk | Critical | ❌ Ajan yürütemez | |
| Gümrük/HS kodu | Critical | ❌ Ajan yürütemez | |
| Kayıt silme | Critical | ❌ Ajan yürütemez | |

## 8 Virtual Agents — Fully Operational

All 8 agents are now live with their own scripts and cron jobs. Each agent picks up its routed tasks, executes the work, and logs to ERPNext.

| Agent | Key | Script | Cron | Does What |
|-------|-----|--------|------|-----------|
| **Orchestrator** | orchestrator | `agent_orchestrator.py` | **every 2m** | Routes [Orchestrator] tasks to specialists. Assigns orphan tasks via keyword matching (pricing→Pricing, supplier→Supplier, etc.) |
| **Email Gateway** | email_gateway | `gmail_monitor.py` | **every 1m** | Email ingestion, classification, routing, founder reply parsing |
| **CRM** | crm | `agent_crm.py` | **every 3m** | Creates/updates Customer & Contact records from tasks. Extracts company names, contact info |
| **Research** | research | `agent_research.py` | **every 5m** | Multi-source research (Amazon UK, eBay UK, Etsy UK, Bing News RSS + Wikipedia). Creates Opportunity Case records with market analysis. **Per-task 60s SIGALRM timeout + DDG timeout 6s (no retry)** — DDG timeout reduction is primary fix, SIGALRM is safety net. **Max 1 task per tick** (2×60s almost hits 120s cron limit). **Chains downstream:** for scores ≥30, auto-creates `[Supplier Agent]` + `[Pricing Agent]` tasks via BOTH Agent Bus messages AND ERPNext Tasks. See `references/research-agent-topic-extraction.md` for topic extraction, `references/research-agent-downstream-chain.md` for chaining logic, `references/research-agent-bing-news.md` for Bing News RSS technique |
| **Supplier** | supplier | `agent_supplier.py` | **every 3m** | Creates Supplier & Supplier Research records. Extracts product/city/phone from tasks |
| **Pricing** | pricing | `agent_pricing.py` | **every 3m** | Extracts cost/target/MOQ from task text. Calculates margins. Creates Pricing Analysis records |
| **Approval Manager** | approval_manager | `agent_approval.py` | **every 5m** | Tracks pending approval requests. Coordinates with approval_orchestrator.py |
| **Reporting** | reporting | `agent_reporting.py` | **every 5m** | Generates activity summaries. Creates Daily Executive Report records |

### Permission Matrix

| Agent | ERPNext Read | ERPNext Write | External Email | Forbidden |
|-------|-------------|--------------|---------------|-----------|
| **Orchestrator** | orchestrator | All | Task, AgentActionLog, ApprovalRequest, FounderInstruction | ❌ | payment, legal_commitment, delete, self_approval |
| **Email Gateway** | email_gateway | Customer, Contact, Supplier, Opportunity, Task | EmailThreadSummary, FounderInstruction, AgentActionLog | ❌ | external_send |
| **CRM** | crm | Customer, Contact, Supplier, Opportunity | Customer, Contact, Supplier, Note, AgentActionLog | ❌ | delete, merge_without_approval |
| **Research** | research | OpportunityCase, Supplier, Item, Customer | OpportunityCase, AgentTask, AgentActionLog, RiskEvent | ❌ | external_send, final_go_no_go |
| **Supplier** | supplier | Supplier, OpportunityCase, Item, SupplierResearch | Supplier, SupplierResearch, AgentActionLog, RiskEvent | ✅ onaylı | payment, binding_agreement |
| **Pricing** | pricing | Customer, Supplier, Item, Opportunity, Quotation | PricingAnalysis, AgentActionLog, ApprovalRequest | ❌ | binding_price, customer_email |
| **Approval Manager** | approval_manager | All | ApprovalRequest, AgentActionLog, Task, AgentTask | ✅ founder | self_approval, rule_bypass |
| **Reporting** | reporting | All | DailyExecutiveReport, AgentActionLog | ✅ founder | state_change |

## ERPNext API Helper & Shared Utilities (ithalat_erpnext_api.py)

```python
from ithalat_erpnext_api import ERPNext
erp = ERPNext()  # auto-login Administrator/admin on localhost:8080

# CRUD
records = erp.get_list("Email Thread Summary", filters=[["creation", ">", "2026-06-24"]], limit=10)
record = erp.get("Approval Request", "abc123")
created = erp.create("Agent Action Log", {"agent_name": "Orchestrator", "action_type": "test", "status": "Submitted"})
updated = erp.update("External Email Draft", "def456", {"send_status": "Sent"})

# Convenience methods
erp.log_action(agent_name="Email Gateway", action_type="email_processed", ...)
erp.create_approval(requested_by="Pricing Agent", action_type="customer_discount", ...)
erp.health_check()  # → True/False

# Bing Web/News Search (no API key)
from ithalat_erpnext_api import search_bing_web, search_bing_news
results = search_bing_web("ostim ankara imalatçı firma")       # → [{title, snippet, url}]
news = search_bing_news("UK import trends")                      # → [{title, snippet, url, date}]

# Agent-specific email (set different From name + plus-address per agent)
from ithalat_erpnext_api import send_agent_email
send_agent_email(
    to="batuhan@budak.net",
    subject="[Onay Gerekli] ...",
    body="...",
    agent_name="Approval Manager",
    plus_tag="approvals",          # → budaknetmail+approvals@gmail.com
    app_password=APP_PASSWORD      # Passed from each script's own credential
)
```

## ERPNext Setup Notes

- Docker stack: `~/erpnext/docker-compose.yml` (from frappe_docker pwd.yml)
- Start: `sudo dockerd &` then `sudo chmod 666 /var/run/docker.sock` then `docker compose -f ~/erpnext/docker-compose.yml up -d`
- Login: Administrator / admin at http://localhost:8080
- CSRF token for curl: `curl -s http://localhost:8080/desk | grep -oP 'csrf_token = "([^"]+)"'`

## Email Accounts

| Role | Email | Status | Notes |
|------|-------|--------|-------|
| Founder | batuhan@budak.net | ✅ Workspace, app password works | Himalaya: accounts.budaknet |
| Agent Mailbox | budaknetmail@gmail.com | ✅ Gmail, app password | Himalaya: accounts.budaknetmail. ALL agents share this inbox |
| Work | batuhan.budak@fcdo.gov.uk | Gmail, not set up in Himalaya | NewsBank only |
| Personal | anarchyfunk@gmail.com | ✅ Gmail, app password, default | Himalaya: accounts.gmail (default) |
| Outlook | batuhan_budak@hotmail.com | ⏸ OAuth2 gerekli | Azure app 7830894f-87f6-46a6-bdf8-2eca59c9f7ea |

## Project Architecture Docs

Two canonical documents define the system design, agent responsibilities, approval rules, and roadmap. Read these whenever a question about *why* something is built a certain way arises:

| File | Contents |
|------|----------|
| `~/.hermes/ithalat-agent/docs/HERMES_PROJECT_BRIEF.md` | Full project brief: architecture, 8 agent specs, 19 custom DocTypes, email model, approval rules, workflows, first 30-day plan |
| `~/.hermes/ithalat-agent/docs/HERMES_MISSED_ITEMS_ADDENDUM.md` | Addendum: laptop deployment model, LLM Gateway, trade readiness, grants agent, model tier strategy, sensitive data handling |

## Local laptop setup

- OS: WSL (Windows Subsystem for Linux) Ubuntu
- Docker Engine installed directly in WSL (no Docker Desktop)
- ERPNext runs locally on port 8080
- Foundation scripts in ~/.hermes/scripts/ (all ithalat_*.py)
- Cron jobs managed by Hermes Agent scheduler
- Backup: daily at 03:00 via crontab (DB dump + Hermes config tar.gz)
- Systemd user service available (enable: `systemctl --user enable ithalat-docker`)

## Common Tasks

```bash
# Check all containers
docker compose -f ~/erpnext/docker-compose.yml ps

# Check ERPNext health (wait 45s after starting — frontend takes time to boot)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080

# Run monitor manually
python3 ~/.hermes/scripts/ithalat_gmail_monitor.py

# Generate HTML report for remote viewing (user on another machine)\n# See references/erpnext-html-reports.md for full pattern
python3 -c "from ithalat_erpnext_api import ERPNext; erp=ERPNext(); opps=erp.get_list('Opportunity Case', fields=['title','go_no_go_score','status'], limit=100); [print(f\"{o.get('go_no_go_score','?'):>4} | {o.get('title','?')[:60]}\") for o in sorted(opps, key=lambda x: float(x.get('go_no_go_score',0)or 0), reverse=True)]"

# Check cron jobs
hermes cron list

# Check state files
cat ~/.hermes/ithalat_gmail_state.json
cat ~/.hermes/ithalat_health_alerts.json

# Backup manually
bash ~/.hermes/scripts/ithalat_backup.sh
```

## Background Services (systemd user)

| Service | Status | Purpose | Auto-start |
|---------|--------|---------|------------|
| `ithalat-trigger-daemon.service` | ✅ Running | Gmail 30s polling — instant email trigger | ✅ enabled |

Monitors budaknetmail@gmail.com IMAP every 30s. On new email: runs gmail_monitor, approval_orchestrator, and founder_notifier instantly — faster than 1-min cron polling.

```bash
# Status
systemctl --user status ithalat-trigger-daemon.service

# Logs
journalctl --user -u ithalat-trigger-daemon -n 50 --no-pager

# Restart if needed
systemctl --user restart ithalat-trigger-daemon.service
```

## System Email Template Audit — Keeping Approval Emails Readable

The approval email pipeline has a recurring pattern: email subjects and bodies lack context, making the founder's inbox unreadable. When this happens, use the following audit methodology.

### Email Quality Categories (from batuhan@budak.net inbox)

| Category | Quality | Readable? | Subject Pattern |
|----------|---------|-----------|-----------------|
| Approval Manager | ❌ Berbat (was fixed June 28) | No context | `[Onay Gerekli] go_no_go_decision - HASH` |
| Research Agent | ✅ İyi | Company + score + product | `[Research Agent] 5 UK Pazar Fırsatı — Dardanel...` |
| Supplier Discovery | ✅ İyi | Company names listed | `[Supplier Discovery] 5 yeni tedarikci...` |
| Reporting Agent | ⚠️ Tartışmalı | Numbers OK, approvals listed as hash | `[Gunluk Rapor] 28 June 2026` |

**The 80/20 rule:** Approval Manager emails account for ~80% of inbox volume but ~95% of incomprehensible emails. Fixing this one agent's template resolves most of the readability problem.

### Audit Procedure

When the founder says "emails are incomprehensible":

1. **List the inbox** — Check ALL senders, not just the one complained about:
   ```bash
   himalaya envelope list --account budaknet --folder INBOX --page-size 100
   ```
2. **Count readable vs unreadable** — Approximate ratio determines root cause:
   - 80%+ unreadable → template issue in the sender's script
   - 50/50 → mixed templates, code regression (different agents using different template versions)
   - All unreadable → systematic issue (e.g., a shared `send_agent_email()` wrapper)
3. **Read representative samples** — Read one "good" and one "bad" email body to see the exact template difference
4. **Trace the code path** — Compare the good email's template fields against the bad one's. The good one has `Ne: Go/No-Go Decision — Company Name` and `Skor: N/100`; the bad one has `Ne: go_no_go_decision` and `Finansal Etki: £0.00`. This tells you they came from different code paths or were generated at different versions.
5. **Check ERPNext** — Query the Approval Request records to see if they have `related_document` populated. If yes, the email template just isn't using it. If no, the upstream agent isn't setting the relation.
6. **Look up the Opportunity Cases** — For approvals that DO have `related_document`, check if the Opportunity Case title is populated.
7. **Fix the template** — The fix is always in the email-sending script. The `lookup_opportunity_case()` helper in `ithalat_founder_notifier.py` provides the pattern:
   ```python
   def lookup_opportunity_case(erp, related_document):
       if not related_document:
           return None, None, None
       try:
           oc = erp.get("Opportunity Case", related_document)
           if oc:
               return oc.get("title"), oc.get("product_category"), oc.get("status")
       except Exception:
           pass
       return None, None, None
   ```
8. **Verify the fix** — Check the subject line generates something like `[Onay Gerekli] Go/No-Go: Ozdilek Tekstil — Home Textiles (score=62)` instead of `[Onay Gerekli] go_no_go_decision - HASH`.

### Related Issue: Reporting Agent Also Lists Approvals by Hash

The `[Gunluk Rapor]` pending approvals section uses the same raw hash pattern:
```
--- BEKLEYEN ONAYLAR (50) ---
- dt7hu37pqd: go_no_go_decision (High) [Trade Readiness]
```
This has the same problem — the founder sees hashes, not company names. The report accesses `Approval Request` records; each record has `related_document` pointing to an Opportunity Case. A future fix should enrich this section with OC titles.

### Verification: Readable Subject Examples

**❌ Before fix (June 28):**
```
[Onay Gerekli] go_no_go_decision - dt7hu37pqd
```

**✅ After fix:**
```
[Onay Gerekli] Go/No-Go: Ozdilek Tekstil — Turkish Home Textiles UK Import Opportunity (score=62)
```

**✅ Other good agents:**
```
[Research Agent] 2 yeni firsat: Pinar Sut & Ozdilek - Skor 55 & 62
[Supplier Discovery] 5 yeni tedarikci eklendi - Ulker, Marmarabirlik, Fiskobirlik...
```

## Pitfalls

1. **ERPNext CSRF required** — All POST/PUT/DELETE must include `X-Frappe-CSRF-Token` header. The helper script fetches it from /desk page HTML. Without it, API returns 403 Forbidden.

2. **ERPNext naming** — Custom DocTypes auto-generate hash names. `record.get("name")` returns the hash. Tasks use sequential naming (TASK-2026-00001).

3. **Docker on WSL** — Must start daemon after WSL reboot: `sudo dockerd &`. Socket permissions: `sudo chmod 666 /var/run/docker.sock`. Docker group membership requires new login session. See `references/scheduler-db-health-check.md` for cron monitoring.

4. **Himalaya account switching** — v1.2.0 lacks `--account` flag. Change `default=true` in `~/.config/himalaya/config.toml`, execute command, change back.

5. **Google Workspace email mismatch** — Wrong email in config produces "Invalid credentials" even with correct password. Double-check the exact login email (e.g. batuhan@ vs batu@).

6. **no_agent cron jobs** — Script-only jobs must have all imports self-contained. They can't access hermes_tools or Hermes internal APIs. Output is delivered as plain text.

7. **Plus-address CC detection** — When founder CC's `budaknetmail+pricing@gmail.com`, the To field contains the supplier and Cc contains the plus-address. The monitor detects the local-part ("budaknetmail") in both fields using substring matching.

8. **Agent mailbox rule** — ONE inbox for ALL agents. Agent identity is tracked only in ERPNext (Agent Profile + Agent Action Log.actual_agent).

9. **External email policy** — Draft auto, send requires founder approval. Never send autonomously.

10. **no_agent=True scripts MUST be silent when empty** — The cron scheduler delivers stdout verbatim when no_agent=True. If your script prints `{"count": 0}` or any progress/debug lines, the user gets those every tick. Pattern:
    ```python
    if __name__ == "__main__":
        result = run()
        if result["processed"] > 0 or result.get("all_ok") == False:
            print(json.dumps(result))  # only print when there's actual work or failures
    ```
    Also ensure `run()` itself doesn't `print()` intermediate lines (progress bars, check names, timestamps). Collect output in a list and only emit it conditionally at the end. The user corrected this twice — every script that runs on a cron schedule must follow this pattern.

11. **Approval Request `approval_status` only accepts specific values** — `Pending`, `Approved`, `Rejected`, `Modified`. Do NOT write `"Completed"` — it causes HTTP 417. Use `"Modified"` to mark an approval as processed after executing its action. See `references/approval-doctype-select-options.md` for all DocType select-field options in this system.

12. **Concurrent ERPNext logins crash** — When multiple `no_agent=True` scripts run at the same second (e.g. orchestrator@:00, crm@:00, supplier@:00), each creates an independent `ERPNext()` session with a login POST. Frappe's session handling doesn't serialize concurrent logins, causing HTTP 500/timeout on some. Fixed by:
    - **Staggered cron schedules** — Use minute-offset CRON expressions so no two ithalat jobs align. Pattern: `1-59/2`, `2-59/3`, `3-59/3`, etc. Never use bare `every N` for multiple agent scripts.
    - **Retry in `ERPNext.__init__`** — The constructor retries up to 3 times with exponential backoff (1.0s, 1.5s, 2.0s). This recovers from transient login conflicts without crashing the script.

13. **Standard ERPNext DocTypes have strict Select-field enums** — `Supplier.supplier_type` is `Company|Individual|Partnership`, NOT `Local`. Using invalid values causes HTTP 417. See `references/standard-doctype-field-options.md` for all standard doctype field constraints in this system.

14. **Preserve `sys.path.insert` when refactoring imports** — When moving shared SMTP/email code into `ithalat_erpnext_api.py`, don't remove the `sys.path.insert(0, os.path.expanduser("~/.hermes/scripts"))` line from each script. Cron jobs run with `no_agent=True` where PYTHONPATH doesn't include `~/.hermes/scripts`. Without this insert, `from ithalat_erpnext_api import ...` fails silently at runtime. Every ithalat script that imports the API helper needs this line near the top, after `import sys, os`.

15. **Supplier Research DocType has NO `source`, `research_notes`, `district`, or `address` field** — When writing supplier discovery scrapers (e.g. `ithalat_ostim_scraper.py`), map these fields carefully:
    - Use `supplier_name`, `city`, `website`, `contact_email`, `phone`, `product_category`, `notes`, `verification_status` (these exist)
    - Do NOT use `source`, `research_notes`, `district`, `address`, `email` — they cause HTTP 417. Use `notes` for free-text notes and `contact_email` for email.
    - For deduplication, query all existing records by `supplier_name` and `website` (no filter on `source` since it doesn't exist).

16. **LLM agent prompts should be self-contained and include exact terminal commands** — When authoring `no_agent=False` cron prompts for ITHALAT agents, always include working Python one-liners that the agent can copy-paste into `terminal()`. The prompts reference the `ithalat-agent` skill for context but the task instructions must be explicit about which tools to call, in what order, and what exact ERPNext fields to use. See `references/llm-agent-prompt-guide.md` for the template.

17. **Per-task timeout via `signal.alarm` for slow network scripts** — The Research Agent (`ithalat_agent_research.py`) scrapes DuckDuckGo HTML for Amazon/eBay/Etsy pricing, which can hang indefinitely (DDG rate-limiting, slow responses). Each individual HTTP search can take up to 24s (12s POST + 1s retry delay + 12s retry). With 6+ searches per task, even a single task can timeout the 120s cron limit.

    Solution: wrap the per-task processing function with `signal.SIGALRM`:
    ```python
    import signal
    class TimeoutError(Exception): pass
    def timeout_handler(signum, frame): raise TimeoutError("Task took too long")
    
    def process_task(erp, task, per_task_timeout=60):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(per_task_timeout)
        try:
            return _process_task_inner(erp, task)
        except TimeoutError:
            # Leave task Open, will retry next tick
            erp.log_action(agent_name="...", action_type="task_timeout", ...)
            return {"error": "timeout"}
        finally:
            signal.alarm(0)  # disarm
    ```

    Also limit tasks per tick with `max_tasks=2` so backlog doesn't compound. This pattern applies to any script making external HTTP requests at scale.

    ⚠ `signal.alarm` is per-process, not per-thread. The `finally: signal.alarm(0)` must execute between tasks, which the for-loop wrapper ensures. Nested SIGALRM contexts are NOT supported — disarm before returning.

23. **`html` module shadowed by local variable** — When importing `html` (Python stdlib for `html.unescape()`) in the same function that stores HTML content in a variable named `html`, the local variable shadows the module. Always rename the content variable to `raw_html` to avoid `'str' object has no attribute 'unescape'` errors.

24. **`send_agent_email()` REQUIRES `plus_tag` for every agent** — Every call to `send_agent_email()` MUST pass a `plus_tag` matching the agent's identity in the identity table (see §Agent Email Identity). The default `plus_tag=None` produces the bare `budaknetmail@gmail.com`, breaking inbox filtering. Both mechanical scripts and LLM agent prompts must include `plus_tag`.

25. **SIGALRM does NOT reliably interrupt `requests` library calls** — Python's `signal.alarm()` raises `TimeoutError` only when Python bytecode executes, NOT when blocked in a C-level socket call inside `requests`/`urllib3`. The Research Agent's SIGALRM timeout is a safety net for Python-level hangs, NOT a guarantee. The **real fix** is reducing HTTP timeouts directly (DDG from 12s→6s) and removing retry logic. When writing scripts that make external HTTP calls, reduce `timeout=` parameter on `requests.get()`/`requests.post()` rather than relying on SIGALRM to interrupt socket waits.

26. **Mechanical agent cron jobs MUST use `deliver='local'`** — The founder does not want JSON/stdout notifications from no_agent=True scripts. Set `deliver='local'` on every ithalat mechanical cron job so output is saved to `~/.hermes/cron/output/` instead of sent to the user's chat. Only cron jobs the user explicitly asks to see should use `deliver='origin'`. Error notifications from the scheduler still arrive regardless of deliver setting.

27. **`max_tasks` must account for cron timeout** — Research agent runs every 5 minutes with 120s cron timeout. Each task takes up to 60s (SIGALRM). `max_tasks=2` gives 120s which hits the limit exactly. Always leave headroom: set `max_tasks=1` so a single 60s task completes well within 120s, leaving room for DB queries and logging.

28. **Pricing Agent sends good-margin results to Trade Readiness** — When `gross_margin > 15%`, the pricing agent (`ithalat_agent_pricing.py`) sends an Agent Bus `result` message to "Trade Readiness" with subject `"Good margin: {product} — {margin}%"`. The Orchestrator catches this and creates a `[Trade Readiness]` task. The 15% threshold is in the pricing agent code — adjust in `ithalat_agent_pricing.py` if needed.

29. **`ERPNext.get_list()` default limit=50 causes cascading duplicates in dedup checks** — The `ERPNext.get_list()` method defaults to `limit=50`. When used for dedup checks (e.g., checking whether a notification was already sent or a task already exists), only the 50 most recent records are considered. Beyond that threshold, the dedup silently fails and the script creates/sends duplicates on every tick. This cascades through the pipeline:

    ```
    Trade Readiness ──(limit=50 dedup)──→ duplicate Go/No-Go Tasks every 30m
        → Approval Agent ──→ duplicate Approval Requests every 5m
            → Founder Notifier ──(limit=50 dedup)──→ duplicate emails every 60m
    ```

    **Fix pattern — ALWAYS pass explicit large limit for dedup queries:**
    ```python
    # BAD — default limit=50, misses records beyond 50th
    existing = erp.get_list("Founder Email Notification",
        filters=[["notification_type", "=", "approval_request"]],
        fields=["related_document"])

    # GOOD — explicit large limit covers all records
    existing = erp.get_list("Founder Email Notification",
        filters=[["notification_type", "=", "approval_request"]],
        fields=["related_document"],
        limit=10000)
    ```

    **Affected scripts — FIXED 2026-06-25/26 🛠️:**
    - `ithalat_trade_readiness.py` — task dedup: `limit=10000` added. ALSO: after creating a Go/No-Go task, the opportunity status is updated to `"Pending Approval"` so subsequent ticks won't re-process it even if dedup misses.
    - `ithalat_founder_notifier.py` — notification dedup: `limit=10000` added. Each approval now gets exactly ONE email.
    - `ithalat_agent_approval.py` — task query already used `limit=1000` (coincidentally correct).
    
    **Double-safety pattern:** Always pair `limit=10000` with a source-record status update. The limit prevents silent misses; the status update prevents re-processing even if dedup somehow fails.

    **Verification:** To check if dupes are accumulating, inspect the inbox or ERPNext:
    ```bash
    # Count duplicate approval emails in budaknet inbox
    himalaya envelope list --account budaknet -s 200 -p 1 2>&1 | grep -c "Onay Gerekli"
    
    # Check for duplicate Approval Requests by counting distinct decision IDs
    # vs. total Approval Request count in ERPNext
    ```
    
    See `references/approval-duplicate-debugging.md` for the full debugging chain from the June 2025 email storm incident.

30. **Agent Orchestrator work tracking** — The orchestrator (`ithalat_agent_orchestrator.py`) has a `compile_work_status()` function that queries ERPNext for open tasks grouped by agent prefix. Agents can request a status report by sending a `question`-type Agent Bus message to "Agent Orchestrator" with subject containing "status" or "work". The orchestrator replies with the compiled report.

31. **ALL mechanical agents now send Agent Bus messages** — In addition to creating ERPNext Tasks for downstream work, these agents also send Agent Bus messages:
    - Research Agent → Supplier Agent + Pricing Agent (`command`)
    - Supplier Agent → CRM Agent (`result`)
    - CRM Agent → Research Agent (`result`)
    - Pricing Agent → Trade Readiness (`result`, when margin >15%)
    - Any agent → Agent Orchestrator (`notification`, work report after each tick)
    
    This dual-path (Task + Message) ensures visibility and resilience: Tasks provide durable queueing, messages enable real-time chaining. When modifying an agent, always add the bus message alongside the Task creation.

32. **ERPNext container crash recovery — "backend:8000 host not found"**

    **Quick fix** — check which services are actually running:
    ```bash
    docker compose -f ~/erpnext/docker-compose.yml ps
    ```
    If backend is missing or restarting, start it:
    ```bash
    docker compose -f ~/erpnext/docker-compose.yml up -d backend
    # Wait 10s, then
    docker compose -f ~/erpnext/docker-compose.yml restart frontend
    ```

    **Full restart** — if the above doesn't work (backend still crash-looping), do a clean restart. This re-creates the Docker network, fixing DNS resolution:
    ```bash
    docker compose -f ~/erpnext/docker-compose.yml down
    sleep 5
    docker compose -f ~/erpnext/docker-compose.yml up -d
    ```

    **Boot time** — ERPNext takes 30-60 seconds after `up -d` before port 8080 responds. The frontend container status says "Up" immediately but nginx needs the backend to be reachable. Wait 60s before testing:
    ```bash
    # After compose up -d, wait:
    sleep 45
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
    # 200 = ready, 000 = not ready yet
    ```

33. **`ERPNext` connector may throw `ConnectionResetError` when container just started** — If you call `ERPNext()` immediately after `docker compose up`, the connection resets because the backend is still booting gunicorn. **Pattern:** retry with a delay rather than failing immediately. The `ERPNext.__init__` already retries login 3 times, but the connection reset happens before login (at TCP level). Wrap the entire query in a retry:
    ```python
    import time
    for attempt in range(3):
        try:
            erp = ERPNext()
            opps = erp.get_list(...)
            break
        except (ConnectionResetError, ConnectionError):
            if attempt == 2: raise
            time.sleep(5)
    ```

34. **`requested_by_agent` NOT `requested_by` when creating Approval Requests**
    ```python
    # CORRECT:
    erp.create("Approval Request", {"requested_by_agent": "Trade Readiness", ...})
    
    # EVEN BETTER — use the helper that already has the right field name:
    erp.create_approval(requested_by="Trade Readiness", action_type="go_no_go_decision", ...)
    ```
    
    Applied to `ithalat_agent_approval.py` on 2026-06-26. Check any new script that creates Approval Requests for this bug.

35. **Approval email subjects must include opportunity context** — The `send_approval_request()` function in `ithalat_founder_notifier.py` originally used a generic subject: `[Onay Gerekli] go_no_go_decision - <hash>`. This makes approval emails incomprehensible because the recipient has no idea what product/company the decision is about.

    **Fix pattern — always enrich approval emails with Opportunity Case context:**
    ```python
    def send_approval_request(approval):
        related_doc = approval.get("related_document", "")
        
        # Look up the Opportunity Case for company/product context
        if related_doc:
            oc = erp.get("Opportunity Case", related_doc)
            if oc:
                display_name = oc.get("title", "")  # e.g. "Aydin Celik Kasa — Steel Safes"
                score = extract_score(recommendation)
                subject = f"[Onay Gerekli] Go/No-Go: {display_name} (score={score})"
    ```
    
    The Approval Request's `related_document` field stores the Opportunity Case hash. Always query it before sending the email. The body should include: Fırsat adı, Kategori, Durum, Skor, Risk seviyesi, Finansal etki.
    
    Applied to `ithalat_founder_notifier.py` on 2026-06-28. Any new script or prompt that sends approval emails must follow this pattern — the founder checks email on mobile and needs to know what the decision is about from the subject line alone.
