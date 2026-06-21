"""
core/generator.py — Geração do PDF traduzido com ReportLab.

Responsabilidade única: receber páginas traduzidas e gerar o arquivo PDF.
Não sabe nada sobre extração ou tradução.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT

from config.settings import (
    PDF_MARGIN_CM,
    PDF_BODY_SIZE,
    PDF_TITLE_SIZE,
    PDF_BODY_LEAD,
    PDF_TITLE_LEAD,
)


def _build_styles() -> dict:
    """Cria e retorna todos os estilos usados no PDF."""
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "Title2", parent=base["Normal"],
            fontSize=PDF_TITLE_SIZE,
            leading=PDF_TITLE_LEAD,
            fontName="Helvetica-Bold",
            alignment=TA_LEFT,
            spaceAfter=6,
            spaceBefore=10,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["Normal"],
            fontSize=PDF_BODY_SIZE,
            leading=PDF_BODY_LEAD,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "list": ParagraphStyle(
            "List", parent=base["Normal"],
            fontSize=PDF_BODY_SIZE,
            leading=PDF_BODY_LEAD,
            alignment=TA_LEFT,
            leftIndent=12,
            spaceAfter=4,
        ),
        "italic": ParagraphStyle(
            "Italic2", parent=base["Normal"],
            fontSize=PDF_BODY_SIZE,
            leading=PDF_BODY_LEAD,
            fontName="Helvetica-Oblique",
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "page_label": ParagraphStyle(
            "PageLabel", parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#888888"),
            spaceAfter=6,
            spaceBefore=12,
        ),
    }


def _safe_text(text: str) -> str:
    """Escapa caracteres especiais do ReportLab."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _block_to_paragraph(block: dict, styles: dict) -> Paragraph:
    """Converte um bloco de texto no Paragraph correto baseado no tipo."""
    text = _safe_text(block["text"])

    if block.get("is_title"):
        content = f"<i>{text}</i>" if block.get("italic") else f"<b>{text}</b>"
        return Paragraph(content, styles["title"])
    elif block.get("is_list"):
        return Paragraph(text, styles["list"])
    elif block.get("bold"):
        return Paragraph(f"<b>{text}</b>", styles["body"])
    elif block.get("italic"):
        return Paragraph(text, styles["italic"])
    else:
        return Paragraph(text, styles["body"])


def generate_pdf(translated_pages: list[dict], output_path: str, target_lang: str) -> None:
    """
    Gera o PDF traduzido a partir das páginas traduzidas.

    Args:
        translated_pages: lista de páginas com blocos traduzidos
        output_path: caminho onde o PDF será salvo
        target_lang: idioma de destino (usado para metadados futuros)
    """
    margin = PDF_MARGIN_CM * cm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    styles = _build_styles()
    story = []

    for page_data in translated_pages:
        # Rótulo de página
        story.append(Paragraph(f"— Page {page_data['page']} —", styles["page_label"]))

        # Blocos da página
        for block in page_data["blocks"]:
            story.append(_block_to_paragraph(block, styles))

        # Separador visual entre páginas
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#dddddd")))
        story.append(Spacer(1, 8))

    doc.build(story)