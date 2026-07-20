"""Normalize legacy shipment status values for the review-ready workflow.

Revision ID: 20260720_0002
Revises: 20260720_0001
Create Date: 2026-07-20
"""

from alembic import op


revision = "20260720_0002"
down_revision = "20260720_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Dossier output alone is not proof of readiness; old records therefore
    # enter the explicit review queue. This migration is safe on a fresh DB.
    op.execute("UPDATE shipments SET status = 'processing' WHERE status = 'review_submitted'")
    op.execute("UPDATE shipments SET status = 'needs_review' WHERE status = 'dossier_generated'")


def downgrade() -> None:
    op.execute("UPDATE shipments SET status = 'review_submitted' WHERE status = 'processing'")
    op.execute("UPDATE shipments SET status = 'dossier_generated' WHERE status = 'needs_review'")
