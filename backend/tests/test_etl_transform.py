import datetime
from collections.abc import Iterator

import pytest
from maps.etl import Artist, Company, Master, Release
from maps.models import Direction, EdgeLabel, VertexLabel


@pytest.fixture
def today() -> datetime.date:
    return datetime.date.today()


@pytest.mark.parametrize(
    "artist_id, expected_edge_dicts",
    [
        (
            1,
            [
                {
                    "direction": Direction.BIDIRECTIONAL,
                    "name": EdgeLabel.ALIAS_OF,
                    "that_id": that_id,
                    "that_index": 0,
                    "that_label": VertexLabel.ARTIST,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabel.ARTIST,
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
                    "label": VertexLabel.ARTIST,
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
    "company_id, expected_edge_dicts",
    [
        (
            1,
            [
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": EdgeLabel.SUBSIDIARY_OF,
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabel.COMPANY,
                    "this_id": this_id,
                    "this_index": 0,
                    "this_label": VertexLabel.COMPANY,
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
                    "label": VertexLabel.COMPANY,
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
                    "label": VertexLabel.MASTER,
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
    "release_id, expected_edge_dicts",
    [
        (
            1,
            [
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": EdgeLabel.RELEASED_BY,
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabel.ARTIST,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabel.RELEASE,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": EdgeLabel.RELEASED_ON,
                    "that_id": 5,
                    "that_index": 0,
                    "that_label": VertexLabel.COMPANY,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabel.RELEASE,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Music By",
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabel.RELEASE,
                    "this_id": 239,
                    "this_index": 0,
                    "this_label": VertexLabel.ARTIST,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Pressed By",
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabel.RELEASE,
                    "this_id": 56025,
                    "this_index": 0,
                    "this_label": VertexLabel.COMPANY,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Recorded At",
                    "that_id": 1,
                    "that_index": 0,
                    "that_label": VertexLabel.RELEASE,
                    "this_id": 271046,
                    "this_index": 0,
                    "this_label": VertexLabel.COMPANY,
                },
                {
                    "direction": Direction.THIS_TO_THAT,
                    "name": "Subrelease Of",
                    "that_id": 1660109,
                    "that_index": 0,
                    "that_label": VertexLabel.MASTER,
                    "this_id": 1,
                    "this_index": 0,
                    "this_label": VertexLabel.RELEASE,
                },
                *(
                    {
                        "direction": Direction.THIS_TO_THAT,
                        "name": EdgeLabel.INCLUDED_ON,
                        "that_id": 1,
                        "that_index": 0,
                        "that_label": VertexLabel.RELEASE,
                        "this_id": 1,
                        "this_index": track_index,
                        "this_label": VertexLabel.TRACK,
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
                    "label": VertexLabel.RELEASE,
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
                    "label": VertexLabel.TRACK,
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
                    "label": VertexLabel.TRACK,
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
                    "label": VertexLabel.TRACK,
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
                    "label": VertexLabel.TRACK,
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
                    "label": VertexLabel.TRACK,
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
                    "label": VertexLabel.TRACK,
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
