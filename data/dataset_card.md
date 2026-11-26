# Dataset card — Restaurant Order and Sales Tracking System (ROSTS)

**Student:** Queen Ineza · **Student ID:** 29354
**Course:** INSY 8311 – Database Development with PL/SQL · **Instructor:** Eric Maniraguha
**Institution:** Adventist University of Central Africa · **Academic year:** 2026–2027, Semester I
**Phase II deliverable:** `data/dataset_card.md`

---

## 1. Identity

| Field | Value |
| --- | --- |
| Title | Anonymous Transactional Dataset (Version 2) |
| Authors | Engel, M. M., Gaol, F. L., Kurniawan, A., & Budiharto, W. (2026) |
| Publisher | Mendeley Data (Elsevier) |
| DOI | 10.17632/kcgf45y24m.2 |
| Landing page | https://data.mendeley.com/datasets/kcgf45y24m/2 |
| Licence | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| Format | CSV, comma-separated, quoted where a field contains a comma, UTF-8 text. Source files use CRLF; the copies committed here use LF, which is the only change made to them. |
| Size in this repository | 7 files, 70,421 bytes: 6 daily receipt files (`pos_shop001_2025-01-02.csv` … `-01-07.csv`) at 55,541 bytes in total, plus `products_catalog.csv` at 14,880 bytes |
| Rows | 550 receipts (plus 6 header rows) and 96 products (plus 1 header row) |
| Period covered by this extract | Trading days 2025-01-02 to 2025-01-07 (six days; the source has no 1 January rows) |
| Date collected | Transactions recorded by the shop's point-of-sale between 2 and 7 January 2025; downloaded from Mendeley Data in November 2026 as version 2 of the deposit |
| Producer of the data | A food-and-beverage micro/small enterprise operating three outlets in Indonesia, exported from its own POS system and anonymised by the dataset authors before publication |
| Currency | Indonesian rupiah (IDR). The amounts are plain integers and decimals, not RWF. |

## 2. What one record represents

**One row is one receipt, not one product sold.** A row records a single completed sale at a single outlet at a single timestamp: the receipt number the POS printed, the trading day and time, the net amount before tax, the 11 % tax, the amount actually paid, the payment method, whether a loyalty card was used, and the name(s) of the items on that receipt written into one cell, separated by a comma.

So 550 rows describe 550 sales, and those sales contain **638 item occurrences** (462 receipts carry one item, 88 carry two). The item names are free text produced by the till, for example `Basic Latte (Ice Arabica)` or `Green Thai Tea, WHITE (Arabica)`.

`products_catalog.csv` is the second half of the dataset: one row per sellable product and variant, with its product id, name, variant, category, catalogue price and a short Indonesian description.

## 3. Scope of this extract and how it was taken

The full source holds 53,820 receipts from three outlets across nine months. The assignment asks for a few hundred records, so the committed extract is the whole of one outlet for the first week:

```
receipts where Outlet = 'SHOP001' and Date between 2025-01-02 and 2025-01-07   ->  550 rows
```

The 550 rows are split into six files, one per trading day, and every row keeps all eleven original columns in their original order. No value was edited, re-priced, joined or invented; each daily file was produced by filtering the original file and keeping its header row. `data/README.md` §3 records the rule and §7 shows how to rebuild the files from the full download and check them with SHA-256.

Per-day row counts and takings in this extract:

| Trading day | Receipts | TotalAmount |
| --- | ---: | ---: |
| 2025-01-02 (Thu) | 82 | 2,007,000 |
| 2025-01-03 (Fri) | 101 | 2,591,000 |
| 2025-01-04 (Sat) | 99 | 2,473,000 |
| 2025-01-05 (Sun) | 90 | 2,114,000 |
| 2025-01-06 (Mon) | 82 | 1,885,000 |
| 2025-01-07 (Tue) | 96 | 2,472,000 |
| **Total** | **550** | **13,542,000** |

## 4. Columns as stored

`pos_shop001_YYYY-MM-DD.csv` — 11 columns, 550 rows:

| Column | Meaning | Example | Stored as |
| --- | --- | --- | --- |
| `Outlet` | Shop code | `SHOP001` | Text |
| `Date` | Sale date, ISO order | `2025-01-02` | Text |
| `Time` | Sale time, 24-hour | `07:01:05` | Text |
| `NetSales` | Amount before tax (3 decimals) | `20720.721` | Text that reads as a decimal |
| `Tax` | Tax on the sale, 11 % (3 decimals) | `2279.279` | Text that reads as a decimal |
| `TotalAmount` | Amount paid, whole rupiah | `23000` | Text that reads as an integer |
| `ReceiptNumber` | Receipt / order number | `SHOP001JAN2500001` | Text |
| `Items` | Item name or names, comma-separated inside quotes | `"Green Thai Tea, WHITE (Arabica)"` | Text holding a list |
| `TotalItem` | Number of items on the receipt (1 or 2) | `2` | Text that reads as an integer |
| `PaymentMethod` | How the customer paid | `BCA` | Text |
| `UseLoyaltyCard` | 0/1 loyalty-card flag | `0` | Text that reads as 0 or 1 |

