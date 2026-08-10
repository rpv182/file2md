"""file2md — multi-format → Markdown GUI for Windows."""

from __future__ import annotations

import json
import os
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter import convert_to_markdown
from detect import UnsupportedFormatError
from i18n import (
    APP_AUTHOR_BRAND,
    APP_AUTHOR_NAME,
    APP_NAME,
    APP_VERSION,
    DEFAULT_LANG,
    LANG_OPTIONS,
    PAYPAL_URL,
    about_text,
    credits_text,
    file_types,
    normalize_lang,
    t,
    welcome_text,
)


def _settings_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "file2md"
    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.json"


def load_language() -> str:
    path = _settings_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return normalize_lang(str(data.get("language", DEFAULT_LANG)))
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return DEFAULT_LANG


def save_language(lang: str) -> None:
    path = _settings_path()
    path.write_text(
        json.dumps({"language": normalize_lang(lang)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class DocMarkdownApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.lang = load_language()
        self.title(f"{APP_NAME} — {APP_AUTHOR_BRAND}")
        self.minsize(640, 600)
        self.geometry("740x640")
        self.configure(bg="#f3f4f6")

        self.source_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.force_ocr_var = tk.BooleanVar(value=False)
        self.lang_var = tk.StringVar(value=self._lang_label(self.lang))
        self._busy = False
        self._widgets: dict[str, tk.Widget] = {}

        self._build_menu()
        self._build_ui()
        self._apply_language()
        self._center()
        self.after(120, self._show_welcome)

    def _lang_label(self, code: str) -> str:
        code = normalize_lang(code)
        for value, label in LANG_OPTIONS:
            if value == code:
                return label
        return LANG_OPTIONS[0][1]

    def _lang_code_from_label(self, label: str) -> str:
        for value, name in LANG_OPTIONS:
            if name == label:
                return value
        return DEFAULT_LANG

    def _center(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_menu(self) -> None:
        self.menubar = tk.Menu(self)
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="Donate", command=self._open_paypal)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="How", command=self._show_how_it_works)
        self.help_menu.add_command(label="Credits", command=self._show_credits)
        self.help_menu.add_command(label="About", command=self._show_about)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.config(menu=self.menubar)

    def _build_ui(self) -> None:
        pad = {"padx": 16, "pady": 8}
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)
        self._root = root

        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")

        header = ttk.Frame(root)
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(side="left")

        lang_box = ttk.Frame(header)
        lang_box.pack(side="right")
        self._widgets["lang_label"] = ttk.Label(lang_box, text="Language")
        self._widgets["lang_label"].pack(side="left", padx=(0, 6))
        self._widgets["lang_combo"] = ttk.Combobox(
            lang_box,
            textvariable=self.lang_var,
            values=[label for _, label in LANG_OPTIONS],
            state="readonly",
            width=12,
        )
        self._widgets["lang_combo"].pack(side="left")
        self._widgets["lang_combo"].bind("<<ComboboxSelected>>", self._on_language_change)

        self._widgets["made_by"] = ttk.Label(root, text="", font=("Segoe UI", 9))
        self._widgets["made_by"].pack(anchor="w", pady=(0, 8))
        self._widgets["how"] = ttk.Label(
            root, text="", font=("Segoe UI", 9), wraplength=680, justify="left"
        )
        self._widgets["how"].pack(anchor="w", fill="x", pady=(0, 12))

        src_row = ttk.Frame(root)
        src_row.pack(fill="x", **pad)
        self._widgets["source_label"] = ttk.Label(src_row, text="Source", width=14)
        self._widgets["source_label"].pack(side="left")
        ttk.Entry(src_row, textvariable=self.source_var).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self._widgets["file_btn"] = ttk.Button(src_row, text="File…", command=self._pick_file)
        self._widgets["file_btn"].pack(side="left", padx=(0, 4))
        self._widgets["folder_btn"] = ttk.Button(src_row, text="Folder…", command=self._pick_folder)
        self._widgets["folder_btn"].pack(side="left")

        out_row = ttk.Frame(root)
        out_row.pack(fill="x", **pad)
        self._widgets["output_label"] = ttk.Label(out_row, text="Output", width=14)
        self._widgets["output_label"].pack(side="left")
        ttk.Entry(out_row, textvariable=self.out_var).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self._widgets["browse_btn"] = ttk.Button(out_row, text="Browse…", command=self._pick_out)
        self._widgets["browse_btn"].pack(side="left")

        self._widgets["url_hint"] = ttk.Label(root, text="", font=("Segoe UI", 8))
        self._widgets["url_hint"].pack(anchor="w")

        self._widgets["ocr_check"] = ttk.Checkbutton(
            root, text="Force OCR", variable=self.force_ocr_var
        )
        self._widgets["ocr_check"].pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(16, 8))
        self.convert_btn = ttk.Button(actions, text="Convert", command=self._start_convert)
        self.convert_btn.pack(side="left")
        self._widgets["clear_btn"] = ttk.Button(actions, text="Clear", command=self._clear)
        self._widgets["clear_btn"].pack(side="left", padx=8)
        self._widgets["donate_btn"] = ttk.Button(
            actions, text="Donate", command=self._open_paypal
        )
        self._widgets["donate_btn"].pack(side="right")

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", pady=(8, 4))
        ttk.Label(root, textvariable=self.status_var, font=("Segoe UI", 9)).pack(
            anchor="w", pady=(8, 0)
        )
        ttk.Label(
            root,
            text=f"© {APP_AUTHOR_BRAND} — {APP_AUTHOR_NAME}",
            font=("Segoe UI", 8),
        ).pack(anchor="e", pady=(12, 0))

    def _apply_language(self) -> None:
        lang = self.lang
        self._widgets["lang_label"].configure(text=t(lang, "language"))
        self._widgets["made_by"].configure(
            text=t(lang, "made_by", brand=APP_AUTHOR_BRAND, author=APP_AUTHOR_NAME)
        )
        self._widgets["how"].configure(text=t(lang, "how_it_works"))
        self._widgets["source_label"].configure(text=t(lang, "source"))
        self._widgets["output_label"].configure(text=t(lang, "output"))
        self._widgets["file_btn"].configure(text=t(lang, "file"))
        self._widgets["folder_btn"].configure(text=t(lang, "folder"))
        self._widgets["browse_btn"].configure(text=t(lang, "browse"))
        self._widgets["url_hint"].configure(text=t(lang, "url_hint"))
        self._widgets["ocr_check"].configure(text=t(lang, "force_ocr"))
        self.convert_btn.configure(text=t(lang, "convert"))
        self._widgets["clear_btn"].configure(text=t(lang, "clear"))
        self._widgets["donate_btn"].configure(text=t(lang, "donate"))

        self.help_menu.entryconfigure(0, label=t(lang, "donate_menu"))
        self.help_menu.entryconfigure(2, label=t(lang, "how_menu"))
        self.help_menu.entryconfigure(3, label=t(lang, "credits_menu"))
        self.help_menu.entryconfigure(4, label=t(lang, "about_menu"))
        self.menubar.entryconfigure(0, label=t(lang, "help"))

        if not self._busy:
            current = self.status_var.get().strip()
            idle_keys = {
                t("en", "status_idle"),
                t("es", "status_idle"),
                "",
            }
            if current in idle_keys:
                self.status_var.set(t(lang, "status_idle"))

    def _on_language_change(self, _event: object | None = None) -> None:
        new_lang = self._lang_code_from_label(self.lang_var.get())
        if new_lang == self.lang:
            return
        self.lang = new_lang
        save_language(self.lang)
        self._apply_language()

    def _pick_file(self) -> None:
        path = filedialog.askopenfilename(
            title=t(self.lang, "pick_file"),
            filetypes=file_types(self.lang),
        )
        if not path:
            return
        self.source_var.set(path)
        p = Path(path)
        if p.suffix.lower() == ".zip":
            self.out_var.set(str(p.with_suffix("")) + "_markdown")
        else:
            self.out_var.set(str(p.with_suffix(".md")))
        self.status_var.set(t(self.lang, "status_ready"))

    def _pick_folder(self) -> None:
        path = filedialog.askdirectory(title=t(self.lang, "pick_folder"))
        if not path:
            return
        self.source_var.set(path)
        self.out_var.set(str(Path(path) / "_markdown"))
        self.status_var.set(t(self.lang, "status_folder_ready"))

    def _pick_out(self) -> None:
        source = self.source_var.get().strip()
        if source and (Path(source).is_dir() or source.lower().endswith(".zip")):
            path = filedialog.askdirectory(title=t(self.lang, "pick_out_folder"))
            if path:
                self.out_var.set(path)
            return
        initial = self.out_var.get().strip() or "output.md"
        path = filedialog.asksaveasfilename(
            title=t(self.lang, "save_markdown"),
            defaultextension=".md",
            initialfile=Path(initial).name,
            filetypes=[
                (t(self.lang, "ft_markdown"), "*.md"),
                (t(self.lang, "ft_all"), "*.*"),
            ],
        )
        if path:
            self.out_var.set(path)

    def _clear(self) -> None:
        if self._busy:
            return
        self.source_var.set("")
        self.out_var.set("")
        self.force_ocr_var.set(False)
        self.status_var.set(t(self.lang, "status_idle"))

    def _start_convert(self) -> None:
        if self._busy:
            return
        source = self.source_var.get().strip()
        out = self.out_var.get().strip() or None
        if not source:
            messagebox.showwarning(
                t(self.lang, "missing_source_title"),
                t(self.lang, "missing_source_body"),
            )
            return

        ocr_mode = "always" if self.force_ocr_var.get() else "auto"
        self._busy = True
        self.convert_btn.configure(state="disabled")
        self.progress.start(12)
        self.status_var.set(t(self.lang, "status_converting"))
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
            self.status_var.set(
                t(self.lang, "status_done_many", count=len(result), folder=folder)
            )
            msg = t(self.lang, "done_many", count=len(result), folder=folder)
            open_path = folder
        else:
            self.out_var.set(str(result))
            self.status_var.set(t(self.lang, "status_done_one", path=result))
            msg = t(self.lang, "done_one", path=result)
            open_path = result.parent
        if messagebox.askyesno(t(self.lang, "done_title"), msg):
            try:
                os.startfile(open_path)  # type: ignore[attr-defined]
            except OSError:
                pass

    def _on_error(self, message: str) -> None:
        self._busy = False
        self.progress.stop()
        self.convert_btn.configure(state="normal")
        self.status_var.set(t(self.lang, "status_error"))
        messagebox.showerror(t(self.lang, "error"), message)

    def _show_welcome(self) -> None:
        messagebox.showinfo(f"{APP_NAME} — {APP_AUTHOR_BRAND}", welcome_text(self.lang))

    def _show_how_it_works(self) -> None:
        messagebox.showinfo(t(self.lang, "how_title"), t(self.lang, "how_it_works"))

    def _open_paypal(self) -> None:
        webbrowser.open(PAYPAL_URL)

    def _show_about(self) -> None:
        messagebox.showinfo(t(self.lang, "about_title"), about_text(self.lang))

    def _show_credits(self) -> None:
        win = tk.Toplevel(self)
        win.title(t(self.lang, "credits_title"))
        win.transient(self)
        win.grab_set()
        win.minsize(520, 420)
        win.geometry("560x480")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(
            frame, text=t(self.lang, "credits_heading"), font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")
        text = tk.Text(frame, wrap="word", font=("Consolas", 9), height=22)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True, pady=(8, 8))
        scroll.pack(side="right", fill="y", pady=(8, 8))
        text.insert("1.0", credits_text(self.lang))
        text.configure(state="disabled")
        ttk.Button(win, text=t(self.lang, "close"), command=win.destroy).pack(pady=(0, 12))


def main() -> None:
    app = DocMarkdownApp()
    app.mainloop()


if __name__ == "__main__":
    main()
