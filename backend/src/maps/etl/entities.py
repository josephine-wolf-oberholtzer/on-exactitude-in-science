import dataclasses
import datetime
import enum
import json
import logging
import random
import re
import time
import traceback
import uuid
from collections.abc import Generator, Mapping, Sequence
from pathlib import Path
from typing import Any, NotRequired, Self, TypedDict

import lxml.etree
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import DeclarativeBase

from ..constants import Direction, EdgeLabel, VertexLabel
from ..models import Edge, Vertex, VideoDict
from . import xml
from .checkpoint import Checkpoint

logger = logging.getLogger(__name__)

DATE_REGEX = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
DATE_NO_DASHES_REGEX = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
YEAR_REGEX = re.compile(r"^\d\d\d\d$")


class VertexDict(TypedDict):
    """
    For use in typing bulk upsert statements.
    """

    country: NotRequired[str | None]
    dataset: datetime.date
    eid: int
    formats: NotRequired[list[str] | None]
    genres: NotRequired[list[str] | None]
    index: int
    label: VertexLabel
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

    this_eid: int
    this_label: VertexLabel
    this_index: int
    that_eid: int
    that_label: VertexLabel
    that_index: int
    name: str
    direction: int
    dataset: datetime.date


def _encode_value(value: Any, type_: Any) -> Any:
    """
    Coerce a Python value to what asyncpg's binary COPY expects.
    """
    if value is None:
        return None
    if isinstance(type_, JSONB):
        return json.dumps(value)  # asyncpg's default jsonb codec takes text
    if isinstance(value, enum.IntEnum):
        return int(value)
    return value


