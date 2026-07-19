# FreightDoc — 10_API_REFERENCE.md

## External APIs

### USITC HTS REST API
Base: https://hts.usitc.gov/reststop/api
Auth: none
Use: HS code lookup, US duty rate by code

### UN Comtrade
Base: https://comtradeplus.un.org
Auth: free registration key required
Use: bilateral tariff/trade data by country pair and HS code

### EU TARIC
Base: https://ec.europa.eu/taxation_customs/dds2/taric/taric_consultation.jsp
Auth: none
Use: EU-specific duty rates and compliance flags

### REST Countries
Base: https://restcountries.com
Auth: none
Use: country metadata (names, codes, regions)

## Prompt: HS Code Classification
```python
CLASSIFY_PROMPT = """
You are a customs classification expert with 20 years of experience.
Classify the following product into the correct 6-digit Harmonized System
(HS) code.

Product Name: {product_name}
Product Description: {product_description}

Respond in JSON only:
{{
  "hs_code": "XXXXXX",
  "hs_description": "official description",
  "confidence": 0.0-1.0,
  "category": "electronics|textiles|food|chemicals|machinery|other",
  "notes": "any classification notes or caveats"
}}
"""
```

## Prompt: Document Generation
```python
DOCUMENT_PROMPT = """
You are a trade documentation expert. Generate complete, accurate export
documents.

Shipment Details:
- Product: {product_name}
- HS Code: {hs_code}
- Origin: {origin_country}
- Destination: {destination_country}
- Quantity: {quantity}
- Declared Value: {declared_value} USD
- Exporter: {exporter_name}
- Importer: {importer_name}

Generate the following documents: {required_docs}

Respond in JSON only:
{{
  "commercial_invoice": {{...}},
  "packing_list": {{...}},
  "certificate_of_origin": {{...}},
  "customs_declaration": {{...}}
}}
"""
```

## Prompt: Cross-Validation
```python
VALIDATE_PROMPT = """
You are a customs compliance auditor. Review these export documents for
errors.

Documents: {all_documents_json}
Shipment: {origin} -> {destination}
HS Code: {hs_code}
Product Category: {category}

Check for:
1. HS code consistency across all documents
2. Value/quantity mismatches between invoice and packing list
3. Missing required fields for {destination} imports
4. Destination-specific compliance gaps (CE marking, certifications, etc.)
5. Country of origin consistency

Respond in JSON only:
{{
  "errors": [
    {{"severity": "critical|warning", "document": "...", "field": "...",
      "issue": "...", "fix": "..."}}
  ],
  "compliance_score": 0-100,
  "ready_to_ship": true|false
}}
"""
```

## Country Rules JSON (seed structure)
```json
{
  "US-DE": {"required_docs": ["commercial_invoice","packing_list",
    "certificate_of_origin","customs_declaration"],
    "conditional": {"electronics": ["ce_declaration"]}},
  "US-GB": {"required_docs": ["commercial_invoice","packing_list",
    "certificate_of_origin","customs_declaration"],
    "conditional": {"electronics": ["ukca_marking"]}}
}
```
