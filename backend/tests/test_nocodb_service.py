from typing import Any

import pytest
from pytest_mock import MockerFixture

from app.services.nocodb import (
    COURT_DECISIONS_JURISDICTIONS_FIELD_ID,
    COURT_DECISIONS_PDF_FIELD_ID,
    COURT_DECISIONS_TABLE_ID,
    JURISDICTIONS_TABLE_ID,
    NocoDBService,
)


@pytest.mark.parametrize("alpha_code_key", ["Alpha-3 Code", "Alpha_3_Code"])
def test_list_jurisdictions_accepts_api_title_and_physical_column_name(
    mocker: MockerFixture,
    alpha_code_key: str,
) -> None:
    rows: list[dict[str, Any]] = [
        {
            "Id": 42,
            alpha_code_key: "GTM",
            "Name": "Guatemala",
        }
    ]
    service = NocoDBService.__new__(NocoDBService)
    list_rows = mocker.patch.object(service, "list_rows", return_value=rows)

    assert service.list_jurisdictions("GTM") == [42]
    list_rows.assert_called_once_with(JURISDICTIONS_TABLE_ID, limit=1000)


def test_list_rows_uses_v2_table_id_endpoint(mocker: MockerFixture) -> None:
    response = mocker.Mock()
    response.json.return_value = {
        "list": [{"Id": 42, "Alpha-3 Code": "GTM"}],
        "pageInfo": {"isLastPage": True},
    }
    service = NocoDBService(
        "https://nocodb.example/api/v1/db/data/noco/p1q5x3pj29vkrdr",
        "token",
    )
    service.session = mocker.Mock()
    service.session.get.return_value = response

    assert service.list_rows(JURISDICTIONS_TABLE_ID) == [{"Id": 42, "Alpha-3 Code": "GTM"}]
    service.session.get.assert_called_once_with(
        f"https://nocodb.example/api/v2/tables/{JURISDICTIONS_TABLE_ID}/records",
        headers={"xc-token": "token"},
        params={"limit": 100, "offset": 0},
    )


def test_create_and_read_use_v2_table_endpoint(mocker: MockerFixture) -> None:
    create_response = mocker.Mock()
    create_response.json.return_value = {"Id": 7}
    create_response.text = ""
    read_response = mocker.Mock()
    read_response.json.return_value = {"Id": 7, "Case Citation": "Example"}
    read_response.text = ""
    service = NocoDBService(
        "https://nocodb.example/api/v1/db/data/noco/p1q5x3pj29vkrdr",
        "token",
    )
    service.session = mocker.Mock()
    service.session.post.return_value = create_response
    service.session.get.return_value = read_response

    assert service.create_row(COURT_DECISIONS_TABLE_ID, {"Case Citation": "Example"}) == {"Id": 7}
    assert service.get_row(COURT_DECISIONS_TABLE_ID, "7") == {"Id": 7, "Case Citation": "Example"}
    service.session.post.assert_called_once_with(
        f"https://nocodb.example/api/v2/tables/{COURT_DECISIONS_TABLE_ID}/records",
        headers={"xc-token": "token"},
        json={"Case Citation": "Example"},
    )
    service.session.get.assert_called_once_with(
        f"https://nocodb.example/api/v2/tables/{COURT_DECISIONS_TABLE_ID}/records/7",
        headers={"xc-token": "token"},
    )


def test_link_records_uses_named_table_and_field_ids(mocker: MockerFixture) -> None:
    response = mocker.Mock()
    response.json.return_value = {"success": True}
    response.text = ""
    service = NocoDBService("https://nocodb.example", "token")
    service.session = mocker.Mock()
    service.session.post.return_value = response

    assert service.link_records(
        COURT_DECISIONS_TABLE_ID,
        7,
        COURT_DECISIONS_JURISDICTIONS_FIELD_ID,
        [42],
    ) == {"success": True}
    service.session.post.assert_called_once_with(
        "https://nocodb.example/api/v2/tables/"
        f"{COURT_DECISIONS_TABLE_ID}/links/{COURT_DECISIONS_JURISDICTIONS_FIELD_ID}/records/7",
        headers={"xc-token": "token"},
        json=[{"Id": 42}],
    )


def test_upload_file_updates_named_attachment_field(mocker: MockerFixture) -> None:
    upload_response = mocker.Mock()
    upload_response.json.return_value = [{"url": "download/noco/example.pdf"}]
    upload_response.text = ""
    update_response = mocker.Mock()
    update_response.json.return_value = {"Id": 7}
    update_response.text = ""
    service = NocoDBService("https://nocodb.example", "token")
    service.session = mocker.Mock()
    service.session.post.return_value = upload_response
    service.session.patch.return_value = update_response
    mocker.patch.object(service, "get_row", return_value={"Official Source (PDF)": []})

    assert service.upload_file(
        COURT_DECISIONS_TABLE_ID,
        7,
        COURT_DECISIONS_PDF_FIELD_ID,
        b"pdf",
        "example.pdf",
        field_name="Official Source (PDF)",
    ) == {"Id": 7}
    service.session.patch.assert_called_once_with(
        f"https://nocodb.example/api/v2/tables/{COURT_DECISIONS_TABLE_ID}/records/7",
        headers={"xc-token": "token"},
        json={"Official Source (PDF)": [{"url": "download/noco/example.pdf"}]},
    )
