"""Orquestador: convierte archivos, URLs, ZIP y carpetas a Markdown."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path
from typing import Callable

from detect import UnsupportedFormatError, detect_path, is_url
from formats import convert_detected, convert_url
from markdown_out import write_markdown

ProgressCallback = Callable[[str], None]

CONVERTIBLE_KINDS = {
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
    "epub",
    "eml",
    "msg",
    "png",
    "jpg",
    "tiff",
}


def convert_to_markdown(
    source: str | Path,
    output: str | Path | None = None,
    *,
    ocr_mode: str = "auto",
    progress: ProgressCallback | None = None,
) -> Path | list[Path]:
    """Convierte un archivo, URL, ZIP o carpeta a Markdown.

    Devuelve una ruta (.md) o una lista de rutas si el origen es lote.
    """
    if ocr_mode not in {"auto", "always", "never"}:
        raise ValueError("ocr_mode debe ser auto, always o never.")

    src = str(source).strip()
    if is_url(src):
        out = Path(output).expanduser().resolve() if output else Path.cwd() / "url_page.md"
        if out.suffix.lower() != ".md":
            out = out / "url_page.md" if out.exists() and out.is_dir() else out.with_suffix(".md")
        if progress:
            progress("Convirtiendo URL…")
        result = convert_url(src, md_path=out, progress=progress)
        return write_markdown(out, result)

    path = Path(src).expanduser().resolve()
    detected = detect_path(path)

    if detected.kind == "folder":
        out_dir = Path(output).expanduser().resolve() if output else path / "_markdown"
        return convert_folder(path, out_dir, ocr_mode=ocr_mode, progress=progress)

    if detected.kind == "zip":
        out_dir = Path(output).expanduser().resolve() if output else path.with_suffix("") / "_markdown"
        return convert_zip(path, out_dir, ocr_mode=ocr_mode, progress=progress)

    if detected.kind not in CONVERTIBLE_KINDS:
        raise UnsupportedFormatError(
            f"Tipo detectado «{detected.label}» no es convertible de forma individual."
        )

    out = Path(output).expanduser().resolve() if output else path.with_suffix(".md")
    if out.is_dir():
        out = out / f"{path.stem}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    if progress:
        progress(f"Tipo detectado: {detected.label} ({detected.confidence})")
    result = convert_detected(
        path, detected, md_path=out, ocr_mode=ocr_mode, progress=progress
    )
    written = write_markdown(out, result)
    if progress:
        progress("Conversión terminada.")
    return written


def convert_folder(
    folder: Path,
    out_dir: Path,
    *,
    ocr_mode: str = "auto",
    progress: ProgressCallback | None = None,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = [p for p in sorted(folder.rglob("*")) if p.is_file()]
    # Evitar convertir la propia salida si está dentro.
    files = [p for p in files if out_dir.resolve() not in p.resolve().parents and p.resolve() != out_dir.resolve()]
    results: list[Path] = []
    errors: list[str] = []
    total = len(files)
    for i, file_path in enumerate(files, start=1):
        rel = file_path.relative_to(folder)
        if progress:
            progress(f"Lote carpeta {i}/{total}: {rel}")
        try:
            detected = detect_path(file_path)
            if detected.kind not in CONVERTIBLE_KINDS:
                continue
            target = out_dir / rel.with_suffix(".md")
            target.parent.mkdir(parents=True, exist_ok=True)
            result = convert_detected(
                file_path, detected, md_path=target, ocr_mode=ocr_mode, progress=progress
            )
            results.append(write_markdown(target, result))
        except UnsupportedFormatError:
            continue
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel}: {exc}")
    if not results:
        detail = "; ".join(errors[:5]) if errors else "no había archivos soportados"
        raise RuntimeError(f"No se pudo convertir ningún archivo de la carpeta ({detail}).")
    if progress:
        progress(f"Lote terminado: {len(results)} archivo(s).")
    return results


def convert_zip(
    zip_path: Path,
    out_dir: Path,
    *,
    ocr_mode: str = "auto",
    progress: ProgressCallback | None = None,
) -> list[Path]:
    if progress:
        progress("Extrayendo ZIP…")
    with tempfile.TemporaryDirectory(prefix="k3d_zip_") as tmp:
        tmp_path = Path(tmp)
        try:
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(tmp_path)
        except zipfile.BadZipFile as exc:
            raise UnsupportedFormatError(f"ZIP inválido o dañado: {zip_path.name}") from exc
        return convert_folder(tmp_path, out_dir, ocr_mode=ocr_mode, progress=progress)


# Compatibilidad con la API anterior.
def pdf_to_markdown(
    pdf_path: str | Path,
    md_path: str | Path | None = None,
    *,
    ocr_mode: str = "auto",
    progress: ProgressCallback | None = None,
) -> Path:
    result = convert_to_markdown(pdf_path, md_path, ocr_mode=ocr_mode, progress=progress)
    if isinstance(result, list):
        if not result:
            raise RuntimeError("No se generó ningún Markdown.")
        return result[0]
    return result