@dataclasses.dataclass(unsafe_hash=True)
class Entity:
    """
    An entity base class.
    """

    id: int
    name: str

    @staticmethod
    async def _copy_and_merge(
        connection: AsyncConnection,
        model: type[DeclarativeBase],
        rows: Sequence[Mapping[str, Any]],
    ) -> int:
        """
        Upsert rows via a temporary staging table, returning the number of
        distinct rows merged.

        Rows are ``COPY``'d into an unindexed temporary table, then merged into the
        target with a single ``INSERT ... SELECT ... ON CONFLICT DO UPDATE``. The
        staging table is dropped when the current transaction ends.
        """

        def quote(name: str) -> str:
            return f'"{name}"'

        table: Any = model.__table__
        # The database assigns an autoincrementing surrogate key itself, so it is
        # neither copied nor updated.
        columns = [
            column
            for column in table.columns
            if column is not table.autoincrement_column
        ]
        column_names = [column.name for column in columns]
        # Conflicts are detected on the natural key: a unique index if the table
        # has one, otherwise the primary key.
        unique_index = next((index for index in table.indexes if index.unique), None)
        key_names = [
            column.name
            for column in (
                unique_index.columns
                if unique_index is not None
                else table.primary_key.columns
            )
        ]
        # Postgres refuses to update the same row twice in one statement, so
        # collapse duplicate keys up front. The last occurrence wins.
        deduplicated = {tuple(row[name] for name in key_names): row for row in rows}
        records = [
            tuple(
                _encode_value(row.get(column.name), column.type) for column in columns
            )
            for _, row in sorted(deduplicated.items())  # Stable lock order
        ]
        if not records:
            return 0
        uuid4 = str(uuid.uuid4()).replace("-", "")
        temp_table_name = f"{table.name}_import_{uuid4}"
        update_names = [name for name in column_names if name not in key_names]
        quoted_column_names = ", ".join(map(quote, column_names))
        await connection.execute(
            text(
                f"CREATE TEMP TABLE {quote(temp_table_name)} ON COMMIT DROP AS "
                f"SELECT {quoted_column_names} FROM {quote(table.name)} WITH NO DATA"
            )
        )
        raw_connection = await connection.get_raw_connection()
        await raw_connection.driver_connection.copy_records_to_table(  # type: ignore[union-attr]
            f"{temp_table_name}", records=records, columns=column_names
        )
        await connection.execute(
            text(
                f"INSERT INTO {quote(table.name)} ({quoted_column_names}) "
                f"SELECT {quoted_column_names} "
                f"FROM {quote(temp_table_name)} "
                f"ON CONFLICT ({', '.join(map(quote, key_names))}) DO UPDATE SET "
                + ", ".join(
                    f"{quote(name)} = EXCLUDED.{quote(name)}" for name in update_names
                )
            )
        )
        return len(records)

    @classmethod
    async def _flush(
        cls,
        *,
        checkpoint_path: Path | None,
        connection: AsyncConnection,
        date: datetime.date,
        edge_dicts: list[EdgeDict],
        flush_count: int,
        last_entity_id: int | None,
        load_started: float,
        processed_entities: int,
        progress: xml.Progress,
        vertex_dicts: list[VertexDict],
    ) -> tuple[int, int]:
        """
        Merge the buffered dicts, commit, checkpoint and clear the buffers.

        ``flush_count`` is the 1-based number of this flush. Returns the number of
        vertices and edges committed.
        """
        flush_started = time.perf_counter()
        vertex_count = await cls._copy_and_merge(connection, Vertex, vertex_dicts)
        edge_count = await cls._copy_and_merge(connection, Edge, edge_dicts)
        await connection.commit()  # Also drops the temporary tables
        if checkpoint_path is not None and last_entity_id is not None:
            Checkpoint(entity=cls.__name__, last_id=last_entity_id, dataset=date).write(
                checkpoint_path
            )
        vertex_dicts.clear()
        edge_dicts.clear()
        now = time.perf_counter()
        logger.info(
            "... %s flush %d (%.2f%% of file): committed %d vertices and %d edges "
            "from %d entities in %.2fs (%.2fs elapsed)",
            cls.__name__,
            flush_count,
            progress.percentage,
            vertex_count,
            edge_count,
            processed_entities,
            now - flush_started,
            now - load_started,
        )
        return vertex_count, edge_count

    def build_edge_dict(
        self, that: Entity, name: str, direction: Direction, dataset: datetime.date
    ) -> EdgeDict:
        return EdgeDict(
            this_eid=self.id,
            this_label=self.label,
            this_index=int(getattr(self, "index", 0)),
            that_eid=that.id,
            that_label=that.label,
            that_index=int(getattr(that, "index", 0)),
            name=name,
            direction=direction,
            dataset=dataset,
        )

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> Self:
        raise NotImplementedError

    @classmethod
    def get_xml_path(cls, data_directory_path: Path) -> tuple[Path, datetime.date]:
        return xml.get_xml_path(data_directory_path, cls.get_xml_slug())

    @classmethod
    def get_xml_slug(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator[Self]:
        """
        Iterate entities from an XML archive.
        """
        for element in xml.iterate_xml(xml_path, cls.__name__.lower()):
            yield cls.from_element(element)

    @classmethod
    async def load(
        cls,
        *,
        checkpoint_path: Path | None = None,
        chunk_size: int = 50_000,
        connection: AsyncConnection,
        data_directory_path: Path,
        limit: int | None = None,
        resume_after_id: int | None = None,
    ) -> None:
        """
        Load entities in large chunks, using ``COPY`` into a staging table
        followed by a single merge, rather than one upsert per entity.

        If ``checkpoint_path`` is given, record the last committed entity ID there
        after every flush. If ``resume_after_id`` is given, skip entities up to and
        including that ID.
        """

        limit = limit or None
        if limit is not None and limit < 0:
            raise ValueError(limit)

        vertex_dicts: list[VertexDict] = []
        edge_dicts: list[EdgeDict] = []
        flush_count = 0
        total_vertices = 0
        total_edges = 0
        load_started = time.perf_counter()
        xml_path, date = cls.get_xml_path(data_directory_path)
        logger.info(
            "Loading %s from %s (chunk_size=%s limit=%s)",
            cls.__name__,
            xml_path,
            chunk_size,
            limit,
        )
        progress = xml.Progress()
        processed_entities = 0
        last_entity_id: int | None = None
        skipping = resume_after_id is not None
        for element in xml.iterate_xml(xml_path, cls.get_xml_slug(), progress):
            if limit and processed_entities == limit:
                break
            entity = cls.from_element(element)
            if skipping:
                skipping = entity.id != resume_after_id
                continue
            last_entity_id = entity.id
            vertex_dicts.extend(entity.to_vertex_dicts(date))
            edge_dicts.extend(entity.to_edge_dicts(date))
            processed_entities += 1
            if len(vertex_dicts) >= chunk_size or len(edge_dicts) >= chunk_size:
                vertex_count, edge_count = await cls._flush(
                    connection=connection,
                    vertex_dicts=vertex_dicts,
                    edge_dicts=edge_dicts,
                    processed_entities=processed_entities,
                    flush_count=flush_count + 1,
                    checkpoint_path=checkpoint_path,
                    last_entity_id=last_entity_id,
                    date=date,
                    progress=progress,
                    load_started=load_started,
                )
                flush_count += 1
                total_vertices += vertex_count
                total_edges += edge_count
        if skipping:
            raise RuntimeError(
                f"Checkpoint entity ID {resume_after_id} not found in {xml_path}"
            )
        if vertex_dicts or edge_dicts:
            vertex_count, edge_count = await cls._flush(
                connection=connection,
                vertex_dicts=vertex_dicts,
                edge_dicts=edge_dicts,
                processed_entities=processed_entities,
                flush_count=flush_count + 1,
                checkpoint_path=checkpoint_path,
                last_entity_id=last_entity_id,
                date=date,
                progress=progress,
                load_started=load_started,
            )
            flush_count += 1
            total_vertices += vertex_count
            total_edges += edge_count
        logger.info(
            "... Finished loading %s: %d flushes, %d vertices and %d edges committed "
            "in %.2fs",
            cls.__name__,
            flush_count,
            total_vertices,
            total_edges,
            time.perf_counter() - load_started,
        )

    def to_edge_dicts(self, dataset: datetime.date) -> list[EdgeDict]:
        raise NotImplementedError

    def to_vertex_dicts(self, dataset: datetime.date) -> list[VertexDict]:
        raise NotImplementedError

    @property
    def label(self) -> VertexLabel:
        raise NotImplementedError


@dataclasses.dataclass(unsafe_hash=True)
class Artist(Entity):
    """
    An artist entity.
    """

    aliases: list[Artist] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    groups: list[Artist] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    members: list[Artist] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    roles: list[Role] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> Artist:
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
    def iterate_xml(cls, xml_path: Path) -> Generator[Artist]:
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
                    name=EdgeLabel.ALIAS_OF,
                    that=alias,
                )
                for alias in self.aliases
            ),
            *(
                member.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.THIS_TO_THAT,
                    name=EdgeLabel.MEMBER_OF,
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
                eid=self.id,
                index=0,
                label=VertexLabel.ARTIST,
                name=self.name,
                random=random.random(),
            )
        ]

    @property
    def label(self) -> VertexLabel:
        return VertexLabel.ARTIST


