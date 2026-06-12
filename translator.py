"""
translator.py — PDF extraction, translation and PDF generation.
Supports: Groq, Google Gemini, OpenRouter, Ollama (local)
Focus: good reading experience, not pixel-perfect layout replication.
"""

import pdfplumber
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT

LANGUAGES = {
    "Portuguese": "Portuguese (Brazil)",
    "English": "English",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Italian": "Italian",
    "Japanese": "Japanese",
    "Chinese": "Chinese (Simplified)",
    "Russian": "Russian",
    "Arabic": "Arabic",
}

PROVIDERS = {
    "Groq":       {"label": "Groq",          "needs_key": True,  "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]},
    "Gemini":     {"label": "Gemini",         "needs_key": True,  "models": ["gemini-1.5-flash", "gemini-1.5-pro"]},
    "OpenRouter": {"label": "OpenRouter",     "needs_key": True,  "models": ["meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-r1:free", "meta-llama/llama-4-maverick:free", "qwen/qwen3-235b-a22b:free", "openrouter/auto"]},
    "Ollama":     {"label": "Ollama (Local)", "needs_key": False, "models": ["gemma4:e4b", "llama3.3:8b", "llama3.2:3b", "phi4-mini", "qwen2.5:7b", "mistral"]},
}


# ─────────────────────────────────────────────
#  Helpers de fonte
# ─────────────────────────────────────────────

def is_bold(fontname):
    return "Bold" in fontname or "bold" in fontname

def is_italic(fontname):
    return "Italic" in fontname or "italic" in fontname or "Oblique" in fontname


# ─────────────────────────────────────────────
#  Extração inteligente
# ─────────────────────────────────────────────

def extract_blocks(pdf_path):
    """
    Extrai blocos de texto do PDF com metadados de formatação.
    Cada bloco tem: text, bold, italic, size, is_title, is_list_item
    """
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(
                extra_attrs=["fontname", "size"],
                use_text_flow=True,
            )
            if not words:
                pages.append({"page": page_num + 1, "blocks": []})
                continue

            # Agrupa palavras por linha
            lines_dict = {}
            for word in words:
                top = round(word["top"], 1)
                if top not in lines_dict:
                    lines_dict[top] = []
                lines_dict[top].append(word)

            sorted_tops = sorted(lines_dict.keys())

            # Calcula gap mínimo real para detectar parágrafos
            gaps = [sorted_tops[i+1] - sorted_tops[i] for i in range(len(sorted_tops)-1)]
            min_gap = min(gaps) if gaps else 14
            para_threshold = min_gap * 1.4

            # Monta linhas com metadados
            line_objects = []
            for top in sorted_tops:
                words_in_line = lines_dict[top]
                text = " ".join(w["text"] for w in words_in_line)
                fonts = [w.get("fontname", "") for w in words_in_line]
                sizes = [w.get("size", 12) for w in words_in_line]
                bold_count = sum(1 for f in fonts if is_bold(f))
                italic_count = sum(1 for f in fonts if is_italic(f))
                line_objects.append({
                    "top": top,
                    "text": text,
                    "bold": bold_count > len(fonts) / 2,
                    "italic": italic_count > len(fonts) / 2,
                    "size": max(sizes),
                })

            # Agrupa linhas em parágrafos
            raw_blocks = []
            current = []
            prev_top = None

            for line in line_objects:
                if prev_top is not None and (line["top"] - prev_top) > para_threshold:
                    if current:
                        raw_blocks.append(current)
                        current = []
                current.append(line)
                prev_top = line["top"]
            if current:
                raw_blocks.append(current)

            # Converte blocos em objetos finais
            page_width = page.width
            blocks = []
            for block_lines in raw_blocks:
                full_text = " ".join(l["text"] for l in block_lines)
                bold = any(l["bold"] for l in block_lines)
                italic = any(l["italic"] for l in block_lines)
                size = max(l["size"] for l in block_lines)

                # Detecta título: bloco de 1 linha, curto, negrito ou fonte grande
                is_title = (
                    len(block_lines) == 1 and
                    (bold or size > 13) and
                    len(full_text) < 80
                )

                # Detecta lista numerada: começa com "1." "2." etc
                is_list = bool(re.match(r'^\d+[\.\)]\s', full_text.strip()))

                # Se for um bloco longo com múltiplos itens de lista grudados,
                # divide nos números (1. 2. 3. etc)
                sub_blocks = []
                if not is_title and re.search(r'\s\d+[\.\)]\s', full_text):
                    # Divide nas ocorrências de "N. " no meio do texto
                    parts = re.split(r'(?<=\s)(?=\d+[\.\)]\s)', full_text)
                    for part in parts:
                        part = part.strip()
                        if part:
                            sub_blocks.append({
                                "text": part,
                                "bold": bold,
                                "italic": italic,
                                "size": size,
                                "is_title": False,
                                "is_list": bool(re.match(r'^\d+[\.\)]\s', part)),
                            })
                else:
                    sub_blocks.append({
                        "text": full_text,
                        "bold": bold,
                        "italic": italic,
                        "size": size,
                        "is_title": is_title,
                        "is_list": is_list,
                    })

                blocks.extend(sub_blocks)

            pages.append({"page": page_num + 1, "blocks": blocks})

    return pages


# ─────────────────────────────────────────────
#  Tradução
# ─────────────────────────────────────────────

def translate_text(text, target_lang, provider, model, api_key=""):
    prompt_system = (
        f"You are a professional translator. Translate everything to {target_lang}.\n"
        "Rules:\n"
        "- Return ONLY the translation, no explanations\n"
        "- Preserve the meaning and tone exactly\n"
        "- Keep names, proper nouns and acronyms unchanged"
    )

    if provider == "Groq":
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": text},
            ]
        )
        return response.choices[0].message.content.strip()

    elif provider == "Gemini":
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=f"{prompt_system}\n\nText to translate:\n{text}"
        )
        return response.text.strip()

    elif provider == "OpenRouter":
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": text},
            ]
        )
        return response.choices[0].message.content.strip()

    elif provider == "Ollama":
        import ollama
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": text},
            ]
        )
        return response["message"]["content"].strip()

    else:
        raise ValueError(f"Unknown provider: {provider}")


