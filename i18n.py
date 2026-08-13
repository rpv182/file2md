"""UI strings for file2md (English default, Spanish optional)."""

from __future__ import annotations

from typing import Any

APP_NAME = "file2md"
APP_AUTHOR_BRAND = "K3D Technology"
APP_AUTHOR_NAME = "Ricardo Pena"
APP_VERSION = "2.3.1"
PAYPAL_URL = "https://www.paypal.com/paypalme/RicardoVasquez329"

DEFAULT_LANG = "en"
LANG_OPTIONS = (("en", "English"), ("es", "Español"))

_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "made_by": "Made by {brand} · {author}",
        "how_it_works": (
            "How it works: choose a file, folder, ZIP, or paste a URL and click Convert. "
            "The app detects the real type from content (not only the extension). "
            "If there is text (PDF, Word, Excel, HTML, etc.), it converts it to GFM Markdown "
            "keeping headings, lists, and tables. If a PDF or image has no text layer, OCR "
            "runs automatically. Extracted images go into a *_assets/ folder with relative "
            "paths, and each .md file includes YAML front-matter (title, author, date, and "
            "source format). If a format is not recognized, you get a clear error instead of "
            "corrupted text."
        ),
        "welcome": (
            "Welcome to {app}\n\n"
            "Made by {brand}\n"
            "Author: {author}\n\n"
            "{how}\n\n"
            "If you find the app useful, you can support the project with PayPal."
        ),
        "credits": (
            "{app} v{version}\n\n"
            "Made by {brand}\n"
            "Author: {author}\n\n"
            "This program uses open-source software:\n\n"
            "• PyMuPDF / pymupdf4llm — AGPL-3.0\n"
            "• python-docx — MIT\n"
            "• python-pptx — MIT\n"
            "• openpyxl — MIT\n"
            "• odfpy — Apache-2.0\n"
            "• striprtf — BSD\n"
            "• markdownify — MIT\n"
            "• ebooklib — AGPL-3.0\n"
            "• extract-msg — GPL-3.0\n"
            "• Pillow — HPND\n"
            "• winocr / PyWinRT — MIT\n"
            "• Python / Tkinter / PyInstaller\n\n"
            "OCR: Windows.Media.Ocr (Microsoft Windows API)\n\n"
            "Thanks to the open-source communities."
        ),
        "language": "Language",
        "source": "Source",
        "output": "Output .md",
        "file": "File…",
        "folder": "Folder…",
        "browse": "Browse…",
        "url_hint": "You can also paste an https://… URL in Source.",
        "force_ocr": "Force OCR (scanned PDF/image)",
        "convert": "Convert",
        "clear": "Clear",
        "donate": "Donate with PayPal",
        "help": "Help",
        "donate_menu": "Donate with PayPal…",
        "how_menu": "How it works…",
        "credits_menu": "Open-source credits…",
        "about_menu": "About…",
        "status_idle": "Select a file, folder, ZIP, or URL.",
        "status_ready": "Source ready. Click Convert.",
        "status_folder_ready": "Folder ready. Click Convert.",
        "status_converting": "Converting…",
        "status_error": "Conversion error.",
        "status_done_one": "Done: {path}",
        "status_done_many": "Done: {count} file(s) in {folder}",
        "pick_file": "Select file",
        "pick_folder": "Select folder",
        "pick_out_folder": "Output folder",
        "save_markdown": "Save Markdown",
        "missing_source_title": "Source missing",
        "missing_source_body": "Select a file/folder or paste a URL.",
        "done_title": "Conversion complete",
        "done_one": "Saved:\n{path}\n\nOpen the folder?",
        "done_many": "Created {count} Markdown files in:\n{folder}\n\nOpen the folder?",
        "error": "Error",
        "how_title": "How it works",
        "about_title": "About",
        "about_body": (
            "{app} v{version}\n\n"
            "Made by {brand}\n"
            "Author: {author}\n\n"
            "{how}\n\n"
            "Support the project: {paypal}"
        ),
        "credits_title": "Open-source credits",
        "credits_heading": "Credits and licenses",
        "close": "Close",
        "ft_supported": "Supported documents",
        "ft_pdf": "PDF",
        "ft_office": "Office / ODF",
        "ft_text": "Text / data",
        "ft_web": "Web / books / mail",
        "ft_images": "Images",
        "ft_zip": "ZIP",
        "ft_all": "All",
        "ft_markdown": "Markdown",
        "made_by_short": "Made by",
        "author_label": "Author",
    },
    "es": {
        "made_by": "Hecho por {brand} · {author}",
        "how_it_works": (
            "Cómo funciona: elige un archivo, una carpeta, un ZIP o pega una URL y pulsa "
            "Convertir. La app detecta el tipo real por el contenido (no solo por la extensión). "
            "Si hay texto (PDF, Word, Excel, HTML, etc.), lo convierte a Markdown GFM conservando "
            "títulos, listas y tablas. Si es un PDF o imagen sin texto, aplica OCR automáticamente. "
            "Las imágenes extraídas se guardan en una carpeta *_assets/ con rutas relativas, y cada "
            ".md incluye front-matter YAML (título, autor, fecha y formato de origen). "
            "Si el formato no se reconoce, verás un error claro en lugar de texto corrupto."
        ),
        "welcome": (
            "Bienvenido a {app}\n\n"
            "Hecho por {brand}\n"
            "Autor: {author}\n\n"
            "{how}\n\n"
            "Si te sirve la app, puedes apoyar el proyecto con PayPal."
        ),
        "credits": (
            "{app} v{version}\n\n"
            "Hecho por {brand}\n"
            "Autor: {author}\n\n"
            "Este programa usa software de código abierto:\n\n"
            "• PyMuPDF / pymupdf4llm — AGPL-3.0\n"
            "• python-docx — MIT\n"
            "• python-pptx — MIT\n"
            "• openpyxl — MIT\n"
            "• odfpy — Apache-2.0\n"
            "• striprtf — BSD\n"
            "• markdownify — MIT\n"
            "• ebooklib — AGPL-3.0\n"
            "• extract-msg — GPL-3.0\n"
            "• Pillow — HPND\n"
            "• winocr / PyWinRT — MIT\n"
            "• Python / Tkinter / PyInstaller\n\n"
            "OCR: Windows.Media.Ocr (API de Microsoft Windows)\n\n"
            "Agradecimientos a las comunidades open source."
        ),
        "language": "Idioma",
        "source": "Origen",
        "output": "Salida .md",
        "file": "Archivo…",
        "folder": "Carpeta…",
        "browse": "Examinar…",
        "url_hint": "También puedes pegar una URL https://… en Origen.",
        "force_ocr": "Forzar OCR (PDF/imagen escaneados)",
        "convert": "Convertir",
        "clear": "Limpiar",
        "donate": "Donar con PayPal",
        "help": "Ayuda",
        "donate_menu": "Donar con PayPal…",
        "how_menu": "Cómo funciona…",
        "credits_menu": "Créditos open source…",
        "about_menu": "Acerca de…",
        "status_idle": "Selecciona un archivo, carpeta, ZIP o URL.",
        "status_ready": "Origen listo. Pulsa Convertir.",
        "status_folder_ready": "Carpeta lista. Pulsa Convertir.",
        "status_converting": "Convirtiendo…",
        "status_error": "Error en la conversión.",
        "status_done_one": "Listo: {path}",
        "status_done_many": "Listo: {count} archivo(s) en {folder}",
        "pick_file": "Seleccionar archivo",
        "pick_folder": "Seleccionar carpeta",
        "pick_out_folder": "Carpeta de salida",
        "save_markdown": "Guardar Markdown",
        "missing_source_title": "Falta el origen",
        "missing_source_body": "Selecciona un archivo/carpeta o pega una URL.",
        "done_title": "Conversión completada",
        "done_one": "Se guardó:\n{path}\n\n¿Abrir la carpeta?",
        "done_many": "Se generaron {count} archivos Markdown en:\n{folder}\n\n¿Abrir la carpeta?",
        "error": "Error",
        "how_title": "Cómo funciona",
        "about_title": "Acerca de",
        "about_body": (
            "{app} v{version}\n\n"
            "Hecho por {brand}\n"
            "Autor: {author}\n\n"
            "{how}\n\n"
            "Apoya el proyecto: {paypal}"
        ),
        "credits_title": "Créditos open source",
        "credits_heading": "Créditos y licencias",
        "close": "Cerrar",
        "ft_supported": "Documentos soportados",
        "ft_pdf": "PDF",
        "ft_office": "Office / ODF",
        "ft_text": "Texto / datos",
        "ft_web": "Web / libros / correo",
        "ft_images": "Imágenes",
        "ft_zip": "ZIP",
        "ft_all": "Todos",
        "ft_markdown": "Markdown",
        "made_by_short": "Hecho por",
        "author_label": "Autor",
    },
}


