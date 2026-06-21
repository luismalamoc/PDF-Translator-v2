"""
core/translator.py — Lógica de tradução dos blocos extraídos.

Responsabilidade única: receber blocos de texto e devolvê-los traduzidos.
Não sabe nada sobre extração de PDF ou geração de PDF.
Delega a chamada de API para o service correto.

Otimizações aplicadas:
- Instrução de batch removida do user message (agora está no system prompt de cada service)
- Aviso explícito quando fallback bloco-a-bloco é ativado
"""

from config.settings import BLOCK_SEPARATOR


def _get_service(provider: str):
    """
    Retorna o módulo de service correto para o provider escolhido.
    Para adicionar um novo provider: crie o service e adicione aqui.
    """
    if provider == "Groq":
        from services import groq_service
        return groq_service
    elif "Gemini" in provider:
        from services import gemini_service
        return gemini_service
    elif "OpenRouter" in provider:
        from services import openrouter_service
        return openrouter_service
    elif provider == "Ollama":
        from services import ollama_service
        return ollama_service
    else:
        raise ValueError(f"Unknown provider: {provider}")


def translate_text(
    text: str,
    target_lang: str,
    provider: str,
    model: str,
    api_key: str = "",
) -> str:
    """Traduz um bloco de texto usando o provider especificado."""
    service = _get_service(provider)
    return service.translate(text, target_lang, model, api_key)


def translate_blocks(
    blocks: list[dict],
    target_lang: str,
    provider: str,
    model: str,
    api_key: str = "",
    progress_callback=None,
) -> list[dict]:
    """
    Traduz todos os blocos de uma página em uma única chamada batch.
    Usa |||BLOCK||| para manter a estrutura.

    Se a IA não respeitar os separadores, cai no fallback bloco a bloco.
    O feedback de progresso durante o batch é feito via heartbeat no pipeline.
    """
    if not blocks:
        return []

    SEP = BLOCK_SEPARATOR
    combined = (SEP + "\n").join(b["text"] for b in blocks)

    # Ollama recebe a instrução no user message (system prompt é mantido curto para não estourar VRAM)
    # Groq e outros recebem só o texto (instrução já está no system prompt do service)
    if provider == "Ollama":
        instruction = (
            "The text below has blocks separated by '" + SEP + "'. "
            "Translate each block to " + target_lang + " and return them separated by '" + SEP + "'. "
            "Keep the EXACT same number of blocks. Return ONLY the translated blocks with separators.\n\n"
        )
        combined = instruction + combined

    try:
        result = translate_text(combined, target_lang, provider, model, api_key)
        parts = [p.strip() for p in result.split(SEP)]

        if len(parts) == len(blocks):
            return [{**block, "text": parts[i]} for i, block in enumerate(blocks)]

        # Fallback se a IA não respeitou os separadores
        if progress_callback:
            progress_callback(0, len(blocks), "⚠️ Retrying page block by block...")
        return _translate_block_by_block(blocks, target_lang, provider, model, api_key, progress_callback)

    except Exception as e:
        raise RuntimeError(f"Translation failed ({provider}/{model}): {e}")


def _translate_block_by_block(
    blocks: list[dict],
    target_lang: str,
    provider: str,
    model: str,
    api_key: str,
    progress_callback=None,
) -> list[dict]:
    """Fallback: traduz cada bloco individualmente."""
    translated = []
    total = len(blocks)

    for i, block in enumerate(blocks):
        if progress_callback:
            progress_callback(i, total, f"Translating block {i + 1} of {total}...")
        try:
            t_text = translate_text(block["text"], target_lang, provider, model, api_key)
        except Exception as e:
            raise RuntimeError(f"Block {i + 1} translation failed ({provider}/{model}): {e}")
        translated.append({**block, "text": t_text})

    return translated