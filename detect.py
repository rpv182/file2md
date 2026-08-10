"""Detección de tipo de archivo por contenido (magic bytes / firmas)."""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path


class UnsupportedFormatError(ValueError):
    """Formato no reconocido o no soportado."""


@dataclass(frozen=True)
class DetectedType:
    kind: str  # pdf, docx, pptx, ...
    label: str
    mime: str
    confidence: str  # content | extension | url


SUPPORTED_KINDS = {
    "pdf",
    "docx",
    "pptx",
    "xlsx",
    "odt",
    "rtf",
    "txt",
    "csv",
    "tsv",
    "json",
    "html",
    "url",
    "epub",
    "eml",
    "msg",
    "png",
    "jpg",
    "tiff",
    "zip",
    "folder",
}


def is_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value.strip(), re.I))


def detect_path(path: str | Path) -> DetectedType:
    p = Path(path)
    if p.is_dir():
        return DetectedType("folder", "Carpeta", "inode/directory", "content")
    if not p.is_file():
        raise FileNotFoundError(f"No se encontró: {p}")
    return detect_file(p)


def detect_file(path: Path) -> DetectedType:
    data = path.read_bytes()[:8192]
    by_content = _detect_bytes(data, path)
    if by_content:
        return by_content

    # Fallback controlado por extensión solo para texto plano ambiguo.
    ext = path.suffix.lower()
    ext_map = {
        ".txt": ("txt", "Texto plano", "text/plain"),
        ".csv": ("csv", "CSV", "text/csv"),
        ".tsv": ("tsv", "TSV", "text/tab-separated-values"),
        ".json": ("json", "JSON", "application/json"),
        ".html": ("html", "HTML", "text/html"),
        ".htm": ("html", "HTML", "text/html"),
        ".rtf": ("rtf", "RTF", "application/rtf"),
        ".eml": ("eml", "Correo EML", "message/rfc822"),
        ".md": ("txt", "Markdown/texto", "text/markdown"),
    }
    if ext in ext_map:
        kind, label, mime = ext_map[ext]
        # Validación extra para evitar corrupción.
        if kind == "json":
            try:
                json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
            except json.JSONDecodeError as exc:
                raise UnsupportedFormatError(
                    f"La extensión es .json pero el contenido no es JSON válido: {exc}"
                ) from exc
        return DetectedType(kind, label, mime, "extension")

    raise UnsupportedFormatError(
        f"Formato no reconocido para «{path.name}». "
        "Formatos soportados: PDF, DOCX, PPTX, XLSX, ODT, RTF, TXT, CSV, TSV, "
        "JSON, HTML, EPUB, EML, MSG, PNG, JPG, TIFF, ZIP y carpetas."
    )


def _detect_bytes(data: bytes, path: Path | None = None) -> DetectedType | None:
    if not data:
        return DetectedType("txt", "Texto vacío", "text/plain", "content")

    # PDF
    if data.startswith(b"%PDF"):
        return DetectedType("pdf", "PDF", "application/pdf", "content")

    # ZIP-based containers (OOXML, ODT, EPUB, generic ZIP)
    if data.startswith(b"PK\x03\x04") or data.startswith(b"PK\x05\x06"):
        return _detect_zip_container(path) if path else DetectedType(
            "zip", "ZIP", "application/zip", "content"
        )

    # RTF
    if data.lstrip().startswith(b"{\\rtf"):
        return DetectedType("rtf", "RTF", "application/rtf", "content")

    # Images
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return DetectedType("png", "PNG", "image/png", "content")
    if data.startswith(b"\xff\xd8\xff"):
        return DetectedType("jpg", "JPEG", "image/jpeg", "content")
    if data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
        return DetectedType("tiff", "TIFF", "image/tiff", "content")

    # MSG (OLE CFB)
    if data.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        # Could also be old .doc; try to distinguish via extension hint only as secondary.
        name = (path.name.lower() if path else "")
        if name.endswith(".msg"):
            return DetectedType("msg", "Correo MSG", "application/vnd.ms-outlook", "content")
        # OLE without clear type — refuse rather than corrupt.
        if name.endswith((".doc", ".xls", ".ppt")):
            raise UnsupportedFormatError(
                "Se detectó un documento Office antiguo (OLE). "
                "Guárdalo como .docx / .xlsx / .pptx e inténtalo de nuevo."
            )
        return DetectedType("msg", "Correo MSG / OLE", "application/vnd.ms-outlook", "content")

    text = _as_text(data)
    if text is not None:
        stripped = text.lstrip().lower()
        if stripped.startswith("<!doctype html") or stripped.startswith("<html") or (
            "<html" in stripped[:500] and ("<body" in stripped[:2000] or "<head" in stripped[:2000])
        ):
            return DetectedType("html", "HTML", "text/html", "content")
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                json.loads(text)
                return DetectedType("json", "JSON", "application/json", "content")
            except json.JSONDecodeError:
                pass
        if "\n" in text and _looks_like_eml(text):
            return DetectedType("eml", "Correo EML", "message/rfc822", "content")
        if _looks_like_tsv(text):
            return DetectedType("tsv", "TSV", "text/tab-separated-values", "content")
        if _looks_like_csv(text):
            return DetectedType("csv", "CSV", "text/csv", "content")
        # Plain text fallback only if mostly printable.
        if _mostly_text(data):
            return DetectedType("txt", "Texto plano", "text/plain", "content")

    return None