def normalize_lang(code: str | None) -> str:
    if not code:
        return DEFAULT_LANG
    code = code.strip().lower()
    if code.startswith("es"):
        return "es"
    if code.startswith("en"):
        return "en"
    return DEFAULT_LANG


def t(lang: str, key: str, **kwargs: Any) -> str:
    lang = normalize_lang(lang)
    catalog = _STRINGS.get(lang) or _STRINGS[DEFAULT_LANG]
    template = catalog.get(key) or _STRINGS[DEFAULT_LANG].get(key) or key
    if kwargs:
        return template.format(**kwargs)
    return template


def file_types(lang: str) -> list[tuple[str, str]]:
    patterns = (
        "*.pdf *.docx *.pptx *.xlsx *.odt *.rtf *.txt *.csv *.tsv "
        "*.json *.html *.htm *.epub *.eml *.msg *.png *.jpg *.jpeg *.tif *.tiff *.zip"
    )
    return [
        (t(lang, "ft_supported"), patterns),
        (t(lang, "ft_pdf"), "*.pdf"),
        (t(lang, "ft_office"), "*.docx *.pptx *.xlsx *.odt *.rtf"),
        (t(lang, "ft_text"), "*.txt *.csv *.tsv *.json"),
        (t(lang, "ft_web"), "*.html *.htm *.epub *.eml *.msg"),
        (t(lang, "ft_images"), "*.png *.jpg *.jpeg *.tif *.tiff"),
        (t(lang, "ft_zip"), "*.zip"),
        (t(lang, "ft_all"), "*.*"),
    ]


def welcome_text(lang: str) -> str:
    how = t(lang, "how_it_works")
    return t(
        lang,
        "welcome",
        app=APP_NAME,
        brand=APP_AUTHOR_BRAND,
        author=APP_AUTHOR_NAME,
        how=how,
    )


def credits_text(lang: str) -> str:
    return t(
        lang,
        "credits",
        app=APP_NAME,
        version=APP_VERSION,
        brand=APP_AUTHOR_BRAND,
        author=APP_AUTHOR_NAME,
    )


def about_text(lang: str) -> str:
    return t(
        lang,
        "about_body",
        app=APP_NAME,
        version=APP_VERSION,
        brand=APP_AUTHOR_BRAND,
        author=APP_AUTHOR_NAME,
        how=t(lang, "how_it_works"),
        paypal=PAYPAL_URL,
    )
