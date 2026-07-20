from __future__ import annotations

import json
import logging

from groq import AsyncGroq
from pydantic import BaseModel, ValidationError as PydanticValidationError

from app.config import get_settings
from app.models import ClassificationResult, DocumentPackage, ShipmentRequest, TariffData, ValidationResult

logger = logging.getLogger("freightdoc.groq")

CLASSIFY_SYSTEM = "You are a customs classifier. Return ONLY a valid JSON object matching the requested schema. Do not include markdown."
GENERATE_SYSTEM = "You fill export-document templates. Return ONLY valid JSON matching the requested schema. Preserve shipment facts exactly; no prose."
VALIDATE_SYSTEM = "You are an export-document auditor. Return ONLY valid JSON matching the requested schema. Every error must contain an actionable fix."


class AIServiceError(RuntimeError):
    """A provider failure that is safe to return through the public API.

    The original provider exception is intentionally not retained on this
    object. Provider responses can include request content or operational
    details that must never be sent to the browser or emitted in logs.
    """

    def __init__(
        self,
        *,
        code: str,
        stage: str,
        request_id: str,
        retryable: bool,
        status_code: int = 502,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.request_id = request_id
        self.retryable = retryable
        self.status_code = status_code


def _provider_status_code(exc: Exception) -> int | None:
    """Read only the public HTTP status attribute exposed by the SDK."""
    status_code = getattr(exc, "status_code", None)
    return status_code if isinstance(status_code, int) else None


def _safe_failure(
    *,
    stage: str,
    request_id: str,
    malformed_output: bool,
    last_error: Exception | None,
) -> AIServiceError:
    if malformed_output:
        return AIServiceError(
            code="AI_MALFORMED_RESPONSE",
            stage=stage,
            request_id=request_id,
            retryable=True,
        )

    if _provider_status_code(last_error) == 429:
        return AIServiceError(
            code="AI_RATE_LIMITED",
            stage=stage,
            request_id=request_id,
            retryable=True,
            status_code=429,
        )

    # Authentication and model-access failures are configuration problems on
    # our side. Do not reveal whether a key or a model name was rejected.
    if _provider_status_code(last_error) in {401, 403, 404}:
        return AIServiceError(
            code="AI_CONFIGURATION_ERROR",
            stage=stage,
            request_id=request_id,
            retryable=False,
        )

    return AIServiceError(
        code="AI_SERVICE_ERROR",
        stage=stage,
        request_id=request_id,
        retryable=True,
    )


class GroqClient:
    def __init__(self) -> None:
        key = get_settings().groq_api_key
        self.client = AsyncGroq(api_key=key) if key else None

    async def _request(
        self,
        system: str,
        payload: dict,
        schema: type[BaseModel],
        request_id: str,
        *,
        stage: str,
    ) -> BaseModel:
        model = get_settings().ai_model
        if not self.client:
            logger.error(
                "request_id=%s provider=groq stage=%s model=%s attempt=0 status=failed error_type=configuration",
                request_id,
                stage,
                model,
            )
            raise AIServiceError(
                code="AI_CONFIGURATION_ERROR",
                stage=stage,
                request_id=request_id,
                retryable=False,
            )
        last_error: Exception | None = None
        malformed_output = False
        instruction = {"schema": schema.model_json_schema(), "payload": payload}
        for attempt in range(2):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    temperature=0,
                    response_format={"type": "json_object"},
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps(instruction)}],
                )
                content = response.choices[0].message.content or "{}"
                result = schema.model_validate_json(content)
                logger.info(
                    "request_id=%s provider=groq stage=%s model=%s attempt=%s status=ok",
                    request_id,
                    stage,
                    model,
                    attempt + 1,
                )
                return result
            except Exception as exc:
                last_error = exc
                malformed_output = isinstance(exc, (AttributeError, IndexError, PydanticValidationError, TypeError))
                logger.warning(
                    "request_id=%s provider=groq stage=%s model=%s attempt=%s status=retry error_type=%s",
                    request_id,
                    stage,
                    model,
                    attempt + 1,
                    type(exc).__name__,
                )
        failure = _safe_failure(
            stage=stage,
            request_id=request_id,
            malformed_output=malformed_output,
            last_error=last_error,
        )
        logger.error(
            "request_id=%s provider=groq stage=%s model=%s attempt=2 status=failed error_type=%s code=%s",
            request_id,
            stage,
            model,
            type(last_error).__name__ if last_error else "UnknownError",
            failure.code,
        )
        raise failure from None

    async def classify_product(self, shipment: ShipmentRequest, request_id: str) -> ClassificationResult:
        return await self._request(
            CLASSIFY_SYSTEM,
            shipment.model_dump(mode="json"),
            ClassificationResult,
            request_id,
            stage="classification",
        )

    async def generate_documents(self, shipment: ShipmentRequest, classification: ClassificationResult, tariff: TariffData, required_docs: list[str], request_id: str) -> DocumentPackage:
        return await self._request(
            GENERATE_SYSTEM,
            {
                "shipment": shipment.model_dump(mode="json"),
                "classification": classification.model_dump(mode="json"),
                "tariff": tariff.model_dump(mode="json"),
                "required_docs": required_docs,
            },
            DocumentPackage,
            request_id,
            stage="generation",
        )

    async def validate_documents(self, document_package: DocumentPackage, shipment: ShipmentRequest, required_docs: list[str], request_id: str) -> ValidationResult:
        return await self._request(
            VALIDATE_SYSTEM,
            {
                "documents": document_package.model_dump(mode="json"),
                "shipment": shipment.model_dump(mode="json"),
                "required_docs": required_docs,
            },
            ValidationResult,
            request_id,
            stage="validation",
        )
