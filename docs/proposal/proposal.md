# Restaurant Order and Sales Tracking System (ROSTS): Automating Billing, Stock and Sales Control in Oracle PL/SQL

**Queen Ineza — Student ID 29354**
INSY 8311 Database Development with PL/SQL · Instructor: Eric Maniraguha
Adventist University of Central Africa · 2026–2027, Semester I · Phase 0 proposal
Repository: `queenineza18-boop/Queen_29354_restaurent`

## 1. Problem

A small restaurant runs on an order pad, a calculator, a cash drawer and a mobile-money
message. The waiter writes the order, the cashier re-adds the bill by hand, and at closing the
manager compares the drawer and the phone messages with a pile of duplicate receipts. Each
instrument fails differently: **the bill is arithmetic done by a person under pressure** (a
line added twice, a price remembered wrongly, a discount nobody authorised); **the money and
the order live apart**, so a payment that cannot be matched to a receipt disappears from the
day's total; **stock is not connected to sales**, so a cappuccino's milk is discovered to be
finished at 12:30 during the peak, or over-ordered and thrown away; **nothing is audited**, so
a changed price or a deleted receipt cannot be attributed to anyone; and **there is no sales
reporting**, so "which item earns most" and "what did we sell last Tuesday" are answered from
memory.

The sector makes this an operational problem worth solving. Rwanda's 2023 Establishment
Census counted 269,326 establishments; accommodation and food service activities are 23.0 % of
them and 12.9 % of the country's 927,739 workers, and 92.2 % of establishments are
micro-enterprises with fewer than four workers (National Institute of Statistics of Rwanda
[NISR], 2024). Businesses of that size cannot buy and configure an enterprise POS.

Research agrees on both the benefit and the barrier. Staff in restaurants running a management
system report easier operations, higher sales and more standard service, but every group rated
the technical cost high, and the least favourable responses came from restaurants with ten or
fewer staff (Memis Kocaman, 2021). Work on restaurant inventory finds the real difficulty is
perishability — over-buying, expiry, shrinkage — and that the system must follow how that
kitchen buys, stores and consumes (Zamora Saltos & Rodríguez Borges, 2024). Both leave one gap:
**where the rules live.** In the systems they describe, correctness depends on the application,
and the database stores whatever it is handed.

## 2. Solution

One Oracle pluggable database, `ROSTS_PDB`, with fifteen normalised tables and every rule in
PL/SQL, so no client can store an inconsistent state.

- **Billing inside the database.** `sp_place_order` inserts the receipt and its lines in one
  transaction; a `BEFORE` row trigger prices each line from `MENU_ITEM.unit_price` and refuses
  a negative quantity; functions compute net, 11 % tax and total. The screen never computes a
  total.
- **Stock moves because a sale happened.** An `AFTER` row trigger writes `STOCK_MOVEMENT` and
  decrements `INGREDIENT.qty_on_hand` through the recipe table `MENU_ITEM_INGREDIENT`. If
  stock cannot cover the line it raises `-20001` and the order rolls back.
- **Payment rules enforced, not advised.** `sp_record_payment` applies money to a receipt;
  triggers refuse payment on a cancelled order (`-20003`), payment above the bill (`-20004`)
  and any edit of a paid order (`-20002`); an order cannot close with a positive balance, and
  a discount above 20 % requires the `MANAGER` role (`-20005`).
- **Everything sensitive is audited.** `AUDIT_LOG` holds old and new value, database user,
  timestamp and record key for price changes, deletions and refused operations.
- **Reporting is SQL:** `fn_daily_revenue`, a monthly sales cursor, a top-items cursor and a
  low-stock cursor feed the views `v_daily_sales`, `v_top_items` and `v_low_stock`.

## 3. Data Source

Real point-of-sale history: *Anonymous Transactional Dataset*, version 2, by Engel, Gaol,
Kurniawan and Budiharto (2026), Mendeley Data, CC BY 4.0 (DOI 10.17632/kcgf45y24m.2). It comes
from a food-and-beverage micro/small enterprise with three outlets, covers 2 January to 30
September 2025, and holds **53,820 receipts** (outlet, date, time, net sales, 11 % tax, total,
receipt number, items, item count, payment method `BCA`/`Cash`/`GoFood`) plus **96 products**.
No customer name, phone or card number exists; the only customer field is a 0/1 loyalty flag.
The repository loads **550 receipts** from outlet `SHOP001`, 2–7 January 2025, with the product
catalogue. The source has no recipes, stock or staff, so those tables are built as clearly
labelled derived sample data (`record_source = 'DERIVED'`) and `data/README.md` states which
rows are real and which are derived.