`products_catalog.csv` — 6 columns, 96 rows: `ProductId` (1–96), `ProductName`, `Variant` (`-` when the product has no variant), `Category`, `Price` (IDR, 0–30000), `Description` (Indonesian free text).

Catalogue composition: Coffee 34, Menu Gedhe 19, Other 15, Tea 13, Snacks 9, Add on 6. Fifty-six products have no variant (`-`); the other forty use the `Variant` column.

## 5. Personal data

There is none, and this is why the dataset was chosen. The receipt file carries no customer name, phone number, e-mail, card number, address or national ID; the only customer-related field is `UseLoyaltyCard` (0 or 1), which says that a loyalty card was presented without saying whose. Outlets appear as codes (`SHOP001`–`SHOP003`), never as an address, and there is no staff identifier at all.

Nothing was added to the source files, so the committed copies are exactly as anonymised by the authors, and every value in them is already non-identifying. The staff names that Phase IV will need are invented placeholder records and are labelled `record_source = 'DERIVED'` in `data/README.md` §6 so they cannot be mistaken for real employees.

## 6. Quality check — what was measured

Every file was read with a script (Python 3, `csv` module, no cleaning applied) and the checks below were run over all 550 rows and 96 catalogue rows. The point of the table is the count, not the verdict.

| # | Check | Count of what was found |
| --- | --- | --- |
| 1 | Rows per file | 82, 101, 99, 90, 82, 96 → **550** receipts (+ 6 headers) |
| 2 | Cells expected / cells filled | 550 × 11 = 6,050 expected, **6,050 filled, 0 blank** |
| 3 | Duplicate receipt numbers | **0** (550 distinct receipt numbers) |
| 4 | Fully duplicated rows | **0** |
| 5 | Receipt-number sequence | 1 … 550, **0 gaps**, 0 malformed numbers |
| 6 | `Date` against the file's own name | **0 mismatches** (550 of 550 agree) |
| 7 | `TotalItem` against the number of names in `Items` | **0 mismatches**; 638 item occurrences in total |
| 8 | Items per receipt | 462 receipts with 1 item, **88 with 2 items** (16 %) |
| 9 | Distinct item names | **94** names, appearing 638 times |
| 10 | Item names that resolve to the product catalogue | **94 of 94 resolve, 0 unresolved** |
| 11 | Products in the catalogue that were never sold | **2** (`Add on Aren` id 1, `Add on Simple Syrup` id 2, both price 0) |
| 12 | `NetSales` + `Tax` − `TotalAmount` | **0 for all 550 rows** (the three amounts agree exactly, no rounding gap in this extract) |
| 13 | `Tax` against 11 % of `NetSales` | **0 exceptions** in 550 rows |
| 14 | Receipt total against the sum of catalogue prices of its items | **534 of 550 equal to the rupiah; 16 differ** |
| 15 | Receipts whose paid amount is 0 | **16** (2.9 %), all with `UseLoyaltyCard = 1` and all `Cash`; they are also the 16 rows in check 14 |
| 16 | Amounts stored as text | **1,650 of 1,650** money cells need conversion (`NetSales` and `Tax` with 3 decimals, `TotalAmount` as integer) |
| 17 | Date and time stored as two text fields | **550 of 550** rows need combining into one timestamp |
| 18 | `Items` cells holding more than one value | **88 cells** hold 2 values, 462 hold 1 → 638 values in 550 cells |
| 19 | Negative, zero-length or non-numeric amounts | **0** |
| 20 | Trading hours | 07:01:05 to 22:59:03, **0 receipts outside 07:00–23:00** |
| 21 | Distinct outlets | **1** (`SHOP001`), repeated on all 550 rows |
| 22 | Distinct payment methods | **2** — `BCA` 433, `Cash` 117. `GoFood` exists in the full source but not in this week |
| 23 | Records with a loyalty card | **16** (2.9 %), all of them zero-value receipts |
| 24 | Amount range | `TotalAmount` 0 to 60,000; mean 24,621.82 |
| 25 | Spelling of "Houseblend" in the data | **2 forms**: `Houesblend` in 1 catalogue row (id 5) and 7 receipt lines, `Houseblend` everywhere else |
| 26 | Product names that already contain their variant | **11** (`Apple Pie Latte (Gedhe)`, `BLACK`, …) against **40** products that use the `Variant` column instead |
| 27 | Categories | **6**; `Menu Gedhe` holds 19 products and is a cup size, not a family of drinks |
| 28 | Catalogue rows with price 0 | **2** (the two add-ons in check 11) |

In short: the extract is complete and internally consistent — no duplicates, no blanks, no broken numbers, tax and totals agree everywhere — and its real problems are structural rather than dirty. Those are listed next.

