"""
services/gemini_service.py — Integração com a API do Google Gemini.
Marcado como alfa — pode ter problemas regionais de autenticação.
"""

from google import genai


def translate(text: str, target_lang: str, model: str, api_key: str) -> str:
    client = genai.Client(api_key=api_key)
    prompt = _system_prompt(target_lang) + "\n\nText to translate:\n" + text
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text.strip()


def _system_prompt(target_lang: str) -> str:
    return (
        f"You are a professional translator. Translate everything to {target_lang}.\n"
        "Rules:\n"
        "- Return ONLY the translation, no explanations\n"
        "- Preserve the meaning and tone exactly\n"
        "- Keep names, proper nouns and acronyms unchanged"
    )