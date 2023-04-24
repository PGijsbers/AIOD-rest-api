"""
Schemas of the AIoD resources.

Note that these objects are different from the ORM objects defined in the database. This leads to
code duplication, so it is not ideal. But it makes it possible to differentiate between the database
objects and the externally used AIoD schemas. The dataset, for example, contains keywords,
which should be a separate object inside a separate table in the database (so that we can easily
search for all datasets having the same keyword). In the external schema, a set of strings is
easier.
"""
from datetime import datetime, timedelta, date
from typing import Set, List, Optional

from pydantic import BaseModel, Field

from platform_names import PlatformName


class AIoDResource(BaseModel):
    """
    The base class of all our Resources
    """

    identifier: int | None
    platform: str = Field(max_length=30, default=PlatformName.aiod)
    platform_identifier: str | None = Field(max_length=250, default=None)


class AIoDAIResource(AIoDResource):
    """
    The base class of all our AIResources such as Datasets, Publications etc..

    For now, it contains no fields, we will have to extend it later.
    """

    pass


class AIoDChecksum(BaseModel):
    algorithm: str = Field(max_length=150)
    value: str = Field(max_length=500)


class AIoDDistribution(BaseModel):
    content_url: str = Field(max_length=150)
    content_size_kb: int | None
    description: str | None = Field(max_length=5000)
    name: str | None = Field(max_length=150)
    encoding_format: str | None = Field(max_length=150)
    checksum: list[AIoDChecksum] = Field(default_factory=list)


class AIoDMeasurementValue(BaseModel):
    variable: str | None
    technique: str | None


class AIoDPublication(AIoDAIResource):
    """The complete metadata of a publication. For now, only a couple of fields are shown,
    we have to decide which fields to use."""

    doi: str | None = Field(max_length=150)
    title: str = Field(max_length=250)
    url: str | None = Field(max_length=250)
    datasets: Set[int] = Field(
        description="Identifiers of datasets that are connected to this publication",
        default_factory=list,
    )


class AIoDProject(AIoDAIResource):
    """The complete metadata of a project. For now, only a couple of fields are shown,
    we have to decide which fields to use."""

    name: str | None = Field(max_length=250)
    doi: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    founded_under: Optional[str]
    total_cost_euro: Optional[float]
    eu_contribution_euro: Optional[float]
    coordinated_by: Optional[str]
    project_description_title: Optional[str]
    project_description_text: Optional[str]
    programmes_url: Optional[str]
    topic_url: Optional[str]
    call_for_proposal: Optional[str]
    founding_scheme: Optional[str]
    image: Optional[str]  # url of the image
    url: Optional[str]

    # partners: Optional[list[str]]
    keywords: Set[str] = Field(default_factory=set)


class AIoDDataset(AIoDAIResource):
    """
    The complete metadata of a dataset in AIoD format.
    """

    description: str = Field(max_length=5000)
    name: str = Field(max_length=150)
    same_as: str = Field(max_length=150)

    # Recommended fields
    contact: str | None = Field(max_length=150)
    creator: str | None = Field(max_length=150)
    date_modified: datetime | date | None
    date_published: datetime | date | None
    funder: str | None
    is_accessible_for_free: bool = Field(default=True)
    issn: str | None = Field(max_length=8, min_length=8)
    publisher: str | None = Field(max_length=150)
    size: int | None
    spatial_coverage: str | None = Field(max_length=500)
    temporal_coverage_from: datetime | date | None
    temporal_coverage_to: datetime | date | None
    version: str | None = Field(max_length=150)

    # Relations
    license: str | None = Field(max_length=150)
    has_parts: Set[int] = Field(
        description="Identifiers of datasets that are part of this " "dataset.",
        default_factory=set,
    )
    is_part: Set[int] = Field(
        description="Identifiers of datasets this dataset is part of.", default_factory=set
    )
    alternate_names: List[str] = Field(default_factory=list)
    citations: Set[int] = Field(
        description="Identifiers of publications linked to this dataset",
        default_factory=set,
    )
    distributions: List[AIoDDistribution] = []
    keywords: list[str] = Field(default_factory=list)
    measured_values: List[AIoDMeasurementValue] = Field(default_factory=list)


class AIoDNews(AIoDAIResource):
    """The complete metadata for news entity"""

    title: str = Field(max_length=500)
    date_modified: datetime
    body: str = Field(max_length=2000)
    headline: str = Field(max_length=500)
    alternative_headline: Optional[str] = Field(max_length=500)
    section: str = Field(max_length=500)
    word_count: int

    media: Optional[list[str]]
    source: Optional[str]
    news_categories: Optional[list[str]]
    business_categories: Optional[list[str]]
    keywords: Optional[list[str]]