def translate_blocks(blocks, target_lang, provider, model, api_key, progress_callback=None):
    """Translate all blocks of a page in a single API call."""
    if not blocks:
        return []

    SEP = "|||BLOCK|||"
    combined = (SEP + "\n").join(b["text"] for b in blocks)
    instruction = (
        "The text below has blocks separated by '" + SEP + "'. "
        "Translate each block to " + target_lang + " and return them separated by '" + SEP + "'. "
        "Keep the EXACT same number of blocks. Return ONLY the translated blocks with separators.\n\n"
    )

    try:
        result = translate_text(instruction + combined, target_lang, provider, model, api_key)
        parts = [p.strip() for p in result.split(SEP)]
        if len(parts) == len(blocks):
            return [{**block, "text": parts[i]} for i, block in enumerate(blocks)]
        # fallback: block by block
        translated = []
        for i, block in enumerate(blocks):
            if progress_callback:
                progress_callback(i, len(blocks), "Translating block " + str(i+1) + "...")
            try:
                t_text = translate_text(block["text"], target_lang, provider, model, api_key)
            except Exception as e2:
                raise RuntimeError(f"Block translation failed ({provider}/{model}): {e2}")
            translated.append({**block, "text": t_text})
        return translated
    except Exception as e:
        raise RuntimeError(f"Translation failed ({provider}/{model}): {e}")

def generate_pdf(translated_pages, output_path, target_lang):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title2", parent=styles["Normal"],
        fontSize=13, leading=18,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
        spaceAfter=6, spaceBefore=10,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=11, leading=17,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    list_style = ParagraphStyle(
        "List", parent=styles["Normal"],
        fontSize=11, leading=17,
        alignment=TA_LEFT,
        leftIndent=12,
        spaceAfter=4,
    )
    italic_style = ParagraphStyle(
        "Italic2", parent=styles["Normal"],
        fontSize=11, leading=17,
        fontName="Helvetica-Oblique",
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    page_label_style = ParagraphStyle(
        "PageLabel", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#888888"),
        spaceAfter=6, spaceBefore=12,
    )

    story = []

    for page_data in translated_pages:
        story.append(Paragraph(f"— Page {page_data['page']} —", page_label_style))

        for block in page_data["blocks"]:
            text = (block["text"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))

            if block.get("is_title"):
                if block.get("italic"):
                    story.append(Paragraph(f"<i>{text}</i>", title_style))
                else:
                    story.append(Paragraph(f"<b>{text}</b>", title_style))
            elif block.get("is_list"):
                story.append(Paragraph(text, list_style))
            elif block.get("bold"):
                story.append(Paragraph(f"<b>{text}</b>", body_style))
            elif block.get("italic"):
                story.append(Paragraph(text, italic_style))
            else:
                story.append(Paragraph(text, body_style))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.4,
                                color=colors.HexColor("#dddddd")))
        story.append(Spacer(1, 8))

    doc.build(story)


# ─────────────────────────────────────────────
#  Pipeline principal
# ─────────────────────────────────────────────

def translate_pdf(input_path, output_path, target_lang_display, provider, model,
                  api_key="", progress_callback=None):
    target_lang_en = LANGUAGES.get(target_lang_display, target_lang_display)

    if progress_callback:
        progress_callback(0, 1, "Extracting text from PDF...")

    pages = extract_blocks(input_path)
    total_pages = len(pages)

    if total_pages == 0:
        raise ValueError("No text found in this PDF. It may be a scanned document.")

    translated_pages = []
    total_blocks = sum(len(p["blocks"]) for p in pages)
    done = 0

    for page_data in pages:
        if progress_callback:
            progress_callback(done, total_blocks,
                              f"Translating page {page_data['page']} of {total_pages}...")

        def cb(i, total, msg, _done=done):
            if progress_callback:
                progress_callback(_done + i, total_blocks, msg)

        t_blocks = translate_blocks(
            page_data["blocks"], target_lang_en, provider, model, api_key, cb
        )
        done += len(page_data["blocks"])
        translated_pages.append({"page": page_data["page"], "blocks": t_blocks})

    if progress_callback:
        progress_callback(total_blocks, total_blocks, "Generating translated PDF...")

    generate_pdf(translated_pages, output_path, target_lang_display)
    return output_path