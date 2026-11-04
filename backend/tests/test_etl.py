import datetime
from collections.abc import Iterator

import pytest

from maps.models import Direction, EdgeLabels, VertexLabels
from maps.etl import Artist, Company, Master, Release, Role, Track


@pytest.fixture
def today() -> datetime.date:
    return datetime.date.today()


def test_Artist_iterate_xml(artists_iterator: Iterator[Artist]) -> None:
    assert next(artists_iterator) == Artist(
        id=1,
        name="The Persuader",
        aliases=[
            Artist(id=239, name="Jesper Dahlbäck", aliases=[], groups=[], members=[]),
        ],
    )


def test_Artist_to_edge_dicts(artists_iterator: Iterator[Artist], today: datetime.date) -> None:
    assert next(artists_iterator).to_edge_dicts(datetime.date.today()) == [
        {
            'dataset': today,
            'direction': Direction.BIDIRECTIONAL,
            'name': EdgeLabels.ALIAS_OF,
            'that_id': 239,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
        {
            'dataset': today,
            'direction': Direction.BIDIRECTIONAL,
            'name': EdgeLabels.ALIAS_OF,
            'that_id': 16055,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
        {
            'dataset': today,
            'direction': Direction.BIDIRECTIONAL,
            'name': EdgeLabels.ALIAS_OF,
            'that_id': 19541,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
        {
            'dataset': today,
            'direction': Direction.BIDIRECTIONAL,
            'name': EdgeLabels.ALIAS_OF,
            'that_id': 25227,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
        {
            'dataset': today,
            'direction': Direction.BIDIRECTIONAL,
            'name': EdgeLabels.ALIAS_OF,
            'that_id': 196957,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
        {
            'dataset': today,
            'direction': Direction.BIDIRECTIONAL,
            'name': EdgeLabels.ALIAS_OF,
            'that_id': 278760,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
        {
            'dataset': today,
            'direction': Direction.BIDIRECTIONAL,
            'name': EdgeLabels.ALIAS_OF,
            'that_id': 439150,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
    ]


def test_Artist_to_vertex_dicts(artists_iterator: Iterator[Artist], today: datetime.date) -> None:
    vertex_dicts = [
        dict_ | {"random": ...} for dict_ in
        next(artists_iterator).to_vertex_dicts(datetime.date.today())
    ]
    assert vertex_dicts == [
        {
            'dataset': today,
            'id': 1,
            'index': 0,
            'label': VertexLabels.ARTIST,
            'name': 'The Persuader',
            'random': ...,
        },
    ]


def test_Company_iterate_xml(companies_iterator: Iterator[Company]) -> None:
    assert next(companies_iterator) == Company(
        id=1,
        name="Planet E",
        parent_company=None,
        subsidiaries=[
            Company(id=31405, name="I Ner Zon Sounds"),
            Company(id=1560615, name="Planet E Productions"),
        ],
    )


def test_Company_to_edge_dicts(companies_iterator: Iterator[Company], today: datetime.date) -> None:
    assert next(companies_iterator).to_edge_dicts(today) == [
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 31405,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 41841,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 86537,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 153760,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 277579,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 294738,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 488315,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.SUBSIDIARY_OF,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 1560615,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
    ]


def test_Company_to_vertex_dicts(companies_iterator: Iterator[Company], today: datetime.date) -> None:
    vertex_dicts = [
        dict_ | {"random": ...} for dict_ in
        next(companies_iterator).to_vertex_dicts(today)
    ]
    assert vertex_dicts == [
        {
            'dataset': today,
            'id': 1,
            'index': 0,
            'label': VertexLabels.COMPANY,
            'name': 'Planet E',
            'random': ...,
        },
    ]


def test_Master_iterate_xml(masters_iterator: Iterator[Master]) -> None:
    assert next(masters_iterator) == Master(
        id=18500, main_release_id=155102, name="New Soil"
    )


def test_Master_to_edge_dicts(masters_iterator: Iterator[Master], today: datetime.date) -> None:
    assert next(masters_iterator).to_edge_dicts(today) == []


def test_Master_to_vertex_dicts(masters_iterator: Iterator[Master], today: datetime.date) -> None:
    vertex_dicts = [
        dict_ | {"random": ...} for dict_ in
        next(masters_iterator).to_vertex_dicts(today)
    ]
    assert vertex_dicts == [
        {
            'dataset': today,
            'id': 18500,
            'index': 0,
            'label': VertexLabels.MASTER,
            'name': 'New Soil',
            'random': ...,
        },
    ]


def test_Release_iterate_xml(releases_iterator: Iterator[Release]) -> None:
    assert next(releases_iterator) == Release(
        id=1,
        name="Stockholm",
        artists=[Artist(id=1, name="The Persuader")],
        companies=[
            Company(id=56025, name="MPO", roles=[Role(name="Pressed By")]),
            Company(
                id=271046,
                name="The Globe Studios",
                roles=[Role(name="Recorded At")],
            ),
        ],
        country="Sweden",
        extra_artists=[
            Artist(
                id=239,
                name="Jesper Dahlbäck",
                roles=[Role(name="Music By", detail="All Tracks By")],
            ),
        ],
        formats=['12"', "33 ⅓ RPM", "Vinyl"],
        genres=["Electronic"],
        is_main_release=True,
        labels=[Company(id=5, name="Svek")],
        master_id=1660109,
        styles=["Deep House"],
        tracks=[
            Track(id=1, index=1, name="Östermalm", position="A"),
            Track(id=1, index=2, name="Vasastaden", position="B1"),
            Track(id=1, index=3, name="Kungsholmen", position="B2"),
            Track(id=1, index=4, name="Södermalm", position="C1"),
            Track(id=1, index=5, name="Norrmalm", position="C2"),
            Track(id=1, index=6, name="Gamla Stan", position="D"),
        ],
        videos=[
            {
                "title": "The Persuader - Östermalm",
                "url": "https://www.youtube.com/watch?v=MpmbntGDyNE",
            },
            {
                "title": "The Persuader - Vasastaden",
                "url": "https://www.youtube.com/watch?v=Cawyll0pOI4",
            },
            {
                "title": "The Persuader - Kungsholmen",
                "url": "https://www.youtube.com/watch?v=XExCZfMCXdo",
            },
            {
                "title": "The Persuader - Södermalm",
                "url": "https://www.youtube.com/watch?v=WDZqiENap_U",
            },
            {
                "title": "The Persuader - Norrmalm",
                "url": "https://www.youtube.com/watch?v=EBBHR3EMN50",
            },
            {
                "title": "The Persuader - Gamla Stan",
                "url": "https://www.youtube.com/watch?v=afMHNll9EVM",
            },
        ],
        year=1999,
    )


def test_Release_to_edge_dicts(releases_iterator: Iterator[Release], today: datetime.date) -> None:
    assert next(releases_iterator).to_edge_dicts(today) == [
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.RELEASED_BY,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.ARTIST,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.RELEASE,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.RELEASED_ON,
            'that_id': 5,
            'that_index': 0,
            'that_label': VertexLabels.COMPANY,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.RELEASE,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': 'Music By',
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 239,
            'this_index': 0,
            'this_label': VertexLabels.ARTIST,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': 'Pressed By',
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 56025,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': 'Recorded At',
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 271046,
            'this_index': 0,
            'this_label': VertexLabels.COMPANY,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': 'Subrelease Of',
            'that_id': 1660109,
            'that_index': 0,
            'that_label': VertexLabels.MASTER,
            'this_id': 1,
            'this_index': 0,
            'this_label': VertexLabels.RELEASE,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.INCLUDED_ON,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 1,
            'this_index': 1,
            'this_label': VertexLabels.TRACK,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.INCLUDED_ON,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 1,
            'this_index': 2,
            'this_label': VertexLabels.TRACK,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.INCLUDED_ON,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 1,
            'this_index': 3,
            'this_label': VertexLabels.TRACK,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.INCLUDED_ON,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 1,
            'this_index': 4,
            'this_label': VertexLabels.TRACK,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.INCLUDED_ON,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 1,
            'this_index': 5,
            'this_label': VertexLabels.TRACK,
        },
        {
            'dataset': today,
            'direction': Direction.THIS_TO_THAT,
            'name': EdgeLabels.INCLUDED_ON,
            'that_id': 1,
            'that_index': 0,
            'that_label': VertexLabels.RELEASE,
            'this_id': 1,
            'this_index': 6,
            'this_label': VertexLabels.TRACK,
        },
    ]


def test_Release_to_vertex_dicts(releases_iterator: Iterator[Release], today: datetime.date) -> None:
    release = next(releases_iterator)
    vertex_dicts = [
        dict_ | {"random": ...} for dict_ in release.to_vertex_dicts(today)
    ]
    common = {
        'country': 'Sweden',
        'dataset': today,
        'formats': ['12"', '33 ⅓ RPM', 'Vinyl'],
        'genres': ['Electronic'],
        'id': 1,
        'primacy': True,
        'styles': ['Deep House'],
        'videos': release.videos,
        'year': 1999,
    }
    assert vertex_dicts == [
        {
            **common,
            'index': 0,
            'label': VertexLabels.RELEASE,
            'name': 'Stockholm',
            'random': ...,
        },
        {
            **common,
            'index': 1,
            'label': VertexLabels.TRACK,
            'name': 'Östermalm',
            'position': 'A',
            'random': ...,
        },
        {
            **common,
            'index': 2,
            'label': VertexLabels.TRACK,
            'name': 'Vasastaden',
            'position': 'B1',
            'random': ...,
        },
        {
            **common,
            'index': 3,
            'label': VertexLabels.TRACK,
            'name': 'Kungsholmen',
            'position': 'B2',
            'random': ...,
        },
        {
            **common,
            'index': 4,
            'label': VertexLabels.TRACK,
            'name': 'Södermalm',
            'position': 'C1',
            'random': ...,
        },
        {
            **common,
            'index': 5,
            'label': VertexLabels.TRACK,
            'name': 'Norrmalm',
            'position': 'C2',
            'random': ...,
        },
        {
            **common,
            'index': 6,
            'label': VertexLabels.TRACK,
            'name': 'Gamla Stan',
            'position': 'D',
            'random': ...,
        },
    ]
