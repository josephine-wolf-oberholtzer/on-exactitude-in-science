import datetime
from typing import TypedDict

from sqlalchemy import Index, String, func, literal_column, text
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

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[VertexLabel] = mapped_column(SMALLINT, primary_key=True)
    index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)

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
        Index("ix_vertices_label_random", "label", "random"),
        Index(
            "ix_vertices_name_trigram",
            text("immutable_unaccent(name) gin_trgm_ops"),
            postgresql_using="gin",
        ),
        Index(
            "ix_vertices_name_ts_vector",
            func.to_tsvector(literal_column("'english'"), name),
            postgresql_using="gin",
        ),
        Index("ix_vertices_random", "random"),
    )


class Edge(Base):
    """
    An edge.
    """

    __tablename__ = "edges"

    this_id: Mapped[int] = mapped_column(primary_key=True)
    this_label: Mapped[VertexLabel] = mapped_column(SMALLINT, primary_key=True)
    this_index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    that_id: Mapped[int] = mapped_column(primary_key=True)
    that_label: Mapped[VertexLabel] = mapped_column(SMALLINT, primary_key=True)
    that_index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    direction: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    dataset: Mapped[datetime.date] = mapped_column(DATE)
