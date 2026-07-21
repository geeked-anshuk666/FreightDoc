import base64

import pytest

from app.services.pdf_generator import render_complete_dossier, render_documents


@pytest.mark.unit
def test_pdf_artifacts_are_nonempty_and_include_each_document_section():
    documents = {
        "commercial_invoice": {"invoice_number": "INV-123", "quantity": 5},
        "packing_list": {"packages": 1},
        "certificate_of_origin": {"origin": "US"},
    }
    artifacts = render_documents(documents)
    assert [item.filename for item in artifacts] == ["commercial_invoice.pdf", "packing_list.pdf", "certificate_of_origin.pdf"]
    assert all(base64.b64decode(item.content_base64).startswith(b"%PDF") for item in artifacts)
    dossier = render_complete_dossier(documents, "US -> DE", hs_code="851830", readiness_score=95)
    assert dossier.startswith(b"%PDF")
    assert len(dossier) > 1000


@pytest.mark.unit
def test_pdf_generation_is_repeatably_structured_for_fixed_input():
    first = render_documents({"customs_declaration": {"foo": "bar"}})[0]
    second = render_documents({"customs_declaration": {"foo": "bar"}})[0]
    # ReportLab timestamps metadata, so assert stable contract rather than byte identity.
    assert first.filename == second.filename == "customs_declaration.pdf"
    assert first.mime_type == second.mime_type == "application/pdf"
    assert len(base64.b64decode(first.content_base64)) == len(base64.b64decode(second.content_base64))