## 4. Planned Tables

`OUTLET` · `STAFF` · `MENU_CATEGORY` · `MENU_ITEM` · `PRICE_HISTORY` · `INGREDIENT` (unit,
quantity on hand, reorder level) · `MENU_ITEM_INGREDIENT` (recipe: quantity per unit sold) ·
`PAYMENT_METHOD` · `ORDERS` (receipt header, status, net, tax, total) · `ORDER_LINE` (item,
quantity, price at sale time, line total) · `PAYMENT` · `STOCK_MOVEMENT` (ingredient in/out,
linked to the order) · `PROMOTION` · `ORDER_PROMOTION` · `AUDIT_LOG`. Phase II splits the flat
receipt into `ORDERS` → `ORDER_LINE` → `PAYMENT` and resolves free-text item names against
`MENU_ITEM`; the ERD is in the repository README.

## 5. Planned PL/SQL Features

- **Procedures:** `sp_place_order`, `sp_add_order_line`, `sp_record_payment`, `sp_close_order`,
  `sp_apply_promotion`, `sp_change_price`, `sp_adjust_stock`.
- **Functions:** `fn_item_price`, `fn_line_total`, `fn_order_tax`, `fn_order_total`,
  `fn_stock_available`, `fn_payment_balance`, `fn_daily_revenue`.
- **Cursors:** monthly sales ranking, low-stock alert list, daily cash-up by payment method,
  and a `FOR UPDATE` cursor that stops two cashiers selling the last portion of milk at once.
- **Package:** `pkg_rosts_ops` with public order, billing, inventory and reporting subprograms
  and private helpers, so every APEX page calls one interface.
- **Triggers:** `trg_line_price`, `trg_line_stock`, `trg_order_totals`, `trg_payment_guard`,
  `trg_price_audit`, `trg_order_audit` — `BEFORE` where `:NEW` must be written, `AFTER` where
  only consequences are recorded, as Oracle permits at each timing point (Oracle, 2026a).
- **Restriction rule:** no sale without stock, no closure with an unpaid balance, no discount
  above 20 % without `MANAGER`, no negative stock, no edit of a paid receipt.
- **Exception handling:** named exception per rule, `RAISE_APPLICATION_ERROR` shown verbatim in
  the interface, `SAVEPOINT`/`ROLLBACK` per order, `NO_DATA_FOUND` and `DUP_VAL_ON_INDEX`
  handled in the package.

## 6. Innovation

**Option: user interface — Oracle APEX.** The database is the engine; the innovation is
`ROSTS Console` on top of it. A cashier gets one order screen whose product buttons call
`sp_place_order` and show the bill the database computed, and one payment screen calling
`sp_record_payment`. A manager gets a dashboard on the views above: revenue per outlet per day,
best sellers, payment mix, a low-stock badge and a read-only audit log — the real-time
reporting a commercial POS already sets as the expectation (Oracle, 2026b). No rule lives in a
page — the pages only call PL/SQL — so the same rules protect SQL*Plus users too, and a
four-person business needs only a browser: no per-terminal licence, no application server.

## 7. References

Engel, M. M., Gaol, F. L., Kurniawan, A., & Budiharto, W. (2026). *Anonymous transactional
dataset* (Version 2) [Data set]. Mendeley Data. https://doi.org/10.17632/kcgf45y24m.2

Memis Kocaman, E. (2021). Operational effects of using restaurant management system: An
assessment according to business features. *International Journal of Gastronomy and Food
Science, 25*, 100408. https://doi.org/10.1016/j.ijgfs.2021.100408

National Institute of Statistics of Rwanda. (2024). *Establishment Census 2023*.
https://statistics.gov.rw/data-sources/censuses/Establishment-Census/establishment-census-2023

Oracle. (2026a). *CREATE TRIGGER statement* (Oracle Database 19c PL/SQL Language Reference).
https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/CREATE-TRIGGER-statement.html

Oracle. (2026b). *Oracle Simphony restaurant POS system*.
https://www.oracle.com/food-beverage/restaurant-pos-systems/

Zamora Saltos, C. E., & Rodríguez Borges, C. G. (2024). Design of an inventory management
system for a Manabita restaurant. *InGenio, 7*(2). https://doi.org/10.18779/ingenio.v7i2.808