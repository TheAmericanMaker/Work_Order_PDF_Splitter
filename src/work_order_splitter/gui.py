"""Tkinter desktop interface for the PDF splitter."""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .core import PDFSplitError, bundle_pages

logger = logging.getLogger(__name__)


class SplitterGUI:
    """Simple desktop interface for PDF splitting."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Work Order PDF Splitter")
        self.root.geometry("720x300")
        self.root.minsize(640, 280)

        base_dir = Path(__file__).resolve().parents[2]
        default_output = base_dir / "output"
        default_output.mkdir(parents=True, exist_ok=True)

        self.input_pdf_path = tk.StringVar()
        self.output_directory = tk.StringVar(value=str(default_output))
        self.status_message = tk.StringVar(value="Select a PDF to begin.")

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill="both", expand=True)

        container.columnconfigure(1, weight=1)

        title_label = ttk.Label(container, text="Work Order PDF Splitter", font=("Segoe UI", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        description_label = ttk.Label(
            container,
            text="Split bulk work-order PDFs into individual files using page number boundaries.",
            wraplength=620,
        )
        description_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 18))

        ttk.Label(container, text="Input PDF").grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(container, textvariable=self.input_pdf_path).grid(row=2, column=1, sticky="ew", padx=(12, 12))
        ttk.Button(container, text="Browse", command=self.browse_input_file).grid(row=2, column=2, sticky="ew")

        ttk.Label(container, text="Output Folder").grid(row=3, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(container, textvariable=self.output_directory).grid(row=3, column=1, sticky="ew", padx=(12, 12))
        ttk.Button(container, text="Browse", command=self.browse_output_folder).grid(row=3, column=2, sticky="ew")

        ttk.Button(container, text="Split PDF", command=self.process_pdf).grid(
            row=4, column=0, columnspan=3, sticky="ew", pady=(18, 12)
        )

        ttk.Label(container, textvariable=self.status_message, wraplength=620).grid(
            row=5, column=0, columnspan=3, sticky="w"
        )

    def browse_input_file(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.input_pdf_path.set(file_path)

    def browse_output_folder(self) -> None:
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_directory.set(folder_path)

    def process_pdf(self) -> None:
        input_pdf = Path(self.input_pdf_path.get()).expanduser()
        output_dir = Path(self.output_directory.get()).expanduser()

        if not input_pdf.exists() or not input_pdf.is_file():
            messagebox.showerror("Invalid Input", "Select a valid PDF file before processing.")
            return

        if input_pdf.suffix.lower() != ".pdf":
            messagebox.showerror("Invalid Input", "The selected file must be a PDF.")
            return

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_files = bundle_pages(input_pdf, output_dir)
        except FileNotFoundError as exc:
            logger.warning("Input PDF not found: %s", exc)
            messagebox.showerror("File Not Found", str(exc))
            return
        except PDFSplitError as exc:
            logger.warning("Split failed: %s", exc)
            messagebox.showerror("Split Failed", str(exc))
            return
        except Exception as exc:
            logger.exception("Unexpected desktop error")
            messagebox.showerror("Unexpected Error", str(exc))
            return

        message = f"Split complete. Generated {len(output_files)} file(s) in {output_dir}"
        self.status_message.set(message)
        messagebox.showinfo("Success", message)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    SplitterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
