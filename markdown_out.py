"""Utilidades de salida Markdown (front-matter, assets, GFM)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ConversionResult:
    markdown_body: str
    title: str | None = None
    author: str | None = None
    date: str | None = None
    source_format: str = "unknown"
    source_name: str = ""
    extra_meta: dict[str, Any] = field(default_factory=dict)
    asset_files: list[Path] = field(default_factory=list)


def assets_dir_for(md_path: Path) -> Path:
    base = md_path.with_suffix("")
    return Path(f"{base}_assets") if base.name else md_path.parent / "assets"


def relative_asset_path(md_path: Path, asset_path: Path) -> str:
    try:
        return asset_path.resolve().relative_to(md_path.parent.resolve()).as_posix()
    except ValueError:
        return asset_path.name


def yaml_front_matter(result: ConversionResult) -> str:
    title = result.title or Path(result.source_name).stem or "Sin título"
    date = result.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = ["---", f"title: {_yaml_str(title)}"]
    if result.author:
        lines.append(f"author: {_yaml_str(result.author)}")
    lines.append(f"date: {_yaml_str(date)}")
    lines.append(f"source_format: {_yaml_str(result.source_format)}")
    if result.source_name:
        lines.append(f"source_file: {_yaml_str(result.source_name)}")
    for key, value in result.extra_meta.items():
        if value is None or value == "":
            continue
        lines.append(f"{key}: {_yaml_str(value)}")
    lines.append("---")
    return "\n".join(lines)


def write_markdown(md_path: Path, result: ConversionResult) -> Path:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    body = (result.markdown_body or "").strip()
    if not body:
        raise RuntimeError("La conversión no produjo contenido Markdown útil.")
    content = f"{yaml_front_matter(result)}\n\n{body}\n"
    md_path.write_text(content, encoding="utf-8")
    return md_path


def _yaml_str(value: Any) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if text == "":
        return '""'
    if re.search(r'[:#\[\]{},&*?|>!%@`"\']', text) or text.lower() in {"null", "true", "false"}:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def gfm_table(headers: list[str], rows: list[list[str]]) -> str:
    if not headers and not rows:
        return ""
    if not headers and rows:
        headers = [f"Columna {i}" for i in range(1, len(rows[0]) + 1)]
    headers = [_cell(h) for h in headers]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    width = len(headers)
    for row in rows:
        cells = [_cell(c) for c in row]
        if len(cells) < width:
            cells.extend([""] * (width - len(cells)))
        lines.append("| " + " | ".join(cells[:width]) + " |")
    return "\n".join(lines)


def _cell(value: Any) -> str:
    text = str(value if value is not None else "").replace("\n", " ").replace("|", "\\|").strip()
    return text


def heading(level: int, text: str) -> str:
    level = max(1, min(6, level))
    clean = re.sub(r"\s+", " ", text).strip()
    return f"{'#' * level} {clean}" if clean else ""
