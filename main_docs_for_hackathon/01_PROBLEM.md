# FreightDoc — 01_PROBLEM.md

## One-line pitch
An agent that takes a product description and shipment destination, generates
the complete country-specific export documentation package, checks it for
consistency, and flags the errors that cause real shipment holds.

## The problem, stated plainly
Every year, tens of thousands of small exporters — DTC brands, Amazon FBA
sellers, Etsy sellers shipping internationally, small equipment manufacturers
— must produce a correct, consistent set of customs documents for every
international shipment. Getting this wrong is expensive and common:

- Cross-border e-commerce reached **$1.47 trillion in 2025.**
- A single missing or incorrect document can hold cargo at the border for
  **days**, with fines that can **exceed $10,000 per incident**.
- HS (Harmonized System) code classification — the code that determines the
  duty rate — spans **99 chapters and thousands of subheadings**. Most small
  importers/exporters guess, and guessing wrong is either underpayment
  (a customs violation) or overpayment (wasted margin).
- Manual documentation via a freight forwarder costs **$500–$2,000 per
  shipment**, and errors still slip through because forwarders don't
  cross-check every document against every other document line by line.

## Evidence of severity
- 99 HTS chapters, thousands of subheadings — a genuinely specialized skill,
  not something a small business owner can reliably self-serve today.
- Enterprise trade compliance software (Amber Road, Thomson Reuters
  ONESOURCE) costs **$30,000+/year** and requires months of implementation —
  completely inaccessible to a $2M revenue e-commerce brand.
- The compliance requirement is not static: destination-specific rules (CE
  marking for EU electronics, BIS certification for India, PSE marks for
  Japan) change and are easy to miss if you're not a trade specialist.

## Who feels this pain
- Small/mid e-commerce exporters shipping product internationally for the
  first time or at growing volume.
- Freight forwarders and customs brokers who currently do this manually
  and would use this as an internal acceleration tool.
- Manufacturers exporting equipment/components who don't have an in-house
  trade compliance team.

## Why this is NOT a solved problem
Existing tools generate documents (templates) or handle logistics booking
(Flexport, ShipBob) — none of them **cross-validate the generated package
against itself** and flag the specific destination-country compliance gap
before the shipment leaves the warehouse. That gap is where real financial
and time loss happens, and it's exactly the gap FreightDoc closes.
