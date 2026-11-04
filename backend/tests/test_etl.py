import datetime
from collections.abc import Iterator

import pytest
from maps.etl import Artist, Company, Master, Release, Role, Track
from maps.models import Direction, EdgeLabels, VertexLabels


@pytest.fixture
def today() -> datetime.date:
    return datetime.date.today()


@pytest.mark.parametrize(
    "artist_id, expected_artist",
    [
        (
            1,
            Artist(
                id=1,
                name="The Persuader",
                aliases=[
                    Artist(
                        id=239,
                        name="Jesper Dahlbäck",
                        aliases=[],
                        groups=[],
                        members=[],
                    ),
                ],
            ),
        ),
    ],
)
def test_Artist_iterate_xml(
    artist_id: int, artists_iterator: Iterator[Artist], expected_artist: Artist
) -> None:
    while (actual_artist := next(artists_iterator)).id != artist_id:
        continue
    assert actual_artist == expected_artist


@pytest.mark.parametrize(
    "artist_id, expected_edge_dicts",
    [
        (
            1,
            [
                {
                    "direction": Direction.BIDIRECTIONAL,
                    "name": EdgeLabels.ALIAS_OF,
                    "that_id": that_id,
                    "that_index": 0,
                    "that_label": VertexLabels.ARTIST,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabels.ARTIST,
                }
                for that_id in (239, 16055, 19541, 25227, 196957, 278760, 439150)
            ],
        ),
    ],
)
def test_Artist_to_edge_dicts(
    artist_id: int,
    artists_iterator: Iterator[Artist],
    expected_edge_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_artist := next(artists_iterator)).id != artist_id:
        continue
    assert actual_artist.to_edge_dicts(today) == [
        {**d, "dataset": today} for d in expected_edge_dicts
    ]


@pytest.mark.parametrize(
    "artist_id, expected_vertex_dicts",
    [
        (
            1,
            [
                {
                    "id": 1,
                    "index": 0,
                    "label": VertexLabels.ARTIST,
                    "name": "The Persuader",
                    "random": ...,
                },
            ],
        ),
    ],
)
def test_Artist_to_vertex_dicts(
    artist_id: int,
    artists_iterator: Iterator[Artist],
    expected_vertex_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_artist := next(artists_iterator)).id != artist_id:
        continue
    assert [
        dict_ | {"random": ...} for dict_ in actual_artist.to_vertex_dicts(today)
    ] == [{**d, "dataset": today} for d in expected_vertex_dicts]


@pytest.mark.parametrize(
    "company_id, expected_company",
    [
        (
            1,
            Company(
                id=1,
                name="Planet E",
                parent_company=None,
                subsidiaries=[
                    Company(id=31405, name="I Ner Zon Sounds"),
                    Company(id=1560615, name="Planet E Productions"),
                ],
            ),
        ),
    ],
)
def test_Company_iterate_xml(
    company_id: int, companies_iterator: Iterator[Company], expected_company: Company
) -> None:
    while (actual_company := next(companies_iterator)).id != company_id:
        continue
    assert actual_company == expected_company


@pytest.mark.parametrize(
    "company_id, expected_edge_dicts",
    [
        (
            1,
            [
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": EdgeLabels.SUBSIDIARY_OF,
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabels.COMPANY,
                    "this_id": this_id,
                    "this_index": 0,
                    "this_label": VertexLabels.COMPANY,
                }
                for this_id in (
                    31405,
                    41841,
                    86537,
                    153760,
                    277579,
                    294738,
                    488315,
                    1560615,
                )
            ],
        ),
    ],
)
def test_Company_to_edge_dicts(
    company_id: int,
    companies_iterator: Iterator[Company],
    expected_edge_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_company := next(companies_iterator)).id != company_id:
        continue
    assert actual_company.to_edge_dicts(today) == [
        {**d, "dataset": today} for d in expected_edge_dicts
    ]


