# Phase 0 presentation — Restaurant Order and Sales Tracking System (ROSTS)

Queen Ineza · 29354 · INSY 8311 · 12 slides

---

## Slide 1 — Title

**Restaurant Order and Sales Tracking System (ROSTS)**
Automating order management, billing, stock and sales reporting in Oracle PL/SQL

Queen Ineza — Student ID 29354
INSY 8311 Database Development with PL/SQL · Instructor: Eric Maniraguha
AUCA · 2026–2027 Semester I · Phase 0

---

## Slide 2 — The problem in one shift

- A waiter writes the order on a pad; the cashier **re-adds the bill by hand**.
- Payment arrives by cash or mobile money, **separate from the receipt**.
- Stock is counted **weekly by eye**, not per sale.
- Price changes, discounts and deleted receipts leave **no trace**.
- "What did we sell last Tuesday?" is answered **from memory**.

---

## Slide 3 — Why it matters in Rwanda

- 269,326 establishments in the 2023 Establishment Census; **accommodation and food services
  = 23.0 %** — second largest activity (NISR, 2024).
- The same activity employs **12.9 %** of 927,739 workers.
- **92.2 %** of establishments are micro-enterprises with **fewer than four workers**.
- Small enough to need the system; too small to buy and configure an enterprise POS.

---

## Slide 4 — What the research says

- 385 restaurant employees surveyed: with a management system, staff report **easier
  operations, higher sales, more standard service** — but **everyone rates the technical cost
  high**, and the least positive responses come from restaurants with **≤ 10 staff**
  (Memis Kocaman, 2021).
- Restaurant inventory fails on **perishability**: over-buying, expiry, shrinkage; the design
  must follow how that kitchen really buys, stores and consumes (Zamora Saltos & Rodríguez
  Borges, 2024).

**The gap both papers leave open: where do the rules live?** In the systems they describe,
correctness depends on the application.

---

## Slide 5 — The solution

One Oracle pluggable database, **`ROSTS_PDB`**, 15 normalised tables, **all rules in PL/SQL**:

- `sp_place_order` writes the receipt and its lines in one transaction.
- A trigger prices each line from the menu; functions compute net, 11 % tax and total.
- The sale itself **decrements ingredient stock** through the recipe table.
- Payment rules are **enforced, not advised**.
- Price changes and deletions go to `AUDIT_LOG`.
- Reporting is **SQL**, not spreadsheet.

---

## Slide 6 — Four rules the database will not break

| Rule | Enforcement | Error |
| --- | --- | --- |
| Cannot sell what is not in stock | `trg_line_stock` | `-20001` |
| Cannot edit a paid receipt | `trg_order_totals` | `-20002` |
| Cannot pay a cancelled order | `trg_payment_guard` | `-20003` |
| Cannot discount > 20 % without `MANAGER` | `sp_apply_promotion` | `-20005` |

Timing is deliberate: `BEFORE` triggers write `:NEW` (price, totals); `AFTER` triggers write
consequences (stock movement, audit) — that is what Oracle permits at each point (Oracle, 2026a).

---

## Slide 7 — Data source (real, licensed, no personal data)

**Anonymous Transactional Dataset**, v2 — Engel, Gaol, Kurniawan & Budiharto (2026),
Mendeley Data, **CC BY 4.0**, DOI `10.17632/kcgf45y24m.2`.

- Real POS receipts from an F&B micro/small enterprise with **3 outlets**, 2 Jan – 30 Sep 2025.
- **53,820 receipts**, **96 products**, 3 payment methods (`BCA`, `Cash`, `GoFood`), 11 % tax per receipt.
- **No customer name, phone or card number** — only a 0/1 loyalty flag.
- Loaded here: **550 receipts** (`SHOP001`, 2–7 Jan 2025, 13,542,000 total) + 96 products.
- No recipes or stock in the source → those tables are **derived**, and labelled
  `record_source = 'DERIVED'`.

---

## Slide 8 — Fifteen tables, third normal form

`OUTLET` · `STAFF` · `MENU_CATEGORY` · `MENU_ITEM` · `PRICE_HISTORY` · `INGREDIENT` ·
`MENU_ITEM_INGREDIENT` · `PAYMENT_METHOD` · `ORDERS` · `ORDER_LINE` · `PAYMENT` ·
`STOCK_MOVEMENT` · `PROMOTION` · `ORDER_PROMOTION` · `AUDIT_LOG`

The flat receipt (`ReceiptNumber`, `Items`, `TotalItem`, `NetSales`, `Tax`, `TotalAmount`,
`PaymentMethod`) is split into **`ORDERS` → `ORDER_LINE` → `PAYMENT`** in Phase II, with
free-text item names resolved against `MENU_ITEM`.

---

## Slide 9 — Where each PL/SQL feature is used

| Feature | Use in ROSTS |
| --- | --- |
| Procedures | `sp_place_order`, `sp_record_payment`, `sp_close_order`, `sp_apply_promotion` |
| Functions | `fn_order_total`, `fn_order_tax`, `fn_stock_available`, `fn_daily_revenue` |
| Cursors | Monthly sales ranking; low-stock list; cash-up by method; `FOR UPDATE` on stock |
| Package | `pkg_rosts_ops` — one interface for every APEX page |
| Triggers | Price a line, deduct stock, recompute totals, guard payments, audit price and delete |
| Auditing | `AUDIT_LOG`: old/new value, table, record key, database user, time |

---

## Slide 10 — Innovation: Oracle APEX `ROSTS Console`

**Option chosen: user interface — Oracle APEX.**

- **Cashier:** one order screen (product buttons → `sp_place_order`) and a bill the database
  computed; one payment screen (→ `sp_record_payment`).
- **Manager:** dashboard on `v_daily_sales`, `v_top_items`, `v_low_stock` — revenue per outlet
  per day, best sellers, payment mix, low-stock badge, read-only audit log.
- **Why it is the innovation:** no rule lives in a page. The interface *calls* PL/SQL, so it
  cannot be edited into an inconsistency — and the same rules protect SQL*Plus users.
- **Cost:** a browser. No per-terminal licence, no application server.

---

## Slide 11 — Phase 0 deliverables

| Deliverable | Location |
| --- | --- |
| Research log (6 verified sources) | `docs/research/research_log.md` |
| 2-page proposal | `docs/proposal/proposal.md` + `proposal.docx` |
| 12-slide deck | `docs/presentation/phase0_slides.md` |
| Real dataset + provenance | `data/raw/` + `data/README.md` |
| Innovation plan | `docs/innovation/innovation.md` |
| Repository | `github.com/queenineza18-boop/Queen_29354_restaurent` |

Every source link in the log was opened and read; the earlier placeholder links were deleted.

---

## Slide 12 — Next: Phase I

Model the real flow before writing a table:

**customer order → kitchen preparation → bill → payment → stock consumption → cash-up**

- BPMN process for the shift, and a UML swimlane across waiter, cashier, kitchen and manager.
- Then Phase II: 3NF from the flat receipts, ERD, data dictionary.
- Then Phase III–VI: PDB, tables, PL/SQL, triggers and audit.
- Then Phase VII: `ROSTS Console` demo.

**Thank you — questions.**
