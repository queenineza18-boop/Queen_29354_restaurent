# Phase II — Normalisation from the raw POS extract to a 3NF logical design

**Student:** Queen Ineza · **Student ID:** 29354
**Course:** INSY 8311 – Database Development with PL/SQL · **Instructor:** Eric Maniraguha
**Project:** Restaurant Order and Sales Tracking System (ROSTS)
**Deliverables in this folder:** `normalization.md` (this file), `erd.png`, `data_dictionary.md`

---

## 0. What this document does and which data it uses

The raw data is one wide CSV row per receipt, plus a separate product catalogue. This
document takes five real receipts from `data/raw/` and pushes them through UNF, 1NF, 2NF and
3NF in order, showing the actual rows at each step and naming the dependency that each split
removes. Nothing here is invented: every value below was copied from the committed files, and
every count was produced by reading all seven files. Where the design needs a table the source
cannot fill (staff, ingredients, recipes), §10 says so openly.

The five receipts used throughout, taken from `pos_shop001_2025-01-02.csv` and
`pos_shop001_2025-01-03.csv`:

| # | ReceiptNumber | Date | Time | Items (as stored) | TotalItem | PaymentMethod | Loyalty | NetSales | Tax | TotalAmount |
| --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| A | SHOP001JAN2500001 | 2025-01-02 | 07:01:05 | `Basic Latte (Ice Arabica)` | 1 | BCA | 0 | 20720.721 | 2279.279 | 23000 |
| B | SHOP001JAN2500009 | 2025-01-02 | 09:33:52 | `Green Thai Tea, WHITE (Arabica)` | 2 | BCA | 0 | 45945.946 | 5054.054 | 51000 |
| C | SHOP001JAN2500013 | 2025-01-02 | 10:37:45 | `Cappuccino (Hot Houseblend)` | 1 | Cash | 1 | 0.0 | 0.0 | 0 |
| D | SHOP001JAN2500029 | 2025-01-02 | 13:27:28 | `Espresso Houseblend (On The Rock), Basic Latte (Ice Arabica)` | 2 | BCA | 0 | 31531.532 | 3468.468 | 35000 |
| E | SHOP001JAN2500092 | 2025-01-03 | 08:49:19 | `Friendly Coffee (Ice double shot)` | 1 | Cash | 1 | 0.0 | 0.0 | 0 |

Two of the five (C and E) are zero-value loyalty receipts. They are kept in the sample on
purpose, because they are the case the design has to survive: a receipt with a real product on
it and a real payment method, but no money.

**The numbers behind the sample:** 550 receipts in the extract contain 638 item occurrences;
462 receipts carry one item and 88 carry two; the 638 occurrences use 94 distinct item names,
which resolve to 94 of the 96 catalogue products.

---

## 1. Unnormalised form (UNF)

As delivered, one row is one receipt and the items sit inside a single cell, comma-separated
inside quotes. Nothing is atomic and one table holds facts about four different things: the
sale, the product, the payment and the shop.

| Outlet | Date | Time | NetSales | Tax | TotalAmount | ReceiptNumber | Items | TotalItem | PaymentMethod | UseLoyaltyCard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SHOP001 | 2025-01-02 | 07:01:05 | 20720.721 | 2279.279 | 23000 | SHOP001JAN2500001 | Basic Latte (Ice Arabica) | 1 | BCA | 0 |
| SHOP001 | 2025-01-02 | 09:33:52 | 45945.946 | 5054.054 | 51000 | SHOP001JAN2500009 | Green Thai Tea, WHITE (Arabica) | 2 | BCA | 0 |
| SHOP001 | 2025-01-02 | 10:37:45 | 0.0 | 0.0 | 0 | SHOP001JAN2500013 | Cappuccino (Hot Houseblend) | 1 | Cash | 1 |
| SHOP001 | 2025-01-02 | 13:27:28 | 31531.532 | 3468.468 | 35000 | SHOP001JAN2500029 | Espresso Houseblend (On The Rock), Basic Latte (Ice Arabica) | 2 | BCA | 0 |
| SHOP001 | 2025-01-03 | 08:49:19 | 0.0 | 0.0 | 0 | SHOP001JAN2500092 | Friendly Coffee (Ice double shot) | 1 | Cash | 1 |

**What is wrong with it, in one sentence each:**