@pytest.mark.parametrize(
    "company_id, expected_vertex_dicts",
    [
        (
            1,
            [
                {
                    "id": 1,
                    "index": 0,
                    "label": VertexLabels.COMPANY,
                    "name": "Planet E",
                    "random": ...,
                },
            ],
        ),
    ],
)
def test_Company_to_vertex_dicts(
    company_id: int,
    companies_iterator: Iterator[Company],
    expected_vertex_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_company := next(companies_iterator)).id != company_id:
        continue
    assert [
        dict_ | {"random": ...} for dict_ in actual_company.to_vertex_dicts(today)
    ] == [{**d, "dataset": today} for d in expected_vertex_dicts]


@pytest.mark.parametrize(
    "master_id, expected_master",
    [
        (18500, Master(id=18500, main_release_id=155102, name="New Soil")),
    ],
)
def test_Master_iterate_xml(
    master_id: int, masters_iterator: Iterator[Master], expected_master: Master
) -> None:
    while (actual_master := next(masters_iterator)).id != master_id:
        continue
    assert actual_master == expected_master


@pytest.mark.parametrize(
    "master_id, expected_edge_dicts",
    [
        (18500, []),
    ],
)
def test_Master_to_edge_dicts(
    master_id: int,
    masters_iterator: Iterator[Master],
    expected_edge_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_master := next(masters_iterator)).id != master_id:
        continue
    assert actual_master.to_edge_dicts(today) == [
        {**d, "dataset": today} for d in expected_edge_dicts
    ]


@pytest.mark.parametrize(
    "master_id, expected_vertex_dicts",
    [
        (
            18500,
            [
                {
                    "id": 18500,
                    "index": 0,
                    "label": VertexLabels.MASTER,
                    "name": "New Soil",
                    "random": ...,
                },
            ],
        ),
    ],
)
def test_Master_to_vertex_dicts(
    master_id: int,
    masters_iterator: Iterator[Master],
    expected_vertex_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_master := next(masters_iterator)).id != master_id:
        continue
    assert [
        dict_ | {"random": ...} for dict_ in actual_master.to_vertex_dicts(today)
    ] == [{**d, "dataset": today} for d in expected_vertex_dicts]


@pytest.mark.parametrize(
    "release_id, expected_release",
    [
        (
            1,
            Release(
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
            ),
        ),
    ],
)
def test_Release_iterate_xml(
    release_id: int, releases_iterator: Iterator[Release], expected_release: Release
) -> None:
    while (actual_release := next(releases_iterator)).id != release_id:
        continue
    assert actual_release == expected_release


@pytest.mark.parametrize(
    "release_id, expected_edge_dicts",
    [
        (
            1,
            [
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": EdgeLabels.RELEASED_BY,
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabels.ARTIST,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabels.RELEASE,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": EdgeLabels.RELEASED_ON,
                    "that_id": 5,
                    "that_index": 0,
                    "that_label": VertexLabels.COMPANY,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabels.RELEASE,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Music By",
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabels.RELEASE,
                    "this_id": 239,
                    "this_index": 0,
                    "this_label": VertexLabels.ARTIST,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Pressed By",
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabels.RELEASE,
                    "this_id": 56025,
                    "this_index": 0,
                    "this_label": VertexLabels.COMPANY,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Recorded At",
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabels.RELEASE,
                    "this_id": 271046,
                    "this_index": 0,
                    "this_label": VertexLabels.COMPANY,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Subrelease Of",
                    "that_id": 1660109,
                    "that_index": 0,
                    "that_label": VertexLabels.MASTER,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabels.RELEASE,
                },
                *(
                    {
                        "direction": Direction.THIS_TO_THAT,
                        "name": EdgeLabels.INCLUDED_ON,
                        "that_id": 1,
                        "that_index": 0,
                        "that_label": VertexLabels.RELEASE,
                        "this_id": 1,
                        "this_index": track_index,
                        "this_label": VertexLabels.TRACK,
                    }
                    for track_index in range(1, 7)
                ),
            ],
        ),
    ],
)
def test_Release_to_edge_dicts(
    release_id: int,
    releases_iterator: Iterator[Release],
    expected_edge_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_release := next(releases_iterator)).id != release_id:
        continue
    assert actual_release.to_edge_dicts(today) == [
        {**d, "dataset": today} for d in expected_edge_dicts
    ]


