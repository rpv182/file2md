"""OCR compartido (Windows.Media.Ocr) para PDF e imágenes."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[str], None]


def pick_ocr_language() -> str:
    from winrt.windows.media.ocr import OcrEngine

    available = {lang.language_tag for lang in OcrEngine.available_recognizer_languages}
    for candidate in ("es-ES", "es-MX", "es", "en-US", "en"):
        if candidate in available:
            return candidate
    if available:
        return sorted(available)[0]
    raise RuntimeError(
        "Windows no tiene ningún paquete OCR instalado. "
        "En Configuración → Hora e idioma → Idioma, instala español o inglés "
        "con reconocimiento de texto / OCR."
    )


def windows_ocr_to_text(result: dict | object) -> str:
    if isinstance(result, dict):
        lines = result.get("lines") or []
        texts = []
        for line in lines:
            if isinstance(line, dict):
                text = str(line.get("text") or "").strip()
            else:
                text = str(getattr(line, "text", "") or "").strip()
            if text:
                texts.append(text)
        if texts:
            return "\n\n".join(texts)
        return str(result.get("text") or "").strip()
    return str(getattr(result, "text", "") or "").strip()


def ocr_pil_image(image, progress: ProgressCallback | None = None) -> str:
    from winocr import recognize_pil_sync

    lang = pick_ocr_language()
    if progress:
        progress(f"OCR imagen ({lang})…")
    result = recognize_pil_sync(image.convert("RGB"), lang)
    return windows_ocr_to_text(result)


def ocr_image_file(path: Path, progress: ProgressCallback | None = None) -> str:
    from PIL import Image

    with Image.open(path) as img:
        return ocr_pil_image(img, progress=progress)


def pdf_looks_like_scan(pdf: Path, min_chars_per_page: int = 40) -> bool:
    import pymupdf

    with pymupdf.open(pdf) as doc:
        if len(doc) == 0:
            return False
        total = 0
        for page in doc:
            total += len(page.get_text("text").strip())
        return total < max(min_chars_per_page, min_chars_per_page * len(doc) // 2)


def ocr_pdf_to_markdown(pdf: Path, progress: ProgressCallback | None = None) -> str:
    import pymupdf
    from PIL import Image
    from winocr import recognize_pil_sync

    lang = pick_ocr_language()
    parts: list[str] = []
    with pymupdf.open(pdf) as doc:
        total = len(doc)
        for index, page in enumerate(doc, start=1):
            if progress:
                progress(f"OCR página {index}/{total} ({lang})…")
            mat = pymupdf.Matrix(220 / 72, 220 / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            image = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
            page_text = windows_ocr_to_text(recognize_pil_sync(image, lang))
            if page_text.strip():
                if total > 1:
                    parts.append(f"## Página {index}\n\n{page_text.strip()}")
                else:
                    parts.append(page_text.strip())
    return "\n\n".join(parts).strip()
