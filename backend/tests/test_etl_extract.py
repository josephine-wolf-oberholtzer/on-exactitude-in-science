from collections.abc import Iterator

import pytest
from maps.etl import Artist, Company, Master, Release, Role, Track


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
