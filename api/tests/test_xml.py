import json
from pathlib import Path

from maps import xml


def test_iterate_artists():
    path = Path(__file__).parent / "data" / "discogs_test_artists.xml.gz"
    iterator = xml.iterate_artists(path)
    artist = next(iterator)
    assert artist == xml.Artist(
        entity_id=1,
        name="The Persuader",
        aliases=[
            xml.Artist(
                entity_id=239, name="Jesper Dahlbäck", aliases=[], groups=[], members=[]
            ),
        ],
    )


def test_iterate_companies():
    path = Path(__file__).parent / "data" / "discogs_test_labels.xml.gz"
    iterator = xml.iterate_companies(path)
    label = next(iterator)
    assert label == xml.Company(
        entity_id=1,
        name="Planet E",
        parent_company=None,
        subsidiaries=[
            xml.Company(entity_id=31405, name="I Ner Zon Sounds"),
            xml.Company(entity_id=1560615, name="Planet E Productions"),
        ],
    )


def test_iterate_masters():
    path = Path(__file__).parent / "data" / "discogs_test_masters.xml.gz"
    iterator = xml.iterate_masters(path)
    master = next(iterator)
    assert master == xml.Master(
        entity_id=18500, main_release_id=155102, name="New Soil"
    )


def test_iterate_releases():
    path = Path(__file__).parent / "data" / "discogs_test_releases.xml.gz"
    iterator = xml.iterate_releases(path)
    release = next(iterator)
    assert release == xml.Release(
        entity_id=1,
        name="Stockholm",
        artists=[xml.Artist(entity_id=1, name="The Persuader")],
        companies=[
            xml.Company(
                entity_id=56025, name="MPO", roles=[xml.Role(name="Pressed By")]
            ),
            xml.Company(
                entity_id=271046,
                name="The Globe Studios",
                roles=[xml.Role(name="Recorded At")],
            ),
        ],
        country="Sweden",
        extra_artists=[
            xml.Artist(
                entity_id=239,
                name="Jesper Dahlbäck",
                roles=[{"name": "Music By", "detail": "All Tracks By"}],
            ),
        ],
        formats=['12"', "33 ⅓ RPM", "Vinyl"],
        genres=["Electronic"],
        is_main_release=True,
        labels=[xml.Company(entity_id=5, name="Svek")],
        master_id=1660109,
        styles=["Deep House"],
        tracks=[
            xml.Track(entity_id="1-A", name="Östermalm", position="A"),
            xml.Track(entity_id="1-B1", name="Vasastaden", position="B1"),
            xml.Track(entity_id="1-B2", name="Kungsholmen", position="B2"),
            xml.Track(entity_id="1-C1", name="Södermalm", position="C1"),
            xml.Track(entity_id="1-C2", name="Norrmalm", position="C2"),
            xml.Track(entity_id="1-D", name="Gamla Stan", position="D"),
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
