from __future__ import annotations

import json
import logging
from groq import AsyncGroq
from pydantic import BaseModel
from app.config import get_settings
from app.models import ClassificationResult, DocumentPackage, ShipmentRequest, TariffData, ValidationResult

logger = logging.getLogger("freightdoc.groq")

CLASSIFY_SYSTEM = "You are a customs classifier. Return ONLY a valid JSON object matching the requested schema. Do not include markdown."
GENERATE_SYSTEM = "You fill export-document templates. Return ONLY valid JSON matching the requested schema. Preserve shipment facts exactly; no prose."
VALIDATE_SYSTEM = "You are an export-document auditor. Return ONLY valid JSON matching the requested schema. Every error must contain an actionable fix."


class GroqClient:
    def __init__(self) -> None:
        key = get_settings().groq_api_key
        self.client = AsyncGroq(api_key=key) if key else None

    async def _request(self, system: str, payload: dict, schema: type[BaseModel], request_id: str) -> BaseModel:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured")
        last_error: Exception | None = None
        instruction = {"schema": schema.model_json_schema(), "payload": payload}
        for attempt in range(2):
            try:
                response = await self.client.chat.completions.create(model=get_settings().ai_model, temperature=0, response_format={"type": "json_object"}, messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps(instruction)}])
                content = response.choices[0].message.content or "{}"
                result = schema.model_validate_json(content)
                logger.info("request_id=%s groq_step=%s attempt=%s status=ok", request_id, schema.__name__, attempt + 1)
                return result
            except Exception as exc:
                last_error = exc
                logger.warning("request_id=%s groq_step=%s attempt=%s status=retry", request_id, schema.__name__, attempt + 1)
        raise RuntimeError(f"Groq returned invalid {schema.__name__} output") from last_error

    async def classify_product(self, shipment: ShipmentRequest, request_id: str) -> ClassificationResult:
        return await self._request(CLASSIFY_SYSTEM, shipment.model_dump(mode="json"), ClassificationResult, request_id)

    async def generate_documents(self, shipment: ShipmentRequest, classification: ClassificationResult, tariff: TariffData, required_docs: list[str], request_id: str) -> DocumentPackage:
        return await self._request(GENERATE_SYSTEM, {"shipment": shipment.model_dump(mode="json"), "classification": classification.model_dump(mode="json"), "tariff": tariff.model_dump(mode="json"), "required_docs": required_docs}, DocumentPackage, request_id)

    async def validate_documents(self, document_package: DocumentPackage, shipment: ShipmentRequest, required_docs: list[str], request_id: str) -> ValidationResult:
        return await self._request(VALIDATE_SYSTEM, {"documents": document_package.model_dump(mode="json"), "shipment": shipment.model_dump(mode="json"), "required_docs": required_docs}, ValidationResult, request_id)
