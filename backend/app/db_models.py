"""Owner-scoped persistence models.

``owner_id`` is only the opaque Clerk ``sub`` claim. No Clerk profile, session,
email, OAuth token, or avatar data belongs in these tables.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _id() -> str:
    return str(uuid.uuid4())


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Shipment(Timestamped, Base):
    __tablename__ = "shipments"
    __table_args__ = (
        Index("ix_shipments_owner_created", "owner_id", "created_at"),
        Index("ix_shipments_owner_status", "owner_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    owner_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Only user-entered shipment facts, never uploaded bytes or Clerk PII.
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    review_submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TradeParty(Timestamped, Base):
    __tablename__ = "trade_parties"
    __table_args__ = (Index("ix_trade_parties_owner_kind_name", "owner_id", "kind", "name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    owner_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class IntakeDocument(Timestamped, Base):
    __tablename__ = "intake_documents"
    __table_args__ = (Index("ix_intake_documents_shipment_created", "shipment_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    shipment_id: Mapped[str] = mapped_column(
        ForeignKey("shipments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(64), nullable=False)
    filename: Mapped[str] = mapped_column(String(120), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="extracted", nullable=False)
    # Bounded extracted content/facts only. Original file bytes are never stored.
    extracted_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    normalized_fields: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    findings: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    extraction_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    extraction_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    original_deleted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parser_provenance: Mapped[str] = mapped_column(String(160), default="native", nullable=False)


class GeneratedPackage(Timestamped, Base):
    __tablename__ = "generated_packages"
    __table_args__ = (Index("ix_generated_packages_shipment_created", "shipment_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    shipment_id: Mapped[str] = mapped_column(
        ForeignKey("shipments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    request_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    classification: Mapped[dict] = mapped_column(JSON, nullable=False)
    tariff: Mapped[dict] = mapped_column(JSON, nullable=False)
    requirements: Mapped[dict] = mapped_column(JSON, nullable=False)
    documents: Mapped[dict] = mapped_column(JSON, nullable=False)
    validation: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Base64 PDF artifacts are a short-lived MVP trade-off. They are protected
    # by owner checks and removed with the shipment; originals remain absent.
    pdfs: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_provenance: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    legal_disclaimer: Mapped[str] = mapped_column(Text, nullable=False)


class ValidationFinding(Timestamped, Base):
    __tablename__ = "validation_findings"
    __table_args__ = (Index("ix_validation_findings_package_severity", "package_id", "severity"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    package_id: Mapped[str] = mapped_column(
        ForeignKey("generated_packages.id", ondelete="CASCADE"), index=True, nullable=False
    )
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    document: Mapped[str] = mapped_column(String(120), nullable=False)
    field: Mapped[str] = mapped_column(String(120), nullable=False)
    issue: Mapped[str] = mapped_column(String(1000), nullable=False)
    fix: Mapped[str] = mapped_column(String(1000), nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_events_owner_created", "owner_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    owner_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(64), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Deliberately bounded metadata: no document content / credentials / PII.
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
