# Work Order PDF Splitter

Split a large PDF containing multiple work orders into individual PDF files.

## What It Does

The splitter scans each page for a `page <number>` marker. When it finds a new `page 1` after pages have already been collected, it starts a new output PDF.

The project ships with two interfaces:

- A Flask web app for browser-based uploads and downloads
- A tkinter desktop app for local use without a server

## Features

- Shared core splitting logic used by both interfaces
- Safer file handling and input validation
- CSRF protection for the web app
- Structured logging instead of ad-hoc `print()` calls
- Unit and integration tests
- CI workflow for linting, type checking, and tests
- Docker support for the web interface

## Installation

### Runtime Install

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

### Development Install

```bash
python -m pip install -e ".[web,dev]"
```

## Configuration

Copy `.env.example` values into your environment if you need custom paths or a fixed Flask secret key.

Available environment variables:

- `FLASK_SECRET_KEY`
- `UPLOAD_FOLDER`
- `OUTPUT_FOLDER`
- `FLASK_ENV`

Defaults use local `uploads/` and `output/` folders in the project root.

## Running the Web App

```bash
python app.py
```

Then open `http://127.0.0.1:5000`.

## Running the Desktop App

```bash
python Work_Order_PDF_Splitter_V1.py
```

## CLI Usage

```bash
python bundle_pages.py input.pdf output
```

Or, after installation:

```bash
wo-split input.pdf output
```

## Testing

```bash
pytest
ruff check .
mypy src
```

## Docker

Build and run the web app with:

```bash
docker build -t work-order-pdf-splitter .
docker run --rm -p 5000:5000 work-order-pdf-splitter
```

## Project Layout

```text
.
├── app.py
├── bundle_pages.py
├── Work_Order_PDF_Splitter_V1.py
├── src/work_order_splitter/
│   ├── core.py
│   ├── gui.py
│   └── web/
├── templates/
├── static/
├── tests/
└── .github/workflows/ci.yml
```

## Notes

- The web app only replaces existing output files after a successful split.
- Pages without a detected page marker are preserved in the current output bundle.
- The desktop app and CLI both use the same shared core module.

## License

CC0 1.0 Universal.