- `Items` is a *repeating group*: row B holds two products in one cell, and row D holds two as
  well, so a cell does not hold a single value.
- `TotalItem` is a count of a repeating group, so it will be wrong the moment a line is added
  or removed rather than counted.
- The row mixes four subjects: the sale (date, time, amounts), the product (name), the payment
  (method) and the shop (outlet). One row cannot be the record of all four without repeating.
- Nothing identifies a product or a shop: `Basic Latte (Ice Arabica)` is text, not a key, and
  `SHOP001` is repeated on all 550 rows although there is only one shop.
- The only key available is the whole row, because nothing smaller is unique: `Date` repeats,
  `PaymentMethod` repeats, and even `Items` repeats.

In the whole extract the repeating group is not an edge case: **88 of the 550 receipts carry
two items**, which is 16 % of the trade.

---

## 2. First normal form (1NF) — remove the repeating group

One row per item sold. The list in `Items` is exploded into one row per element, and a line
number is added so that the two lines of a receipt can be told apart. `TotalItem` is no longer
needed to describe a row.

**1NF key:** (`ReceiptNumber`, `LineNo`).

| ReceiptNumber | LineNo | ItemName | Outlet | Date | Time | NetSales | Tax | TotalAmount | PaymentMethod | Loyalty |
| --- | ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | ---: |
| SHOP001JAN2500001 | 1 | Basic Latte (Ice Arabica) | SHOP001 | 2025-01-02 | 07:01:05 | 20720.721 | 2279.279 | 23000 | BCA | 0 |
| SHOP001JAN2500009 | 1 | Green Thai Tea | SHOP001 | 2025-01-02 | 09:33:52 | 45945.946 | 5054.054 | 51000 | BCA | 0 |
| SHOP001JAN2500009 | 2 | WHITE (Arabica) | SHOP001 | 2025-01-02 | 09:33:52 | 45945.946 | 5054.054 | 51000 | BCA | 0 |
| SHOP001JAN2500013 | 1 | Cappuccino (Hot Houseblend) | SHOP001 | 2025-01-02 | 10:37:45 | 0.0 | 0.0 | 0 | Cash | 1 |
| SHOP001JAN2500029 | 1 | Espresso Houseblend (On The Rock) | SHOP001 | 2025-01-02 | 13:27:28 | 31531.532 | 3468.468 | 35000 | BCA | 0 |
| SHOP001JAN2500029 | 2 | Basic Latte (Ice Arabica) | SHOP001 | 2025-01-02 | 13:27:28 | 31531.532 | 3468.468 | 35000 | BCA | 0 |
| SHOP001JAN2500092 | 1 | Friendly Coffee (Ice double shot) | SHOP001 | 2025-01-03 | 08:49:19 | 0.0 | 0.0 | 0 | Cash | 1 |

**Dependency removed:** the repeating group — `Items` held two values in one cell, and 1NF
replaces it with one row per product so that every column holds a single, atomic value.

**Row count:** the extract goes from 550 rows to **638 rows**, because 462 receipts stay at one
row and 88 become two. That 550 → 638 is the first check to reproduce in Phase IV.

**What this step did not fix:** rows B1 and B2 still carry the same amounts, the same date and
the same payment method, twice. That repetition is the partial dependency removed next.

---

## 3. Second normal form (2NF) — remove partial dependencies

The key is composite, (`ReceiptNumber`, `LineNo`). Ask of each column: does it need *both*
parts of the key? `ItemName` needs both, because line 1 and line 2 of the same receipt are
different products. `Date`, `Time`, `Outlet`, `NetSales`, `Tax`, `TotalAmount`,
`PaymentMethod` and `Loyalty` need only `ReceiptNumber` — they describe the whole sale, and
they say exactly the same thing on every line of that sale.

So the receipt header moves out into `ORDERS` and the product stays in `ORDER_LINE`.

**`ORDERS`** — key `ReceiptNumber` (5 of the 550 rows):