@dataclasses.dataclass(unsafe_hash=True)
class Company(Entity):
    """
    A company entity.
    """

    parent_company: Company | None = dataclasses.field(
        default=None, compare=False, hash=False
    )
    roles: list[Role] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )
    subsidiaries: list[Company] = dataclasses.field(
        default_factory=list, compare=False, hash=False
    )

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> Company:
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
    def get_xml_slug(cls) -> str:
        return "label"

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator[Company]:
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
                    name=EdgeLabel.SUBSIDIARY_OF,
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
                eid=self.id,
                index=0,
                label=VertexLabel.COMPANY,
                name=self.name,
                random=random.random(),
            )
        ]

    @property
    def label(self) -> VertexLabel:
        return VertexLabel.COMPANY


@dataclasses.dataclass
class Master(Entity):
    """
    A master entity.

    Masters are the "platonic ideal" of a release, allowing for the correlation
    together of multiple releases.
    """

    main_release_id: int

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> Master:
        """
        Instantiate a master entity from an XML element.
        """
        return Master(
            id=int(element.get("id") or ""),
            name=element.findtext("title") or "",
            main_release_id=int(element.findtext("main_release") or ""),
        )

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator[Master]:
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
                eid=self.id,
                index=0,
                label=VertexLabel.MASTER,
                name=self.name,
                random=random.random(),
            )
        ]

    @property
    def label(self) -> VertexLabel:
        return VertexLabel.MASTER


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
    def _get_artists(cls, element: lxml.etree._Element) -> list[Artist]:
        artists: set[Artist] = set()
        for artist in xml.find_list(element, "artists"):
            if not (artist_id_text := artist.findtext("id")):
                continue
            artists.add(
                Artist(
                    id=int(artist_id_text),
                    name=artist.findtext("name") or "",
                )
            )
        return sorted(artists, key=lambda x: x.id)

    @classmethod
    def _get_companies(cls, element: lxml.etree._Element) -> list[Company]:
        companies: list[Company] = []
        for company in xml.find_list(element, "companies"):
            if not (company_id_text := company.findtext("id")):
                continue
            companies.append(
                Company(
                    id=int(company_id_text),
                    name=company.findtext("name") or "",
                    roles=Role.parse(company.findtext("entity_type_name") or ""),
                )
            )
        return sorted(companies, key=lambda x: x.id)

    @classmethod
    def _get_country(cls, element: lxml.etree._Element) -> str | None:
        if (country := element.find("country")) is not None:
            return country.text
        return None

    @classmethod
    def _get_extra_artists(cls, element: lxml.etree._Element) -> list[Artist]:
        extra_artists: list[Artist] = []
        for extra_artist in xml.find_list(element, "extraartists"):
            if not (extra_artist_id_text := extra_artist.findtext("id")):
                continue
            extra_artists.append(
                Artist(
                    id=int(extra_artist_id_text),
                    name=extra_artist.findtext("name") or "",
                    roles=Role.parse(extra_artist.findtext("role") or ""),
                )
            )
        return sorted(extra_artists, key=lambda x: x.id)

    @classmethod
    def _get_formats(cls, element: lxml.etree._Element) -> list[str]:
        formats: set[str] = set()
        for format_ in xml.find_list(element, "formats"):
            formats.add(format_.get("name") or "")
            for description in xml.find_list(format_, "descriptions"):
                formats.add(description.text or "")
        return sorted(formats)

    @classmethod
    def _get_genres(cls, element: lxml.etree._Element) -> list[str]:
        result = []
        for genre in xml.find_list(element, "genres"):
            if genre.text:
                result.append(genre.text)
        return sorted(set(result))

    @classmethod
    def _get_is_main_release(cls, element: lxml.etree._Element) -> bool | None:
        if (master_id := element.find("master_id")) is not None:
            return master_id.get("is_main_release") == "true"
        return None

    @classmethod
    def _get_labels(cls, element: lxml.etree._Element) -> list[Company]:
        labels: set[Company] = set()
        for label in xml.find_list(element, "labels"):
            if not (label_id_text := label.get("id")):
                continue
            labels.add(
                Company(
                    id=int(label_id_text),
                    name=label.get("name") or "",
                )
            )
        return sorted(labels, key=lambda x: x.id)

    @classmethod
    def _get_master_id(cls, element: lxml.etree._Element) -> int | None:
        if (master_id := element.findtext("master_id")) is not None:
            return int(master_id)
        return None

    @classmethod
    def _get_styles(cls, element: lxml.etree._Element) -> list[str]:
        result = []
        for style in xml.find_list(element, "styles"):
            result.append(style.text or "")
        return sorted(set(result))

    @classmethod
    def _get_tracks(cls, element: lxml.etree._Element, release_id: int) -> list[Track]:
        tracks: list[Track] = []
        for i, track in enumerate(xml.find_list(element, "tracklist"), 1):
            position = (track.findtext("position") or "").strip() or str(i)
            tracks.append(
                Track(
                    id=release_id,
                    index=i,
                    name=track.findtext("title") or "",
                    position=position,
                    artists=cls._get_artists(track),
                    extra_artists=cls._get_extra_artists(track),
                )
            )
        return tracks

    @classmethod
    def _get_videos(cls, element: lxml.etree._Element) -> list[VideoDict] | None:
        videos: list[VideoDict] = []
        for video in xml.find_list(element, "videos"):
            title = video.findtext("title")
            url = video.get("src")
            if url and title:
                videos.append({"title": title, "url": url})
        return None or videos

    @classmethod
    def _get_year(cls, element: lxml.etree._Element) -> int | None:
        if (released := element.findtext("released")) is not None and (
            date := cls._parse_release_date(released)
        ):
            return date.year
        return None

    @staticmethod
    def _parse_release_date(text: str) -> datetime.datetime | None:
        """
        Attempt to parse a string into a Python datetime object or None.
        """

        def validate_release_date(
            year: str, month: str, day: str
        ) -> datetime.datetime | None:
            try:
                year_ = int(year)
                if (month_ := int(month)) < 1:
                    month_ = 1
                if (day_ := int(day)) < 1:
                    day_ = 1
                if 12 < month_:
                    day_, month_ = month_, day_
                date = datetime.datetime(year_, month_, 1, 0, 0)
                return date + datetime.timedelta(days=day_ - 1)
            except ValueError:
                traceback.print_exc()
                print("BAD DATE:", year, month, day)
                return None

        # empty string
        if not text:
            return None

        # yyyy-mm-dd
        if match := DATE_REGEX.match(text):
            year, month, day = match.groups()
            return validate_release_date(year, month, day)
        # yyyymmdd
        if match := DATE_NO_DASHES_REGEX.match(text):
            year, month, day = match.groups()
            return validate_release_date(year, month, day)
        # yyyy
        if match := YEAR_REGEX.match(text):
            year, month, day = match.group(), "1", "1"
            return validate_release_date(year, month, day)
        # other: "?", "????", "None", "Unknown"
        return None

    @classmethod
    def from_element(cls, element: lxml.etree._Element) -> Release:
        """
        Instantiate an release entity from an XML element.
        """

        return Release(
            artists=cls._get_artists(element),
            companies=cls._get_companies(element),
            country=cls._get_country(element),
            extra_artists=cls._get_extra_artists(element),
            formats=cls._get_formats(element),
            genres=cls._get_genres(element),
            id=int(element.get("id") or ""),
            is_main_release=bool(cls._get_is_main_release(element)),
            labels=cls._get_labels(element),
            master_id=cls._get_master_id(element),
            name=element.findtext("title") or "",
            styles=cls._get_styles(element),
            tracks=cls._get_tracks(element, int(element.get("id") or "")),
            videos=cls._get_videos(element),
            year=cls._get_year(element),
        )

    @classmethod
    def iterate_xml(cls, xml_path: Path) -> Generator[Release]:
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
                    name=EdgeLabel.RELEASED_BY,
                    that=artist,
                )
                for artist in self.artists
            ),
            *(
                self.build_edge_dict(
                    dataset=dataset,
                    direction=Direction.THIS_TO_THAT,
                    name=EdgeLabel.RELEASED_ON,
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
                        name=EdgeLabel.INCLUDED_ON,
                        that=self,
                    ),
                    *(
                        track.build_edge_dict(
                            that=artist,
                            name=EdgeLabel.RELEASED_BY,
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
                eid=self.id,
                formats=self.formats,
                genres=self.genres,
                index=0,
                label=VertexLabel.RELEASE,
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
                    eid=self.id,
                    formats=self.formats,
                    genres=self.genres,
                    index=track.index,
                    label=VertexLabel.TRACK,
                    name=track.name,
                    position=track.position,
                    primacy=self.is_main_release or self.master_id is None,
                    random=random.random(),
                    styles=self.styles,
                    year=self.year,
                )
                for track in self.tracks
            ),
        ]
        return vertex_dicts

    @property
    def label(self) -> VertexLabel:
        return VertexLabel.RELEASE


