# Agent Message Bus — Full Reference

SQLite-based inter-agent communication for the İthalat Agent system.

## Architecture

```
Agent A ──send()──→ agent_bus.db ──get_messages()──→ Agent B
                                            ↕
                                     Agent Orchestrator
                                     (routes, tracks, replies)
```

- **Library:** `ithalat_agent_bus.py`
- **DB path:** `~/.hermes/data/agent_bus.db`
- **Persistence:** WAL mode, 7-day cleanup, thread-safe via thread-local connections

## Schema

```sql
CREATE TABLE agent_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    from_agent      TEXT NOT NULL,       -- sender name (e.g. "Research Agent")
    to_agent        TEXT NOT NULL,       -- recipient name
    subject         TEXT,                -- short label, max 200 chars
    body            TEXT,                -- full message content
    msg_type        TEXT DEFAULT 'notification',  -- see Message Types below
    related_doctype TEXT,                -- ERPNext DocType link
    related_docname TEXT,                -- ERPNext document name
    thread_id       TEXT,                -- UUID for conversation threading
    status          TEXT DEFAULT 'unread',  -- unread | read | processed
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_to_status ON agent_messages(to_agent, status);
```

## Message Types

| Type | Direction | Meaning | Handler Pattern |
|------|-----------|---------|-----------------|
| `command` | A → B | "Execute this task" | Create Task, reply with name |
| `result`  | A → B | "Completed X, here's what I found" | Chain to next agent |
| `question` | A → B | "What do you think about X?" | Orchestrator answers |
| `answer`  | B → A | Reply (in same thread_id) | Orchestrator routes |
| `notification` | Any → Orchestrator | Work report / FYI | Logged to Agent Action Log |

## API

### `AgentMessageBus()`

Initialize message bus. Creates DB + tables on first use.

```python
from ithalat_agent_bus import AgentMessageBus
bus = AgentMessageBus()
```

### `send(from_agent, to_agent, subject="", body="", msg_type="notification", related_doctype=None, related_docname=None, thread_id=None)`

Send a message. Auto-generates thread_id if not provided.

```python
bus.send("Research Agent", "Supplier Agent",
         subject="Find suppliers for: Olive Oil",
         body="UK market analysis done. Score: 65/100.",
         msg_type="command",
         related_doctype="Opportunity Case",
         related_docname="OC-0001")
```

### `get_messages(agent_name, msg_type=None, limit=10)`

Get unread messages for an agent. Returns list of dicts.

```python
for msg in bus.get_messages("Supplier Agent", limit=5):
    print(msg["subject"], msg["body"][:100])
    bus.mark_processed(msg["id"])
```

### `mark_processed(msg_id)` / `mark_processed_bulk(msg_ids)`

Mark messages as processed (sets status='processed').

### `get_conversation(thread_id)`

Get all messages in a conversation thread, ordered chronologically.

### `reply(original_msg_id, from_agent, to_agent, body="", msg_type="answer")`

Reply to an existing message (same thread_id, subject prefixed "Re:").

### `count_unread(agent_name)`

Get unread message count for an agent.

### `ask(from_agent, to_agent, question, related_doctype=None, related_docname=None)`

Shorthand: send a `question`-type message.

### `cleanup_old(days=7)`

Delete messages older than N days. Called by orchestrator periodically.

## Chained Operations (Active)

All chains below are live. Each step creates BOTH an ERPNext Task (durable queue) AND an Agent Bus message (real-time awareness).

```
Research Agent ──command──→ Supplier Agent ──result──→ CRM Agent ──result──→ Research Agent
      │                              ↑                                     (loop complete)
      └──command──→ Pricing Agent ───┘
                         ↓ (margin >15%)
                   Trade Readiness → Approval
```

### Orchestrator Message Routing

The orchestrator (`ithalat_agent_orchestrator.py` at `~/.hermes/scripts/`) uses a `MESSAGE_HANDLERS` dict:

```python
MESSAGE_HANDLERS = {
    ("Research Agent", "command"): [
        # "Find suppliers for: X" → Supplier Agent task
        # "Price analysis for: X" → Pricing Agent task
    ],
    ("Supplier Agent", "result"): [
        # "Supplier registered: X" → CRM Agent task
    ],
    ("CRM Agent", "result"): [
        # "Contact created: X" → Research Agent loop complete
    ],
    ("Pricing Agent", "result"): [
        # "Good margin: X — Y%" → Trade Readiness task
    ],
    ("Trade Readiness", "result"): [
        # "Grant" in subject → email alert to founder
    ],
    (None, "notification"): [
        # Work reports from any agent → Agent Action Log
    ],
    (None, "question"): [
        # "status" or "work" in subject → compile_work_status()
        # Other questions → system status reply
    ],
}
```

## Work Status Query

Any agent (or the founder) can query work status:

```python
from ithalat_agent_bus import AgentMessageBus
bus = AgentMessageBus()

# Ask Orchestrator for status
bus.send("Founder", "Agent Orchestrator",
         subject="status report",
         msg_type="question")

# Orchestrator replies via bus with open tasks per agent + pending approvals
# Read answer:
for msg in bus.get_messages("Founder", limit=1):
    print(msg["body"])
```

Or query directly from Python:
```python
from ithalat_agent_orchestrator import compile_work_status
from ithalat_erpnext_api import ERPNext
print(compile_work_status(ERPNext()))
```

## Performance Notes

- DB uses WAL mode — concurrent reads don't block
- `busy_timeout=5000` — 5s wait on write contention
- Thread-local connections via `threading.local()` — safe for multi-agent orchestration
- Index on `(to_agent, status)` — unread queries are fast regardless of total message count
- ~50 bytes per message (excluding body) — 100K messages ≈ 5MB
