# Research log — Restaurant Order and Sales Tracking System (ROSTS)

Queen Ineza · 29354 · INSY 8311 · Phase 0

## How this log was built

Each entry below was opened and read before it was written down: papers through their
abstract and introduction, the statistic on the producer's own page, the existing system on
the vendor's product page, the dataset by downloading its files and counting the rows, the
technical reference in Oracle's 19c manual. Where a source was only read as an abstract, the
entry says so. No source here is cited from memory, and no citation was written before the
page was open.

The previous version of this file (`Reseach_log.md`) is deleted: it listed "ResearchGate
Link", "IJIRT Link", "NISR Rwanda" and "Kaggle" as links, and at least one entry
("Islama et al., 2024, Restaurant Order Management System") could not be located at all.
A citation that cannot be opened is not evidence, and the assignment treats an unread
reference as plagiarism.

---

## 1. Memis Kocaman, E. (2021) — research paper

**Reference.** Memis Kocaman, E. (2021). Operational effects of using restaurant management
system: An assessment according to business features. *International Journal of Gastronomy
and Food Science, 25*, 100408. https://doi.org/10.1016/j.ijgfs.2021.100408

**Type.** Peer-reviewed research paper (Elsevier, Scopus-indexed journal).
**Link.** https://doi.org/10.1016/j.ijgfs.2021.100408 — abstract, highlights and introduction read.

**Key finding.** A structured questionnaire answered by 385 restaurant employees shows that
where a Restaurant Management System (RMS) is used, staff report that it facilitated
operations management, increased sales and produced a more standard service (p < 0.05).
Staff in restaurants without an RMS scored higher on "the system is difficult to use", and
**all** participants agreed that the technical cost of an RMS is high. The positive effect on
operations and sales is strongest in chain restaurants and weakest in restaurants with ten or
fewer staff, so business size drives the need for — and the return on — such a system.

**Gap it shows.** The paper measures the *perception* of existing commercial systems. It does
not look at where the rules live. In the systems it studies, business rules sit in the
application; the database stores whatever it is given. It also confirms the cost barrier that
makes a licensed RMS unattractive to the micro-restaurants that dominate Rwanda's food
service sector.

**What it changes in this design.** Two decisions. (1) The interface must be thin and free —
Oracle APEX in a browser, no per-terminal licence — because the cost of the system is what
small operators object to. (2) The rules must be enforced in the database, so that the value
the paper measures (fewer errors, standard service) does not depend on every cashier using
the screen correctly.

---

## 2. Zamora Saltos, C. E., & Rodríguez Borges, C. G. (2024) — research paper

**Reference.** Zamora Saltos, C. E., & Rodríguez Borges, C. G. (2024). Design of an inventory
management system for a Manabita restaurant. *InGenio, 7*(2).
https://doi.org/10.18779/ingenio.v7i2.808

**Type.** Peer-reviewed research paper (InGenio, Universidad Técnica Estatal de Quevedo).
**Link.** https://revistas.uteq.edu.ec/index.php/ingenio/article/view/808 — abstract read; the
article's PDF is open access.

**Key finding.** A restaurant's inventory problem is not "counting stock" but perishability:
without a system, the restaurant carries high procurement and holding costs, buys more than
it needs, and loses product to damage, expiry and shrinkage. The authors design the system in
six phases fitted to the restaurant's own process and conclude that the design must follow how
that kitchen actually buys, stores and consumes, or the inventory figures will not be trusted.

**Gap it shows.** The delivered tool is a Windows desktop program (PQ) used for tracking; the
stock rules are procedures the staff follow, not constraints the software cannot break. There
is no recipe-level link between a sold dish and the raw materials it consumed, and no audit of
who changed a stock figure.

**What it changes in this design.** The recipe table `MENU_ITEM_INGREDIENT` sits between the
menu and stock, and the deduction is a trigger fired by the sale itself, not a separate data
entry step. The six-phase, process-first lesson is why Phase I models the real flow (order →
kitchen → bill → payment) before any table is created.

---

## 3. National Institute of Statistics of Rwanda (2024) — report / statistic

**Reference.** National Institute of Statistics of Rwanda. (2024). *Establishment Census 2023*.
https://statistics.gov.rw/data-sources/censuses/Establishment-Census/establishment-census-2023

