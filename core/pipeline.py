"""
core/pipeline.py — Pipeline principal de tradução.

Responsabilidade única: orquestrar as 3 etapas do processo:
1. Extrair texto do PDF (extractor)
2. Traduzir os blocos (translator)
3. Gerar o PDF traduzido (generator)

Otimizações aplicadas:
- Estimativa de tokens antes de começar (previne erro 429 no meio da tradução)
- Aviso ao usuário quando o PDF é grande demais para o free tier do Groq
- Paralelismo com ThreadPoolExecutor para providers sem rate limit (Ollama)
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from config.settings import LANGUAGES
from core.extractor import extract_blocks
from core.translator import translate_blocks
from core.generator import generate_pdf

# Limite conservador do Groq free tier (real é 6000, usamos 5000 por segurança)
GROQ_FREE_TOKENS_PER_MIN = 5000

# Chars por token (estimativa: 1 token ≈ 4 caracteres)
CHARS_PER_TOKEN = 4

# Providers que suportam paralelismo (sem rate limit rígido)
# NOTA: Ollama removido do paralelo — modelos grandes (gemma4, llama3.3) não têm
# VRAM suficiente para rodar múltiplas instâncias. Sequencial com feedback é melhor.
PARALLEL_PROVIDERS: set = set()

# Número de páginas traduzidas em paralelo (reservado para uso futuro com API paga)
PARALLEL_WORKERS = 4


def _estimate_tokens(pages: list[dict]) -> int:
    """Estima o total de tokens que o PDF vai consumir na API."""
    total_chars = sum(
        len(block["text"])
        for page in pages
        for block in page["blocks"]
    )
    return total_chars // CHARS_PER_TOKEN


def _estimated_minutes(tokens: int, provider: str) -> float | None:
    """
    Retorna estimativa de minutos mínimos pelo rate limit do provider.
    Retorna None se o provider não tiver rate limit conhecido (ex: Ollama).
    """
    if provider == "Groq":
        return tokens / GROQ_FREE_TOKENS_PER_MIN
    return None


def _translate_page_parallel(
    page_data: dict,
    target_lang_en: str,
    provider: str,
    model: str,
    api_key: str,
    progress_callback: Callable | None,
    done_counter: list,
    total_blocks: int,
    lock: threading.Lock,
) -> dict:
    """
    Traduz uma única página. Projetado para ser chamado em thread paralela.

    Usa lock para atualizar o progresso de forma thread-safe.
    Retorna o dict da página com os blocos traduzidos.
    """
    t_blocks = translate_blocks(
        page_data["blocks"],
        target_lang_en,
        provider,
        model,
        api_key,
        progress_callback=None,  # progresso individual desativado no paralelo
    )

    # Atualiza contador de progresso de forma thread-safe
    with lock:
        done_counter[0] += len(page_data["blocks"])
        done = done_counter[0]
        if progress_callback:
            progress_callback(
                done,
                total_blocks,
                f"Translated page {page_data['page']} ✓",
            )

    return {"page": page_data["page"], "blocks": t_blocks}


def translate_pdf(
    input_path: str,
    output_path: str,
    target_lang_display: str,
    provider: str,
    model: str,
    api_key: str = "",
    progress_callback: Callable | None = None,
) -> str:
    """
    Pipeline completo: extrai → traduz → gera PDF.

    Para Ollama: traduz páginas em paralelo (4 workers simultâneos).
    Para Groq:   traduz sequencialmente, respeitando o rate limit.

    Args:
        input_path: caminho do PDF original
        output_path: caminho onde o PDF traduzido será salvo
        target_lang_display: idioma de destino (ex: "Portuguese")
        provider: provider de IA (ex: "Groq")
        model: modelo de IA (ex: "llama-3.3-70b-versatile")
        api_key: chave de API (vazio para Ollama)
        progress_callback: função chamada a cada etapa (current, total, message)

    Returns:
        output_path do PDF gerado
    """
def translate_pdf(
    input_path: str,
    output_path: str,
    target_lang_display: str,
    provider: str,
    model: str,
    api_key: str = "",
    progress_callback: Callable | None = None,
    log_callback: Callable | None = None,
) -> str:
    """
    Pipeline completo: extrai → traduz → gera PDF.

    progress_callback(current, total, msg) — atualiza barra + status (heartbeat incluso)
    log_callback(msg, tag)                 — log detalhado independente (eventos reais)
    """
    def log(msg: str, tag: str = "info"):
        if log_callback:
            log_callback(msg, tag)

    target_lang_en = LANGUAGES.get(target_lang_display, target_lang_display)

    # ── Etapa 1: Extração ──
    if progress_callback:
        progress_callback(0, 1, "Extracting text from PDF...")
    log(f"Opening PDF: {input_path.split('/')[-1].split(chr(92))[-1]}", "info")

    pages = extract_blocks(input_path)

    total_pages = len(pages)
    total_blocks = sum(len(p["blocks"]) for p in pages)
    ocr_pages = [p for p in pages if p.get("ocr")]

    log(f"Extracted {total_pages} page(s), {total_blocks} blocks total", "ok")

    if ocr_pages:
        log(f"OCR applied to {len(ocr_pages)} scanned page(s): "
            f"{[p['page'] for p in ocr_pages]}", "warn")
        if progress_callback:
            progress_callback(0, 1, f"OCR applied to {len(ocr_pages)} scanned page(s). Continuing...")

    if not pages or all(not p["blocks"] for p in pages):
        raise ValueError(
            "No text could be extracted from this PDF, even with OCR.\n"
            "The file may be corrupted, password-protected, or contain only images.\n\n"
            "If using OCR: make sure Tesseract is installed on your system.\n"
            "  Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "  Linux:   sudo apt install tesseract-ocr\n"
            "  Mac:     brew install tesseract"
        )

    # ── Estimativa de tokens ──
    estimated_tokens = _estimate_tokens(pages)
    estimated_min = _estimated_minutes(estimated_tokens, provider)

    log(f"Estimated tokens: ~{estimated_tokens:,}", "info")

    if estimated_min is not None:
        if estimated_min > 2:
            log(f"⚠️ Large PDF — estimated {estimated_min:.0f}+ min (Groq free tier limit)", "warn")
            if progress_callback:
                progress_callback(0, 1,
                    f"⚠️ Large PDF (~{estimated_tokens:,} tokens). "
                    f"Estimated time: {estimated_min:.0f}+ min due to Groq free tier limits.")
        else:
            if progress_callback:
                progress_callback(0, 1, f"Estimated tokens: ~{estimated_tokens:,}. Starting translation...")
    else:
        if progress_callback:
            progress_callback(0, 1,
                f"Starting translation — {total_pages} pages, ~{total_blocks} blocks (Ollama local)...")

    log(f"Provider: {provider}  |  Model: {model}  |  Target: {target_lang_display}", "info")
    log(f"Starting translation of {total_pages} page(s)...", "info")

    # ── Etapa 2: Tradução ──
    use_parallel = provider in PARALLEL_PROVIDERS

    if use_parallel:
        translated_pages = _translate_parallel(
            pages, target_lang_en, provider, model, api_key,
            progress_callback, log_callback, total_blocks
        )
    else:
        translated_pages = _translate_sequential(
            pages, target_lang_en, provider, model, api_key,
            progress_callback, log_callback, total_blocks, total_pages
        )

    # ── Etapa 3: Geração do PDF ──
    log("Generating translated PDF...", "info")
    if progress_callback:
        progress_callback(total_blocks, total_blocks, "Generating translated PDF...")

    generate_pdf(translated_pages, output_path, target_lang_display)
    log(f"✅ Done! Saved to: {output_path.split('/')[-1].split(chr(92))[-1]}", "ok")
    return output_path


def _translate_sequential(
    pages, target_lang_en, provider, model, api_key,
    progress_callback, log_callback, total_blocks, total_pages
) -> list[dict]:
    """Tradução sequencial com heartbeat por página e log detalhado."""
    import time
    import threading

    def log(msg, tag="info"):
        if log_callback:
            log_callback(msg, tag)

    translated_pages = []
    done = 0

    for page_data in pages:
        page_num = page_data["page"]
        page_blocks = len(page_data["blocks"])
        page_start = time.time()

        log(f"── Page {page_num}/{total_pages} ── {page_blocks} blocks", "info")

        if progress_callback:
            progress_callback(done, total_blocks,
                f"Translating page {page_num}/{total_pages} — {page_blocks} blocks...")

        # Heartbeat: atualiza status a cada 5s enquanto o batch roda
        stop_hb = threading.Event()

        def _hb(_done=done, _page=page_num, _pages=total_pages, _start=page_start):
            msgs = [
                "⏳ Model processing batch...",
                "⏳ Still translating, please wait...",
                "⏳ Working on it, hang tight...",
                "⏳ Almost there...",
            ]
            i = 0
            while not stop_hb.wait(5):
                elapsed = int(time.time() - _start)
                if progress_callback:
                    progress_callback(_done, total_blocks,
                        f"Page {_page}/{_pages} — {msgs[i % len(msgs)]} ({elapsed}s)")
                i += 1

        hb = threading.Thread(target=_hb, daemon=True)
        hb.start()

        try:
            block_times = []

            def cb(i, total, msg, _done=done, _page=page_num, _pages=total_pages):
                # Bloco individual — só no fallback bloco a bloco
                log(f"  block {i+1}/{total}: {msg}", "info")
                if progress_callback:
                    progress_callback(_done + i, total_blocks,
                        f"Page {_page}/{_pages} — {msg}")

            t_blocks = translate_blocks(
                page_data["blocks"], target_lang_en,
                provider, model, api_key, cb,
            )
        finally:
            stop_hb.set()

        done += page_blocks
        elapsed_page = int(time.time() - page_start)

        log(f"✅ Page {page_num}/{total_pages} done — "
            f"{page_blocks} blocks in {elapsed_page}s "
            f"({done}/{total_blocks} total)", "ok")

        if progress_callback:
            progress_callback(done, total_blocks,
                f"✅ Page {page_num}/{total_pages} done — "
                f"{done}/{total_blocks} blocks ({elapsed_page}s)")

        translated_pages.append({"page": page_data["page"], "blocks": t_blocks})

    return translated_pages


def _translate_parallel(
    pages, target_lang_en, provider, model, api_key,
    progress_callback, total_blocks
) -> list[dict]:
    """
    Tradução paralela — usada para Ollama e providers sem rate limit.
    Mantém a ordem original das páginas no resultado final.

    Inclui thread de heartbeat que mantém a UI atualizada mesmo quando
    nenhuma página terminou ainda (modelos grandes podem demorar minutos).
    """
    lock = threading.Lock()
    done_counter = [0]        # blocos traduzidos (para barra de progresso)
    pages_done_counter = [0]  # páginas concluídas (para mensagem do heartbeat)
    results: dict[int, dict] = {}
    errors: list[Exception] = []
    total_pages = len(pages)
    finished_flag = threading.Event()

    # Mensagens rotativas exibidas enquanto o modelo está processando
    waiting_messages = [
        "⏳ Model is processing... this may take a while",
        "⏳ Still translating in parallel, please wait...",
        "⏳ Working hard on your PDF, hang tight...",
        "⏳ Large model = better quality, just takes a moment...",
        "⏳ Translation in progress, do not close the app...",
    ]

    def _heartbeat():
        """Envia mensagens periódicas para a UI a cada 8 segundos."""
        import time as _time
        msg_index = 0
        while not finished_flag.is_set():
            _time.sleep(8)
            if finished_flag.is_set():
                break
            with lock:
                done = done_counter[0]
                pages_done = pages_done_counter[0]
            if progress_callback:
                msg = waiting_messages[msg_index % len(waiting_messages)]
                progress_callback(
                    done,
                    total_blocks,
                    f"{msg} ({pages_done}/{total_pages} pages done)",
                )
            msg_index += 1

    # Inicia a thread de heartbeat
    hb_thread = threading.Thread(target=_heartbeat, daemon=True)
    hb_thread.start()

    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        futures = {
            executor.submit(
                _translate_page_parallel,
                page_data,
                target_lang_en,
                provider,
                model,
                api_key,
                progress_callback,
                done_counter,
                total_blocks,
                lock,
            ): page_data["page"]
            for page_data in pages
        }

        for future in as_completed(futures):
            page_num = futures[future]
            try:
                result = future.result()
                results[page_num] = result
                with lock:
                    pages_done_counter[0] += 1
            except Exception as e:
                errors.append(e)
                for f in futures:
                    f.cancel()
                break

    # Para o heartbeat
    finished_flag.set()

    if errors:
        raise RuntimeError(f"Parallel translation failed: {errors[0]}")

    # Reordena os resultados pela ordem original das páginas
    return [results[p["page"]] for p in pages]