"""
services/openrouter_service.py — Integração com OpenRouter.
Marcado como alfa — modelos gratuitos podem ser descontinuados a qualquer momento.
"""

from openai import OpenAI


def translate(text: str, target_lang: str, model: str, api_key: str) -> str:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _system_prompt(target_lang)},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()


def _system_prompt(target_lang: str) -> str:
    return (
        f"You are a professional translator. Translate everything to {target_lang}.\n"
        "Rules:\n"
        "- Return ONLY the translation, no explanations\n"
        "- Preserve the meaning and tone exactly\n"
        "- Keep names, proper nouns and acronyms unchanged"
    )