from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models import AuditEvent, GeneratedPackage, IntakeDocument, Shipment, TradeParty, ValidationFinding


class FreightRepository:
    """All resource reads include owner scope, so route code cannot forget it."""

    def __init__(self, session: AsyncSession, owner_id: str) -> None:
        self.session = session
        self.owner_id = owner_id

    async def _commit(self) -> None:
        await self.session.commit()

    async def audit(self, event_type: str, resource_type: str, resource_id: str, request_id: str | None, metadata: dict | None = None) -> AuditEvent:
        event = AuditEvent(
            owner_id=self.owner_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=request_id,
            metadata_json=metadata or {},
        )
        self.session.add(event)
        return event

    async def create_shipment(self, payload: dict[str, Any], title: str | None, request_id: str | None) -> Shipment:
        shipment = Shipment(owner_id=self.owner_id, title=title, payload=payload, status="draft")
        self.session.add(shipment)
        await self.session.flush()
        await self.audit("shipment.created", "shipment", shipment.id, request_id)
        await self._commit()
        await self.session.refresh(shipment)
        return shipment

    async def get_shipment(self, shipment_id: str, *, include_deleted: bool = False) -> Shipment | None:
        query: Select = select(Shipment).where(Shipment.id == shipment_id, Shipment.owner_id == self.owner_id)
        if not include_deleted:
            query = query.where(Shipment.deleted_at.is_(None))
        return (await self.session.execute(query)).scalar_one_or_none()

    async def list_shipments(self, limit: int, cursor: datetime | None = None) -> list[Shipment]:
        query: Select = (
            select(Shipment)
            .where(Shipment.owner_id == self.owner_id, Shipment.deleted_at.is_(None))
            .order_by(Shipment.created_at.desc(), Shipment.id.desc())
            .limit(limit)
        )
        if cursor:
            query = query.where(Shipment.created_at < cursor)
        return list((await self.session.execute(query)).scalars())

    async def update_shipment(self, shipment: Shipment, payload: dict[str, Any], title: str | None, request_id: str | None) -> Shipment:
        shipment.payload = payload
        shipment.title = title
        await self.audit("shipment.updated", "shipment", shipment.id, request_id)
        await self._commit()
        await self.session.refresh(shipment)
        return shipment

    async def submit_for_review(self, shipment: Shipment, request_id: str | None) -> Shipment:
        shipment.status = "review_submitted"
        shipment.review_submitted_at = datetime.now().astimezone()
        await self.audit("shipment.review_submitted", "shipment", shipment.id, request_id)
        await self._commit()
        await self.session.refresh(shipment)
        return shipment

    async def delete_shipment(self, shipment: Shipment, request_id: str | None) -> None:
        # Hard deletion honours the stated retention policy: removing a shipment
        # removes its business data, extractions, generated packages and PDFs.
        await self.audit("shipment.deleted", "shipment", shipment.id, request_id)
        await self.session.delete(shipment)
        await self._commit()

    async def create_party(self, kind: str, name: str, details: dict[str, str], request_id: str | None) -> TradeParty:
        party = TradeParty(owner_id=self.owner_id, kind=kind, name=name, details=details)
        self.session.add(party)
        await self.session.flush()
        await self.audit("party.created", "party", party.id, request_id)
        await self._commit()
        await self.session.refresh(party)
        return party

    async def search_parties(self, kind: str | None, query_text: str | None, limit: int = 20) -> list[TradeParty]:
        statement: Select = select(TradeParty).where(TradeParty.owner_id == self.owner_id)
        if kind:
            statement = statement.where(TradeParty.kind == kind)
        if query_text:
            statement = statement.where(TradeParty.name.ilike(f"%{query_text.strip()}%"))
        statement = statement.order_by(TradeParty.created_at.desc()).limit(limit)
        return list((await self.session.execute(statement)).scalars())

    async def create_document(self, shipment: Shipment, values: dict[str, Any], request_id: str | None) -> IntakeDocument:
        document = IntakeDocument(shipment_id=shipment.id, **values)
        self.session.add(document)
        await self.session.flush()
        await self.audit("document.extracted", "document", document.id, request_id, {"status": document.status})
        await self._commit()
        await self.session.refresh(document)
        return document

    async def list_documents(self, shipment: Shipment) -> list[IntakeDocument]:
        statement: Select = (
            select(IntakeDocument)
            .where(IntakeDocument.shipment_id == shipment.id)
            .order_by(IntakeDocument.created_at.desc())
        )
        return list((await self.session.execute(statement)).scalars())

    async def get_document(self, shipment: Shipment, document_id: str) -> IntakeDocument | None:
        statement: Select = select(IntakeDocument).where(
            IntakeDocument.id == document_id, IntakeDocument.shipment_id == shipment.id
        )
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def delete_document(self, shipment: Shipment, document: IntakeDocument, request_id: str | None) -> None:
        await self.audit("document.deleted", "document", document.id, request_id, {"shipment_id": shipment.id})
        await self.session.delete(document)
        await self._commit()

    async def create_package(self, shipment: Shipment, values: dict[str, Any], request_id: str | None) -> GeneratedPackage:
        package = GeneratedPackage(shipment_id=shipment.id, **values)
        self.session.add(package)
        await self.session.flush()
        validation = values.get("validation", {})
        for finding in validation.get("errors", []):
            self.session.add(
                ValidationFinding(
                    package_id=package.id,
                    severity=str(finding.get("severity", "warning")),
                    document=str(finding.get("document", "package")),
                    field=str(finding.get("field", "")),
                    issue=str(finding.get("issue", "")),
                    fix=str(finding.get("fix", "")),
                )
            )
        await self.audit("dossier.generated", "dossier", package.id, request_id)
        await self._commit()
        await self.session.refresh(package)
        return package

    async def get_package(self, shipment: Shipment, package_id: str) -> GeneratedPackage | None:
        statement: Select = select(GeneratedPackage).where(
            GeneratedPackage.id == package_id, GeneratedPackage.shipment_id == shipment.id
        )
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def latest_package(self, shipment: Shipment) -> GeneratedPackage | None:
        statement: Select = (
            select(GeneratedPackage)
            .where(GeneratedPackage.shipment_id == shipment.id)
            .order_by(GeneratedPackage.created_at.desc())
            .limit(1)
        )
        return (await self.session.execute(statement)).scalar_one_or_none()
