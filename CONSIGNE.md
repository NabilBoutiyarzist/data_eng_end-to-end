# Data Engineer Exercise

## Context

You work for RetailStore Switzerland, a retail company operating multiple sales channels and stores distributed by region.

The business team wants to better understand **commercial performance** and have **self-service–ready** data.

You are provided with several CSV files describing sales, products, and stores, along with related documentation.

---

## Data Description

The data is provided as CSV files.

### `product.csv`

Product master data.

Includes in particular:

* a product identifier
* classification information (e.g. category)
* descriptive product attributes

### `ent_cde.csv`

Order headers.

Includes in particular:

* store identifier (CMINT)
* order number (NUMCOM)
* order channel (TYPEDEVIS: 0 = store / 54 = web)
* order type (ENTYPE: BL = delivery / EI = immediate pickup / ED = delayed pickup)
* customer identifier (CLINUM)
* delivery customer identifier (CLILIVNUM)
* delivery carrier (CNUFTRP: Post or RetailStore carrier)
* order date (ENDSAI)
* delivery date announced at order time (LIVDAY)

This file represents the **order-level view** (1 row = 1 order).

### `det_cde.csv`

Order details (order lines).

Includes in particular:

* store identifier (CMINT)
* order number (NUMCOM)
* order line number (NUMLIG)
* product identifier (ARTEAN)
* internal product identifier (ARTCAINT)
* short product label (ARTLIBC)
* line status (ETAT: 7 = validated / 17 = cancelled)
* discount flag (CODEREM: -1 = yes / 0 = no)
* discount percentage (REMISE)
* commercial gesture reason (MOTIFREM)
* VAT amount (MNTTVA)
* original unit price incl. VAT (PRIXORI)
* unit sales price incl. VAT (PRIXUPV)
* quantity ordered (VENQTE)
* total sales price incl. VAT (MNTTOT2)
* unit discount amount (REMISE_POURCENT_MNT_U)
* unit exceptional discount amount (REMISE_EXCEPTIONNELLE_MNT_U)

This file represents the **order-line–level view**.

### `store.csv`

Store master data.

Includes in particular:

* store identifier
* geographic information (region, zone, etc.)
* descriptive attributes of the point of sale

---

## Business Questions

The business wants to track RetailStore Switzerland’s commercial performance over time. For example:

* How does **revenue evolve over time**?
* What are the **performance differences** between stores? by channel? by region?
* Which **products or categories** stand out compared to others?

---

## Expected Work

Based on the provided data, you are free to propose a solution that answers these questions.

The exercise is **open-ended**. What we primarily expect:

* your understanding of the business needs,
* your ability to **structure and model** data,
* your ability to produce **reliable and readable KPIs**.

You are free to choose:

* the tools used (SQL, dbt strongly recommended but not mandatory),
* the data structure,
* the chosen granularity,
* the proposed KPIs (beyond those mentioned, if you find them relevant).

---

## Expected Deliverables

Please provide:

* your code (SQL / dbt),
* a short `README` explaining:

  * your approach,
  * the business assumptions made,
  * the proposed data structure,
* a **simple visualization** allowing the main KPIs to be read.

