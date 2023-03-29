"""
Fixtures that provide default instances for AIoD and ORM classes.

This way you have easy access to, for instance, an AIoDDataset filled with default values.
"""


import datetime

import pytest

from database.model.dataset import OrmDataset, OrmDataDownload
from database.model.publication import OrmPublication
from schemas import AIoDDataset, AIoDDistribution, AIoDMeasurementValue


@pytest.fixture
def aiod_dataset() -> AIoDDataset:
    return AIoDDataset(
        id=7,
        description="description",
        name="name",
        node="node",
        node_specific_identifier="node_specific_identifier",
        same_as="same_as",
        creator="creator",
        date_modified=datetime.datetime(2002, 1, 1),
        date_published=datetime.datetime(2001, 1, 1),
        funder="funder",
        is_accessible_for_free=True,
        issn="12345678",
        size=100,
        spatial_coverage="spatial_coverage",
        temporal_coverage_from=datetime.datetime(2000, 1, 1),
        temporal_coverage_to=datetime.datetime(2000, 1, 2),
        version="version",
        license="license.name",
        has_parts=[],
        is_part=[],
        alternate_names=["alternative_1", "alternative_2"],
        citations=[],
        distributions=[
            AIoDDistribution(
                content_url="distr.content_url",
                content_size_kb=123,
                description="distr.description",
                name="distr.name",
                encoding_format="distr.encoding_format",
            )
        ],
        keywords=["a", "b", "c"],
        measured_values=[AIoDMeasurementValue(variable="variable", technique="technique")],
    )


@pytest.fixture()
def orm_dataset() -> OrmDataset:
    return OrmDataset(
        description="description",
        name="name",
        node="example",
        node_specific_identifier="node_specific_identifier",
        same_as="same_as",
        creator="creator",
        date_modified=datetime.datetime(2002, 1, 1),
        date_published=datetime.datetime(2001, 1, 1),
        funder="funder",
        is_accessible_for_free=True,
        issn="12345678",
        size=100,
        spatial_coverage="spatial_coverage",
        temporal_coverage_from=datetime.datetime(2000, 1, 1),
        temporal_coverage_to=datetime.datetime(2000, 1, 2),
        version="version",
        license=None,
        has_parts=[],
        is_part=[],
        alternate_names=[],
        citations=[],
        distributions=[],
        keywords=[],
        measured_values=[],
    )


@pytest.fixture()
def orm_data_download() -> OrmDataDownload:
    return OrmDataDownload(
        content_url="url",
        content_size_kb=128,
        description="description",
        encoding_format="text/csv",
        name="name",
    )


@pytest.fixture()
def orm_publication() -> OrmPublication:
    return OrmPublication(
        title="Title",
        doi="12345678",
        node="example",
        node_specific_identifier="1",
        datasets=[],
    )
