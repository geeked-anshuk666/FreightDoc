"""Canonical records, review workflow, hashes, and optional AI suggestion ledger.

Revision ID: 20260721_0003
Revises: 20260720_0002
"""
from alembic import op
import sqlalchemy as sa

revision = "20260721_0003"
down_revision = "20260720_0002"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("organizations", sa.Column("id",sa.String(36),primary_key=True), sa.Column("name",sa.String(160),nullable=False), sa.Column("personal_owner_id",sa.String(128),unique=True), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False), sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
    op.create_table("organization_memberships", sa.Column("id",sa.String(36),primary_key=True), sa.Column("organization_id",sa.String(36),sa.ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False), sa.Column("owner_id",sa.String(128),nullable=False), sa.Column("role",sa.String(32),nullable=False), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False), sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
    op.create_index("ix_org_membership_owner_org", "organization_memberships", ["owner_id", "organization_id"], unique=True)
    with op.batch_alter_table("shipments") as batch:
        batch.add_column(sa.Column("organization_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("canonical_revision_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("revision_number", sa.Integer(), nullable=False, server_default="0"))
    op.create_index("ix_shipments_organization_id", "shipments", ["organization_id"])
    with op.batch_alter_table("intake_documents") as batch:
        batch.add_column(sa.Column("sha256", sa.String(64), nullable=True))
        batch.add_column(sa.Column("retention_metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.create_index("ix_intake_documents_sha256", "intake_documents", ["sha256"])
    with op.batch_alter_table("audit_events") as batch:
        batch.add_column(sa.Column("event_hash", sa.String(64), nullable=True))
        batch.add_column(sa.Column("previous_event_hash", sa.String(64), nullable=True))
    op.create_table("shipment_revisions", sa.Column("id",sa.String(36),primary_key=True), sa.Column("shipment_id",sa.String(36),sa.ForeignKey("shipments.id",ondelete="CASCADE"),nullable=False), sa.Column("revision_number",sa.Integer(),nullable=False), sa.Column("payload",sa.JSON(),nullable=False), sa.Column("actor_id",sa.String(128),nullable=False), sa.Column("reason",sa.String(500)), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
    op.create_table("trade_facts", sa.Column("id",sa.String(36),primary_key=True), sa.Column("shipment_id",sa.String(36),sa.ForeignKey("shipments.id",ondelete="CASCADE"),nullable=False), sa.Column("field",sa.String(120),nullable=False), sa.Column("value",sa.JSON(),nullable=False), sa.Column("confidence",sa.Float(),nullable=False), sa.Column("provenance",sa.String(160),nullable=False), sa.Column("status",sa.String(24),nullable=False), sa.Column("revision_number",sa.Integer(),nullable=False), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
    op.create_table("review_tasks", sa.Column("id",sa.String(36),primary_key=True), sa.Column("shipment_id",sa.String(36),sa.ForeignKey("shipments.id",ondelete="CASCADE"),nullable=False), sa.Column("status",sa.String(24),nullable=False), sa.Column("kind",sa.String(80),nullable=False), sa.Column("reason",sa.String(1000),nullable=False), sa.Column("maker_id",sa.String(128)), sa.Column("assignee_id",sa.String(128)), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False), sa.Column("resolved_at",sa.DateTime(timezone=True)))
    op.create_table("review_decisions", sa.Column("id",sa.String(36),primary_key=True), sa.Column("task_id",sa.String(36),sa.ForeignKey("review_tasks.id",ondelete="CASCADE"),nullable=False), sa.Column("actor_id",sa.String(128),nullable=False), sa.Column("decision",sa.String(24),nullable=False), sa.Column("reason",sa.String(1000),nullable=False), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
    op.create_table("ai_suggestions", sa.Column("id",sa.String(36),primary_key=True), sa.Column("shipment_id",sa.String(36),sa.ForeignKey("shipments.id",ondelete="CASCADE"),nullable=False), sa.Column("payload",sa.JSON(),nullable=False), sa.Column("provider",sa.String(80)), sa.Column("model",sa.String(120)), sa.Column("prompt_version",sa.String(80),nullable=False), sa.Column("input_references",sa.JSON(),nullable=False), sa.Column("confidence",sa.Float()), sa.Column("rationale",sa.String(1000)), sa.Column("status",sa.String(24),nullable=False), sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))

def downgrade() -> None:
    op.drop_table("ai_suggestions"); op.drop_table("review_decisions"); op.drop_table("review_tasks"); op.drop_table("trade_facts"); op.drop_table("shipment_revisions")
    with op.batch_alter_table("audit_events") as b: b.drop_column("previous_event_hash"); b.drop_column("event_hash")
    op.drop_index("ix_intake_documents_sha256", table_name="intake_documents")
    with op.batch_alter_table("intake_documents") as b: b.drop_column("retention_metadata"); b.drop_column("sha256")
    op.drop_index("ix_shipments_organization_id", table_name="shipments")
    with op.batch_alter_table("shipments") as b: b.drop_column("revision_number"); b.drop_column("canonical_revision_id"); b.drop_column("organization_id")
    op.drop_index("ix_org_membership_owner_org", table_name="organization_memberships")
    op.drop_table("organization_memberships"); op.drop_table("organizations")
