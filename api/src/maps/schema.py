import dataclasses
import datetime
import random
from pathlib import Path
from typing import Generator, NotRequired, Optional, Self, TypedDict

import lxml.etree
from sqlalchemy.dialects.postgresql import Insert, insert
from sqlalchemy.orm import Session

from . import xml
from .models import (
    Direction,
    Edge,
    EdgeLabels,
    Vertex,
    VertexLabels,
    VideoDict,
)


class VertexDict(TypedDict):
    """
    For use in typing bulk upsert statements.
    """

    country: NotRequired[str | None]
    dataset: datetime.date
    formats: NotRequired[list[str] | None]
    genres: NotRequired[list[str] | None]
    id: int
    index: int
    label: VertexLabels
    name: str
    position: NotRequired[str | None]
    primacy: NotRequired[bool | None]
    random: float
    styles: NotRequired[list[str] | None]
    videos: NotRequired[list[VideoDict] | None]
    year: NotRequired[int | None]


class EdgeDict(TypedDict):
    """
    For use in typing bulk upsert statements.
    """

    this_id: int
    this_label: VertexLabels
    this_index: int
    that_id: int
    that_label: VertexLabels
    that_index: int
    name: str
    direction: int
    dataset: datetime.date


@dataclasses.dataclass(unsafe_hash=True)
class Entity:
    """
    An entity base class.
    """

    id: int
    name: str

    def build_edge_dict(
        self, that: "Entity", name: str, direction: Direction, dataset: datetime.date
    ) -> EdgeDict:
        return EdgeDict(
            this_id=self.id,
            this_label=self.label,
            this_index=int(getattr(self, "index")),
            that_id=that.id,
            that_label=that.label,
            that_index=int(getattr(that, "index")),
            name=name,
            direction=direction,
            dataset=dataset,
        )

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> Self:
        raise NotImplementedError

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator[Self, None, None]:
        """
        Iterate entities from an XML archive.
        """
        for element in xml.iterate_xml(xml_path, cls.__name__.lower()):
            yield cls.from_element(element)

    @classmethod
    def load(cls, *, data_path: Path, dataset: datetime.date, session: Session) -> None:
        def upsert_vertices(values: list[VertexDict]) -> Insert:
            insert_statement = insert(Vertex).values(values)
            index_columns = ["id", "label", "index"]
            update_columns = {
                column.name: column
                for column in insert_statement.excluded
                if column.name not in index_columns
            }
            return insert_statement.on_conflict_do_update(
                index_elements=index_columns, set_=update_columns
            )

        def upsert_edges(values: list[EdgeDict]) -> Insert:
            insert_statement = insert(Edge).values(values)
            index_columns = [
                "this_id",
                "this_label",
                "this_index",
                "that_id",
                "that_label",
                "that_index",
                "direction",
                "name",
            ]
            update_columns = {
                column.name: column
                for column in insert_statement.excluded
                if column.name not in index_columns
            }
            return insert_statement.on_conflict_do_update(
                index_elements=index_columns, set_=update_columns
            )

        xml_path = xml.get_xml_path(data_path, cls.__name__.lower())
        for entity in cls.iterate_xml(xml_path):
            session.execute(upsert_vertices(entity.to_vertex_dicts(dataset)))
            session.execute(upsert_edges(entity.to_edge_dicts(dataset)))
            session.commit()

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        raise NotImplementedError

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        raise NotImplementedError

    @property
    def label(self) -> VertexLabels:
        raise NotImplementedError


@dataclasses.dataclass(unsafe_hash=True)
class Artist(Entity):
    """
    An artist entity.
    """

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
        """
        Instantiate an artist entity from an XML element.
        """
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
        """
        Iterate artist entities from an XML archive.
        """
        for element in xml.iterate_xml(xml_path, "artist"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        """
        Generate edge dicts for bulk upsertion into the database.
        """
        return [
            *(
                self.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.BIDIRECTIONAL,
                    name=EdgeLabels.ALIAS_OF,
                    that=alias,
                )
                for alias in self.aliases
            ),
            *(
                member.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.THIS_TO_THAT,
                    name=EdgeLabels.MEMBER_OF,
                    that=self,
                )
                for member in self.members
            ),
        ]

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        """
        Generate vertex dicts for bulk upsertion into the database.
        """
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

    @property
    def label(self) -> VertexLabels:
        return VertexLabels.ARTIST


@dataclasses.dataclass(unsafe_hash=True)
class Company(Entity):
    """
    A company entity.
    """

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
        """
        Instantiate a company entity from an XML element.
        """
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
        """
        Iterate master entities from an XML archive.
        """
        for element in xml.iterate_xml(xml_path, "label"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        """
        Generate edge dicts for bulk upsertion into the database.
        """
        return [
            *(
                subsidiary.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.THIS_TO_THAT,
                    name=EdgeLabels.SUBSIDIARY_OF,
                    that=self,
                )
                for subsidiary in self.subsidiaries
            ),
        ]

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        """
        Generate vertex dicts for bulk upsertion into the database.
        """
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

    @property
    def label(self) -> VertexLabels:
        return VertexLabels.COMPANY