**Type.** Official national statistic (government census report).
**Link.** https://statistics.gov.rw/data-sources/censuses/Establishment-Census/establishment-census-2023 — results page read.

**Key finding.** Rwanda had 269,326 establishments in 2023, of which 261,549 are enterprises.
Wholesale and retail trade accounts for 53.5 % of them, **accommodation and food services for
23.0 %** — the second largest activity in the country. Accommodation and food service
activities employ 12.9 % of the 927,739 workers counted. 95.9 % of establishments are private,
92.0 % are owned by one person and 92.2 % are micro-enterprises with fewer than four workers.
The three districts of Kigali concentrate 24.0 % of all establishments (Gasabo 9.3 %,
Nyarugenge 8.4 %, Kicukiro 6.3 %).

**Gap it shows.** The census counts establishments and workers; it says nothing about how a
single restaurant records a sale. There is no national data on receipts, bills or stock
movements — which is exactly the layer this project builds.

**What it changes in this design.** It sets the scale and the constraint: the target user is a
one-owner, under-four-staff business, so the system must be operable by one cashier on one
screen, must not require an IT administrator, and must produce the day's cash-up without an
accountant.

---

## 4. Oracle (2026b) — existing system

**Reference.** Oracle. (2026). *Oracle Simphony restaurant POS system*.
https://www.oracle.com/food-beverage/restaurant-pos-systems/

**Type.** Existing commercial system (vendor product documentation page).
**Link.** https://www.oracle.com/food-beverage/restaurant-pos-systems/ — product page read.

**Key finding.** Simphony is Oracle's cloud-native restaurant POS: it connects ordering,
payments, kitchen display, inventory, labour management and reporting in one platform, exposes
an open API with more than 200 integration partners, and offers real-time KPI reporting,
table management, promotions and multi-currency support.

**Gap it shows.** It is the system this project is *not*: cloud, licensed per site and per
module, configured through a front-line manager application, and closed to inspection. A
student cannot show the rules that make it correct, cannot change them, and cannot audit them;
and a three-outlet micro-business cannot pay for it. Its existence also sets the bar for what
"good" looks like — real-time reporting and an operator dashboard are expected, not optional.

**What it changes in this design.** The innovation must deliver the two things users of such a
system actually touch: an order/payment screen and a live manager dashboard. Everything else
(recipe deduction, rule triggers, audit log) is the part a commercial POS hides, and it is
where this project's marks are.

---

## 5. Engel, Gaol, Kurniawan & Budiharto (2026) — dataset

**Reference.** Engel, M. M., Gaol, F. L., Kurniawan, A., & Budiharto, W. (2026). *Anonymous
transactional dataset* (Version 2) [Data set]. Mendeley Data.
https://doi.org/10.17632/kcgf45y24m.2

**Type.** Research dataset (Mendeley Data / Elsevier, DOI-registered, CC BY 4.0).
**Link.** https://data.mendeley.com/datasets/kcgf45y24m/2 — files downloaded and counted.

**Key finding (measured, not quoted).** The deposit holds two files. `Transactions.csv`
(5,412,042 bytes, SHA-256 `36f2412…ef90`) contains **53,820 real POS receipts** from a food and beverage MSME with three outlets (`SHOP001`–`SHOP003`), dated 2 January to 30 September
2025, with columns `Outlet, Date, Time, NetSales, Tax, TotalAmount, ReceiptNumber, Items,
TotalItem, PaymentMethod, UseLoyaltyCard`. 45,667 receipts carry one item and 8,153 carry two;
payments are `BCA` (42,805), `Cash` (10,913) and `GoFood` (102); a receipt of 20,720.721 net plus 2,279.279 tax
settles at 23,000, i.e. an 11 % tax line. `Products.csv` (14,976 bytes) lists **96 products** across six categories (Coffee 34, Menu Gedhe 19,
Other 15, Tea 13, Snacks 9, Add on 6) with name, variant, category, price and a description. The authors state the data is real
sales history collected by the business's own POS and anonymised — no customer identifier of
any kind, only a 0/1 loyalty flag.

**Gap it shows.** Receipts are flat rows: item names are free text inside one quoted field,
there is no recipe, no ingredient stock, no staff identifier and no order status. Nothing in
the file links a sold drink to the milk it consumed.