| ReceiptNumber | Outlet | Date | Time | NetSales | Tax | TotalAmount | PaymentMethod | Loyalty |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | ---: |
| SHOP001JAN2500001 | SHOP001 | 2025-01-02 | 07:01:05 | 20720.721 | 2279.279 | 23000 | BCA | 0 |
| SHOP001JAN2500009 | SHOP001 | 2025-01-02 | 09:33:52 | 45945.946 | 5054.054 | 51000 | BCA | 0 |
| SHOP001JAN2500013 | SHOP001 | 2025-01-02 | 10:37:45 | 0.0 | 0.0 | 0 | Cash | 1 |
| SHOP001JAN2500029 | SHOP001 | 2025-01-02 | 13:27:28 | 31531.532 | 3468.468 | 35000 | BCA | 0 |
| SHOP001JAN2500092 | SHOP001 | 2025-01-03 | 08:49:19 | 0.0 | 0.0 | 0 | Cash | 1 |

**`ORDER_LINE`** — key (`ReceiptNumber`, `LineNo`):

| ReceiptNumber | LineNo | ItemName |
| --- | ---: | --- |
| SHOP001JAN2500001 | 1 | Basic Latte (Ice Arabica) |
| SHOP001JAN2500009 | 1 | Green Thai Tea |
| SHOP001JAN2500009 | 2 | WHITE (Arabica) |
| SHOP001JAN2500013 | 1 | Cappuccino (Hot Houseblend) |
| SHOP001JAN2500029 | 1 | Espresso Houseblend (On The Rock) |
| SHOP001JAN2500029 | 2 | Basic Latte (Ice Arabica) |
| SHOP001JAN2500092 | 1 | Friendly Coffee (Ice double shot) |

**Dependency removed:** the partial dependency — `Date`, `Time`, `Outlet`, `NetSales`, `Tax`,
`TotalAmount`, `PaymentMethod` and `Loyalty` depended on `ReceiptNumber` alone, so they were
duplicating content on every line and are now stored once per receipt.

**What this step did not fix:** `ItemName` is still free text. Two different lines that sold the
same drink store the same name and, once price and category are brought in, will store the same
price and the same category on every one of the 638 lines. That is the next split.

---

## 4. Third normal form (3NF) — remove the transitive dependencies

There are five of them in the 2NF tables, and each one is a column that depends on a non-key
column instead of on the key.

### 4.1 Product facts hang off the product name, not off the line

In `ORDER_LINE`, `ItemName` is not a key but everything about the product depends on it: its
catalogue price, its category, its variant and its description. With the catalogue joined in,
2NF would look like this, and 638 lines would repeat these facts 638 times:

| ItemName | Category | Variant | CataloguePrice |
| --- | --- | --- | ---: |
| Basic Latte (Ice Arabica) | Coffee | Ice Arabica | 23000 |
| Green Thai Tea | Tea | - | 21000 |
| WHITE (Arabica) | Menu Gedhe | Arabica | 30000 |
| Cappuccino (Hot Houseblend) | Coffee | Hot Houseblend | 22000 |
| Espresso Houseblend (On The Rock) | Coffee | On The Rock | 12000 |
| Friendly Coffee (Ice double shot) | Coffee | Ice double shot | 23000 |

**Dependency removed:** a transitive dependency — the price, variant and description depend on
the product, not on the sale, so they move to `MENU_ITEM` and the line keeps only a reference
to the product.

