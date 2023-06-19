from unittest.mock import Mock

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from authentication import keycloak_openid
from database.model.ai_asset import AIAsset
from database.model.dataset.dataset import Dataset
from database.model.event.event import Event


def test_happy_path(client: TestClient, engine: Engine, mocked_privileged_token: Mock):
    keycloak_openid.decode_token = mocked_privileged_token
    with Session(engine) as session:
        session.add_all(
            [
                AIAsset(type="dataset"),
                Dataset(
                    identifier=1,
                    name="Parent",
                    platform="example",
                    platform_identifier="2",
                    description="description text",
                    same_as="",
                ),
            ]
        )
        session.commit()
    with Session(engine) as session:
        # It should be possible to add the event and dataset in the same session, but it leads to
        # a weird IntegrityError. This problem is avoided by removing the foreign key constraint
        # dataset.identfier to ai_asset.identifier, or by removing the event.relevant_resources
        # and event.used_resources. After some debugging the cause of this error was still
        # unclear.
        session.add_all(
            [
                AIAsset(type="event"),
                Event(
                    identifier=2,
                    name="Parent",
                    platform="example",
                    platform_identifier="1",
                    description="description text",
                    registration_url="https://example.com/event/example/registration",
                    location="Example location Event",
                ),
            ]
        )
        session.commit()
    body = {
        "platform": "example",
        "platform_identifier": "2",
        "name": "Example Event",
        "description": "example descriprion",
        "registration_url": "https://example.com/event/example/registration",
        "location": "Example location Event",
        "start_date": "2022-01-01T15:15:00",
        "end_date": "2022-01-01T15:15:00",
        "duration": "Example duration Event",
        "status": "Example status Event",
        "attendance_mode": "Example attendance mode Event",
        "type": "Example type Event",
        "super_events": [2],
        "sub_events": [2],
        "research_areas": ["research_area1", "research_area2"],
        "application_areas": ["application_area1", "application_area2"],
        "relevant_resources": [1],
        "used_resources": [2],
        "business_categories": ["business category 1", "business category 2"],
    }
    response = client.post("/events/v0", json=body, headers={"Authorization": "Fake token"})
    assert response.status_code == 200

    response = client.get("/events/v0/3")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["identifier"] == 3
    assert response_json["platform"] == "example"
    assert response_json["platform_identifier"] == "2"
    assert response_json["name"] == "Example Event"
    assert response_json["description"] == "example descriprion"
    assert response_json["registration_url"] == "https://example.com/event/example/registration"
    assert response_json["location"] == "Example location Event"
    assert response_json["start_date"] == "2022-01-01T15:15:00"
    assert response_json["end_date"] == "2022-01-01T15:15:00"
    assert response_json["duration"] == "Example duration Event"
    assert response_json["status"] == "Example status Event"
    assert response_json["attendance_mode"] == "Example attendance mode Event"
    assert response_json["type"] == "Example type Event"
    assert set(response_json["super_events"]) == {2}
    assert set(response_json["sub_events"]) == {2}
    assert set(response_json["research_areas"]) == {"research_area1", "research_area2"}
    assert set(response_json["application_areas"]) == {"application_area1", "application_area2"}
    assert set(response_json["relevant_resources"]) == {1}
    assert set(response_json["used_resources"]) == {2}
    assert set(response_json["business_categories"]) == {
        "business category 1",
        "business category 2",
    }

    response = client.delete("/events/v0/3", headers={"Authorization": "Fake token"})
    assert response.status_code == 200

    response = client.get("/events/v0", headers={"Authorization": "Fake token"})
    assert response.status_code == 200