**What it changes in this design.** This is the data the project loads, and it dictates the
Phase II work: split `ORDERS`/`ORDER_LINE`/`PAYMENT` out of the flat row, resolve free-text
item names to `MENU_ITEM`, and derive the recipe, stock and staff tables — labelled
`record_source = 'DERIVED'` in `data/README.md` — rather than pretending the source contains
them. 550 receipts (outlet `SHOP001`, 2–7 January 2025) are committed to `data/raw/`.

---

## 6. Oracle (2026a) — technical source

**Reference.** Oracle. (2026). *CREATE TRIGGER statement* (Oracle Database 19c PL/SQL
Language Reference).
https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/CREATE-TRIGGER-statement.html

**Type.** Official technical reference.
**Link.** https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/CREATE-TRIGGER-statement.html — read.

**Key finding.** A trigger is a stored PL/SQL block the database runs automatically when a
specified condition occurs. `BEFORE` row triggers fire before each affected row changes and
may **write** `:NEW` fields (which is how a line total can be priced from the menu);
`AFTER` row triggers fire per row and may read `:OLD` and `:NEW` but not write them (which is
how the stock movement and the audit row are written). `FOR EACH ROW` makes it a row trigger;
`WHEN (condition)` restricts it per row and may not contain a subquery; a trigger can be
created `DISABLE`d to compile it before it is enabled.

**Gap it shows.** The manual defines the mechanism and the restrictions, not the restaurant
rules; it is also the reason several planned rules must be split across `BEFORE` (price and
total computation) and `AFTER` (stock movement, audit), and why a rule that needs a subquery
must be implemented in a procedure call instead of a `WHEN` clause.

**What it changes in this design.** The trigger set is fixed: `trg_line_price` and
`trg_order_totals` are `BEFORE … FOR EACH ROW` because they write `:NEW`; `trg_line_stock`,
`trg_price_audit` and `trg_order_audit` are `AFTER … FOR EACH ROW`; the mutating-table
problem (`ORDERS` trigger reading `ORDERS`) is avoided by computing totals from `ORDER_LINE`
and by keeping cross-row checks in the package.

---

## Mapping to the assignment's source requirements

| Required | Provided |
| --- | --- |
| At least 2 research papers | Memis Kocaman (2021); Zamora Saltos & Rodríguez Borges (2024) |
| 1 report or statistic | NISR Establishment Census 2023 |
| 1 existing system | Oracle Simphony restaurant POS |
| 1 dataset | Engel et al. (2026), Mendeley Data, CC BY 4.0 |
| 1 technical source | Oracle 19c `CREATE TRIGGER` reference |

## What the research changes about the design (summary)

1. **Rules in the database, not the screen** — the value a management system delivers is
   eroded when the application is the only enforcement point (Memis Kocaman, 2021).
2. **Recipe-level stock, deducted by the sale** — perishability and shrinkage are the real
   inventory problem (Zamora Saltos & Rodríguez Borges, 2024).
3. **One cashier, one screen, no administrator** — 92.2 % of Rwandan establishments are
   micro-enterprises (NISR, 2024).
4. **Dashboard and order screen are mandatory** — a commercial POS already sets that
   expectation (Oracle, 2026b).
5. **Flat receipts must be normalised** into orders, lines and payments, and derived tables
   must be declared as derived (Engel et al., 2026).
6. **`BEFORE` for computation, `AFTER` for consequences** — the trigger timing is not a
   style choice, it is what the engine permits (Oracle, 2026a).

## Sources checked and rejected

- *"Islama, M. A., et al. (2024). Restaurant Order Management System. ResearchGate"* — listed
  in the deleted log with no DOI and no URL; not locatable, therefore not cited.
- Kaggle "Restaurant Sales Data" (rohitgrewal) — no author, no version, and the licence field
  reads "Database: Open Database, Contents: Database Contents"; the deposit gives no
  provenance for the sales rows, so it cannot support a claim about real restaurant trade.
- *Databasesample.com* restaurant sample database (CC0, 23 tables, 2,321 rows) — downloaded
  and inspected; the publisher states the rows are generated, "nothing was sampled from
  anything real". Useful for practising SQL, not evidence, so it is not the data source.
- OpenAIRE/Google Scholar hits behind a paywall with no readable abstract — not cited.
