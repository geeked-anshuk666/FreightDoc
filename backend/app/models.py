from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SUPPORTED_BILATERAL_CORRIDORS = {"US-DE", "US-GB", "US-IN", "US-JP", "US-CA", "US-AU", "IN-US"}
EU_MEMBER_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV",
    "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
}


def _safe_text(value: str) -> str:
    """Reject invisible control characters before they reach logs, PDFs, or AI prompts."""
    cleaned = value.strip()
    if any(ord(char) < 32 and char not in "\n\t" for char in cleaned):
        raise ValueError("Text contains unsupported control characters")
    return cleaned


class Category(str, Enum):
    electronics = "electronics"
    textiles = "textiles"
    food = "food"
    chemicals = "chemicals"
    machinery = "machinery"
    other = "other"


class DocumentType(str, Enum):
    commercial_invoice = "commercial_invoice"
    packing_list = "packing_list"
    bill_of_lading = "bill_of_lading"
    air_waybill = "air_waybill"
    certificate_of_origin = "certificate_of_origin"
    import_export_license = "import_export_license"
    customs_declaration = "customs_declaration"
    insurance_certificate = "insurance_certificate"
    supporting_document = "supporting_document"


class ShipmentRequest(BaseModel):
    """Minimum complete facts required by the six-stage documentation pipeline."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    product_name: str = Field(min_length=2, max_length=160)
    product_description: str = Field(min_length=10, max_length=3000)
    origin_country: str = Field(min_length=2, max_length=2)
    destination_country: str = Field(min_length=2, max_length=2)
    quantity: int = Field(gt=0, le=1_000_000)
    declared_value: float = Field(gt=0, le=100_000_000)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    exporter_name: str | None = Field(default=None, max_length=160)
    importer_name: str | None = Field(default=None, max_length=160)

    @field_validator("product_name", "product_description", "exporter_name", "importer_name")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return _safe_text(value) if value is not None else value

    @field_validator("origin_country", "destination_country", "currency", mode="before")
    @classmethod
    def uppercase(cls, value: str) -> str:
        result = str(value).upper().strip()
        if not result.isalpha():
            raise ValueError("Must use alphabetic ISO-style codes")
        return result

    @model_validator(mode="after")
    def supported_corridor(self) -> "ShipmentRequest":
        key = f"{self.origin_country}-{self.destination_country}"
        if self.origin_country == "CN":
            if self.destination_country not in EU_MEMBER_COUNTRIES:
                raise ValueError("China exports require a specific EU member-state destination")
        elif key not in SUPPORTED_BILATERAL_CORRIDORS:
            raise ValueError(f"Unsupported corridor: {key}")
        return self


class ShipmentDraftRequest(BaseModel):
    """Partial shipment facts. A draft becomes reviewable only after ShipmentRequest validation."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=2, max_length=120)
    product_name: str | None = Field(default=None, min_length=2, max_length=160)
    product_description: str | None = Field(default=None, min_length=10, max_length=3000)
    origin_country: str | None = Field(default=None, min_length=2, max_length=2)
    destination_country: str | None = Field(default=None, min_length=2, max_length=2)
    quantity: int | None = Field(default=None, gt=0, le=1_000_000)
    declared_value: float | None = Field(default=None, gt=0, le=100_000_000)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    exporter_name: str | None = Field(default=None, max_length=160)
    importer_name: str | None = Field(default=None, max_length=160)

    @field_validator("title", "product_name", "product_description", "exporter_name", "importer_name")
    @classmethod
    def validate_draft_text(cls, value: str | None) -> str | None:
        return _safe_text(value) if value is not None else value

    @field_validator("origin_country", "destination_country", "currency", mode="before")
    @classmethod
    def uppercase_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        result = str(value).upper().strip()
        if not result.isalpha():
            raise ValueError("Must use alphabetic ISO-style codes")
        return result

    @model_validator(mode="after")
    def partial_corridor_is_sane(self) -> "ShipmentDraftRequest":
        if self.origin_country == "CN" and self.destination_country and self.destination_country not in EU_MEMBER_COUNTRIES:
            raise ValueError("China exports require a specific EU member-state destination")
        return self


class ClassificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hs_code: str = Field(pattern=r"^\d{6,10}$")
    hs_description: str = Field(min_length=3, max_length=500)
    confidence: float = Field(ge=0, le=1)
    category: Category
    notes: str = Field(max_length=1000)


