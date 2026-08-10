"""Convertidor multi-formato → Markdown con interfaz gráfica para Windows."""

from __future__ import annotations

import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter import convert_to_markdown
from detect import UnsupportedFormatError

APP_NAME = "file2md"
APP_AUTHOR_BRAND = "K3D Technology"
APP_AUTHOR_NAME = "Ricardo Pena"
APP_VERSION = "2.2"

PAYPAL_URL = "https://www.paypal.com/paypalme/RicardoVasquez329"

HOW_IT_WORKS = (
    "Cómo funciona: elige un archivo, una carpeta, un ZIP o pega una URL y pulsa "
    "Convertir. La app detecta el tipo real por el contenido (no solo por la extensión). "
    "Si hay texto (PDF, Word, Excel, HTML, etc.), lo convierte a Markdown GFM conservando "
    "títulos, listas y tablas. Si es un PDF o imagen sin texto, aplica OCR automáticamente. "
    "Las imágenes extraídas se guardan en una carpeta *_assets/ con rutas relativas, y cada "
    ".md incluye front-matter YAML (título, autor, fecha y formato de origen). "
    "Si el formato no se reconoce, verás un error claro en lugar de texto corrupto."
)

CREDITS_TEXT = f"""{APP_NAME} v{APP_VERSION}

Hecho por {APP_AUTHOR_BRAND}
Autor: {APP_AUTHOR_NAME}

Este programa usa software de código abierto:

• PyMuPDF / pymupdf4llm — AGPL-3.0
• python-docx — MIT
• python-pptx — MIT
• openpyxl — MIT
• odfpy — Apache-2.0
• striprtf — BSD
• markdownify — MIT
• ebooklib — AGPL-3.0
• extract-msg — GPL-3.0
• Pillow — HPND
• winocr / PyWinRT — MIT
• Python / Tkinter / PyInstaller

OCR: Windows.Media.Ocr (API de Microsoft Windows)

Agradecimientos a las comunidades open source.
"""

WELCOME_TEXT = (
    f"Bienvenido a {APP_NAME}\n\n"
    f"Hecho por {APP_AUTHOR_BRAND}\n"
    f"Autor: {APP_AUTHOR_NAME}\n\n"
    f"{HOW_IT_WORKS}\n\n"
    "Si te sirve la app, puedes apoyar el proyecto con PayPal."
)

FILE_TYPES = [
    (
        "Documentos soportados",
        "*.pdf *.docx *.pptx *.xlsx *.odt *.rtf *.txt *.csv *.tsv "
        "*.json *.html *.htm *.epub *.eml *.msg *.png *.jpg *.jpeg *.tif *.tiff *.zip",
    ),
    ("PDF", "*.pdf"),
    ("Office / ODF", "*.docx *.pptx *.xlsx *.odt *.rtf"),
    ("Texto / datos", "*.txt *.csv *.tsv *.json"),
    ("Web / libros / correo", "*.html *.htm *.epub *.eml *.msg"),
    ("Imágenes", "*.png *.jpg *.jpeg *.tif *.tiff"),
    ("ZIP", "*.zip"),
    ("Todos", "*.*"),
]


class DocMarkdownApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} — {APP_AUTHOR_BRAND}")
        self.minsize(620, 560)
        self.geometry("720x600")
        self.configure(bg="#f3f4f6")

        self.source_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Selecciona un archivo, carpeta, ZIP o URL.")
        self.force_ocr_var = tk.BooleanVar(value=False)
        self._busy = False

        self._build_menu()
        self._build_ui()
        self._center()
        self.after(120, self._show_welcome)

    def _center(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Donar con PayPal…", command=self._open_paypal)
        help_menu.add_separator()
        help_menu.add_command(label="Cómo funciona…", command=self._show_how_it_works)
        help_menu.add_command(label="Créditos open source…", command=self._show_credits)
        help_menu.add_command(label="Acerca de…", command=self._show_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        self.config(menu=menubar)

    def _build_ui(self) -> None:
        pad = {"padx": 16, "pady": 8}
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)

        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")

        ttk.Label(root, text="file2md", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", pady=(0, 2)
        )
        ttk.Label(
            root,
            text=f"Hecho por {APP_AUTHOR_BRAND} · {APP_AUTHOR_NAME}",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 8))
        ttk.Label(root, text=HOW_IT_WORKS, font=("Segoe UI", 9), wraplength=660, justify="left").pack(
            anchor="w", fill="x", pady=(0, 12)
        )

        src_row = ttk.Frame(root)
        src_row.pack(fill="x", **pad)
        ttk.Label(src_row, text="Origen", width=14).pack(side="left")
        ttk.Entry(src_row, textvariable=self.source_var).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        ttk.Button(src_row, text="Archivo…", command=self._pick_file).pack(side="left", padx=(0, 4))
        ttk.Button(src_row, text="Carpeta…", command=self._pick_folder).pack(side="left")

        out_row = ttk.Frame(root)
        out_row.pack(fill="x", **pad)
        ttk.Label(out_row, text="Salida .md", width=14).pack(side="left")
        ttk.Entry(out_row, textvariable=self.out_var).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        ttk.Button(out_row, text="Examinar…", command=self._pick_out).pack(side="left")

        ttk.Label(
            root,
            text="También puedes pegar una URL https://… en Origen.",
            font=("Segoe UI", 8),
        ).pack(anchor="w")

        ttk.Checkbutton(
            root,
            text="Forzar OCR (PDF/imagen escaneados)",
            variable=self.force_ocr_var,
        ).pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(16, 8))
        self.convert_btn = ttk.Button(actions, text="Convertir", command=self._start_convert)
        self.convert_btn.pack(side="left")
        ttk.Button(actions, text="Limpiar", command=self._clear).pack(side="left", padx=8)
        ttk.Button(actions, text="Donar con PayPal", command=self._open_paypal).pack(side="right")

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", pady=(8, 4))
        ttk.Label(root, textvariable=self.status_var, font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))
        ttk.Label(
            root,
            text=f"© {APP_AUTHOR_BRAND} — {APP_AUTHOR_NAME}",
            font=("Segoe UI", 8),
        ).pack(anchor="e", pady=(12, 0))

    def _pick_file(self) -> None:
        path = filedialog.askopenfilename(title="Seleccionar archivo", filetypes=FILE_TYPES)
        if not path:
            return
        self.source_var.set(path)
        p = Path(path)
        if p.suffix.lower() == ".zip":
            self.out_var.set(str(p.with_suffix("")) + "_markdown")
        else:
            self.out_var.set(str(p.with_suffix(".md")))
        self.status_var.set("Origen listo. Pulsa Convertir.")

    def _pick_folder(self) -> None:
        path = filedialog.askdirectory(title="Seleccionar carpeta")
        if not path:
            return
        self.source_var.set(path)
        self.out_var.set(str(Path(path) / "_markdown"))
        self.status_var.set("Carpeta lista. Pulsa Convertir.")

    def _pick_out(self) -> None:
        source = self.source_var.get().strip()
        if source and (Path(source).is_dir() or source.lower().endswith(".zip")):
            path = filedialog.askdirectory(title="Carpeta de salida")
            if path:
                self.out_var.set(path)
            return
        initial = self.out_var.get().strip() or "salida.md"
        path = filedialog.asksaveasfilename(
            title="Guardar Markdown",
            defaultextension=".md",
            initialfile=Path(initial).name,
            filetypes=[("Markdown", "*.md"), ("Todos", "*.*")],
        )
        if path:
            self.out_var.set(path)

    def _clear(self) -> None:
        if self._busy:
            return
        self.source_var.set("")
        self.out_var.set("")
        self.force_ocr_var.set(False)
        self.status_var.set("Selecciona un archivo, carpeta, ZIP o URL.")

    def _start_convert(self) -> None:
        if self._busy:
            return
        source = self.source_var.get().strip()
        out = self.out_var.get().strip() or None
        if not source:
            messagebox.showwarning("Falta el origen", "Selecciona un archivo/carpeta o pega una URL.")
            return

        ocr_mode = "always" if self.force_ocr_var.get() else "auto"
        self._busy = True
        self.convert_btn.configure(state="disabled")
        self.progress.start(12)
        self.status_var.set("Convirtiendo…")
        threading.Thread(
            target=self._convert_worker,
            args=(source, out, ocr_mode),
            daemon=True,
        ).start()

    def _convert_worker(self, source: str, out: str | None, ocr_mode: str) -> None:
        try:
            result = convert_to_markdown(
                source,
                out,
                ocr_mode=ocr_mode,
                progress=lambda msg: self.after(0, lambda m=msg: self.status_var.set(m)),
            )
        except UnsupportedFormatError as exc:
            self.after(0, lambda: self._on_error(str(exc)))
            return
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self._on_error(str(exc)))
            return
        self.after(0, lambda: self._on_success(result))

    def _on_success(self, result: Path | list[Path]) -> None:
        self._busy = False
        self.progress.stop()
        self.convert_btn.configure(state="normal")
        if isinstance(result, list):
            folder = result[0].parent if result else Path.cwd()
            self.out_var.set(str(folder))
            self.status_var.set(f"Listo: {len(result)} archivo(s) en {folder}")
            msg = f"Se generaron {len(result)} archivos Markdown en:\n{folder}\n\n¿Abrir la carpeta?"
            open_path = folder
        else:
            self.out_var.set(str(result))
            self.status_var.set(f"Listo: {result}")
            msg = f"Se guardó:\n{result}\n\n¿Abrir la carpeta?"
            open_path = result.parent
        if messagebox.askyesno("Conversión completada", msg):
            try:
                import os

                os.startfile(open_path)  # type: ignore[attr-defined]
            except OSError:
                pass

    def _on_error(self, message: str) -> None:
        self._busy = False
        self.progress.stop()
        self.convert_btn.configure(state="normal")
        self.status_var.set("Error en la conversión.")
        messagebox.showerror("Error", message)

    def _show_welcome(self) -> None:
        messagebox.showinfo(f"{APP_NAME} — {APP_AUTHOR_BRAND}", WELCOME_TEXT)

    def _show_how_it_works(self) -> None:
        messagebox.showinfo("Cómo funciona", HOW_IT_WORKS)

    def _open_paypal(self) -> None:
        webbrowser.open(PAYPAL_URL)

    def _show_about(self) -> None:
        messagebox.showinfo(
            "Acerca de",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            f"Hecho por {APP_AUTHOR_BRAND}\n"
            f"Autor: {APP_AUTHOR_NAME}\n\n"
            f"{HOW_IT_WORKS}\n\n"
            f"Apoya el proyecto: {PAYPAL_URL}",
        )

    def _show_credits(self) -> None:
        win = tk.Toplevel(self)
        win.title("Créditos open source")
        win.transient(self)
        win.grab_set()
        win.minsize(520, 420)
        win.geometry("560x480")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Créditos y licencias", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        text = tk.Text(frame, wrap="word", font=("Consolas", 9), height=22)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True, pady=(8, 8))
        scroll.pack(side="right", fill="y", pady=(8, 8))
        text.insert("1.0", CREDITS_TEXT)
        text.configure(state="disabled")
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=(0, 12))


def main() -> None:
    app = DocMarkdownApp()
    app.mainloop()


if __name__ == "__main__":
    main()
