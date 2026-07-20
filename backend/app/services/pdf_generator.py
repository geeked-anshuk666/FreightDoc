import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app.models import PdfArtifact


def render_documents(documents: dict[str, dict]) -> list[PdfArtifact]:
    artifacts: list[PdfArtifact] = []
    for doc_type, fields in documents.items():
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setTitle(doc_type.replace("_", " ").title())
        y = 800
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(48, y, doc_type.replace("_", " ").title())
        y -= 34
        pdf.setFont("Helvetica", 10)
        for key, value in fields.items():
            for line in f"{key.replace('_', ' ').title()}: {value}".splitlines():
                pdf.drawString(48, y, line[:110])
                y -= 16
                if y < 54:
                    pdf.showPage(); y = 800; pdf.setFont("Helvetica", 10)
        pdf.save()
        artifacts.append(PdfArtifact(filename=f"{doc_type}.pdf", content_base64=base64.b64encode(buffer.getvalue()).decode("ascii")))
    return artifacts


def render_complete_dossier(
    documents: dict[str, dict],
    route: str,
    hs_code: str | None = None,
    readiness_score: int | None = None,
) -> bytes:
    """Render one owner-authorized downloadable dossier PDF in memory.

    This does not write an artifact to disk; the authenticated dossier route
    streams the bytes directly to the caller.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("FreightDoc complete dossier")
    y = 800
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(48, y, "FreightDoc — Complete Dossier")
    y -= 34
    pdf.setFont("Helvetica", 10)
    pdf.drawString(48, y, f"Route: {route}"[:110])
    y -= 16
    if hs_code:
        pdf.drawString(48, y, f"HS classification candidate: {hs_code}"[:110])
        y -= 16
    if readiness_score is not None:
        pdf.drawString(48, y, f"Readiness score: {readiness_score}/100")
        y -= 24
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(48, y, "Informational preparation only. Confirm final filing requirements with a licensed customs broker.")
    for doc_type, fields in documents.items():
        pdf.showPage()
        y = 800
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(48, y, doc_type.replace("_", " ").title())
        y -= 34
        pdf.setFont("Helvetica", 10)
        for key, value in fields.items():
            for line in f"{key.replace('_', ' ').title()}: {value}".splitlines():
                pdf.drawString(48, y, line[:110])
                y -= 16
                if y < 54:
                    pdf.showPage()
                    y = 800
                    pdf.setFont("Helvetica", 10)
    pdf.save()
    return buffer.getvalue()


def commercial_invoice(fields: dict) -> bytes: return base64.b64decode(render_documents({"commercial_invoice": fields})[0].content_base64)
def packing_list(fields: dict) -> bytes: return base64.b64decode(render_documents({"packing_list": fields})[0].content_base64)
def certificate_of_origin(fields: dict) -> bytes: return base64.b64decode(render_documents({"certificate_of_origin": fields})[0].content_base64)
def customs_declaration(fields: dict) -> bytes: return base64.b64decode(render_documents({"customs_declaration": fields})[0].content_base64)
def ce_declaration(fields: dict) -> bytes: return base64.b64decode(render_documents({"ce_declaration": fields})[0].content_base64)
