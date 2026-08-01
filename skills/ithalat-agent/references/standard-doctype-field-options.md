# ERPNext Standard DocType — Select Field Options & Constraints

Non-obvious constraints on standard ERPNext DocTypes encountered during agent script development. Using invalid values causes HTTP 417 errors.

## Customer

| Field | Valid Options | Required |
|-------|---------------|----------|
| `customer_type` | `Company`, `Individual`, `Partnership` | ✅ Yes |
| `customer_name` | Free text | ✅ Yes |
| `customer_group` | Must exist as a Customer Group record. Default: `All Customer Groups` | ❌ No |
| `territory` | Must exist as a Territory record. Default: `All Territories`, `United Kingdom` | ❌ No |

**Wrong:**
```python
erp.create("Customer", {"customer_type": "Local"})
# → HTTP 417: EXPECTATION FAILED
```

**Correct:**
```python
erp.create("Customer", {
    "customer_name": "BlueCo Ltd",
    "customer_type": "Company",
    "customer_group": "All Customer Groups",
    "territory": "United Kingdom"
})
```

## Supplier

| Field | Valid Options | Required |
|-------|---------------|----------|
| `supplier_type` | `Company`, `Individual`, `Partnership` | ✅ Yes |
| `supplier_name` | Free text | ✅ Yes |
| `supplier_group` | Must exist as a Supplier Group record. Fresh ERPNext defaults may not have `All Supplier Groups` — omit if missing. | ❌ No |

**Wrong:**
```python
erp.create("Supplier", {"supplier_type": "Local"})
# → HTTP 417: EXPECTATION FAILED
```

**Correct:**
```python
erp.create("Supplier", {"supplier_type": "Company"})
# Omit supplier_group unless verified it exists
```

## Contact

| Field | Valid Options | Required |
|-------|---------------|----------|
| `first_name` | Free text | ✅ Yes |
| `last_name` | Free text | ❌ No |
| `status` | `Passive`, `Open`, `Replied` | ❌ No |
| `email_ids` | Array of `[{"email_id": "x@y.com", "is_primary": 1}]` | ❌ No |

**Correct usage:**
```python
erp.create("Contact", {
    "first_name": "John",
    "last_name": "Smith",
    "status": "Open",
    "email_ids": [{"email_id": "john@blueco.com", "is_primary": 1}]
})
```

## Task

| Field | Valid Options | Required |
|-------|---------------|----------|
| `status` | `Open`, `Working`, `Pending Review`, `Overdue`, `Template`, `Completed`, `Cancelled` | ❌ No |
| `priority` | `Low`, `Medium`, `High`, `Urgent` | ❌ No |
| `subject` | Free text | ❌ No |

**Note:** `Template` is a valid status — but agents should never set it; it's for ERPNext's Gantt/Task template feature.

## Quotation

| Field | Valid Options | Required |
|-------|---------------|----------|
| `order_type` | `Sales`, `Maintenance`, `Shopping Cart` | ✅ Yes |
| `apply_discount_on` | `Grand Total`, `Net Total` | ❌ No |
| `status` | `Draft`, `Open`, `Replied`, `Partially Ordered`, `Ordered`, `Lost`, `Cancelled`, `Expired` | ✅ Yes |

## Common Errors with Standard DocTypes

| Wrong Value | DocType | Correct Value |
|-------------|---------|---------------|
| `"Local"` on `supplier_type` | Supplier | `"Company"` |
| `"Local"` on `customer_type` | Customer | `"Company"` |
| Missing `customer_type` | Customer | Set to `"Company"` or `"Individual"` |
| Missing `supplier_type` | Supplier | Set to `"Company"` or `"Individual"` |
| `customer_group` that doesn't exist | Customer | Omit the field entirely |
| `supplier_group` that doesn't exist | Supplier | Omit the field entirely |