class AIoDEducationalResource(AIoDAIResource):
    """The complete metadata for educational resource"""

    title: str = Field(max_length=500)
    body: str = Field(max_length=500)
    website_url: str = Field(max_length=500)
    date_modified: datetime | None

    educational_level: str = Field(max_length=500)
    educational_type: str = Field(max_length=500)

    pace: str = Field(max_length=500)
    languages: List[str] = Field(
        description="Languages related with an educational resource", default_factory=list
    )
    target_audience: List[str] = Field(
        description="Target audience related with an educational resource", default_factory=list
    )

    educational_use: str | List[str] = Field(
        description="The intended educational use of the resource, such as lecture, lab exercise"
        ", or homework assignment",
        default_factory=str,
    )
    typical_age_range: str | None = Field(max_length=100)

    interactivity_type: str | None = Field(max_length=100)
    accessibility_api: str | None = Field(max_length=100)
    accessibility_control: str | None = Field(max_length=100)
    access_mode: str | None = Field(max_length=100)

    access_mode_sufficient: str | List[str] = Field(
        description="The set of access modes required to access the educational resource,"
        " such as textual and visual.",
        default_factory=str,
    )
    access_restrictions: str | None = Field(max_length=100)
    is_accessible_for_free: bool | None
    time_required: timedelta | None
    citation: str | None = Field(max_length=200)

    version: str | int | None
    credits: bool | None
    number_of_weeks: int | None
    field_prerequisites: str | None = Field(max_length=500)
    short_summary: str | None = Field(max_length=500)
    duration_in_years: int | None

    duration_minutes_and_hours: Optional[str]
    hours_per_week: Optional[str]
    country: Optional[str]

    technical_categories: List[str] = Field(
        description="Technical categories related with an educational resource",
        default_factory=list,
    )
    business_categories: List[str] = Field(
        description="Business categories related with an educational resource", default_factory=list
    )
    keywords: List[str] = Field(
        description="Keywords or tags categories related with an educational resource",
        default_factory=list,
    )


class AIoDEvent(AIoDResource):
    """The complete metadata for events"""

    name: str = Field(max_length=150)
    description: str = Field(max_length=5000)
    registration_url: str = Field(max_length=150)
    location: str = Field(max_length=500)

    start_date: datetime | None
    end_date: datetime | None
    duration: str | int | None
    status: str | None
    attendance_mode: str | None
    type: str

    sub_events: Set[int] = Field(
        description="Identifiers of events that are sub events of this " "event.",
        default_factory=set,
    )

    super_events: Set[int] = Field(
        description="Identifiers of events that are super events of this " "event.",
        default_factory=set,
    )

    research_areas: List[str] = Field(
        description="Research areas related with an event",
        default_factory=list,
    )

    application_areas: List[str] = Field(
        description="Application areas related with an event",
        default_factory=list,
    )

    relevant_resources: Set[int] = Field(
        description="Identifiers of AiResources that are connected to this event",
        default_factory=set,
    )

    used_resources: Set[int] = Field(
        description="Identifiers of AiResources that are used by this event",
        default_factory=set,
    )

    business_categories: List[str] = Field(
        description="Business categories related with this event", default_factory=list
    )

    media: List[str] = Field(description="Media used in  this event", default_factory=list)


class AIoDAgent(AIoDResource):
    """The complete metadata for agents"""

    name: str = Field(max_length=100)
    description: str | None = Field(max_length=500)
    image_url: str | None = Field(max_length=500)
    email_addresses: List[str] = Field(
        description="Email addresses related with this agent", default_factory=list
    )


class AIoDOrganisation(AIoDAgent):
    """The complete metadata for organisation"""

    connection_to_ai: str | None
    type: str = Field(max_length=500)

    logo_url: str | None
    same_as: str | None
    founding_date: datetime | None
    dissolution_date: datetime | None
    legal_name: str | None
    alternate_name: str | None
    address: str | None
    telephone: str | None

    parent_organisation: int | None
    subsidiary_organisation: int | None

    members: List[AIoDAgent] = Field(
        description="AIoDAgents that are members of this organisation",
        default_factory=set,
    )

    departments: List[AIoDAgent] = Field(
        description="AIoDAgents that are departments of this organisation",
        default_factory=set,
    )

    business_categories: List[str] = Field(
        description="Business categories related with this organisation", default_factory=list
    )
    technical_categories: List[str] = Field(
        description="Technical categories related with this organisation", default_factory=list
    )
