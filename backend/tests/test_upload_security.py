import io
import zipfile

import pytest

from app.services.document_intake import sanitize_and_extract
from app.services.upload_policy import DocumentSafetyError, sanitize_filename, sanitize_upload


def test_rejects_spoofed_document_type() -> None:
    with pytest.raises(DocumentSafetyError) as exc_info:
        sanitize_upload("invoice.pdf", "application/pdf", b"not a PDF")

    assert exc_info.value.code == "TYPE_MISMATCH"


def test_filename_is_path_safe_before_any_parser_runs() -> None:
    assert sanitize_filename("../../supplier invoice.pdf") == "supplier invoice.pdf"


def test_rejects_unsafe_office_archive_member_path() -> None:
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
        archive.writestr("../outside.txt", "not allowed")

    with pytest.raises(DocumentSafetyError) as exc_info:
        sanitize_upload(
            "invoice.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            payload.getvalue(),
        )

    assert exc_info.value.code == "UNSAFE_ARCHIVE"


def test_csv_formula_is_kept_inert_in_extracted_text() -> None:
    result = sanitize_and_extract("packing-list.csv", "text/csv", b"item,amount\nwidgets,=1+1\n")

    assert result.status == "extracted"
    assert "'=1+1" in result.text
    assert result.size_bytes > 0
