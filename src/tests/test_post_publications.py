import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.model.publication import OrmPublication

from authentication import keycloak_openid


def test_happy_path(client: TestClient, engine: Engine, mocked_privileged_token):

    keycloak_openid.decode_token = mocked_privileged_token

    publications = [
        OrmPublication(
            title="pub1",
            doi="doi1",
            url="url1",
            platform="zenodo",
            platform_identifier="1",
        ),
        OrmPublication(
            title="pub1",
            doi="doi1",
            url="url1",
            platform="other_platform",
            platform_identifier="1",
        ),
        OrmPublication(
            title="pub2",
            doi="doi2",
            url="url2",
            platform="other_platform",
            platform_identifier="2",
        ),
    ]
    with Session(engine) as session:
        # Populate database
        session.add_all(publications)
        session.commit()

    response = client.post(
        "/publications/v0",
        json={
            "title": "pub2",
            "doi": "doi2",
            "url": "url2",
            "platform": "zenodo",
            "platformIdentifier": "2",
        },
        headers={"Authorization": "fake-token"},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["title"] == "pub2"
    assert response_json["doi"] == "doi2"
    assert response_json["platform"] == "zenodo"
    assert response_json["platformIdentifier"] == "2"
    assert response_json["identifier"] == 4
    assert len(response_json["datasets"]) == 0
    assert len(response_json) == 7


@pytest.mark.parametrize(
    "title",
    ["\"'é:?", "!@#$%^&*()`~", "Ω≈ç√∫˜µ≤≥÷", "田中さんにあげて下さい", " أي بعد, ", "𝑻𝒉𝒆 𝐪𝐮𝐢𝐜𝐤", "گچپژ"],
)
def test_unicode(client: TestClient, engine: Engine, title, mocked_privileged_token):

    keycloak_openid.decode_token = mocked_privileged_token

    response = client.post(
        "/publications/v0",
        json={"title": title, "doi": "doi2", "platform": "zenodo", "platform_identifier": "2"},
        headers={"Authorization": "fake-token"},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["title"] == title


def test_duplicated_publication(client: TestClient, engine: Engine, mocked_privileged_token):

    keycloak_openid.decode_token = mocked_privileged_token

    publications = [
        OrmPublication(title="pub1", doi="doi1", platform="zenodo", platform_identifier="1")
    ]
    with Session(engine) as session:
        # Populate database
        session.add_all(publications)
        session.commit()
    response = client.post(
        "/publications/v0",
        json={"title": "pub1", "doi": "doi1", "platform": "zenodo", "platform_identifier": "1"},
        headers={"Authorization": "fake-token"},
    )
    assert response.status_code == 409
    assert (
        response.json()["detail"] == "There already exists a publication with the same platform "
        "and name, with identifier=1."
    )


# Test if the api allows creating publications with not all fields
@pytest.mark.parametrize("field", ["title"])
def test_missing_value(client: TestClient, engine: Engine, field: str, mocked_privileged_token):

    keycloak_openid.decode_token = mocked_privileged_token

    data = {
        "title": "pub2",
        "doi": "doi2",
        "platform": "zenodo",
        "platformIdentifier": "2",
    }  # type: typing.Dict[str, typing.Any]
    del data[field]
    response = client.post("/publications/v0", json=data, headers={"Authorization": "fake-token"})
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"loc": ["body", field], "msg": "field required", "type": "value_error.missing"}
    ]


@pytest.mark.parametrize("field", ["title", "platform"])
def test_null_value(client: TestClient, engine: Engine, field: str, mocked_privileged_token):

    keycloak_openid.decode_token = mocked_privileged_token

    data = {
        "title": "pub2",
        "doi": "doi2",
        "platform": "zenodo",
        "platformIdentifier": "2",
    }  # type: typing.Dict[str, typing.Any]
    data[field] = None
    response = client.post("/publications/v0", json=data, headers={"Authorization": "fake-token"})
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {
            "loc": ["body", field],
            "msg": "none is not an allowed value",
            "type": "type_error.none.not_allowed",
        }
    ]


def test_unauthorized_user(client: TestClient, engine: Engine, mocked_token):

    keycloak_openid.decode_token = mocked_token

    response = client.post(
        "/publications/v0",
        json={"title": "title", "doi": "doi2", "platform": "zenodo", "platform_identifier": "2"},
        headers={"Authorization": "fake-token"},
    )
    assert response.status_code == 403
    response_json = response.json()
    assert response_json["detail"] == "You do not have permission to edit Aiod resources."


def test_unauthenticated_user(client: TestClient, engine: Engine):

    response = client.post(
        "/publications/v0",
        json={"title": "title", "doi": "doi2", "platform": "zenodo", "platform_identifier": "2"},
    )
    assert response.status_code == 401
    response_json = response.json()
    assert (
        response_json["detail"] == "This endpoint requires authorization. You need to be logged in."
    )
