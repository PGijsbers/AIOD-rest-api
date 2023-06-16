import huggingface_hub
import responses
from unittest.mock import Mock

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model import AIAsset
from database.model.dataset.dataset import Dataset
from tests.testutils.paths import path_test_resources


def test_happy_path_new_repository(
    client: TestClient, engine: Engine, mocked_privileged_token: Mock
):
    keycloak_openid.decode_token = mocked_privileged_token
    dataset_id = 1
    with Session(engine) as session:
        session.add_all(
            [
                AIAsset(type="dataset"),
                Dataset(
                    identifier=dataset_id,
                    name="Parent",
                    platform="example",
                    platform_identifier="1",
                    description="description text",
                    same_as="",
                ),
            ]
        )
        session.commit()

    data = {
        "token": "huggingface_token",
        "username": "username",
    }

    with open(path_test_resources() / "uploaders" / "huggingface" / "example.csv", "rb") as f:
        files = {"file": f.read()}

    with responses.RequestsMock() as mocked_requests:
        mocked_requests.add(
            responses.POST,
            "https://huggingface.co/api/repos/create",
            json={"url": "url"},
            status=200,
        )
        huggingface_hub.upload_file = Mock(return_value=None)
        response = client.post(
            f"/upload/datasets/{dataset_id}/huggingface",
            data=data,
            params={"username": "Fake-username", "token": "Fake-token"},
            headers={"Authorization": "Fake token"},
            files=files,
        )
    assert response.status_code == 200
    id_response = response.json()
    assert id_response == dataset_id


def test_repo_already_exists(client: TestClient, engine: Engine, mocked_privileged_token: Mock):
    keycloak_openid.decode_token = mocked_privileged_token
    dataset_id = 1
    with Session(engine) as session:
        session.add_all(
            [
                AIAsset(type="dataset"),
                Dataset(
                    identifier=dataset_id,
                    name="Parent",
                    platform="example",
                    platform_identifier="1",
                    description="description text",
                    same_as="",
                ),
            ]
        )
        session.commit()

    data = {
        "token": "huggingface_token",
        "username": "username",
    }

    with open(path_test_resources() / "uploaders" / "huggingface" / "example.csv", "rb") as f:
        files = {"file": f.read()}

    with responses.RequestsMock() as mocked_requests:
        mocked_requests.add(
            responses.POST,
            "https://huggingface.co/api/repos/create",
            json={
                "error": "You already created this dataset repo",
                "url": "url",
            },
            status=409,
        )
        huggingface_hub.upload_file = Mock(return_value=None)
        response = client.post(
            f"/upload/datasets/{dataset_id}/huggingface",
            data=data,
            params={"username": "Fake-username", "token": "Fake-token"},
            headers={"Authorization": "Fake token"},
            files=files,
        )
    assert response.status_code == 200
    id_response = response.json()
    assert id_response == dataset_id


# TODO: tests some error handling?
