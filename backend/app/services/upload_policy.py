"""Trade-document upload policy and file-signature validation.

The policy is intentionally conservative: a trade-document platform receives
untrusted files from many parties, so extension, declared MIME type, and content
signature must agree before any expensive parser is invoked.
"""

from __future__ import annotations

import re
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_REQUEST_BYTES = 40 * 1024 * 1024
MAX_FILES_PER_REQUEST = 10
MAX_FILENAME_LENGTH = 120
MAX_ARCHIVE_MEMBERS = 2_000
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 60 * 1024 * 1024
MAX_ARCHIVE_RATIO = 40
MAX_PDF_PAGES = 150
MAX_PDF_XREFS = 20_000
MAX_PDF_IMAGES = 2_000
MAX_EXTRACTED_TEXT_CHARS = 250_000
MAX_IMAGE_PIXELS = 25_000_000
MAX_IMAGE_DIMENSION = 8_000
MAX_CSV_ROWS = 100_000
MAX_CSV_COLUMNS = 50
MAX_CSV_CELL_CHARS = 10_000
MAX_WORKBOOK_SHEETS = 50
MAX_WORKBOOK_CELLS = 250_000

MIME_BY_EXTENSION = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


class DocumentSafetyError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class SanitizedUpload:
    filename: str
    mime_type: str
    data: bytes


def sanitize_filename(filename: str | None) -> str:
    supplied = (filename or "document").replace("\\", "/")
    supplied = PurePosixPath(supplied).name
    supplied = unicodedata.normalize("NFKC", supplied)
    supplied = "".join(char for char in supplied if ord(char) >= 32 and char not in '<>:"|?*')
    supplied = re.sub(r"\s+", " ", supplied).strip(" .")
    if not supplied:
        raise DocumentSafetyError("INVALID_FILENAME", "The filename is empty or contains unsupported characters.")
    if len(supplied) > MAX_FILENAME_LENGTH:
        stem, dot, suffix = supplied.rpartition(".")
        if dot:
            supplied = f"{stem[:MAX_FILENAME_LENGTH - len(suffix) - 1]}{dot}{suffix}"
        else:
            supplied = supplied[:MAX_FILENAME_LENGTH]
    return supplied


def _zip_kind(data: bytes) -> str | None:
    try:
        with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
            names = set(archive.namelist())
    except zipfile.BadZipFile as exc:
        raise DocumentSafetyError("TYPE_MISMATCH", "The file is not a valid Office document archive.") from exc
    if "[Content_Types].xml" not in names:
        return None
    if "word/document.xml" in names:
        return MIME_BY_EXTENSION[".docx"]
    if "xl/workbook.xml" in names:
        return MIME_BY_EXTENSION[".xlsx"]
    return None


def detect_content_mime(data: bytes, expected_mime: str) -> str:
    if data.startswith(b"%PDF-"):
        return "application/pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return _zip_kind(data) or "application/zip"
    # CSV deliberately has no magic signature. Its extension and declared MIME
    # are both required, then UTF-8/row validation is performed by the parser.
    if expected_mime == "text/csv" and b"\x00" not in data[:8192]:
        return "text/csv"
    return "application/octet-stream"


def inspect_archive(data: bytes) -> None:
    try:
        with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ARCHIVE_MEMBERS:
                raise DocumentSafetyError("UNSAFE_ARCHIVE", "The Office archive contains too many files.")
            total_uncompressed = 0
            for info in infos:
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                    raise DocumentSafetyError("UNSAFE_ARCHIVE", "The Office archive contains an unsafe path.")
                if info.flag_bits & 0x1:
                    raise DocumentSafetyError("UNSAFE_ARCHIVE", "Encrypted Office archives are not accepted.")
                total_uncompressed += info.file_size
                if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    raise DocumentSafetyError("CONTENT_LIMIT_EXCEEDED", "The Office archive expands beyond the safe size limit.")
                if info.file_size and (info.compress_size == 0 or info.file_size / info.compress_size > MAX_ARCHIVE_RATIO):
                    raise DocumentSafetyError("UNSAFE_ARCHIVE", "The Office archive has an unsafe compression ratio.")
    except zipfile.BadZipFile as exc:
        raise DocumentSafetyError("TYPE_MISMATCH", "The Office document archive is invalid.") from exc


def sanitize_upload(filename: str | None, declared_mime: str | None, data: bytes) -> SanitizedUpload:
    if not data:
        raise DocumentSafetyError("EMPTY_FILE", "The uploaded file is empty.")
    if len(data) > MAX_FILE_BYTES:
        raise DocumentSafetyError("FILE_TOO_LARGE", "Each document must be 15 MiB or smaller.")
    clean_name = sanitize_filename(filename)
    suffix = PurePosixPath(clean_name).suffix.lower()
    expected_mime = MIME_BY_EXTENSION.get(suffix)
    if not expected_mime:
        raise DocumentSafetyError("UNSUPPORTED_TYPE", "Supported files are PDF, DOCX, XLSX, CSV, PNG, and JPEG.")
    supplied_mime = (declared_mime or "").lower().split(";", 1)[0].strip()
    if supplied_mime != expected_mime:
        raise DocumentSafetyError("TYPE_MISMATCH", "The declared file type does not match the filename extension.")
    detected_mime = detect_content_mime(data, expected_mime)
    if detected_mime != expected_mime:
        raise DocumentSafetyError("TYPE_MISMATCH", "The file contents do not match its declared document type.")
    if expected_mime.endswith(("wordprocessingml.document", "spreadsheetml.sheet")):
        inspect_archive(data)
    return SanitizedUpload(filename=clean_name, mime_type=expected_mime, data=data)
