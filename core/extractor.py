"""
core/extractor.py — Extração de texto e formatação do PDF.

Responsabilidade única: abrir o PDF e retornar blocos de texto
com metadados de formatação (negrito, itálico, tamanho, tipo).
Não sabe nada sobre tradução ou geração de PDF.

OCR: páginas sem texto (escaneadas) são processadas automaticamente
com Tesseract. Requer: pytesseract + Pillow + Tesseract instalado no sistema.
"""

import re
import pdfplumber

# OCR — importação opcional para não quebrar quem não tem Tesseract
try:
    import pytesseract
    from PIL import Image
    import io
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def _is_bold(fontname: str) -> bool:
    return "Bold" in fontname or "bold" in fontname


def _is_italic(fontname: str) -> bool:
    return "Italic" in fontname or "italic" in fontname or "Oblique" in fontname


def _group_words_by_line(words: list[dict]) -> dict[float, list[dict]]:
    """Agrupa palavras pelo topo (posição vertical), formando linhas."""
    lines: dict[float, list[dict]] = {}
    for word in words:
        top = round(word["top"], 1)
        lines.setdefault(top, []).append(word)
    return lines


def _calculate_paragraph_threshold(sorted_tops: list[float]) -> float:
    """
    Calcula o threshold de gap para detectar novo parágrafo.
    Usa 1.4x o menor gap entre linhas consecutivas.
    """
    if len(sorted_tops) < 2:
        return 14.0
    gaps = [sorted_tops[i + 1] - sorted_tops[i] for i in range(len(sorted_tops) - 1)]
    return min(gaps) * 1.4


def _build_line_objects(lines_dict: dict, sorted_tops: list[float]) -> list[dict]:
    """Converte linhas brutas em objetos com metadados de formatação."""
    line_objects = []
    for top in sorted_tops:
        words_in_line = lines_dict[top]
        text = " ".join(w["text"] for w in words_in_line)
        fonts = [w.get("fontname", "") for w in words_in_line]
        sizes = [w.get("size", 12) for w in words_in_line]

        bold_count = sum(1 for f in fonts if _is_bold(f))
        italic_count = sum(1 for f in fonts if _is_italic(f))

        line_objects.append({
            "top": top,
            "text": text,
            "bold": bold_count > len(fonts) / 2,
            "italic": italic_count > len(fonts) / 2,
            "size": max(sizes),
        })
    return line_objects


def _group_lines_into_blocks(line_objects: list[dict], threshold: float) -> list[list[dict]]:
    """Agrupa linhas consecutivas em blocos (parágrafos) pelo gap entre elas."""
    raw_blocks: list[list[dict]] = []
    current: list[dict] = []
    prev_top: float | None = None

    for line in line_objects:
        if prev_top is not None and (line["top"] - prev_top) > threshold:
            if current:
                raw_blocks.append(current)
                current = []
        current.append(line)
        prev_top = line["top"]

    if current:
        raw_blocks.append(current)

    return raw_blocks


def _classify_block(block_lines: list[dict]) -> list[dict]:
    """
    Classifica um bloco como título, lista ou corpo de texto.
    Se tiver múltiplos itens de lista grudados, divide-os.
    Retorna uma lista de sub-blocos.
    """
    full_text = " ".join(l["text"] for l in block_lines)
    bold = any(l["bold"] for l in block_lines)
    italic = any(l["italic"] for l in block_lines)
    size = max(l["size"] for l in block_lines)

    # Título: linha única, curta, em negrito ou fonte grande
    is_title = (
        len(block_lines) == 1
        and (bold or size > 13)
        and len(full_text) < 80
    )

    is_list = bool(re.match(r"^\d+[\.\)]\s", full_text.strip()))

    # Se tiver vários itens de lista grudados no mesmo bloco, divide
    if not is_title and re.search(r"\s\d+[\.\)]\s", full_text):
        parts = re.split(r"(?<=\s)(?=\d+[\.\)]\s)", full_text)
        return [
            {
                "text": part.strip(),
                "bold": bold,
                "italic": italic,
                "size": size,
                "is_title": False,
                "is_list": bool(re.match(r"^\d+[\.\)]\s", part.strip())),
            }
            for part in parts
            if part.strip()
        ]

    return [
        {
            "text": full_text,
            "bold": bold,
            "italic": italic,
            "size": size,
            "is_title": is_title,
            "is_list": is_list,
        }
    ]


def _ocr_page(page) -> list[dict]:
    """
    Extrai texto de uma página escaneada (sem texto digital) usando OCR.

    Converte a página para imagem em alta resolução (300 DPI) e
    roda o Tesseract. Retorna blocos simples de corpo de texto.
    Cada parágrafo detectado vira um bloco separado.

    Requer: pytesseract + Pillow + Tesseract instalado no sistema.
    """
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "OCR não disponível. Instale as dependências:\n"
            "  pip install pytesseract Pillow\n"
            "E instale o Tesseract no sistema:\n"
            "  Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "  Linux:   sudo apt install tesseract-ocr\n"
            "  Mac:     brew install tesseract"
        )

    # Renderiza a página como imagem (300 DPI para boa qualidade de OCR)
    img_data = page.to_image(resolution=300).original
    # pdfplumber retorna PIL Image diretamente
    ocr_text = pytesseract.image_to_string(img_data, lang="por+eng")

    if not ocr_text.strip():
        return []

    # Divide em parágrafos por linhas em branco
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", ocr_text) if p.strip()]

    blocks = []
    for para in paragraphs:
        # Remove quebras de linha internas (OCR quebra linhas no meio de parágrafos)
        text = " ".join(para.splitlines())
        text = re.sub(r" {2,}", " ", text).strip()
        if not text:
            continue

        # Heurística simples: linha curta em posição inicial = possível título
        is_title = len(text) < 60 and not text.endswith(".")

        blocks.append({
            "text": text,
            "bold": is_title,
            "italic": False,
            "size": 13 if is_title else 11,
            "is_title": is_title,
            "is_list": bool(re.match(r"^\d+[\.\)]\s", text)),
            "ocr": True,  # marca que veio de OCR (útil para debug futuro)
        })

    return blocks


def extract_blocks(pdf_path: str) -> list[dict]:
    """
    Abre o PDF e retorna uma lista de páginas, cada uma com seus blocos.

    Páginas sem texto digital (escaneadas) são processadas via OCR
    automaticamente. O campo 'ocr: True' indica quais páginas usaram OCR.

    Estrutura retornada:
    [
        {
            "page": 1,
            "ocr": False,
            "blocks": [
                {"text": "...", "bold": True, "italic": False,
                 "size": 13, "is_title": True, "is_list": False, "ocr": False},
                ...
            ]
        },
        ...
    ]
    """
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["fontname", "size"], use_text_flow=True)

            # Página sem texto digital → tenta OCR automaticamente
            if not words:
                ocr_blocks = _ocr_page(page)
                pages.append({
                    "page": page_num + 1,
                    "blocks": ocr_blocks,
                    "ocr": True,
                })
                continue

            lines_dict = _group_words_by_line(words)
            sorted_tops = sorted(lines_dict.keys())
            threshold = _calculate_paragraph_threshold(sorted_tops)
            line_objects = _build_line_objects(lines_dict, sorted_tops)
            raw_blocks = _group_lines_into_blocks(line_objects, threshold)

            blocks = []
            for block_lines in raw_blocks:
                blocks.extend(_classify_block(block_lines))

            pages.append({"page": page_num + 1, "blocks": blocks, "ocr": False})

    return pages