def _detect_zip_container(path: Path) -> DetectedType:
    try:
        with zipfile.ZipFile(path) as zf:
            names = {n.replace("\\", "/") for n in zf.namelist()}
    except zipfile.BadZipFile as exc:
        raise UnsupportedFormatError(f"El archivo parece ZIP pero está dañado: {path.name}") from exc

    if "word/document.xml" in names or any(n.startswith("word/") for n in names):
        return DetectedType(
            "docx",
            "Word DOCX",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "content",
        )
    if "ppt/presentation.xml" in names or any(n.startswith("ppt/") for n in names):
        return DetectedType(
            "pptx",
            "PowerPoint PPTX",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "content",
        )
    if "xl/workbook.xml" in names or any(n.startswith("xl/") for n in names):
        return DetectedType(
            "xlsx",
            "Excel XLSX",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "content",
        )
    if "mimetype" in names:
        try:
            with zipfile.ZipFile(path) as zf:
                mime = zf.read("mimetype").decode("utf-8", errors="ignore").strip()
            if "epub" in mime:
                return DetectedType("epub", "EPUB", "application/epub+zip", "content")
            if "opendocument.text" in mime:
                return DetectedType("odt", "OpenDocument Text", "application/vnd.oasis.opendocument.text", "content")
        except KeyError:
            pass
    if "content.xml" in names and "META-INF/manifest.xml" in names:
        return DetectedType("odt", "OpenDocument Text", "application/vnd.oasis.opendocument.text", "content")
    if "META-INF/container.xml" in names:
        return DetectedType("epub", "EPUB", "application/epub+zip", "content")

    return DetectedType("zip", "ZIP", "application/zip", "content")


def _as_text(data: bytes) -> str | None:
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def _mostly_text(data: bytes) -> bool:
    if not data:
        return True
    sample = data[:4096]
    printable = sum(1 for b in sample if 9 <= b <= 13 or 32 <= b <= 126 or b >= 160)
    return printable / max(len(sample), 1) > 0.85


def _looks_like_eml(text: str) -> bool:
    head = text[:2000]
    return bool(re.search(r"(?im)^(from|to|subject|date|mime-version):", head))


def _looks_like_tsv(text: str) -> bool:
    lines = [ln for ln in text.splitlines()[:10] if ln.strip()]
    if len(lines) < 2:
        return False
    tabs = [ln.count("\t") for ln in lines]
    return min(tabs) >= 1 and max(tabs) == min(tabs)


def _looks_like_csv(text: str) -> bool:
    lines = [ln for ln in text.splitlines()[:10] if ln.strip()]
    if len(lines) < 2:
        return False
    # Heurística simple: comas consistentes y no parece prosa.
    commas = [ln.count(",") for ln in lines]
    return min(commas) >= 1 and (max(commas) - min(commas)) <= 2
