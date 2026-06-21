"""
services/ollama_service.py — Integração com Ollama (IA local).
Não requer chave de API. Requer Ollama instalado e rodando localmente.

Otimizações aplicadas:
- Instrução de batch no system prompt (menos tokens por chamada)
- Retry automático para erros de conexão (Ollama às vezes demora a responder)
"""

import time
import ollama


def translate(text: str, target_lang: str, model: str, api_key: str = "") -> str:
    """
    Traduz o texto usando Ollama local.

    Retry automático:
    - Tenta até 3 vezes em caso de erro de conexão ou timeout
    - Espera 3s entre tentativas
    """
    wait_times = [3, 6]  # segundos entre tentativas

    for attempt in range(3):
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": _system_prompt(target_lang)},
                    {"role": "user", "content": text},
                ],
            )
            return response["message"]["content"].strip()

        except Exception as e:
            err = str(e).lower()
            is_connection = "connection" in err or "timeout" in err or "refused" in err

            if attempt == 2:
                if is_connection:
                    raise RuntimeError(
                        "Could not connect to Ollama after 3 attempts.\n"
                        "Make sure Ollama is running: open a terminal and run 'ollama serve'"
                    )
                raise RuntimeError(f"Ollama error after 3 attempts: {e}")

            if is_connection:
                time.sleep(wait_times[attempt])
                continue

            # Erro desconhecido — falha imediata
            raise RuntimeError(f"Ollama error: {e}")


def _system_prompt(target_lang: str) -> str:
    return (
        f"You are a professional translator. Translate everything to {target_lang}.\n"
        "Rules:\n"
        "- Return ONLY the translation, no explanations\n"
        "- Preserve the meaning and tone exactly\n"
        "- Keep names, proper nouns and acronyms unchanged"
    )