@dataclasses.dataclass
class Role:
    """
    A role.

    Describes the relationship between two artists and/or companies.
    """

    name: str
    detail: str | None = None

    @classmethod
    def parse(cls, text: str) -> list[Role]:
        """
        Attempt to parse a string into a list of role entities.
        """

        def from_text(text):
            name = ""
            current_buffer = ""
            details = []
            had_detail = False
            bracket_depth = 0
            for character in text:
                if character == "[":
                    bracket_depth += 1
                    if bracket_depth == 1 and not had_detail:
                        name = current_buffer
                        current_buffer = ""
                        had_detail = True
                    elif 1 < bracket_depth:
                        current_buffer += character
                elif character == "]":
                    bracket_depth -= 1
                    if not bracket_depth:
                        details.append(current_buffer)
                        current_buffer = ""
                    else:
                        current_buffer += character
                else:
                    current_buffer += character
            if current_buffer and not had_detail:
                name = current_buffer
            name = name.strip()
            detail = ", ".join(_.strip() for _ in details)
            return Role(name=name, detail=detail or None)

        roles: list[Role] = []
        if not text:
            return roles
        current_text = ""
        bracket_depth = 0
        for character in text:
            if character == "[":
                bracket_depth += 1
            elif character == "]":
                bracket_depth -= 1
            elif not bracket_depth and character == ",":
                if current_text := current_text.strip():
                    roles.append(from_text(current_text))
                current_text = ""
                continue
            current_text += character
        if current_text := current_text.strip():
            roles.append(from_text(current_text))
        return roles


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
    def label(self) -> VertexLabel:
        return VertexLabel.TRACK
