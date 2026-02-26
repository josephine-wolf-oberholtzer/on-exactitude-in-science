import dataclasses
import datetime
import json
import random
from pathlib import Path
from typing import Generator, Optional

import lxml.etree

from . import xml
from .models import Direction, EdgeDict, EdgeLabels, VertexDict, VertexLabels


@dataclasses.dataclass(unsafe_hash=True)
class Artist:
    id: int
    name: str
    aliases: list["Artist"] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    groups: list["Artist"] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    members: list["Artist"] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    roles: list["Role"] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> "Artist":
        artist = Artist(
            id=int(element.findtext("id", "")), name=element.findtext("name", "")
        )
        for subelement in xml.find_list(element, "aliases"):
            alias = Artist(
                id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            artist.aliases.append(alias)
        for subelement in xml.find_list(element, "groups"):
            group = Artist(
                id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            artist.groups.append(group)
        for subelement in xml.find_list(element, "members"):
            if subelement.tag == "id":
                continue
            member = Artist(
                id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            artist.members.append(member)
        artist.aliases.sort(key=lambda x: x.id)
        artist.groups.sort(key=lambda x: x.id)
        artist.members.sort(key=lambda x: x.id)
        return artist

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator["Artist", None, None]:
        for element in xml.iterate_xml(xml_path, "artist"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        return [
            *(
                EdgeDict(
                    this_id=self.id,
                    this_label=VertexLabels.ARTIST,
                    this_index=0,
                    that_id=alias.id,
                    that_label=VertexLabels.ARTIST,
                    that_index=0,
                    name=EdgeLabels.ALIAS_OF,
                    direction=bool(Direction.THIS_TO_THAT),
                    dataset=dataset,
                )
                for alias in self.aliases
            ),
            *(
                EdgeDict(
                    this_id=self.id,
                    this_label=VertexLabels.ARTIST,
                    this_index=0,
                    that_id=member.id,
                    that_label=VertexLabels.ARTIST,
                    that_index=0,
                    name=EdgeLabels.MEMBER_OF,
                    direction=bool(Direction.THAT_TO_THIS),
                    dataset=dataset,
                )
                for member in self.members
            ),
        ]

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        return [
            VertexDict(
                dataset=dataset,
                id=self.id,
                index=0,
                label=VertexLabels.ARTIST,
                name=self.name,
                random=random.random(),
            )
        ]


@dataclasses.dataclass(unsafe_hash=True)
class Company:
    id: int
    name: str
    parent_company: Optional["Company"] = dataclasses.field(
        default=None, compare=False, hash=False
    )
    roles: list["Role"] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    subsidiaries: list["Company"] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> "Company":
        company = Company(
            id=int(element.findtext("id", "")), name=element.findtext("name", "")
        )
        if (parent_company := element.find("parentLabel")) is not None:
            company.parent_company = Company(
                id=int(parent_company.get("id") or ""),
                name=parent_company.text or "",
            )
        for subelement in xml.find_list(element, "sublabels"):
            subsidiary = Company(
                id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            company.subsidiaries.append(subsidiary)
        company.subsidiaries.sort(key=lambda x: x.id)
        return company

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator["Company", None, None]:
        for element in xml.iterate_xml(xml_path, "label"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        return [
            *(
                EdgeDict(
                    this_id=self.id,
                    this_label=VertexLabels.COMPANY,
                    this_index=0,
                    that_id=subsidiary.id,
                    that_label=VertexLabels.COMPANY,
                    that_index=0,
                    name=EdgeLabels.SUBSIDIARY_OF,
                    direction=bool(Direction.THAT_TO_THIS),
                    dataset=dataset,
                )
                for subsidiary in self.subsidiaries
            ),
        ]

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        return [
            VertexDict(
                dataset=dataset,
                id=self.id,
                index=0,
                label=VertexLabels.COMPANY,
                name=self.name,
                random=random.random(),
            )
        ]


@dataclasses.dataclass
class Master:
    id: int
    main_release_id: int
    name: str

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> "Master":
        return Master(
            id=int(element.get("id") or ""),
            name=element.findtext("title") or "",
            main_release_id=int(element.findtext("main_release") or ""),
        )

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator["Master", None, None]:
        for element in xml.iterate_xml(xml_path, "master"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        return []

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        return [
            VertexDict(
                dataset=dataset,
                id=self.id,
                index=0,
                label=VertexLabels.MASTER,
                name=self.name,
                random=random.random(),
            )
        ]


@dataclasses.dataclass
class Release:
    id: int
    name: str
    artists: list[Artist] = dataclasses.field(default_factory=list)
    companies: list[Company] = dataclasses.field(default_factory=list)
    country: str | None = None
    extra_artists: list[Artist] = dataclasses.field(default_factory=list)
    formats: list[str] = dataclasses.field(default_factory=list)
    genres: list[str] = dataclasses.field(default_factory=list)
    is_main_release: bool = dataclasses.field(default=False)
    labels: list[Company] = dataclasses.field(default_factory=list)
    master_id: int | None = None
    styles: list[str] = dataclasses.field(default_factory=list)
    tracks: list[Track] = dataclasses.field(default_factory=list)
    videos: str | None = None
    year: int | None = None

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> "Release":
        def get_artists(element: lxml.etree._Element) -> list[Artist]:
            artists: set[Artist] = set()
            for artist in xml.find_list(element, "artists"):
                artists.add(
                    Artist(
                        id=int(artist.findtext("id") or ""),
                        name=artist.findtext("name") or "",
                    )
                )
            return sorted(artists, key=lambda x: x.id)

        def get_companies(element: lxml.etree._Element) -> list[Company]:
            companies: list[Company] = []
            for company in xml.find_list(element, "companies"):
                companies.append(
                    Company(
                        id=int(company.findtext("id") or ""),
                        name=company.findtext("name") or "",
                        roles=xml.parse_roles(
                            company.findtext("entity_type_name") or ""
                        ),
                    )
                )
            return sorted(companies, key=lambda x: x.id)

        def get_country(element: lxml.etree._Element) -> str | None:
            if (country := element.find("country")) is not None:
                return country.text
            return None

        def get_extra_artists(element: lxml.etree._Element) -> list[Artist]:
            extra_artists: list[Artist] = []
            for extra_artist in xml.find_list(element, "extraartists"):
                extra_artists.append(
                    Artist(
                        id=int(extra_artist.findtext("id") or ""),
                        name=extra_artist.findtext("name") or "",
                        roles=xml.parse_roles(extra_artist.findtext("role") or ""),
                    )
                )
            return sorted(extra_artists, key=lambda x: x.id)

        def get_formats(element: lxml.etree._Element) -> list[str]:
            formats: set[str] = set()
            for format_ in xml.find_list(element, "formats"):
                formats.add(format_.get("name") or "")
                for description in xml.find_list(format_, "descriptions"):
                    formats.add(description.text or "")
            return sorted(formats)

        def get_genres(element: lxml.etree._Element) -> list[str]:
            result = []
            for genre in xml.find_list(element, "genres"):
                if genre.text:
                    result.append(genre.text)
            return sorted(set(result))

        def get_labels(element: lxml.etree._Element) -> list[Company]:
            labels: set[Company] = set()
            for label in xml.find_list(element, "labels"):
                labels.add(
                    Company(
                        id=int(label.get("id") or ""),
                        name=label.get("name") or "",
                    )
                )
            return sorted(labels, key=lambda x: x.id)

        def get_master_id(element: lxml.etree._Element) -> int | None:
            if (master_id := element.findtext("master_id")) is not None:
                return int(master_id)
            return None

        def get_is_main_release(element: lxml.etree._Element) -> bool | None:
            if (master_id := element.find("master_id")) is not None:
                return master_id.get("is_main_release") == "true"
            return None

        def get_styles(element: lxml.etree._Element) -> list[str]:
            result = []
            for style in xml.find_list(element, "styles"):
                result.append(style.text or "")
            return sorted(set(result))

        def get_tracks(element: lxml.etree._Element, release_id: int) -> list[Track]:
            tracks: list[Track] = []
            for i, track in enumerate(xml.find_list(element, "tracklist"), 1):
                position = (track.findtext("position") or "").strip() or str(i)
                tracks.append(
                    Track(
                        id=release_id,
                        index=i,
                        name=track.findtext("title") or "",
                        position=position,
                        artists=get_artists(track),
                        extra_artists=get_extra_artists(track),
                    )
                )
            return tracks

        def get_videos(element: lxml.etree._Element) -> str | None:
            videos: list[dict] = []
            for video in xml.find_list(element, "videos"):
                title = video.findtext("title") or ""
                url = video.get("src")
                videos.append({"title": title, "url": url})
            if videos:
                return json.dumps(videos)
            return None

        def get_year(element: lxml.etree._Element) -> int | None:
            if (released := element.findtext("released")) is not None:
                if date := xml.parse_release_date(released):
                    return date.year
            return None

        return Release(
            artists=get_artists(element),
            companies=get_companies(element),
            country=get_country(element),
            extra_artists=get_extra_artists(element),
            formats=get_formats(element),
            genres=get_genres(element),
            id=int(element.get("id") or ""),
            is_main_release=bool(get_is_main_release(element)),
            labels=get_labels(element),
            master_id=get_master_id(element),
            name=element.findtext("title") or "",
            styles=get_styles(element),
            tracks=get_tracks(element, int(element.get("id") or "")),
            videos=get_videos(element),
            year=get_year(element),
        )

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator["Release", None, None]:
        for element in xml.iterate_xml(xml_path, "release"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        return []

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        return [
            VertexDict(
                country=self.country,
                dataset=dataset,
                formats=self.formats,
                genres=self.genres,
                id=self.id,
                index=0,
                label=VertexLabels.RELEASE,
                name=self.name,
                primacy=self.is_main_release,
                random=random.random(),
                styles=self.styles,
                videos=self.videos,
                year=self.year,
            ),
            # and the tracks
            *(
                VertexDict(
                    country=self.country,
                    dataset=dataset,
                    formats=self.formats,
                    genres=self.genres,
                    id=self.id,
                    index=track.index,
                    label=VertexLabels.TRACK,
                    name=track.name,
                    position=track.position,
                    primacy=self.is_main_release,
                    random=random.random(),
                    styles=self.styles,
                    videos=self.videos,
                    year=self.year,
                )
                for track in self.tracks
            ),
        ]


@dataclasses.dataclass
class Role:
    name: str
    detail: str | None = None


@dataclasses.dataclass
class Track:
    id: int
    name: str
    index: int
    position: str
    artists: list[Artist] = dataclasses.field(default_factory=list)
    extra_artists: list[Artist] = dataclasses.field(default_factory=list)