class TariffData(BaseModel):
    duty_rate: float | None = Field(default=None, ge=0)
    source: str = Field(max_length=160)
    source_url: str | None = Field(default=None, max_length=1000)
    additional_flags: list[str] = Field(default_factory=list, max_length=20)
    retrieved_at: datetime
    fallback_used: bool = False


class DocumentRequirements(BaseModel):
    corridor: str
    required_docs: list[str] = Field(max_length=30)
    rule_version: str
    effective_date: str
    last_reviewed_at: str
    source_urls: list[str] = Field(max_length=20)


class DocumentPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    commercial_invoice: dict[str, Any]
    packing_list: dict[str, Any]
    certificate_of_origin: dict[str, Any]
    customs_declaration: dict[str, Any]
    ce_declaration: dict[str, Any] | None = None
    additional_documents: dict[str, dict[str, Any]] = Field(default_factory=dict, max_length=20)

    @property
    def documents(self) -> dict[str, dict[str, Any]]:
        documents = {
            "commercial_invoice": self.commercial_invoice,
            "packing_list": self.packing_list,
            "certificate_of_origin": self.certificate_of_origin,
            "customs_declaration": self.customs_declaration,
        }
        if self.ce_declaration is not None:
            documents["ce_declaration"] = self.ce_declaration
        documents.update(self.additional_documents)
        return documents


class ValidationError(BaseModel):
    severity: Literal["critical", "warning"]
    document: str = Field(max_length=120)
    field: str = Field(max_length=120)
    issue: str = Field(max_length=1000)
    fix: str = Field(min_length=3, max_length=1000)


class ValidationResult(BaseModel):
    errors: list[ValidationError] = Field(max_length=100)
    compliance_score: int = Field(ge=0, le=100)
    ready_to_ship: bool


class PdfArtifact(BaseModel):
    filename: str
    mime_type: Literal["application/pdf"] = "application/pdf"
    content_base64: str


class PipelineStatus(BaseModel):
    step: str
    status: Literal["completed", "fallback"]


class PipelineResponse(BaseModel):
    request_id: str
    status: list[PipelineStatus]
    classification: ClassificationResult
    tariff: TariffData
    required_docs: list[str]
    documents: DocumentPackage
    validation: ValidationResult
    pdfs: dict[str, str]
    legal_disclaimer: str
    requirements: DocumentRequirements | None = None
    provider: str | None = None
    model: str | None = None


class GenerateRequest(BaseModel):
    shipment: ShipmentRequest
    classification: ClassificationResult
    requirements: DocumentRequirements


class ValidateRequest(BaseModel):
    shipment: ShipmentRequest
    classification: ClassificationResult
    requirements: DocumentRequirements
    documents: DocumentPackage


class ShipmentSummary(BaseModel):
    id: str
    status: str
    title: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ShipmentDetail(ShipmentSummary):
    payload: dict[str, Any]
    review_submitted_at: datetime | None = None


class ShipmentPage(BaseModel):
    items: list[ShipmentSummary]
    next_cursor: str | None = None


class ExtractionFinding(BaseModel):
    field: str = Field(max_length=120)
    value: str | int | float | bool | None = None
    confidence: float = Field(ge=0, le=1)
    provenance: str = Field(max_length=160)


class IntakeDocumentResponse(BaseModel):
    id: str
    shipment_id: str
    document_type: DocumentType
    filename: str
    mime_type: str
    size_bytes: int
    status: str
    extracted_text: str
    normalized_fields: dict[str, Any]
    findings: list[ExtractionFinding] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    extraction_error_code: str | None = None
    retained_original: Literal[False] = False
    created_at: datetime | None = None


class IntakeDocumentList(BaseModel):
    items: list[IntakeDocumentResponse]


class DossierSummary(BaseModel):
    id: str
    shipment_id: str
    readiness_score: int = Field(ge=0, le=100)
    ready_to_ship: bool
    created_at: datetime | None = None
    legal_disclaimer: str


class DossierDetail(DossierSummary):
    classification: ClassificationResult
    tariff: TariffData
    requirements: DocumentRequirements
    documents: DocumentPackage
    validation: ValidationResult
    source_provenance: dict[str, Any]


class TradePartyRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    kind: Literal["exporter", "importer"]
    name: str = Field(min_length=2, max_length=160)
    details: dict[str, str] = Field(default_factory=dict, max_length=20)

    @field_validator("name")
    @classmethod
    def party_name_safe(cls, value: str) -> str:
        return _safe_text(value)


class TradePartyResponse(BaseModel):
    id: str
    kind: Literal["exporter", "importer"]
    name: str
    details: dict[str, str]
    created_at: datetime | None = None


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    request_id: str | None = None
