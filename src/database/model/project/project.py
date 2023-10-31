from datetime import datetime
from typing import Optional

from pydantic import condecimal
from sqlmodel import Field, Relationship

from database.model.agent.organisation import Organisation
from database.model.ai_asset.ai_asset_table import AIAssetTable
from database.model.ai_resource.resource import AIResourceBase, AbstractAIResource
from database.model.helper_functions import link_factory
from database.model.relationships import ResourceRelationshipList, ResourceRelationshipSingle
from database.model.serializers import (
    AttributeSerializer,
    FindByIdentifierDeserializer,
)


class ProjectBase(AIResourceBase):
    start_date: datetime = Field(
        description="The start date and time of the project as ISO 8601.",
        default=None,
        schema_extra={"example": "2021-02-03T15:15:00"},
    )
    end_date: datetime | None = Field(
        description="The end date and time of the project as ISO 8601.",
        default=None,
        schema_extra={"example": "2022-01-01T15:15:00"},
    )
    total_cost_euro: condecimal(max_digits=12, decimal_places=2) | None = Field(  # type: ignore
        description="The total budget of the project in euros.",
        schema_extra={"example": 1000000},
        default=None,
    )


class Project(ProjectBase, AbstractAIResource, table=True):  # type: ignore [call-arg]
    __tablename__ = "project"

    funder: list[Organisation] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"},
        link_model=link_factory("project", Organisation.__tablename__, table_prefix="funder"),
    )
    participant: list[Organisation] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"},
        link_model=link_factory("project", Organisation.__tablename__, table_prefix="participant"),
    )
    coordinator_identifier: int | None = Field(
        foreign_key=Organisation.__tablename__ + ".identifier"
    )
    coordinator: Optional[Organisation] = Relationship()
    produced: list[AIAssetTable] = Relationship(
        link_model=link_factory("project", AIAssetTable.__tablename__, table_prefix="produced"),
    )
    used: list[AIAssetTable] = Relationship(
        link_model=link_factory("project", AIAssetTable.__tablename__, table_prefix="used"),
    )

    class RelationshipConfig(AbstractAIResource.RelationshipConfig):
        funder: list[int] = ResourceRelationshipList(
            description="Identifiers of organizations that support this project through some kind "
            "of financial contribution. ",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(Organisation),
            default_factory_pydantic=list,
            example=[],
        )
        participant: list[int] = ResourceRelationshipList(
            description="Identifiers of members of this project. ",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(Organisation),
            default_factory_pydantic=list,
            example=[],
        )
        coordinator: Optional[int] = ResourceRelationshipSingle(
            identifier_name="coordinator_identifier",
            description="The coordinating organisation of this project.",
            serializer=AttributeSerializer("identifier"),
        )
        produced: list[int] = ResourceRelationshipList(
            description="Identifiers of AIAssets that are created in this project.",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(AIAssetTable),
            default_factory_pydantic=list,
            example=[],
        )
        used: list[int] = ResourceRelationshipList(
            description="Identifiers of AIAssets that are used (but not created) in this project.",
            serializer=AttributeSerializer("identifier"),
            deserializer=FindByIdentifierDeserializer(AIAssetTable),
            default_factory_pydantic=list,
            example=[],
        )
