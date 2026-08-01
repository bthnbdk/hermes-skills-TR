# Trade Readiness — Grant Application Matching

The `ithalat_trade_readiness.py` script (cron: `8-59/30`) evaluates New Opportunity Cases and, for scores ≥40, matches them to grant programs by creating Grant Application Records.

## Matching Logic (`match_grants_to_opportunity()`)

```
Opportunity Case (score ≥40)
  → List all Grant Opportunity Records from DB
  → For each grant, check if application already exists (dedup by support_program)
  → Apply match rules:
      • KOSGEB → always match (general SME support)
      • Eximbank → always match (export financing)
      • Ticaret Bakanlığı → always match (export supports)
      • Kolay Destek → always match (broad support)
      • E-İhracat/E-Ticaret → always match (e-export)
  → Create Grant Application Record with status "Not Started"
  → Log action
```

### Deduplication

Before creating a Grant Application Record, the script checks if one already exists for the same `support_program` + `grant_opportunity` combination. If found, it skips — no duplicate applications.

### Grant Application Record Fields

| Field | Value |
|-------|-------|
| `grant_opportunity` | Link to Grant Opportunity Record name |
| `support_program` | Program name (e.g. "Ticaret Bakanligi - Ihracat Destekleri") |
| `application_status` | `Not Started` (initial) |
| `responsible_agent` | `Orchestrator Agent` |
| `required_documents` | Reference to Opportunity Case name + score |

## Go/No-Go Approval Task (score ≥50)

For scores ≥50, the script also creates an `[Approval Manager] Go/No-Go: {title}` task. This task flows through the existing pipeline:

1. Trade Readiness creates the task → status: Open
2. Approval Manager (cron: `5-59/5`) picks it up on next tick
3. Approval Manager creates an Approval Request for the founder
4. Founder receives email notification from `ithalat_founder_notifier.py` (every 1h)
5. Founder replies → Email Gateway parses decision → Approval Manager processes

## All 3 Records Created by Trade Readiness

For every New Opportunity Case, the script creates/updates **3 DocType records**:

| DocType | Purpose | Key Fields |
|---------|---------|------------|
| Import Readiness Record | UK-side trade readiness | commodity_code, tariff_check_status, compliance_status, incoterms |
| TR Export Readiness Record | Turkey-side export readiness | turkey_company_status, exporter_union_status, customs_agent_status |
| Supplier Export Flow Record | Supplier documentation | export_documentation_ready, exporter_union_member, customs_broker_contacted |

See `references/approval-doctype-select-options.md` for valid Select field values for these DocTypes.

## No-Go Logic

- Score 0-39: no grant matching, no go/no-go task. Only the 3 readiness records are created.
- Score 40-49: grant matching active, but no founder go/no-go question yet.
- Score 50+: full chain — readiness records + grant matching + approval task.