@pytest.mark.parametrize(
    "release_id, expected_vertex_dicts",
    [
        (
            1,
            [
                {
                    "country": "Sweden",
                    "formats": ['12"', "33 ⅓ RPM", "Vinyl"],
                    "genres": ["Electronic"],
                    "id": 1,
                    "index": 0,
                    "label": VertexLabels.RELEASE,
                    "name": "Stockholm",
                    "primacy": True,
                    "random": ...,
                    "styles": ["Deep House"],
                    "videos": [
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
                    "year": 1999,
                },
                {
                    "country": "Sweden",
                    "formats": ['12"', "33 ⅓ RPM", "Vinyl"],
                    "genres": ["Electronic"],
                    "id": 1,
                    "index": 1,
                    "label": VertexLabels.TRACK,
                    "name": "Östermalm",
                    "position": "A",
                    "primacy": True,
                    "random": ...,
                    "styles": ["Deep House"],
                    "year": 1999,
                },
                {
                    "country": "Sweden",
                    "formats": ['12"', "33 ⅓ RPM", "Vinyl"],
                    "genres": ["Electronic"],
                    "id": 1,
                    "index": 2,
                    "label": VertexLabels.TRACK,
                    "name": "Vasastaden",
                    "position": "B1",
                    "primacy": True,
                    "random": ...,
                    "styles": ["Deep House"],
                    "year": 1999,
                },
                {
                    "country": "Sweden",
                    "formats": ['12"', "33 ⅓ RPM", "Vinyl"],
                    "genres": ["Electronic"],
                    "id": 1,
                    "index": 3,
                    "label": VertexLabels.TRACK,
                    "name": "Kungsholmen",
                    "position": "B2",
                    "primacy": True,
                    "random": ...,
                    "styles": ["Deep House"],
                    "year": 1999,
                },
                {
                    "country": "Sweden",
                    "formats": ['12"', "33 ⅓ RPM", "Vinyl"],
                    "genres": ["Electronic"],
                    "id": 1,
                    "index": 4,
                    "label": VertexLabels.TRACK,
                    "name": "Södermalm",
                    "position": "C1",
                    "primacy": True,
                    "random": ...,
                    "styles": ["Deep House"],
                    "year": 1999,
                },
                {
                    "country": "Sweden",
                    "formats": ['12"', "33 ⅓ RPM", "Vinyl"],
                    "genres": ["Electronic"],
                    "id": 1,
                    "index": 5,
                    "label": VertexLabels.TRACK,
                    "name": "Norrmalm",
                    "position": "C2",
                    "primacy": True,
                    "random": ...,
                    "styles": ["Deep House"],
                    "year": 1999,
                },
                {
                    "country": "Sweden",
                    "formats": ['12"', "33 ⅓ RPM", "Vinyl"],
                    "genres": ["Electronic"],
                    "id": 1,
                    "index": 6,
                    "label": VertexLabels.TRACK,
                    "name": "Gamla Stan",
                    "position": "D",
                    "primacy": True,
                    "random": ...,
                    "styles": ["Deep House"],
                    "year": 1999,
                },
            ],
        ),
    ],
)
def test_Release_to_vertex_dicts(
    release_id: int,
    releases_iterator: Iterator[Release],
    expected_vertex_dicts: list[dict],
    today: datetime.date,
) -> None:
    while (actual_release := next(releases_iterator)).id != release_id:
        continue
    assert [
        dict_ | {"random": ...} for dict_ in actual_release.to_vertex_dicts(today)
    ] == [{**d, "dataset": today} for d in expected_vertex_dicts]
