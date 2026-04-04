import re
import sys
from importlib import import_module
from pathlib import Path

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

create_app = import_module("work_order_splitter.web").create_app


def create_pdf(target_path: Path, page_texts: list[str]) -> Path:
    pdf = canvas.Canvas(str(target_path), pagesize=letter)
    for text in page_texts:
        if text:
            pdf.drawString(72, 720, text)
        pdf.showPage()
    pdf.save()
    return target_path


@pytest.fixture
def sample_work_order_pdf(tmp_path: Path) -> Path:
    return create_pdf(
        tmp_path / "sample.pdf",
        ["page 1", "page 2", "page 1", "page 2", "page 3"],
    )


@pytest.fixture
def mixed_marker_pdf(tmp_path: Path) -> Path:
    return create_pdf(
        tmp_path / "mixed.pdf",
        ["page 1", "work order detail with no marker", "page 1"],
    )


@pytest.fixture
def app(tmp_path: Path):
    upload_dir = tmp_path / "uploads"
    output_dir = tmp_path / "output"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "UPLOAD_FOLDER": upload_dir,
            "OUTPUT_FOLDER": output_dir,
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def csrf_token(client) -> str:
    response = client.get("/")
    html = response.get_data(as_text=True)
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)
