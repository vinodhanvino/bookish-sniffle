# Bar Variance – Domain Model

## Scope

Liquor only. Sales/NC from LucidPOS Excel (section/classification = "Liquor"). Purchase Excel = item master and receipt. No API; read Excel only.

---

## Entities

### Report (header)

- **report_date**: date
- **lines**: list of ReportLine
- Optional: location/bar id for multi-bar later

### ReportLine (one per liquor item per report date)

**Identity**
- particulars: str (item name)
- category: str
- group: str

**Movement**
- opening_balance: Decimal
- receipt: Decimal
- transfer_in: Decimal
- transfer_out: Decimal
- total: Decimal (computed)
- closing_balance: Decimal (computed)
- physical_closing: Decimal (main_bar_closing + store_closing)

**Sales / usage**
- sale_ala_carte: Decimal
- sale_nc: Decimal
- sale_cocktail: Decimal
- sale_banquet: Decimal
- adjustments: Decimal (+/-)
- spillage: Decimal

**Variance**
- variance_qty: Decimal (closing_balance - physical_closing)
- selling_price: Decimal
- variance_in_sales: Decimal (variance_qty * selling_price)
- cost_price: Decimal
- variance_in_cost: Decimal (variance_qty * cost_price)

**Location**
- main_bar_opening: Decimal (yesterday main_bar_closing)
- main_bar_closing: Decimal (manual)
- store_opening: Decimal (yesterday store_closing)
- store_closing: Decimal (manual)

---

## Value objects / DTOs

### ClosingInput (manual entry)

- item_id or particulars: str
- main_bar_closing: Decimal
- store_closing: Decimal
- Optional: adjustments, spillage

### PurchaseRow (from purchase Excel)

- particulars: str
- category: str | None
- group: str | None
- quantity: Decimal (receipt)
- cost_price: Decimal
- selling_price: Decimal | None

### SalesRow (from sales Excel, Liquor only)

- particulars: str
- quantity: Decimal
- sale_type: Ala Carte | NC | Cocktail | Banquet (or mapped enum)

### NCRow (from NC Excel, Liquor only)

- particulars: str
- quantity: Decimal

---

## Repository (abstract)

- get_report(date: date) -> Report | None
- save_report(report: Report) -> None
- get_previous_report(date: date) -> Report | None  # date - 1 day

---

## Computed rules

- total = opening_balance + receipt + transfer_in - transfer_out
- closing_balance = total - (sale_ala_carte + sale_nc + sale_cocktail + sale_banquet + spillage - adjustments)
- physical_closing = main_bar_closing + store_closing
- variance_qty = closing_balance - physical_closing
- variance_in_sales = variance_qty * selling_price
- variance_in_cost = variance_qty * cost_price

Opening: main_bar_opening = previous_report.main_bar_closing; store_opening = previous_report.store_closing. If no previous report, opening = 0.