**`MENU_ITEM`** (6 of 96 rows; `menu_item_id` is the catalogue's `ProductId`):

| menu_item_id | item_name | variant | category_id | unit_price | description |
| ---: | --- | --- | ---: | ---: | --- |
| 18 | Basic Latte | Ice Arabica | 1 | 23000 | (Indonesian description, kept from the catalogue) |
| 53 | Green Thai Tea | - | 4 | 21000 | … |
| 92 | WHITE | Arabica | 2 | 30000 | … |
| 29 | Cappuccino | Hot Houseblend | 1 | 22000 | … |
| 42 | Espresso Houseblend | On The Rock | 1 | 12000 | … |
| 48 | Friendly Coffee | Ice double shot | 1 | 23000 | … |

### 4.2 The category repeats inside the product

`Menu Gedhe` and `Coffee` were written on every product row that belongs to them. A category
name depends on the category, not on the product.

**Dependency removed:** a transitive dependency — the category name depends on `category_id`,
not on the product, so it moves to `MENU_CATEGORY` and 96 products reference 6 categories
instead of repeating the names.

**`MENU_CATEGORY`** (all 6 rows; product counts from the catalogue):

| category_id | category_name | Products in the catalogue |
| ---: | --- | ---: |
| 1 | Coffee | 34 |
| 2 | Menu Gedhe | 19 |
| 3 | Other | 15 |
| 4 | Tea | 13 |
| 5 | Snacks | 9 |
| 6 | Add on | 6 |

### 4.3 The payment method is a fact about a method, not about a sale

`BCA` and `Cash` are written on 550 receipt rows, and the two properties the system needs from
them — whether the method is cash and what to print on the receipt — belong to the method.

**Dependency removed:** a transitive dependency — `method_name` and `is_cash` depend on
`method_code`, not on the receipt, so they move to `PAYMENT_METHOD` and the receipt references
the method.

**`PAYMENT_METHOD`** (both rows; `GoFood` exists in the full source but not in this week):

| method_code | method_name | is_cash |
| --- | --- | --- |
| BCA | Bank transfer (BCA) | N |
| CASH | Cash | Y |

### 4.4 The money received is its own event

The receipt says how the customer paid and how much. That is a payment, with its own time and
status, and the project's rules (`-20003`, `-20004`, no closure with an unpaid balance) are all
about it. Keeping the method on the receipt header would make a split payment impossible.

**Dependency removed:** a transitive dependency — the amount and method depend on the payment
event rather than on the sale's own attributes, and separating them lets one receipt carry more
than one payment row.

**`PAYMENT`** (5 rows, one per receipt in the sample; in the full extract, 550):

| payment_id | order_no | method_code | paid_at | amount | status |
| ---: | --- | --- | --- | ---: | --- |
| 1 | SHOP001JAN2500001 | BCA | 2025-01-02 07:01:05 | 23000 | SETTLED |
| 2 | SHOP001JAN2500009 | BCA | 2025-01-02 09:33:52 | 51000 | SETTLED |
| 3 | SHOP001JAN2500013 | CASH | 2025-01-02 10:37:45 | 0 | SETTLED |
| 4 | SHOP001JAN2500029 | BCA | 2025-01-02 13:27:28 | 35000 | SETTLED |
| 5 | SHOP001JAN2500092 | CASH | 2025-01-03 08:49:19 | 0 | SETTLED |

### 4.5 The shop is named once, not 550 times

`SHOP001` appears on every row and tells us nothing about the shop: not its name, not its city,
not when it opened. Those are facts about the outlet.

**Dependency removed:** a transitive dependency — the outlet's name, city and opening date
depend on the outlet code, not on the receipt, so they move to `OUTLET`.

**`OUTLET`** (1 row from this extract; the full source has three):

| outlet_code | outlet_name | city | opening_date | is_active |
| --- | --- | --- | --- | --- |
| SHOP001 | (shop name not in the source — to be supplied) | (not in the source) | (not in the source) | Y |

### 4.6 The final `ORDER_LINE`

| order_line_id | order_no | menu_item_id | line_no | quantity | unit_price | line_total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | SHOP001JAN2500001 | 18 | 1 | 1 | 23000 | 23000 |
| 2 | SHOP001JAN2500009 | 53 | 1 | 1 | 21000 | 21000 |
| 3 | SHOP001JAN2500009 | 92 | 2 | 1 | 30000 | 30000 |
| 4 | SHOP001JAN2500013 | 29 | 1 | 1 | 0 | 0 |
| 5 | SHOP001JAN2500029 | 42 | 1 | 1 | 12000 | 12000 |
| 6 | SHOP001JAN2500029 | 18 | 2 | 1 | 23000 | 23000 |
| 7 | SHOP001JAN2500092 | 48 | 1 | 1 | 0 | 0 |

`quantity` is 1 on every line of this extract: the till records "one of this product" per
occurrence, so a customer buying two lattes produces two lines, not a quantity of 2. The column
is kept because the recipe and stock logic needs it, and because a future order screen will let
a cashier enter 2.

### 4.7 The final `ORDERS`

| order_id | order_no | outlet_code | ordered_at | status | net_amount | tax_amount | total_amount | amount_paid | loyalty_used |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | SHOP001JAN2500001 | SHOP001 | 2025-01-02 07:01:05 | CLOSED | 20720.721 | 2279.279 | 23000 | 23000 | N |
| 2 | SHOP001JAN2500009 | SHOP001 | 2025-01-02 09:33:52 | CLOSED | 45945.946 | 5054.054 | 51000 | 51000 | N |
| 3 | SHOP001JAN2500013 | SHOP001 | 2025-01-02 10:37:45 | CLOSED | 0 | 0 | 0 | 0 | Y |
| 4 | SHOP001JAN2500029 | SHOP001 | 2025-01-02 13:27:28 | CLOSED | 31531.532 | 3468.468 | 35000 | 35000 | N |
| 5 | SHOP001JAN2500092 | SHOP001 | 2025-01-03 08:49:19 | CLOSED | 0 | 0 | 0 | 0 | Y |

`staff_id` is not in this table on purpose: the source has no cashier field. It is a nullable
foreign key in the data dictionary and will be filled only for orders created inside the
system, so a historical receipt does not get a person attached to it by invention.

---

## 5. The design in one picture

`docs/design/erd.png` is the crow's-foot ERD for all fifteen tables; the columns, keys,
cardinality and optionality of each one are in `docs/design/data_dictionary.md`. The shape of
it, in words:

- `OUTLET` 1 — many `STAFF`, `ORDERS`, and `STOCK_MOVEMENT` through its orders.
- `ORDERS` 1 — 1..many `ORDER_LINE`, 0..many `PAYMENT`, 0..many `ORDER_PROMOTION`.
- `MENU_CATEGORY` 1 — many `MENU_ITEM`; `MENU_ITEM` 1 — many `ORDER_LINE`, `PRICE_HISTORY`,
  `MENU_ITEM_INGREDIENT`.
- `MENU_ITEM` many — many `INGREDIENT`, resolved by the junction table
  `MENU_ITEM_INGREDIENT` (a recipe: how much of an ingredient one sold unit consumes).
- `PROMOTION` many — many `ORDERS`, resolved by the junction table `ORDER_PROMOTION`.
- `PAYMENT_METHOD` 1 — many `PAYMENT`; `INGREDIENT` 1 — many `STOCK_MOVEMENT`.
- `AUDIT_LOG` has no foreign key by design: it must be able to point at any table, including
  ones that no longer exist, so it stores a table name and a record key as text.

The two junction tables are the answer to the assignment's "every many-to-many relationship is
resolved with a junction table": a drink is made of many ingredients and an ingredient is used
by many drinks; an order can carry more than one promotion and a promotion applies to many
orders.

---

## 6. Row counts at every step, and what Phase IV should load

| Step | What is counted | Rows |
| --- | --- | ---: |
| Raw | receipt rows in `data/raw/pos_*.csv` | 550 |
| Raw | product rows in `data/raw/products_catalog.csv` | 96 |
| 1NF | item occurrences after splitting `Items` | 638 |
| 2NF | `ORDERS` rows | 550 |
| 2NF | `ORDER_LINE` rows | 638 |
| 3NF | `OUTLET` rows | 1 |
| 3NF | `PAYMENT_METHOD` rows | 2 |
| 3NF | `MENU_CATEGORY` rows | 6 |
| 3NF | `MENU_ITEM` rows | 96 |
| 3NF | `PAYMENT` rows (one per receipt) | 550 |
| 3NF | `PRICE_HISTORY` seed rows (current price per item) | 96 |
| — | `STAFF`, `INGREDIENT`, `MENU_ITEM_INGREDIENT`, `PROMOTION` | 0 from the source (derived, see §10) |
| — | `STOCK_MOVEMENT`, `ORDER_PROMOTION`, `AUDIT_LOG` | 0 (written by PL/SQL at run time) |

These are the counts to expect after loading, and they are the cheapest sanity check the
database can have: if `ORDER_LINE` says 637, one receipt lost a line while `Items` was being
split.

**Control totals to reconcile after the load** (all from the committed files):

| Total | Expected value |
| --- | ---: |
| `SUM(ORDERS.total_amount)` | 13,542,000 |
| `SUM(PAYMENT.amount)` | 13,542,000 |
| `COUNT(ORDERS)` | 550 |
| `COUNT(ORDER_LINE)` | 638 |
| `SUM(ORDER_LINE.line_total)` | 13,542,000 |
| Receipts by payment method | BCA 433, Cash 117 |
| Receipts with `loyalty_used = 'Y'` | 16 |
| `SUM(ORDERS.net_amount)` | 12,200,000.078 |
| `SUM(ORDERS.tax_amount)` | 1,341,999.922 |

The last two are worth reading carefully, because the obvious hand calculation gives
12,200,000.00 and 1,342,000.00 and the data does not. Each receipt's net is the paid amount
divided by 1.11 and rounded to three decimals, and its tax is the paid amount minus that
rounded net; 550 roundings accumulate to 8 cents of drift across the week (−0.078 on net,
+0.078 on tax). The two still add to exactly 13,542,000. So the load must total the stored
values, and it must not "correct" the net to 11 % of the grand total: the per-receipt net is
the real number, and the drift is the honest consequence of rounding 550 times rather than
twisting the data to make a report look tidy.

---

## 7. Field-by-field mapping (raw field → target table and column)

Every column of both raw files is accounted for below, with the conversion it needs. This is
the cleaning checklist for Phase IV in tabular form.

### 7.1 Receipt file

| Raw field | Target table.column | Conversion | Note |
| --- | --- | --- | --- |
| `Outlet` | `OUTLET.outlet_code`, and `ORDERS.outlet_code` as FK | none (text 7) | One value in the extract; the other two outlets must be added as rows, not as new columns. |
| `Date` | `ORDERS.ordered_at` (date part) | text `YYYY-MM-DD` → `DATE` | 550 values, all valid and all matching their file name. |
| `Time` | `ORDERS.ordered_at` (time part) | text `HH24:MI:SS` → `DATE`/`TIMESTAMP` | Combined with `Date`; 550 conversions. Range 07:01:05–22:59:03. |
| `NetSales` | `ORDERS.net_amount` | text → `NUMBER(12,3)` | Equals `SUM(line_total)/1.11`; 534 of 550 reconcile to the rupiah, the 16 exceptions are the zero-value loyalty receipts. |
| `Tax` | `ORDERS.tax_amount` | text → `NUMBER(12,3)` | Exactly 11 % of `NetSales` in all 550 rows. |
| `TotalAmount` | `ORDERS.total_amount` and `PAYMENT.amount` | text → `NUMBER(12,0)` | Equals `SUM(catalogue price of the items)` in 534 rows; 16 are zero. |
| `ReceiptNumber` | `ORDERS.order_no` (alternate key, unique) | none (text 18) | 550 distinct, sequential 1–550, format `SHOP001JAN25nnnnn`. Becomes the business key the cash-up prints. |
| `Items` | split → `ORDER_LINE.menu_item_id` | text list → rows, then lookup | 638 values: split on `,`, trim, then match `ProductName (Variant)` or `ProductName` against `MENU_ITEM`. All 94 distinct names resolve. |
| `TotalItem` | **dropped** | — | Redundant: it is `COUNT(*)` of the order's lines, and storing it would break 3NF. Kept only as a load-time control (line count per receipt must equal this value). |
| `PaymentMethod` | `PAYMENT_METHOD.method_code`, and `PAYMENT.method_code` as FK | text → lookup | 2 distinct values; `BCA` becomes `BCA`, `Cash` becomes `CASH`. |
| `UseLoyaltyCard` | `ORDERS.loyalty_used` | text `0`/`1` → `CHAR(1)` `N`/`Y` | 16 rows are `1`, all of them zero-value receipts. It is a flag only: no customer is identified, and none may be added. |

Nothing in the receipt file is invented. Line prices are not in the file, and §8 explains what
is used instead.

### 7.2 Product catalogue

| Raw field | Target table.column | Conversion | Note |
| --- | --- | --- | --- |
| `ProductId` | `MENU_ITEM.menu_item_id` | text → `NUMBER` | Reused as the surrogate key so the source ids stay traceable. |
| `ProductName` | `MENU_ITEM.item_name` | trim | 11 names already contain their size in brackets (`Apple Pie Latte (Gedhe)`); those keep the bracket, the variant stays `-`. |
| `Variant` | `MENU_ITEM.variant` | `-` → `NULL` | 40 products have a variant, 56 have `-`. The receipt writes `ProductName (Variant)`, which is the rule that makes the lookup work. |
| `Category` | `MENU_CATEGORY.category_name` + `MENU_ITEM.category_id` | text → lookup (6 rows) | `Menu Gedhe` is a cup size, kept as its own category because that is how the shop prices and sells it. |
| `Price` | `MENU_ITEM.unit_price` and a seed row in `PRICE_HISTORY` | text → `NUMBER(12,0)` | Range 0–30000. Two products are priced 0 and never sold. |
| `Description` | `MENU_ITEM.description` | none (text) | Indonesian text; kept because Phase IV derives recipes from it, and dropped from displays that do not need it. |

### 7.3 What is not mapped, and why

| Raw fact | Decision |
| --- | --- |
| The order of items inside `Items` | Becomes `line_no` in the order they were printed. It is the only signal of sequence the till gives us, and it is needed for the 2NF key. |
| The product's Indonesian description on the receipt | Not on the receipt; it lives only in `MENU_ITEM`. |
| The shop's name, city, opening date | Not in either file. `OUTLET` needs them supplied by hand; they are business facts, not data to invent. |
| Why 16 receipts are worth 0 | Not in the file. Recorded as an open question in §8, not guessed at. |

---

## 8. Cleaning checklist carried into Phase IV

Each line is a conversion or a decision that the load has to make, in the order it has to make
it. Counts are from `data/dataset_card.md` §6.

1. **Combine and convert the timestamp.** 550 rows: `Date` + `Time` → one `DATE`. Reject a row
   if the result cannot be built, rather than defaulting to today.
2. **Convert the three money fields.** 1,650 cells: `NetSales` and `Tax` keep three decimals,
   `TotalAmount` is a whole rupiah. Never `ROUND(NetSales, 0)` — the tax is computed on the
   three-decimal value.
3. **Explode `Items` into 638 lines.** Split on the comma only inside the quoted field, trim
   surrounding spaces, and keep the printed order as `line_no`.
4. **Resolve every item name.** Match `ProductName || ' (' || Variant || ')'` first, then
   `ProductName` alone. All 94 names in this extract resolve; the load must still raise an
   exception on an unresolved name instead of inserting a blank product.
5. **Normalise the two spellings of Houseblend.** 1 catalogue row and 7 receipt lines carry
   `Houesblend`. Decide once: keep the source spelling in a note column and use the corrected
   `Houseblend` in `variant`, or keep the misspelling everywhere. Either is defensible; having
   both at the same time is not.
6. **Convert `UseLoyaltyCard` 0/1 → N/Y.** 550 cells.
7. **Convert `PaymentMethod`** to the two `PAYMENT_METHOD` codes, and add `GOFOOD` as a third
   row so next month's file loads without a schema change.
8. **Insert the outlet row before the orders** (1 row), then the categories (6), the products
   (96), the payment methods (2), then orders (550), lines (638) and payments (550) in that
   order. Foreign keys dictate it.
9. **Set `ORDER_LINE.unit_price` from the catalogue at load time**, then reconcile:
   `SUM(unit_price × quantity)` per order must equal `ORDERS.total_amount`. 534 of 550 will
   match; the 16 that will not are the zero-value receipts.
10. **Decide how to record the 16 zero-value receipts before loading them.** They are real
    sales with a real product and a `Cash` payment of 0. Three options, and the choice must be
    written down: (a) load the line at catalogue price with a 100 % redemption row in
    `ORDER_PROMOTION`; (b) load the line at `unit_price = 0` with a note in `ORDERS.status`;
    (c) reject them. Option (a) is the only one that keeps the menu price honest and the
    revenue at zero, and it is the one this design expects — but it collides with the project
    rule that a discount above 20 % needs a manager, so Phase IV must treat a loyalty
    redemption as a redemption, not as a discount, or `-20005` will refuse to load the history.
11. **Check the 2 dropped products.** `Add on Aren` and `Add on Simple Syrup` (price 0, never
    sold) load as menu items with no sales. That is correct; do not delete them.
12. **Reconcile the totals in §6 after the load**, and fail the load if any of them is off.

---

## 9. What 3NF bought us, measured on this extract

| Before | After | Effect on this data |
| --- | --- | --- |
| `Items` holding up to 2 values in one cell | 1 row per product | 638 lines can be counted with `COUNT(*)`, not by parsing text |
| amounts repeated on every line of a 2-item receipt | once in `ORDERS` | 88 duplicate amount triplets removed |
| item name repeated on 638 lines | 96 product rows | the name is stored 96 times instead of 638 |
| category name repeated on 96 products | 6 category rows | 6 names instead of 96 |
| `BCA`/`Cash` and their properties on 550 rows | 2 method rows | 2 rows instead of 550 |
| `SHOP001` with no shop details, 550 times | 1 outlet row | the shop can finally have a name, a city and an opening date |
| no way to say how a drink was paid for twice | `PAYMENT` table | a split payment is a second row, not a new column |
| price only as a current value | `MENU_ITEM.unit_price` + `PRICE_HISTORY` + `ORDER_LINE.unit_price` | last month's bill keeps last month's price |

### The one deliberate exception

`ORDER_LINE.unit_price` looks like a transitive dependency (`line → product → price`) and a
strict reading would delete it. It is kept, and it is not the product's current price: it is
the price agreed at the moment of sale. If the shop raises a latte from 23,000 to 25,000, the
old receipts must still add up to 23,000, and `fn_order_total` must never recompute history
from today's menu. That is why the price is copied onto the line, why `PRICE_HISTORY` records
the change, and why the trigger `trg_line_price` prices a new line from `MENU_ITEM` at insert
time and never again.

`ORDERS.net_amount`, `tax_amount` and `total_amount` are stored for the same reason and because
the project's rules read them (`trg_order_totals`, `fn_payment_balance`). They are derivable
from the lines; storing them is a controlled redundancy with a trigger keeping them true, not
an unnormalised table.

---

## 10. What this dataset cannot give the schema

The project has fifteen tables and this extract can fill seven of them. Being explicit about
which is which is part of the design, and `data/README.md` §6 states the same split:

| Table | Filled from the real data? | If not, where the rows come from |
| --- | --- | --- |
| `ORDERS`, `ORDER_LINE`, `PAYMENT`, `PAYMENT_METHOD`, `MENU_ITEM`, `MENU_CATEGORY`, `OUTLET` | Yes (outlet name/city supplied by hand) | — |
| `PRICE_HISTORY` | Seed row per product | Written by `trg_price_audit` from then on |
| `STAFF` | No | Derived sample data, `record_source = 'DERIVED'` |
| `INGREDIENT`, `MENU_ITEM_INGREDIENT` | No | Derived from the product descriptions, labelled `DERIVED` |
| `STOCK_MOVEMENT` | No | Generated by `trg_line_stock` when orders are placed |
| `PROMOTION`, `ORDER_PROMOTION` | No | Created by the system (starting with the loyalty redemption in §8 item 10) |
| `AUDIT_LOG` | No | Written by the audit triggers |

No derived row will be presented as observed trade. The receipts are the hard facts; the rest
is a workshop for the PL/SQL, and it says so in the label.

---

## 11. The five-minute demonstration

The exam asks for one raw record and each of its values traced into the 3NF tables. This is that
walk-through, using receipt B, `SHOP001JAN2500009`:

1. **Open the raw file** `data/raw/pos_shop001_2025-01-02.csv` and read the row:
   `SHOP001,2025-01-02,09:33:52,45945.946,5054.054,51000,SHOP001JAN2500009,"Green Thai Tea, WHITE (Arabica)",2,BCA,0`.
2. **`Outlet` → `OUTLET` (1 row) and `ORDERS.outlet_code`.** One shop, named once.
3. **`Date` + `Time` → `ORDERS.ordered_at` = 2025-01-02 09:33:52.**
4. **`ReceiptNumber` → `ORDERS.order_no`**, unique, and the same value on both `ORDER_LINE`
   rows and on `PAYMENT`.
5. **`Items` → two `ORDER_LINE` rows** at line 1 and line 2, each pointing at a `MENU_ITEM`:
   `Green Thai Tea` is `menu_item_id 53`, `WHITE (Arabica)` is `92`.
6. **`TotalItem = 2`** is not stored anywhere: select the lines and count them, and the number
   comes back.
7. **`NetSales`, `Tax`, `TotalAmount` → `ORDERS.net_amount`, `tax_amount`, `total_amount`**, and
   `TotalAmount` again as `PAYMENT.amount` with `method_code = 'BCA'`.
8. **`PaymentMethod` → `PAYMENT_METHOD.method_code`**, where `is_cash = 'N'` is stored once,
   not 433 times.
9. **`UseLoyaltyCard = 0` → `ORDERS.loyalty_used = 'N'`.**
10. **Where the price came from:** it is not in the receipt row at all. `23,000 + 30,000 =
    51,000` is the catalogue price of the two products in `MENU_ITEM`, and `51,000 ÷ 1.11 =
    45,945.946` is the net the till wrote. That is why `ORDER_LINE.unit_price` is priced from
    the menu at sale time, and why the reconciliation in §8 item 9 is the load's proof.
