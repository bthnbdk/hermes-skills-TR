# Research Agent — Downstream Task Chaining

When the Research Agent creates an Opportunity Case with a go/no-go score ≥30, it auto-creates two downstream tasks:

## Agent Bus Messages (v4.2.0+)

In addition to ERPNext Tasks, the Research Agent now sends **Agent Bus command messages** to Supplier and Pricing Agents when it creates an Opportunity Case (score ≥30):

```python
from ithalat_agent_bus import AgentMessageBus
bus = AgentMessageBus()
bus.send(from_agent="Research Agent", to_agent="Supplier Agent",
         subject="Find suppliers for: {topic}",
         body="UK market analysis...",
         msg_type="command",
         related_doctype="Opportunity Case", related_docname=oc_name)
bus.send(from_agent="Research Agent", to_agent="Pricing Agent",
         subject="Price analysis for: {topic}",
         body="UK price range...",
         msg_type="command",
         related_doctype="Opportunity Case", related_docname=oc_name)
```

The **Agent Orchestrator** (2m tick) reads these messages and converts them into ERPNext Tasks (same as before), then replies to confirm. Both Tasks + Bus messages are created — Tasks for persistence, messages for immediate awareness and conversation threading.

See `references/agent-message-bus.md` for the full API.

## Pipeline Flow

```
Research Agent
  → Creates Opportunity Case (score ≥30)
    → [Supplier Agent] Find suppliers for {product}   (subject prefix match)
    → [Pricing Agent] Price analysis for {product}     (subject prefix match)
  → Creates Opportunity Case (score <30)
    → No downstream tasks (low potential, skip supplier/pricing)
```

## Task Subjects

| Agent | Subject Pattern | Description Includes |
|-------|----------------|---------------------|
| Supplier | `[Supplier Agent] Find suppliers for {topic}` | Opportunity Case name, Go/No-Go score, market analysis summary, action: find Turkish suppliers |
| Pricing | `[Pricing Agent] Price analysis for {topic}` | Opportunity Case name, UK price range, Go/No-Go score, action: calculate landed cost + margin |

## Schedule Timing

Cron jobs are staggered so downstream agents run AFTER the Research Agent finishes:

| Agent | Schedule | Delay from Research |
|-------|----------|-------------------|
| Research | `6-59/5` | — |
| Supplier | `3-59/3` | 0-3 minutes (may need 1-2 ticks) |
| Pricing | `4-59/3` | 0-3 minutes |

If no downstream tasks are found on a tick, the agent silently returns `{"processed": 0}` with no output.

## Score Thresholds (Complete Chain)

Full pipeline has **3 tiers** of downstream activation:

| Score | Action | Where |
|-------|--------|-------|
| **≥30** | Research Agent creates `[Supplier Agent]` + `[Pricing Agent]` tasks | `ithalat_agent_research.py` |
| **≥40** | Trade Readiness matches opportunity to grant programs (KOSGEB, Eximbank, etc.) → creates Grant Application Record | `ithalat_trade_readiness.py` |
| **≥50** | Trade Readiness creates `[Approval Manager] Go/No-Go` task → founder decision pipeline | `ithalat_trade_readiness.py` |

### Why Not Single Threshold?

Each threshold gates a different type of investment:

- **≥30**: Cheap — creating a few ERPNext tasks. Worth it for any moderate signal.
- **≥40**: Moderate cost — grant applications involve paperwork overhead. Only for well-scored opportunities.
- **≥50**: High stakes — asking the founder to make a go/no-go decision. Only for genuinely promising leads.

### Approval Manager Go/No-Go Task

The `[Approval Manager] Go/No-Go` task is created by `ithalat_trade_readiness.py`, not by the Research Agent. This is because the trade readiness evaluation needs to complete first (import readiness, TR readiness, supplier flow) before the founder can make an informed decision.

Task description includes:
- Opportunity name + score
- All 3 trade readiness record names
- Import Readiness Record name
- TR Export Readiness Record name
- Supplier Export Flow Record name

The Approval Manager agent then picks up this task and creates an Approval Request for the founder.

## Sources Used

Research Agent now searches **5 sources** per query:

| Source | Method | Good For |
|--------|--------|----------|
| Amazon UK | DDG site:amazon.co.uk | Product listings + prices |
| eBay UK | DDG site:ebay.co.uk | Product listings + prices |
| Etsy UK | DDG site:etsy.com/uk | Niche/handmade product data |
| Bing News RSS | `bing.com/news/search?q=X&format=rss` | Market trends, news, demand signals (see `references/research-agent-bing-news.md`) |
| Wikipedia | API query + extract | Market context fallback |

All 5 results are merged into `all_results` for go/no-go scoring. Bing results contribute to `unique_sources` and `total_listings` counts but rarely include prices.

## Performance & Timeout

DDG HTML scraping is the bottleneck: each `search_ddg()` call makes a POST to `html.duckduckgo.com/html/` with a 12s timeout + 1s retry delay on 202 status. A single task runs up to **6 DDG calls** (amazon primary+fallback, ebay primary+fallback, etsy primary+fallback) plus Bing News + Wikipedia = potentially 60s+ per task.

**Mitigations implemented:**
- **Per-task 60s SIGALRM timeout**: if a task takes >60s, it's cancelled, left Open, and retried next tick
- **max_tasks=2 per tick**: prevents backlog from accumulating faster than it can drain
- **ERPNext timeout logging**: timed-out tasks get an Agent Action Log entry (`action_type=task_timeout`) so the pattern is observable
- **No retry escalation**: timed-out tasks retry every 5min tick until they succeed or are manually closed

On the initial 487-task OSTİM backlog, this means ~3.5 hours to clear (2 tasks × 12 ticks/hour with some timeouts). Each tick processes 2 tasks @ ~60s max = 120s cron budget used.
