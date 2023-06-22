from unittest.mock import Mock

from sqlalchemy.engine import Engine
from sqlmodel import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.agent_table import AgentTable
from database.model.ai_asset_table import AIAssetTable


from database.model.computational_resource.computational_resource import ComputationalResource


def test_happy_path(client: TestClient, engine: Engine, mocked_privileged_token: Mock):
    keycloak_openid.decode_token = mocked_privileged_token
    with Session(engine) as session:
        session.add_all(
            [
                AIAssetTable(type="computational_resource"),
                ComputationalResource(
                    identifier="1",
                    name="Parent",
                    platform="example",
                    platform_identifier="1",
                    description="description text",
                ),
                AIAssetTable(type="computational_resource"),
                ComputationalResource(
                    identifier="2",
                    name="Child",
                    platform="example",
                    platform_identifier="2",
                    description="description text",
                ),
                AgentTable(identifier=1, type="organization"),
            ]
        )
        session.commit()

    body = {
        "platform": "example",
        "platform_identifier": "3",
        "description": "A description.",
        "name": "Example Computational resource",
        "keyword": ["keyword1", "keyword2"],
        "citation": ["citation1", "citation2"],
        "logo": "https://www.example.com/computational_resource/logo.png",
        "creationTime": "2023-01-01T15:15:00.000Z",
        "validity": 5,
        "type": "example type",
        "qualityLevel": "example qualityLevel",
        "otherInfo": ["info1", "info2"],
        "capability": ["capability 1", "capability 2"],
        "complexity": "complexity example",
        "location": "Example location",
        "alternateName": ["name1", "name2"],
        "researchArea": ["research_area1", "research_area2"],
        "applicationArea": ["application_area1", "application_area2"],
        "hasPart": [2],
        "isPartOf": [1],
        "creator": [1],
        "contact": [1],
        "managedBy": [1],
        "distribution": [
            {
                "content_url": "https://www.example.com/dataset/file.csv",
                "content_size_kb": 10000,
                "description": "Description of this file.",
                "encoding_format": "text/csv",
                "name": "Name of this file.",
            }
        ],
        "statusInfo": [{"uri": "uri1"}],
        "hasShare": [{"uri": "uri2"}],
        "service": [{"uri": "uri3"}],
        "hasEndpoint": [{"endpoint": "endpoint"}],
    }
    response = client.post(
        "/computational_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 200

    response = client.get("/computational_resources/v0/3")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["identifier"] == 3
    assert response_json["platform"] == "example"
    assert response_json["platform_identifier"] == "3"
    assert response_json["description"] == "A description."
    assert response_json["name"] == "Example Computational resource"
    assert set(response_json["keyword"]) == {"keyword1", "keyword2"}
    assert set(response_json["citation"]) == {"citation1", "citation2"}
    assert response_json["logo"] == "https://www.example.com/computational_resource/logo.png"
    assert response_json["creationTime"] == "2023-01-01T15:15:00"
    assert response_json["validity"] == 5
    assert set(response_json["otherInfo"]) == {"info1", "info2"}
    assert set(response_json["capability"]) == {"capability 1", "capability 2"}
    assert response_json["complexity"] == "complexity example"
    assert response_json["location"] == "Example location"
    assert response_json["type"] == "example type"
    assert response_json["qualityLevel"] == "example qualityLevel"
    assert set(response_json["alternateName"]) == {"name1", "name2"}
    assert set(response_json["researchArea"]) == {"research_area1", "research_area2"}
    assert set(response_json["applicationArea"]) == {"application_area1", "application_area2"}
    assert set(response_json["isPartOf"]) == {1}
    assert set(response_json["hasPart"]) == {2}
    assert len(response_json["distribution"]) == 1
    assert len(response_json["statusInfo"]) == 1
    assert response_json["statusInfo"][0]["uri"] == "uri1"
    assert len(response_json["hasShare"]) == 1
    assert response_json["hasShare"][0]["uri"] == "uri2"
    assert len(response_json["service"]) == 1
    assert response_json["service"][0]["uri"] == "uri3"
    assert len(response_json["hasEndpoint"]) == 1
    assert response_json["hasEndpoint"][0]["endpoint"] == "endpoint"
