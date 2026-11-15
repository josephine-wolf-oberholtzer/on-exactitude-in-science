import datetime
from typing import TypedDict

from sqlalchemy import BigInteger, Index, String, text
from sqlalchemy.dialects.postgresql import ARRAY, DATE, JSONB, SMALLINT
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from .constants import VertexLabel


class VideoDict(TypedDict):
    title: str
    url: str


class Base(MappedAsDataclass, DeclarativeBase):
    """
    Base for ORM models.
    """


class Vertex(Base):
    """
    A vertex.
    """

    __tablename__ = "vertices"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, init=False
    )
    # The entity's ID within the Discogs system. Together with the label and the
    # index, it uniquely identifies a vertex.
    eid: Mapped[int]
    label: Mapped[VertexLabel] = mapped_column(SMALLINT)
    index: Mapped[int] = mapped_column(SMALLINT)

    name: Mapped[str] = mapped_column(String)
    random: Mapped[float]
    dataset: Mapped[datetime.date] = mapped_column(DATE)

    country: Mapped[str | None]
    formats: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    genres: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    position: Mapped[str | None]
    primacy: Mapped[bool | None]
    styles: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    videos: Mapped[list[VideoDict] | None] = mapped_column(JSONB)
    year: Mapped[int | None]

    __table_args__ = (
        Index("ix_vertices_label_eid_index", "label", "eid", "index", unique=True),
        Index("ix_vertices_label_random", "label", "random"),
        Index(
            "ix_vertices_name_trigram",
            text("immutable_unaccent(name) gin_trgm_ops"),
            postgresql_using="gin",
        ),
        Index("ix_vertices_random", "random"),
    )


class Edge(Base):
    """
    An edge.
    """

    __tablename__ = "edges"

    this_label: Mapped[VertexLabel] = mapped_column(SMALLINT, primary_key=True)
    this_eid: Mapped[int] = mapped_column(primary_key=True)
    this_index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    that_label: Mapped[VertexLabel] = mapped_column(SMALLINT, primary_key=True)
    that_eid: Mapped[int] = mapped_column(primary_key=True)
    that_index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    direction: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    dataset: Mapped[datetime.date] = mapped_column(DATE)
    computed_id: Mapped[str] = mapped_column(String)
