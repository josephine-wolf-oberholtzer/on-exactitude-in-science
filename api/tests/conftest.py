import datetime
from pathlib import Path
from typing import Iterator

import pytest

from maps.etl import Artist, Company, Master, Release


@pytest.fixture
def artists_iterator(artists_xml_path: Path) -> Iterator[Artist]:
    return Artist.iterate_xml(artists_xml_path)


@pytest.fixture
def artists_xml_path(xml_directory_path: Path) -> Path:
    return xml_directory_path / "discogs_test_artists.xml.gz"


@pytest.fixture
def companies_iterator(companies_xml_path: Path) -> Iterator[Company]:
    return Company.iterate_xml(companies_xml_path)


@pytest.fixture
def companies_xml_path(xml_directory_path: Path) -> Path:
    # N.B. Discogs uses the term "labels" but this is imprecise, as the entity
    # actually refers to any company.
    return xml_directory_path / "discogs_test_labels.xml.gz"


@pytest.fixture
def masters_iterator(masters_xml_path: Path) -> Iterator[Master]:
    return Master.iterate_xml(masters_xml_path)


@pytest.fixture
def masters_xml_path(xml_directory_path: Path) -> Path:
    return xml_directory_path / "discogs_test_masters.xml.gz"


@pytest.fixture
def releases_iterator(releases_xml_path: Path) -> Iterator[Release]:
    return Release.iterate_xml(releases_xml_path)


@pytest.fixture
def releases_xml_path(xml_directory_path: Path) -> Path:
    return xml_directory_path / "discogs_test_releases.xml.gz"


@pytest.fixture
def today() -> datetime.date:
    return datetime.date.today()


@pytest.fixture
def xml_directory_path() -> Path:
    return Path(__file__).parent / "data"
