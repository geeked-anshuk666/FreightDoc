"""Create owner-scoped FreightDoc workspace records.

Revision ID: 20260720_0001
Revises:
Create Date: 2026-07-20
"""

from alembic import op
import sqlalchemy as sa

revision = "20260720_0001"
down_revision = None
branch_labels = None
depends_on = None


def _timestamps(columns: list) -> None:
    columns.extend([
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    ])


def upgrade() -> None:
    columns = [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("title", sa.String(120)),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("review_submitted_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    ]
    _timestamps(columns)
    op.create_table("shipments", *columns)
    op.create_index("ix_shipments_owner_id", "shipments", ["owner_id"])
    op.create_index("ix_shipments_owner_created", "shipments", ["owner_id", "created_at"])
    op.create_index("ix_shipments_owner_status", "shipments", ["owner_id", "status"])

    columns = [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
    ]
    _timestamps(columns)
    op.create_table("trade_parties", *columns)
    op.create_index("ix_trade_parties_owner_id", "trade_parties", ["owner_id"])
    op.create_index("ix_trade_parties_owner_kind_name", "trade_parties", ["owner_id", "kind", "name"])

    columns = [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("shipment_id", sa.String(36), sa.ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(64), nullable=False),
        sa.Column("filename", sa.String(120), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="extracted"),
        sa.Column("extracted_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("normalized_fields", sa.JSON(), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("extraction_error_code", sa.String(80)),
        sa.Column("extraction_error_message", sa.String(500)),
        sa.Column("original_deleted", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("parser_provenance", sa.String(160), nullable=False, server_default="native"),
    ]
    _timestamps(columns)
    op.create_table("intake_documents", *columns)
    op.create_index("ix_intake_documents_shipment_id", "intake_documents", ["shipment_id"])
    op.create_index("ix_intake_documents_shipment_created", "intake_documents", ["shipment_id", "created_at"])

    columns = [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("shipment_id", sa.String(36), sa.ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("request_id", sa.String(80), nullable=False),
        sa.Column("classification", sa.JSON(), nullable=False),
        sa.Column("tariff", sa.JSON(), nullable=False),
        sa.Column("requirements", sa.JSON(), nullable=False),
        sa.Column("documents", sa.JSON(), nullable=False),
        sa.Column("validation", sa.JSON(), nullable=False),
        sa.Column("pdfs", sa.JSON(), nullable=False),
        sa.Column("source_provenance", sa.JSON(), nullable=False),
        sa.Column("legal_disclaimer", sa.Text(), nullable=False),
    ]
    _timestamps(columns)
    op.create_table("generated_packages", *columns)
    op.create_index("ix_generated_packages_shipment_id", "generated_packages", ["shipment_id"])
    op.create_index("ix_generated_packages_request_id", "generated_packages", ["request_id"])
    op.create_index("ix_generated_packages_shipment_created", "generated_packages", ["shipment_id", "created_at"])

    columns = [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("package_id", sa.String(36), sa.ForeignKey("generated_packages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("document", sa.String(120), nullable=False),
        sa.Column("field", sa.String(120), nullable=False),
        sa.Column("issue", sa.String(1000), nullable=False),
        sa.Column("fix", sa.String(1000), nullable=False),
    ]
    _timestamps(columns)
    op.create_table("validation_findings", *columns)
    op.create_index("ix_validation_findings_package_id", "validation_findings", ["package_id"])
    op.create_index("ix_validation_findings_package_severity", "validation_findings", ["package_id", "severity"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=False),
        sa.Column("request_id", sa.String(80)),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_audit_events_owner_id", "audit_events", ["owner_id"])
    op.create_index("ix_audit_events_owner_created", "audit_events", ["owner_id", "created_at"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("validation_findings")
    op.drop_table("generated_packages")
    op.drop_table("intake_documents")
    op.drop_table("trade_parties")
    op.drop_table("shipments")
