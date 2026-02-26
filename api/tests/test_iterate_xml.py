import json
from pathlib import Path

from maps import schema


def test_iterate_artists():
    path = Path(__file__).parent / "data" / "discogs_test_artists.xml.gz"
    iterator = schema.Artist.iterate_xml(path)
    artist = next(iterator)
    assert artist == schema.Artist(
        entity_id=1,
        name="The Persuader",
        aliases=[
            schema.Artist(
                entity_id=239, name="Jesper Dahlbäck", aliases=[], groups=[], members=[]
            ),
        ],
    )


def test_iterate_companies():
    path = Path(__file__).parent / "data" / "discogs_test_labels.xml.gz"
    iterator = schema.Company.iterate_xml(path)
    label = next(iterator)
    assert label == schema.Company(
        entity_id=1,
        name="Planet E",
        parent_company=None,
        subsidiaries=[
            schema.Company(entity_id=31405, name="I Ner Zon Sounds"),
            schema.Company(entity_id=1560615, name="Planet E Productions"),
        ],
    )


def test_iterate_masters():
    path = Path(__file__).parent / "data" / "discogs_test_masters.xml.gz"
    iterator = schema.Master.iterate_xml(path)
    master = next(iterator)
    assert master == schema.Master(
        entity_id=18500, main_release_id=155102, name="New Soil"
    )


def test_iterate_releases():
    path = Path(__file__).parent / "data" / "discogs_test_releases.xml.gz"
    iterator = schema.Release.iterate_xml(path)
    release = next(iterator)
    assert release == schema.Release(
        entity_id=1,
        name="Stockholm",
        artists=[schema.Artist(entity_id=1, name="The Persuader")],
        companies=[
            schema.Company(
                entity_id=56025, name="MPO", roles=[schema.Role(name="Pressed By")]
            ),
            schema.Company(
                entity_id=271046,
                name="The Globe Studios",
                roles=[schema.Role(name="Recorded At")],
            ),
        ],
        country="Sweden",
        extra_artists=[
            schema.Artist(
                entity_id=239,
                name="Jesper Dahlbäck",
                roles=[{"name": "Music By", "detail": "All Tracks By"}],
            ),
        ],
        formats=['12"', "33 ⅓ RPM", "Vinyl"],
        genres=["Electronic"],
        is_main_release=True,
        labels=[schema.Company(entity_id=5, name="Svek")],
        master_id=1660109,
        styles=["Deep House"],
        tracks=[
            schema.Track(entity_id=1, index=1, name="Östermalm", position="A"),
            schema.Track(entity_id=1, index=2, name="Vasastaden", position="B1"),
            schema.Track(entity_id=1, index=3, name="Kungsholmen", position="B2"),
            schema.Track(entity_id=1, index=4, name="Södermalm", position="C1"),
            schema.Track(entity_id=1, index=5, name="Norrmalm", position="C2"),
            schema.Track(entity_id=1, index=6, name="Gamla Stan", position="D"),
        ],
        videos=json.dumps(
            [
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
            ]
        ),
        year=1999,
    )
