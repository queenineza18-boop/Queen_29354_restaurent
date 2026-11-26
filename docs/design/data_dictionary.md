# Data dictionary — ROSTS logical schema (Phase II)

**Student:** Queen Ineza · **Student ID:** 29354
**Course:** INSY 8311 – Database Development with PL/SQL · **Instructor:** Eric Maniraguha
**Project:** Restaurant Order and Sales Tracking System (ROSTS)
**Companion files:** `normalization.md` (how these tables were derived), `erd.png` (the crow's-foot diagram)

---

## 0. How to read this document

**No data types and no sizes.** As Phase II asks, this is a logical design: it names the
entities, the columns, the keys and the relationships, and leaves `NUMBER(12,3)`, `VARCHAR2(60)`,
`DATE` and the rest to Phase IV, where they will be chosen against the real values.

**Required** means the column may not be empty (`NOT NULL`). **Unique** means no two rows may
share a value (a unique constraint), and a column marked *unique* and *required* is a candidate
key. A `PK` column is both by definition.

**Two kinds of unique constraint appear here.** A simple one on a single column (`order_no`,
`category_name`), and a composite one on two or more columns together (`order_id, line_no`).
Composites are marked where they apply.

**Column naming.** `_id` is a surrogate key, `_code` is a short business code, `_no` is a
document number a human reads out loud, `_at` is a moment in time, `_amount` is money,
`is_` is a yes/no flag. Foreign key columns carry the name of the key they point at, so
`ORDER_LINE.menu_item_id` is visibly the same thing as `MENU_ITEM.menu_item_id`.

**Three labels** appear in the "source" line of each table, and they are the same labels used in
`data/README.md` §6:

- **Real** — the rows come from the committed receipts and catalogue.
- **Derived** — the source cannot supply these rows, so they are sample data, invented and
  labelled `record_source = 'DERIVED'`.
- **Generated** — the rows are written by the PL/SQL when the system runs; none exist at load.

---

## 1. Entities at a glance

| # | Table | One row is | Key | Rows from this extract | Source |
| --- | --- | --- | --- | ---: | --- |
| 1 | `OUTLET` | one shop | `outlet_code` | 1 | Real (name, city, date supplied) |
| 2 | `STAFF` | one employee | `staff_id` | 0 | Derived |
| 3 | `MENU_CATEGORY` | one menu section | `category_id` | 6 | Real |
| 4 | `MENU_ITEM` | one sellable product + variant | `menu_item_id` | 96 | Real |
| 5 | `PRICE_HISTORY` | one price change | `price_history_id` | 96 seeded | Real seed, generated after |
| 6 | `INGREDIENT` | one stock item | `ingredient_id` | 0 | Derived |
| 7 | `MENU_ITEM_INGREDIENT` | one line of a recipe | (`menu_item_id`, `ingredient_id`) | 0 | Derived |
| 8 | `PAYMENT_METHOD` | one way to pay | `method_code` | 2 | Real |
| 9 | `ORDERS` | one receipt header | `order_id` | 550 | Real |
| 10 | `ORDER_LINE` | one product on a receipt | `order_line_id` | 638 | Real |
| 11 | `PAYMENT` | one payment against a receipt | `payment_id` | 550 | Real |
| 12 | `STOCK_MOVEMENT` | one stock in/out movement | `movement_id` | 0 | Generated |
| 13 | `PROMOTION` | one named discount | `promotion_id` | 0 | Derived |
| 14 | `ORDER_PROMOTION` | one discount on one receipt | `order_promotion_id` | 0 | Generated |
| 15 | `AUDIT_LOG` | one audited change | `audit_id` | 0 | Generated |

---

## 2. Table definitions

### 2.1 `OUTLET` — the shops

One row per physical shop. The receipt file only carries the code, so the descriptive columns
have to be supplied for `SHOP001` in Phase IV. **Source:** real code, supplied description.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `outlet_code` | Short code printed on every receipt (`SHOP001`). PK. | Yes | Yes |
| `outlet_name` | Trading name of the shop, as the manager would say it. | Yes | Yes |
| `city` | City the shop trades in. | Yes | No |
| `opening_date` | Day the shop started trading, used for "since opening" reports. | No | No |
| `is_active` | `Y` if the shop is currently trading; `N` retires it without deleting its history. | Yes | No |

### 2.2 `STAFF` — the people who sell

Needed because an order has to be attributable to whoever took it, and because the 20 % discount
rule asks whether the person holds the `MANAGER` role. **Source:** derived — the receipts have
no staff field, so these are invented placeholder people, labelled as such.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `staff_id` | Surrogate key. PK. | Yes | Yes |
| `outlet_code` | Shop where the person works. FK → `OUTLET`. | Yes | No |
| `full_name` | Name used on the till, shift rota and audit trail. | Yes | No |
| `role` | `CASHIER`, `BARISTA` or `MANAGER`; only `MANAGER` may authorise a discount above 20 %. | Yes | No |
| `hire_date` | First day of employment, for the "length of service" report. | Yes | No |
| `is_active` | `Y` while employed; `N` after leaving, so old orders keep a valid reference. | Yes | No |

### 2.3 `MENU_CATEGORY` — menu sections

One row per section the menu is printed under. Six in the source: Coffee, Menu Gedhe, Other,
Tea, Snacks, Add on. **Source:** real.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `category_id` | Surrogate key. PK. | Yes | Yes |
| `category_name` | Section name as it appears on the menu board. | Yes | Yes |

### 2.4 `MENU_ITEM` — the sellable products

One row per product **and** variant, because the variant is what changes the price on the board:
`Americano` hot and iced are two rows, `WHITE` and `WHITE (Arabica)` are two rows. 96 rows,
taken from the catalogue with `ProductId` reused as the key. **Source:** real.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `menu_item_id` | Surrogate key; equals the catalogue's `ProductId` so the source stays traceable. PK. | Yes | Yes |
| `category_id` | Section the item is sold under. FK → `MENU_CATEGORY`. | Yes | No |
| `item_name` | Name the cashier sees, without the variant (`Basic Latte`, `WHITE`). | Yes | No (see below) |
| `variant` | How this version differs (`Ice Arabica`, `Gedhe`, `Hot`); empty when the product has none. | No | No (see below) |
| `unit_price` | Current selling price, tax-inclusive, the value `trg_line_price` copies onto a new line. | Yes | No |
| `description` | What the item is, kept from the catalogue; the basis for the derived recipes. | No | No |
| `is_active` | `Y` if it can be sold today; `N` hides it from the order screen without erasing its sales history. | Yes | No |

**Composite unique:** (`item_name`, `variant`) — no two rows may describe the same drink in the
same version. In this data 56 products have no variant, so `variant` is empty for them; Phase IV
must enforce the uniqueness against the empty value as one value (a function-based unique index
over `NVL(variant, '-')`), otherwise Oracle would allow the same product to be inserted twice.

### 2.5 `PRICE_HISTORY` — every price the menu has had

Answers "what did a latte cost in January" without touching the current price. One seed row per
product at load, then one row per change. **Source:** real seed, generated afterwards.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `price_history_id` | Surrogate key. PK. | Yes | Yes |
| `menu_item_id` | Product whose price changed. FK → `MENU_ITEM`. | Yes | No |
| `old_price` | Price before the change; empty for the seed row, which has no predecessor. | No | No |
| `new_price` | Price from the moment of the change onwards. | Yes | No |
| `changed_by` | Database user or staff member who made the change. | Yes | No |
| `changed_at` | When the change was made. | Yes | No |

### 2.6 `INGREDIENT` — the stock

One row per thing the kitchen counts: beans, milk, syrup, cups. **Source:** derived — the source
has no inventory, so quantities are sample data.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `ingredient_id` | Surrogate key. PK. | Yes | Yes |
| `ingredient_name` | Name used on the stock sheet (`Whole milk`, `Arabica beans`). | Yes | Yes |
| `unit` | Unit the quantity is counted in: `g`, `ml`, `pc`. | Yes | No |
| `qty_on_hand` | Quantity currently in the store; `trg_line_stock` decrements it on every sale. | Yes | No |
| `reorder_level` | Quantity at or below which the low-stock view raises the item. | Yes | No |

`qty_on_hand` is never allowed below zero: the trigger raises `-20001` instead, so the column is
a running balance the database defends, not a number a screen can overwrite.

### 2.7 `MENU_ITEM_INGREDIENT` — the recipe (junction table)

Resolves the many-to-many between products and ingredients: a drink uses several ingredients, and
an ingredient is used by several drinks. **Source:** derived from the catalogue descriptions.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `menu_item_id` | Product being made. Part of the PK. FK → `MENU_ITEM`. | Yes | Yes (with `ingredient_id`) |
| `ingredient_id` | Ingredient consumed. Part of the PK. FK → `INGREDIENT`. | Yes | Yes (with `menu_item_id`) |
| `qty_per_unit` | How much of the ingredient one sold unit of the product consumes, in the ingredient's unit. | Yes | No |

The composite key is the rule: one product cannot be listed twice for the same ingredient. To
change a quantity you update the row, you do not add a second one.

### 2.8 `PAYMENT_METHOD` — the ways to pay

Two rows in this extract (`BCA`, `Cash`); `GoFood` exists in the full source and will be added so
next month's file loads without a schema change. **Source:** real.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `method_code` | Short code stored on the payment (`BCA`, `CASH`, `GOFOOD`). PK. | Yes | Yes |
| `method_name` | Name printed on the receipt and shown on the cash-up. | Yes | Yes |
| `is_cash` | `Y` if the money lands in the drawer and has to be counted at closing. | Yes | No |

### 2.9 `ORDERS` — the receipt header

One row per receipt: who sold it, where, when, and what it came to. The header never computes its
own totals from the screen; `trg_order_totals` recomputes them from the lines. **Source:** real.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `order_id` | Surrogate key. PK. | Yes | Yes |
| `order_no` | Receipt number the customer is given (`SHOP001JAN2500009`). Alternate key. | Yes | Yes |
| `outlet_code` | Shop that made the sale. FK → `OUTLET`. | Yes | No |
| `staff_id` | Person who took the order. FK → `STAFF`. Empty for historical receipts, which name nobody. | No | No |
| `ordered_at` | Date and time of the sale, built from `Date` + `Time`. | Yes | No |
| `status` | `OPEN` (lines still being added), `PAID`, `CLOSED` (paid and final), `CANCELLED`. | Yes | No |
| `net_amount` | Sale value before tax, from the receipt; equals the sum of the lines divided by 1.11. | Yes | No |
| `tax_amount` | The 11 % tax on that receipt. | Yes | No |
| `total_amount` | What the customer owed, tax-inclusive and rounded to the rupiah. | Yes | No |
| `amount_paid` | Sum of the payments recorded against the receipt; `fn_payment_balance` is this against `total_amount`. | Yes | No |
| `loyalty_used` | `Y` when a loyalty card was presented. A flag only: it identifies no customer. | Yes | No |

**Rule on the amounts:** `status` may not become `CLOSED` while `total_amount − amount_paid > 0`
(`fn_payment_balance`), and a paid receipt may not be edited (`-20002`).

### 2.10 `ORDER_LINE` — one product on one receipt

The 638 lines of the extract. **Source:** real.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `order_line_id` | Surrogate key. PK. | Yes | Yes |
| `order_id` | Receipt the line belongs to. FK → `ORDERS`. | Yes | No |
| `menu_item_id` | Product sold. FK → `MENU_ITEM`. | Yes | No |
| `line_no` | Position of the line on the receipt (1, 2, …), the order the till printed. | Yes | Yes (with `order_id`) |
| `quantity` | Units sold on this line; 1 on every line of this extract. | Yes | No |
| `unit_price` | Price actually charged for one unit, copied from `MENU_ITEM.unit_price` at the moment of sale and never recalculated afterwards. | Yes | No |
| `line_total` | `quantity × unit_price`, net of any line discount, as the bill was printed. | Yes | No |

**Composite unique:** (`order_id`, `line_no`) — a receipt cannot have two line 1s. This is the
natural key from the 1NF step, kept alongside the surrogate.

**Why `unit_price` is stored here:** it is not the product's current price. If the shop raises a
price tomorrow, this month's receipts must still add up to what the customer actually paid. That
is the one deliberate redundancy in the schema, and `normalization.md` §9 defends it.

### 2.11 `PAYMENT` — money received

One row per payment. One receipt normally has one; a split payment is a second row, not a second
column. **Source:** real.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `payment_id` | Surrogate key. PK. | Yes | Yes |
| `order_id` | Receipt being paid. FK → `ORDERS`. | Yes | No |
| `method_code` | How it was paid. FK → `PAYMENT_METHOD`. | Yes | No |
| `paid_at` | When the money was received; normally the same minute as `ordered_at` in this extract. | Yes | No |
| `amount` | Amount received. `SUM(amount)` per receipt may not exceed the bill (`-20004`). | Yes | No |
| `status` | `SETTLED`, or `VOID` for a payment reversed by a manager; a void payment still occupies its row. | Yes | No |

**Rules:** no payment may be recorded against a `CANCELLED` order (`-20003`); no payment may take
the receipt above its total (`-20004`).

### 2.12 `STOCK_MOVEMENT` — every change to stock

One row per movement, written by the trigger that causes it, so the ingredient balance can always
be reconstructed. **Source:** generated.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `movement_id` | Surrogate key. PK. | Yes | Yes |
| `ingredient_id` | Ingredient that moved. FK → `INGREDIENT`. | Yes | No |
| `order_id` | Sale that consumed it. FK → `ORDERS`; empty for a purchase, a count correction or waste. | No | No |
| `movement_type` | `SALE`, `PURCHASE`, `ADJUSTMENT`, `WASTE`. | Yes | No |
| `qty` | Signed quantity in the ingredient's unit: negative when stock leaves, positive when it arrives. | Yes | No |
| `moved_at` | When the movement happened. | Yes | No |

### 2.13 `PROMOTION` — a named discount

One row per offer the shop runs, with the window it is valid in. **Source:** derived (the source
records no discounts; only the 16 zero-value receipts hint at one).

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `promotion_id` | Surrogate key. PK. | Yes | Yes |
| `promo_name` | Name staff use (`Happy hour 15 %`, `Loyalty redemption`). | Yes | Yes |
| `discount_pct` | Percentage taken off; above 20 requires a `MANAGER` (`-20005`). | Yes | No |
| `valid_from` | First day the offer applies. | Yes | No |
| `valid_to` | Last day the offer applies; must not be before `valid_from`. | Yes | No |

### 2.14 `ORDER_PROMOTION` — discounts applied (junction table)

Resolves the many-to-many between receipts and promotions: one receipt can carry more than one
offer, and one offer applies to many receipts. It is also where the amount actually taken off is
frozen, because the percentage may change later. **Source:** generated.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `order_promotion_id` | Surrogate key. PK. | Yes | Yes |
| `order_id` | Discounted receipt. FK → `ORDERS`. | Yes | No |
| `promotion_id` | Offer applied. FK → `PROMOTION`. | Yes | No |
| `discount_pct` | Percentage applied at the time, copied so the receipt keeps its own arithmetic. | Yes | No |
| `discount_amount` | Money taken off that receipt by this offer. | Yes | No |

**Composite unique:** (`order_id`, `promotion_id`) — the same offer cannot be applied twice to one
receipt.

**Open decision (from `normalization.md` §8 item 10):** the 16 zero-value loyalty receipts should
load as a 100 % `Loyalty redemption` promotion rather than as a discount, because a 100 % discount
would be refused by the `-20005` rule. That rule is about protecting the shop from an unauthorised
discount; a loyalty redemption is not one.

### 2.15 `AUDIT_LOG` — what changed, and who changed it

One row per audited action: a price change, a deletion, a refused operation. **Source:** generated.

| Column | Meaning | Required | Unique |
| --- | --- | --- | --- |
| `audit_id` | Surrogate key. PK. | Yes | Yes |
| `table_name` | Table the change happened in (`MENU_ITEM`, `ORDERS`). | Yes | No |
| `record_key` | Key of the affected row, as text, so one log can hold keys of any type. | Yes | No |
| `action` | `INSERT`, `UPDATE`, `DELETE` or `REFUSED`. | Yes | No |
| `old_value` | Value before the change; empty for an insert or a refused attempt. | No | No |
| `new_value` | Value after the change; empty for a delete. | No | No |
| `db_user` | Oracle user that made the change (`ORA_LOGIN`), which is what makes the log trustworthy. | Yes | No |
| `logged_at` | When the row was written. | Yes | No |

**No foreign key, deliberately.** The log has to outlive the rows it describes and must be able
to point at any table, including ones added later, so the reference is a name plus a key rather
than a constraint. This is the one place where a text reference is the right design.

---

## 3. Relationships, cardinality and optionality

Read each row as: *one* parent — *how many* children — and *may the child exist without the
parent*.

| # | Parent | Child | Cardinality | Optionality | On delete |
| --- | --- | --- | --- | --- | --- |
| 1 | `OUTLET` | `STAFF` | 1 — 1..* | Mandatory: every staff member belongs to one shop | Restrict |
| 2 | `OUTLET` | `ORDERS` | 1 — 1..* | Mandatory: every receipt was rung up somewhere | Restrict |
| 3 | `STAFF` | `ORDERS` | 1 — 0..* | Optional: a historical receipt may have no staff member | Set NULL |
| 4 | `MENU_CATEGORY` | `MENU_ITEM` | 1 — 1..* | Mandatory: every product is sold under a section | Restrict |
| 5 | `MENU_ITEM` | `ORDER_LINE` | 1 — 0..* | Mandatory on the line: a line cannot name a product that does not exist | Restrict |
| 6 | `MENU_ITEM` | `MENU_ITEM_INGREDIENT` | 1 — 0..* | Mandatory: a recipe row belongs to exactly one product | Cascade |
| 7 | `INGREDIENT` | `MENU_ITEM_INGREDIENT` | 1 — 0..* | Mandatory: a recipe row names an existing ingredient | Restrict |
| 8 | `INGREDIENT` | `STOCK_MOVEMENT` | 1 — 0..* | Mandatory: every movement is about one ingredient | Restrict |
| 9 | `ORDERS` | `ORDER_LINE` | 1 — 1..* | Mandatory: a receipt with no lines is not a sale | Cascade |
| 10 | `ORDERS` | `PAYMENT` | 1 — 0..* | Optional: an open order has no payment yet | Restrict |
| 11 | `PAYMENT_METHOD` | `PAYMENT` | 1 — 0..* | Mandatory: every payment used a defined method | Restrict |
| 12 | `ORDERS` | `ORDER_PROMOTION` | 1 — 0..* | Mandatory: a discount row belongs to one receipt | Cascade |
| 13 | `PROMOTION` | `ORDER_PROMOTION` | 1 — 0..* | Mandatory: a discount names an existing offer | Restrict |
| 14 | `ORDERS` | `STOCK_MOVEMENT` | 1 — 0..* | Optional: purchases and stock counts have no order | Set NULL |
| 15 | `MENU_ITEM` | `PRICE_HISTORY` | 1 — 0..* | Mandatory: a price change is about one product | Cascade |
| 16 | — | `AUDIT_LOG` | none | No constraint: the log references rows by name and key | — |

**What the extract proves about these cardinalities:** all 550 receipts have at least one line
(minimum 1, maximum 2), so relationship 9 is `1 — 1..*` in practice, not `0..*`. Every receipt has
exactly one payment, so relationship 10 is `1 — 0..*` in the model and one row in the data. No
receipt carries a promotion, which is why `ORDER_PROMOTION` is empty until the loyalty decision
in §2.14 is applied.

**The two many-to-many relationships** are 6/7 (products ↔ ingredients, through
`MENU_ITEM_INGREDIENT`) and 12/13 (receipts ↔ promotions, through `ORDER_PROMOTION`). Neither can
be drawn as a direct link, which is exactly why the junction tables exist.

---

## 4. Business rules and where they live

Every rule in the project README is enforced by the database, not by a screen. This table says
which columns each rule touches, so a reviewer can see the rule has a place to live.

| Rule | Enforced by | Columns involved | Error |
| --- | --- | --- | --- |
| A line is priced from the menu, never typed by the cashier | `trg_line_price` (BEFORE INSERT) | `ORDER_LINE.unit_price` ← `MENU_ITEM.unit_price` | — |
| A line cannot have a negative or zero quantity | `trg_line_price` | `ORDER_LINE.quantity` | `-20001`-family |
| A sale cannot consume stock the shop does not have | `trg_line_stock` (AFTER INSERT) | `INGREDIENT.qty_on_hand`, `MENU_ITEM_INGREDIENT.qty_per_unit` | `-20001` |
| Every sale leaves a stock trail | `trg_line_stock` | `STOCK_MOVEMENT.qty`, `order_id` | — |
| The header totals always equal the sum of the lines | `trg_order_totals` | `ORDERS.net_amount`, `tax_amount`, `total_amount` | — |
| A paid receipt cannot be edited | `trg_order_totals` | `ORDERS.status`, `amount_paid` | `-20002` |
| No payment on a cancelled order | `trg_payment_guard` | `ORDERS.status`, `PAYMENT.amount` | `-20003` |
| No payment above the bill | `trg_payment_guard` | `PAYMENT.amount`, `ORDERS.total_amount` | `-20004` |
| No closure while money is owed | `sp_close_order` + `fn_payment_balance` | `ORDERS.status`, `amount_paid`, `total_amount` | `-20006`-family |
| A discount above 20 % needs a manager | `sp_apply_promotion` | `PROMOTION.discount_pct`, `ORDER_PROMOTION.discount_amount`, `STAFF.role` | `-20005` |
| Stock never goes negative | `INGREDIENT.qty_on_hand` check + trigger | `qty_on_hand` | `-20001` |
| A price change is history, not an edit | `trg_price_audit` | `PRICE_HISTORY.old_price`, `new_price`, `changed_by` | — |
| Deleting an order is visible forever | `trg_order_audit` | `AUDIT_LOG.action`, `record_key`, `db_user` | — |

The two error codes not fixed in the README (`-20006` and the quantity code) are marked as such
rather than invented; Phase IV assigns them when the package is written.

---

## 5. Summary of keys

| Table | Primary key | Alternate keys | Foreign keys |
| --- | --- | --- | --- |
| `OUTLET` | `outlet_code` | — | — |
| `STAFF` | `staff_id` | — | `outlet_code` → OUTLET |
| `MENU_CATEGORY` | `category_id` | `category_name` | — |
| `MENU_ITEM` | `menu_item_id` | (`item_name`, `variant`) | `category_id` → MENU_CATEGORY |
| `PRICE_HISTORY` | `price_history_id` | — | `menu_item_id` → MENU_ITEM |
| `INGREDIENT` | `ingredient_id` | `ingredient_name` | — |
| `MENU_ITEM_INGREDIENT` | (`menu_item_id`, `ingredient_id`) | — | both, → MENU_ITEM / INGREDIENT |
| `PAYMENT_METHOD` | `method_code` | `method_name` | — |
| `ORDERS` | `order_id` | `order_no` | `outlet_code` → OUTLET, `staff_id` → STAFF |
| `ORDER_LINE` | `order_line_id` | (`order_id`, `line_no`) | `order_id` → ORDERS, `menu_item_id` → MENU_ITEM |
| `PAYMENT` | `payment_id` | — | `order_id` → ORDERS, `method_code` → PAYMENT_METHOD |
| `STOCK_MOVEMENT` | `movement_id` | — | `ingredient_id` → INGREDIENT, `order_id` → ORDERS |
| `PROMOTION` | `promotion_id` | `promo_name` | — |
| `ORDER_PROMOTION` | `order_promotion_id` | (`order_id`, `promotion_id`) | `order_id` → ORDERS, `promotion_id` → PROMOTION |
| `AUDIT_LOG` | `audit_id` | — | none (by design) |

Sixteen foreign keys in total, two composite primary keys (`MENU_ITEM_INGREDIENT` and nothing
else — `ORDER_LINE` keeps a surrogate) and seven alternate keys, which are the business keys the
shop actually says out loud: the receipt number, the product and its variant, the section name,
the stock item, the payment method, the promotion name and the line position.
