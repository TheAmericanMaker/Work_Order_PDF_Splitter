"""Flask web application for the PDF splitter."""

import io
import logging
import os
import secrets
import shutil
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from flask import Flask, abort, flash, redirect, render_template, request, send_file, send_from_directory, url_for
from flask.typing import ResponseReturnValue
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from ..core import PDFSplitError, bundle_pages

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf"}
APP_TITLE = "Work Order PDF Splitter"
MAX_UPLOAD_BYTES = 16 * 1024 * 1024


def configure_logging() -> None:
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def resolve_runtime_path(base_dir: Path, configured_path: Optional[str], default_name: str) -> Path:
    raw_path = configured_path or default_name
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve()


def ensure_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)


def clear_directory(directory: Path) -> None:
    ensure_directory(directory)
    for entry in directory.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def list_output_files(output_dir: Path) -> list[str]:
    ensure_directory(output_dir)

    def sort_key(filename: str) -> tuple[int, str]:
        stem = Path(filename).stem
        try:
            return int(stem.split("_")[-1]), filename
        except ValueError:
            return 10**9, filename

    pdfs = [entry.name for entry in output_dir.iterdir() if entry.is_file() and entry.suffix.lower() == ".pdf"]
    return sorted(pdfs, key=sort_key)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(upload_dir: Path, original_filename: str, file_bytes: bytes) -> Path:
    safe_filename = secure_filename(original_filename)
    if not safe_filename:
        raise PDFSplitError("The uploaded filename is invalid.")

    suffix = Path(safe_filename).suffix.lower() or ".pdf"
    target_path = upload_dir / f"upload-{uuid4().hex}{suffix}"
    target_path.write_bytes(file_bytes)
    return target_path


def replace_outputs(input_pdf_path: Path, output_dir: Path) -> list[str]:
    ensure_directory(output_dir)
    temp_output_dir = Path(tempfile.mkdtemp(prefix="wo-split-", dir=str(output_dir.parent)))

    try:
        generated_temp_files = bundle_pages(input_pdf_path, temp_output_dir)
        generated_names = [Path(path).name for path in generated_temp_files]

        clear_directory(output_dir)
        for filename in generated_names:
            shutil.move(str(temp_output_dir / filename), str(output_dir / filename))

        return [str(output_dir / filename) for filename in generated_names]
    finally:
        shutil.rmtree(temp_output_dir, ignore_errors=True)


def build_zip_buffer(output_dir: Path, filenames: Iterable[str]) -> io.BytesIO:
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for filename in filenames:
            file_path = output_dir / filename
            zip_file.write(file_path, arcname=filename)
    buffer.seek(0)
    return buffer


def create_app(test_config: Optional[Mapping[str, Any]] = None) -> Flask:
    configure_logging()

    base_dir = Path(__file__).resolve().parents[3]
    upload_dir = resolve_runtime_path(base_dir, os.environ.get("UPLOAD_FOLDER"), "uploads")
    output_dir = resolve_runtime_path(base_dir, os.environ.get("OUTPUT_FOLDER"), "output")
    secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

    if "FLASK_SECRET_KEY" not in os.environ and test_config is None:
        logger.warning("FLASK_SECRET_KEY is not set. Using an ephemeral development key.")

    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        TITLE=APP_TITLE,
        MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
        UPLOAD_FOLDER=upload_dir,
        OUTPUT_FOLDER=output_dir,
    )

    if test_config:
        app.config.update(test_config)

    ensure_directory(Path(app.config["UPLOAD_FOLDER"]))
    ensure_directory(Path(app.config["OUTPUT_FOLDER"]))

    CSRFProtect(app)

    @app.route("/", methods=["GET", "POST"])
    def index() -> ResponseReturnValue:
        output_directory = Path(app.config["OUTPUT_FOLDER"])
        upload_directory = Path(app.config["UPLOAD_FOLDER"])

        if request.method == "POST":
            uploaded_file = request.files.get("file")
            if uploaded_file is None:
                flash("No file was uploaded.", "danger")
                return redirect(url_for("index"))

            filename = uploaded_file.filename or ""
            if not filename.strip():
                flash("Select a PDF file before submitting.", "danger")
                return redirect(url_for("index"))

            if not allowed_file(filename):
                flash("Only PDF files are supported.", "danger")
                return redirect(url_for("index"))

            file_bytes = uploaded_file.read()
            clear_directory(upload_directory)

            try:
                input_pdf_path = save_upload(upload_directory, filename, file_bytes)
                output_files = replace_outputs(input_pdf_path, output_directory)
            except (FileNotFoundError, PDFSplitError) as exc:
                logger.warning("Upload processing failed: %s", exc)
                flash(str(exc), "danger")
            except Exception:
                logger.exception("Unexpected error while processing upload")
                flash("An unexpected error occurred while processing the PDF.", "danger")
            else:
                flash(f"Split complete. Generated {len(output_files)} file(s).", "success")
            finally:
                clear_directory(upload_directory)

            return redirect(url_for("index"))

        return render_template(
            "index.html",
            error_message=None,
            output_files=list_output_files(output_directory),
            title=app.config["TITLE"],
        )

    @app.get("/download/<filename>")
    def download_file(filename: str) -> ResponseReturnValue:
        if filename != Path(filename).name or not filename.lower().endswith(".pdf"):
            abort(404)

        output_directory = Path(app.config["OUTPUT_FOLDER"])
        file_path = output_directory / filename
        if not file_path.exists() or not file_path.is_file():
            abort(404)

        return send_from_directory(str(output_directory), filename, as_attachment=True)

    @app.get("/download-all")
    def download_all() -> ResponseReturnValue:
        output_directory = Path(app.config["OUTPUT_FOLDER"])
        output_files = list_output_files(output_directory)
        if not output_files:
            flash("There are no output files to download.", "warning")
            return redirect(url_for("index"))

        zip_buffer = build_zip_buffer(output_directory, output_files)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="work-orders.zip",
        )

    @app.post("/delete")
    def delete_files() -> ResponseReturnValue:
        clear_directory(Path(app.config["UPLOAD_FOLDER"]))
        clear_directory(Path(app.config["OUTPUT_FOLDER"]))
        flash("Cleared uploaded and generated files.", "success")
        return redirect(url_for("index"))

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(_error: RequestEntityTooLarge) -> ResponseReturnValue:
        return (
            render_template(
                "index.html",
                error_message="The selected file is too large. The maximum upload size is 16 MB.",
                output_files=list_output_files(Path(app.config["OUTPUT_FOLDER"])),
                title=app.config["TITLE"],
            ),
            413,
        )

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error: CSRFError) -> ResponseReturnValue:
        logger.warning("CSRF validation failed: %s", error.description)
        return (
            render_template(
                "index.html",
                error_message="Your session expired or the request was invalid. Refresh the page and try again.",
                output_files=list_output_files(Path(app.config["OUTPUT_FOLDER"])),
                title=app.config["TITLE"],
            ),
            400,
        )

    return app


def main() -> None:
    app = create_app()
    debug = os.environ.get("FLASK_ENV", "").lower() == "development"
    app.run(debug=debug)


if __name__ == "__main__":
    main()