## 7. Issues found (recorded, not fixed)

**Data is never repaired before Phase IV.** Each item below is a recorded defect plus the count, and each one becomes a line in the cleaning checklist in `docs/design/normalization.md` §8.

1. **16 zero-value receipts.** `SHOP001JAN2500013`, `…038`, `…092`, `…118` and 12 more carry an item and a cash payment of 0 with the loyalty flag set. They look like loyalty redemptions or staff drinks, not errors, but the database cannot tell: the source has no field saying why the amount is zero. 16 rows, 2.9 % of the extract.

2. **Two catalogue products were never sold.** `Add on Aren` and `Add on Simple Syrup` are priced 0 and appear on no receipt. They will load as menu items that are never referenced.

3. **The outlet is repeated on every row.** `SHOP001` appears 550 times and nothing else does, so the shop's name, city and opening date (which the project needs) are not in the receipt file at all and must come from `OUTLET`.

4. **`Items` is a repeating group.** One cell holds one or two item names, comma-separated, inside quotes. Anything that asks "how many espressos did we sell" has to parse text first. 88 cells hold two values.

5. **`TotalItem` duplicates information that can be counted.** It is correct in all 550 rows, which means it is redundant: it repeats what a count of the split lines returns.

6. **Money is stored as text.** `20720.721`, `2279.279` and `23000` are strings that happen to look like numbers. Arithmetic on them silently produces text concatenation or fails.

7. **Date and time are two fields.** `2025-01-02` and `07:01:05` have to be combined to answer "what was sold between 12:00 and 14:00" or to sort a day's receipts.

8. **No line-level money.** For the 88 two-item receipts the receipt gives one net amount, one tax and one total for both items together. The split between the two lines is not in the data, so line prices must come from the catalogue price at the time of sale. That is a modelling decision, not a repair, and it is recorded as such.

9. **One item name is misspelt in both files.** The catalogue writes `Ice Houesblend` for `Americano` (id 5) and the till copied the same spelling onto 7 lines, while every other product spells it `Houseblend`. Two spellings, one product.

10. **The catalogue encodes the variant in two different ways.** Forty products keep it in the `Variant` column (`Americano` + `Ice Arabica`); eleven put it inside the name (`Apple Pie Latte (Gedhe)` with `Variant = -`). The receipts always use the display form `ProductName (Variant)`, which is why all 94 names resolve, but the two conventions have to be normalised into `item_name` + `variant`.

11. **`Menu Gedhe` mixes a size with a product family.** "Gedhe" means large; it is a cup size applied to 19 drinks that also exist in a regular size under Coffee, Tea or Other. As a category it competes with Coffee and Tea instead of describing them.

12. **Fields the restaurant process needs are absent.** There is no recipe, ingredient, stock level, staff member, discount, tax code, order status or customer identity. The database tables for these cannot be loaded from this file and will be derived sample data, labelled as such (`data/README.md` §6).

13. **The week is not a year.** Six days of one outlet out of three, in January. Anything about seasonality, month-end or outlet comparison is outside this extract.

Two things that are *not* issues, checked because they usually are:

- **Rounding.** `NetSales` + `Tax` equals `TotalAmount` in all 550 rows, so no rounding rule has to be invented yet. `23000` paid is `20720.721` net + `2279.279` tax.
- **Duplicates.** None, on either receipt number or whole row, and the receipt numbers run 1 to 550 without a gap, so no receipt was lost when the extract was filtered.

## 8. What this dataset can and cannot answer

**Can answer, from this extract alone:** daily takings and receipt counts per day; which products sold and how many; revenue per product at catalogue price; the split between `BCA` and `Cash`; the busiest hours; how much of the trade is loyalty-linked.

**Cannot answer:** cost, margin or wastage (no purchase prices); ingredient stock (no recipes); which cashier sold what (no staff field); discounts given (no discount field — the 16 zero rows only hint at one); customer behaviour beyond the loyalty flag; anything about outlets 2 and 3, other months, or a full year.

## 9. Licence and attribution

The dataset is published under CC BY 4.0, which allows reuse, adaptation and redistribution provided the authors are credited. This attribution line must stay with any copy of the files:

> Engel, M. M., Gaol, F. L., Kurniawan, A., & Budiharto, W. (2026). *Anonymous transactional dataset* (Version 2) [Data set]. Mendeley Data. https://doi.org/10.17632/kcgf45y24m.2

The data is used unmodified, for coursework only, and is redistributed here under the same licence. It is not resold, and no claim is made that the shop is Rwandan or that the amounts are in RWF.

## 10. Verification

The checksum of every committed file, the exact filter that produced the extract, and the commands to re-download and verify the original are in [`data/README.md`](README.md) §2, §3 and §7. Re-running the filter on the full file reproduces the six daily files byte for byte, so the quality figures in §6 can be re-checked at any time.
