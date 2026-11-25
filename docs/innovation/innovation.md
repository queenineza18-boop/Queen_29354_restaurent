# Innovation plan — Oracle APEX `ROSTS Console`

**Option chosen:** user interface / interactive application and analytics dashboard.
**Tool:** Oracle APEX, connected to the project's own Oracle pluggable database (`ROSTS_PDB`),
APEX installed in the same database (no separate application server).

**Status:** planned in Phase 0. No APEX application has been built or connected yet. Phase VII
must add setup instructions, screenshots and a live demonstration against the actual project
database.

## Why this option

The rules live in PL/SQL, so the interface can be replaced without touching correctness. APEX
gives the two screens a restaurant actually needs — order entry and a manager dashboard — with
no per-terminal licence, no compiled client and no separate web server, which matters for a
business with fewer than four staff (NISR, 2024). It also exposes the database layer the
commercial POS hides: a marker can see the procedure a button calls, the trigger that fired and
the audit row it wrote.

## Planned pages

| Page | Who | What it calls |
| --- | --- | --- |
| **Order entry** | Cashier | `sp_place_order`, `sp_add_order_line` — product buttons, quantity, live bill from `fn_order_total` |
| **Payment** | Cashier | `sp_record_payment`, `fn_payment_balance` — amount, method, change/balance shown |
| **Receipt view** | Cashier, Manager | `v_daily_sales` filtered by receipt number |
| **Manager dashboard** | Manager | `v_daily_sales`, `v_top_items`, `v_low_stock` — revenue per outlet per day, best sellers, payment mix |
| **Low-stock alerts** | Manager | `v_low_stock` with a badge count in the navigation bar |
| **Audit monitor** | Manager only | `v_audit_recent` — read-only list of price changes, deletions and refused operations |
| **Menu maintenance** | Manager | `MENU_ITEM` form; price change goes through `sp_change_price` so `PRICE_HISTORY` and `AUDIT_LOG` are written |

## Implementation rule (the point of the innovation)

The APEX pages **call** PL/SQL; they do not contain business rules. No page computes a total,
checks stock, or decides whether a discount is allowed — `sp_place_order`, `sp_record_payment`,
`fn_order_total` and the triggers do that. A page can therefore be edited, duplicated or
replaced without creating an inconsistency, and the same rules protect a SQL*Plus session.

## Demonstration plan (Phase VII)

1. Sell a drink: stock of the ingredient drops by the recipe quantity, `STOCK_MOVEMENT` gains a
   row, the bill shown equals `fn_order_total`.
2. Try to sell an item whose ingredient is below the required quantity: APEX shows the
   `-20001` message and no order is created.
3. Try to apply a 50 % discount as a cashier: refused with `-20005`; as a manager: allowed and
   audited.
4. Pay a receipt, then try to edit it: `-20002`.
5. Open the dashboard: the same day's revenue and payment mix that `fn_daily_revenue` returns.
6. Open the audit monitor: every refused attempt above is listed with the database user.
