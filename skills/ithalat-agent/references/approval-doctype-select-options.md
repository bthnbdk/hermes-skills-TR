# ERPNext Custom DocTypes — Complete Select Field Reference

All 19 custom DocTypes in CRM module. Using a value not in the options list causes **HTTP 417 EXPECTATION FAILED**. Generated from actual ERPNext DocField definitions.

## Agent Profile

| Field | Valid Options |
|-------|---------------|
| `status` | `Active`, `Inactive`, `Disabled` |

## Agent Permission

No Select fields. Uses `agent` (Data) and `doctype_name` (Data).

## Agent Action Log

| Field | Valid Options |
|-------|---------------|
| `risk_level` | `Low`, `Medium`, `High`, `Critical` |
| `status` | `Draft`, `Submitted`, `Cancelled` |

## Approval Request

| Field | Valid Options |
|-------|---------------|
| `risk_score` | `Low`, `Medium`, `High`, `Critical` |
| `approval_status` | `Pending`, `Approved`, `Rejected`, `Modified` |

🚨 **Do NOT use `"Completed"` for `approval_status`** — use `"Modified"` to mark as processed.

## Daily Executive Report

No Select fields. Uses Text fields: `new_opportunities`, `supplier_activity`, `customer_activity`, `pending_approvals`, `risks`, `recommended_actions`.

## Email Thread Summary

| Field | Valid Options |
|-------|---------------|
| `urgency` | `Low`, `Medium`, `High`, `Critical` |
| `risk_level` | `Low`, `Medium`, `High`, `Critical` |

## External Email Draft

| Field | Valid Options |
|-------|---------------|
| `send_status` | `Draft`, `Pending Approval`, `Approved`, `Sent`, `Rejected` |

## Founder Email Notification

| Field | Valid Options |
|-------|---------------|
| `urgency` | `Low`, `Medium`, `High`, `Critical` |
| `founder_reply_status` | `Pending`, `Received`, `Processed` |
| `erpnext_update_status` | `Pending`, `Updated` |

## Founder Instruction

| Field | Valid Options |
|-------|---------------|
| `risk_level` | `Low`, `Medium`, `High`, `Critical` |
| `status` | `New`, `In Progress`, `Completed`, `Cancelled` |

## Grant Application Record

| Field | Valid Options |
|-------|---------------|
| `application_status` | `Not Started`, `In Progress`, `Submitted`, `Approved`, `Rejected` |

## Grant Expense Mapping Record

No Select fields.

## Grant Opportunity Record

| Field | Valid Options |
|-------|---------------|
| `potential_eligibility` | `Unknown`, `Likely`, `Unlikely`, `Advisor Needed` |

## Import Readiness Record

| Field | Valid Options |
|-------|---------------|
| `tariff_check_status` | `Not Checked`, `In Progress`, `Checked`, `Advisor Needed` |
| `turkey_accountant_review_status` | `Not Reviewed`, `In Progress`, `Reviewed` |
| `compliance_status` | `Unknown`, `In Progress`, `Compliant`, `Non-Compliant` |
| `risk_score` | `Low`, `Medium`, `High`, `Critical` |

## Opportunity Case

| Field | Valid Options |
|-------|---------------|
| `status` | `New`, `Under Review`, `Approved`, `Rejected`, `On Hold` |
| `operational_risk` | `Low`, `Medium`, `High` |
| `compliance_risk` | `Low`, `Medium`, `High` |

## Pricing Analysis

No Select fields. Uses Currency fields: `proposed_price`, `landed_cost`, `minimum_acceptable_price`. Data fields: `related_customer`, `related_supplier`, `related_item`. Text: `recommendation`.

## Risk Event

| Field | Valid Options |
|-------|---------------|
| `severity` | `Low`, `Medium`, `High`, `Critical` |
| `status` | `Open`, `In Progress`, `Mitigated`, `Closed` |

## Supplier Export Flow Record

No Select fields. Uses Data: `supplier`, `incoterms_preferred`, `export_invoice_format`. Text: `notes`.

## Supplier Research

| Field | Valid Options |
|-------|---------------|
| `verification_status` | `Unverified`, `Pending`, `Verified`, `Failed` |
| `initial_risk` | `Low`, `Medium`, `High` |

🚨 **NOT** `Rejected` — the actual field uses `Failed` instead. `In Progress` is also invalid.

## TR Export Readiness Record

| Field | Valid Options |
|-------|---------------|
| `turkey_company_status` | `Active`, `Pending`, `Not Registered` |
| `exporter_union_status` | `Not Checked`, `Member`, `Not Member`, `Pending` |
| `customs_agent_status` | `Not Assigned`, `Contacted`, `Assigned` |
| `tariff_check_status` | `Not Checked`, `In Progress`, `Checked`, `Advisor Needed` |
| `compliance_status` | `Unknown`, `In Progress`, `Compliant`, `Non-Compliant` |
| `risk_score` | `Low`, `Medium`, `High`, `Critical` |

## Supplier Export Flow Record

No Select fields. Checkbox fields: `export_documentation_ready`, `exporter_union_member`, `customs_broker_contacted`. Data fields: `supplier`, `export_invoice_format`, `incoterms_preferred`, `notes`.

## Common Agent Script Errors

| Wrong Value | DocType | Correct Value |
|-------------|---------|---------------|
| `"Completed"` on `approval_status` | Approval Request | `"Modified"` |
| `"Rejected"` on `verification_status` | Supplier Research | `"Failed"` |
| `"In Progress"` on `verification_status` | Supplier Research | `"Pending"` |