@dataclasses.dataclass
class Master(Entity):
    """
    A master entity.

    Masters are the "platonic ideal" of a release, allowing for the correlation
    together of multiple releases.
    """

    main_release_id: int

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> "Master":
        """
        Instantiate a master entity from an XML element.
        """
        return Master(
            id=int(element.get("id") or ""),
            name=element.findtext("title") or "",
            main_release_id=int(element.findtext("main_release") or ""),
        )

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator["Master", None, None]:
        """
        Iterate master entities from an XML archive.
        """
        for element in xml.iterate_xml(xml_path, "master"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        return []

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        """
        Generate vertex dicts for bulk upsertion into the database.
        """
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

    @property
    def label(self) -> VertexLabels:
        return VertexLabels.MASTER


@dataclasses.dataclass
class Release(Entity):
    """
    A release entity.
    """

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
    videos: list[VideoDict] | None = None
    year: int | None = None

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> "Release":
        """
        Instantiate an release entity from an XML element.
        """

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

        def get_videos(element: lxml.etree._Element) -> list[VideoDict] | None:
            videos: list[VideoDict] = []
            for video in xml.find_list(element, "videos"):
                title = video.findtext("title")
                url = video.get("src")
                if url and title:
                    videos.append({"title": title, "url": url})
            return None or videos

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
        """
        Iterate release entities from an XML archive.
        """
        for element in xml.iterate_xml(xml_path, "release"):
            yield cls.from_element(element)

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        """
        Generate edge dicts for bulk upsertion into the database.
        """
        edge_dicts: list[EdgeDict] = [
            *(
                self.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.THIS_TO_THAT,
                    name=EdgeLabels.RELEASED_BY,
                    that=artist,
                )
                for artist in self.artists
            ),
            *(
                self.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.THIS_TO_THAT,
                    name=EdgeLabels.RELEASED_ON,
                    that=label,
                )
                for label in self.labels
            ),
            *(
                extra_artist.build_edge_dict(
                    that=self,
                    name=role.name,
                    direction=Direction.THIS_TO_THAT,
                    dataset=dataset,
                )
                for extra_artist in self.extra_artists
                for role in extra_artist.roles
            ),
            *(
                company.build_edge_dict(
                    that=self,
                    name=role.name,
                    direction=Direction.THIS_TO_THAT,
                    dataset=dataset,
                )
                for company in self.companies
                for role in company.roles
            ),
        ]
        if self.master_id is not None:
            edge_dicts.append(
                self.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.THIS_TO_THAT,
                    name="Subrelease Of",
                    that=Master(id=self.master_id, main_release_id=-1, name=""),
                )
            )
        for track in self.tracks:
            edge_dicts.extend(
                [
                    track.build_edge_dict(
                        dataset=dataset,
                        direction=Direction.THIS_TO_THAT,
                        name=EdgeLabels.INCLUDED_ON,
                        that=self,
                    ),
                    *(
                        track.build_edge_dict(
                            that=artist,
                            name=EdgeLabels.RELEASED_BY,
                            direction=Direction.THIS_TO_THAT,
                            dataset=dataset,
                        )
                        for artist in track.artists
                    ),
                    *(
                        extra_artist.build_edge_dict(
                            that=track,
                            name=role.name,
                            direction=Direction.THIS_TO_THAT,
                            dataset=dataset,
                        )
                        for extra_artist in track.extra_artists
                        for role in extra_artist.roles
                    ),
                ]
            )
        return edge_dicts

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        """
        Generate vertex dicts for bulk upsertion into the database.
        """
        vertex_dicts = [
            VertexDict(
                country=self.country,
                dataset=dataset,
                formats=self.formats,
                genres=self.genres,
                id=self.id,
                index=0,
                label=VertexLabels.RELEASE,
                name=self.name,
                primacy=self.is_main_release or self.master_id is None,
                random=random.random(),
                styles=self.styles,
                videos=self.videos,
                year=self.year,
            ),
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
                    primacy=self.is_main_release or self.master_id is None,
                    random=random.random(),
                    styles=self.styles,
                    videos=self.videos,
                    year=self.year,
                )
                for track in self.tracks
            ),
        ]
        return vertex_dicts

    @property
    def label(self) -> VertexLabels:
        return VertexLabels.RELEASE


@dataclasses.dataclass
class Role:
    """
    A role.

    Describes the relationship between two artists and/or companies.
    """

    name: str
    detail: str | None = None


@dataclasses.dataclass
class Track(Entity):
    """
    A track entity.
    """

    index: int
    position: str
    artists: list[Artist] = dataclasses.field(default_factory=list)
    extra_artists: list[Artist] = dataclasses.field(default_factory=list)

    @property
    def label(self) -> VertexLabels:
        return VertexLabels.TRACK
