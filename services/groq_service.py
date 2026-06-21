"""
services/groq_service.py — Integração com a API do Groq.

Otimizações aplicadas:
- Cliente instanciado uma única vez (reutilizado entre chamadas)
- Instrução de batch movida para o system prompt (menos tokens por chamada)
- Retry automático com backoff exponencial (resolve erro 429 / rate limit)
"""

import time
from groq import Groq

# ── Cliente singleton — instanciado uma vez, reutilizado em todas as chamadas ──
_client: Groq | None = None
_current_key: str = ""


def _get_client(api_key: str) -> Groq:
    """Retorna o cliente Groq, criando um novo só se a key mudou."""
    global _client, _current_key
    if _client is None or api_key != _current_key:
        _client = Groq(api_key=api_key)
        _current_key = api_key
    return _client


def translate(text: str, target_lang: str, model: str, api_key: str) -> str:
    """
    Traduz o texto usando a API do Groq.

    Retry automático:
    - Tenta até 4 vezes em caso de erro 429 (rate limit) ou 5xx (instabilidade)
    - Espera crescente: 5s → 15s → 30s entre tentativas
    - Lança RuntimeError com mensagem clara se todas as tentativas falharem
    """
    client = _get_client(api_key)

    wait_times = [5, 15, 30]  # segundos de espera entre tentativas

    for attempt in range(4):  # 1 tentativa normal + 3 retries
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _system_prompt(target_lang)},
                    {"role": "user", "content": text},
                ],
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            err = str(e)
            is_rate_limit = "429" in err or "rate_limit" in err.lower() or "rate limit" in err.lower()
            is_server_error = "500" in err or "502" in err or "503" in err

            # Se for o último attempt, lança o erro
            if attempt == 3:
                if is_rate_limit:
                    raise RuntimeError(
                        "Groq rate limit reached after 4 attempts.\n"
                        "This PDF may be too large for the free tier (6,000 tokens/min).\n"
                        "Options:\n"
                        "  • Wait a minute and try again\n"
                        "  • Use Ollama (no rate limit)\n"
                        "  • Upgrade your Groq plan"
                    )
                raise RuntimeError(f"Groq API error after 4 attempts: {err}")

            # Se for rate limit ou erro de servidor, tenta de novo
            if is_rate_limit or is_server_error:
                wait = wait_times[attempt]
                time.sleep(wait)
                continue

            # Qualquer outro erro (key inválida, modelo inválido) — falha imediata
            raise RuntimeError(f"Groq API error: {err}")


def _system_prompt(target_lang: str) -> str:
    return (
        f"You are a professional translator. Translate everything to {target_lang}.\n"
        "Rules:\n"
        "- Return ONLY the translation, no explanations\n"
        "- Preserve the meaning and tone exactly\n"
        "- Keep names, proper nouns and acronyms unchanged\n"
        "- When text contains blocks separated by '|||BLOCK|||', "
        "translate each block individually and return them separated by '|||BLOCK|||'. "
        "Keep the EXACT same number of blocks."
    )