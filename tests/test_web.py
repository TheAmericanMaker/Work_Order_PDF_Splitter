from io import BytesIO
from pathlib import Path


def test_index_loads(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Work Order PDF Splitter" in response.get_data(as_text=True)


def test_upload_generates_output_files(client, csrf_token, sample_work_order_pdf: Path) -> None:
    response = client.post(
        "/",
        data={
            "csrf_token": csrf_token,
            "file": (BytesIO(sample_work_order_pdf.read_bytes()), "sample.pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Split complete. Generated 2 file(s)." in body
    assert "output_1.pdf" in body
    assert "output_2.pdf" in body


def test_download_single_file(client, csrf_token, sample_work_order_pdf: Path) -> None:
    client.post(
        "/",
        data={
            "csrf_token": csrf_token,
            "file": (BytesIO(sample_work_order_pdf.read_bytes()), "sample.pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    response = client.get("/download/output_1.pdf")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"


def test_download_all_returns_zip(client, csrf_token, sample_work_order_pdf: Path) -> None:
    client.post(
        "/",
        data={
            "csrf_token": csrf_token,
            "file": (BytesIO(sample_work_order_pdf.read_bytes()), "sample.pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    response = client.get("/download-all")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/zip"
    assert "work-orders.zip" in response.headers["Content-Disposition"]


def test_delete_clears_generated_files(client, csrf_token, sample_work_order_pdf: Path) -> None:
    client.post(
        "/",
        data={
            "csrf_token": csrf_token,
            "file": (BytesIO(sample_work_order_pdf.read_bytes()), "sample.pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    delete_token = client.get("/").get_data(as_text=True).split('name="csrf_token" value="')[1].split('"', 1)[0]
    response = client.post("/delete", data={"csrf_token": delete_token}, follow_redirects=True)

    assert response.status_code == 200
    assert "No split files are available yet." in response.get_data(as_text=True)


def test_post_without_csrf_token_is_rejected(client, sample_work_order_pdf: Path) -> None:
    response = client.post(
        "/",
        data={"file": (BytesIO(sample_work_order_pdf.read_bytes()), "sample.pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "Refresh the page and try again" in response.get_data(as_text=True)
