# Data — provenance, licence and what is real

Project: Restaurant Order and Sales Tracking System (ROSTS) · Queen Ineza · 29354 · INSY 8311

## 1. Source

Engel, M. M., Gaol, F. L., Kurniawan, A., & Budiharto, W. (2026). *Anonymous transactional
dataset* (Version 2) [Data set]. Mendeley Data. https://doi.org/10.17632/kcgf45y24m.2

- **Landing page:** https://data.mendeley.com/datasets/kcgf45y24m/2
- **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0) — reuse, adaptation
  and redistribution allowed with attribution. The attribution line above must stay with any
  copy of the data.
- **What the authors say it is:** "real-world historical sales transactions and product
  metadata collected from a local Food and Beverage (F&B) Micro-Small-Medium Enterprise
  (MSME) operating multiple outlets in Indonesia", extracted from the business's own
  point-of-sale system between January 2025 and September 2025, then cleaned and anonymised.
- **Personal data:** none. The receipt file has no customer name, phone, e-mail, card or
  address; the only customer field is `UseLoyaltyCard` (0/1), and outlets are codes
  (`SHOP001`–`SHOP003`). Nothing in this repository can identify a person.
- **Currency:** Indonesian rupiah (IDR). Amounts are plain numbers; do not read them as RWF.

## 2. Files in this repository

| File | Bytes | Rows | SHA-256 |
| --- | --- | --- | --- |
| `raw/pos_transactions_shop001_2025-01-01_07.csv` | 55,036 | 550 receipts + header | `0704f000dd28d0e575ce151a87fc643a3f2fa223b10e3984985f20dd099b53e8` |
| `raw/products_catalog.csv` | 14,880 | 96 products + header | `7d033598c73778e827d3ed85c1a5b2eac391117e5e562cde130e93c43e0acb62` |

The committed copies use LF line endings (the source uses CRLF); that is the only change,
and the checksums above are the checksums of the files in this repository, so they can be
verified after a clone.

The full receipt file is **not** committed (5.4 MB, 53,820 receipts). Its checksum is recorded
so a re-download can be verified:

| File | Bytes | Rows | SHA-256 |
| --- | --- | --- | --- |
| `Transactions.csv` (full, not committed) | 5,412,042 | 53,820 receipts + header | `36f2412969f8241e72b5f3eb395e5af13a7ba042de1e6ecdbe32bee23723ef90` |

## 3. The subset rule (exactly reproducible)

The assignment asks for a few hundred records. The committed file is the whole of outlet
`SHOP001` for the first week of the source period:

```
receipts where Outlet = 'SHOP001' and Date between 2025-01-02 and 2025-01-07   ->  550 rows
```

Every row keeps all eleven original columns, unmodified and in the original order. Nothing was
edited, re-priced or invented; the file was produced by filtering the original, and the header
row is the original header row.

Facts about the committed subset: 433 receipts paid by `BCA`, 117 by `Cash`; 13,542,000 in
`TotalAmount` across the week; 2025-01-02 to 2025-01-07 (the source has no 1 January rows).

## 4. Columns of the receipt file

| Column | Meaning | Example |
| --- | --- | --- |
| `Outlet` | Shop code | `SHOP001` |
| `Date` | Sale date (ISO) | `2025-01-02` |
| `Time` | Sale time | `07:01:05` |
| `NetSales` | Amount before tax | `20720.721` |
| `Tax` | Tax on the sale (11 %) | `2279.279` |
| `TotalAmount` | Amount paid, whole rupiah | `23000` |
| `ReceiptNumber` | Receipt / order number | `SHOP001JAN2500001` |
| `Items` | Item name(s), comma-separated inside quotes | `"BLACK (Arabica), Americano (Hot Arabica)"` |
| `TotalItem` | Number of items on the receipt (1 or 2) | `2` |
| `PaymentMethod` | `BCA`, `Cash` or `GoFood` | `BCA` |
| `UseLoyaltyCard` | 0/1 loyalty-card flag | `0` |

`products_catalog.csv` columns: `ProductId, ProductName, Variant, Category, Price, Description`
(96 products in six categories: Coffee 34, Menu Gedhe 19, Other 15, Tea 13, Snacks 9, Add on 6).

## 5. Quirks to expect in Phase II

- **One row is one receipt, not one line item.** 45,667 receipts in the full file carry one
  item and 8,153 carry two; `Items` is a quoted, comma-separated list. Splitting it into
  `ORDER_LINE` rows and resolving each free-text name against `MENU_ITEM` is Phase II work.
- **Product names in the receipts do not always match the catalogue verbatim** (for example
  `BLACK (Houseblend)` versus the catalogue's product/variant columns), so matching needs a
  documented rule and an unresolved-name exception list.
- **Two amounts are rounded differently.** `NetSales` + `Tax` is a decimal sum; `TotalAmount`
  is the rounded amount actually paid. The difference must not be "fixed" in the source; it is
  a rounding rule the database has to define.
- **Some receipts carry `Price = 0` products** (`Add on` items with a zero catalogue price) —
  handle them as zero-value lines rather than as missing prices.
- Files are CRLF-terminated in the source and the full source file has no final newline, so
  `wc -l` reports one line fewer than the row count.

## 6. What is real and what is derived

| Table group | Origin |
| --- | --- |
| `ORDERS`, `ORDER_LINE`, `PAYMENT`, `PAYMENT_METHOD`, `MENU_ITEM`, `MENU_CATEGORY`, `OUTLET` | **Real** — built from the receipts and the product catalogue |
| `INGREDIENT`, `MENU_ITEM_INGREDIENT`, `STOCK_MOVEMENT` | **Derived sample data** — the source has no recipes or stock. Quantities will be assigned from the product descriptions and labelled `record_source = 'DERIVED'` |
| `STAFF` | **Derived sample data** — the source has no staff identifier; cashiers/managers are invented, labels say so |
| `PRICE_HISTORY`, `PROMOTION`, `ORDER_PROMOTION`, `AUDIT_LOG` | **Generated by the system** — rows appear when the PL/SQL runs, not from the source |

No derived row will be presented as observed trade. Where a figure is invented, the row says
`DERIVED` and `docs/proposal/proposal.md` and `README.md` say the same thing.

## 7. Re-download and verify

```bash
# full receipt file (5.4 MB)
curl -sSL -o Transactions.csv \
  "https://data.mendeley.com/public-files/datasets/kcgf45y24m/files/37d9b41e-ef66-4e3d-af99-30e14722cc5e/file_downloaded"

# product catalogue
curl -sSL -o Products.csv \
  "https://data.mendeley.com/public-files/datasets/kcgf45y24m/files/f7bc2906-5c36-4791-b84e-04ad26f7f80d/file_downloaded"

# verify (Git Bash / Linux / macOS)
sha256sum Transactions.csv Products.csv
# verify (PowerShell)
Get-FileHash Transactions.csv -Algorithm SHA256
```

Rebuild the committed subset from the full file:

```bash
{ head -1 Transactions.csv; grep -E '^SHOP001,2025-01-0[1-7]' Transactions.csv; } \
  > pos_transactions_shop001_2025-01-01_07.csv
```

The download links above are the direct file URLs of the Mendeley deposit. If a link ever
changes, the DOI (`10.17632/kcgf45y24m.2`) resolves to the current version.
