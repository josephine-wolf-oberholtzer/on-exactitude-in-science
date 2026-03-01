import datetime
import enum
from typing import NotRequired, Optional, TypedDict

from sqlalchemy import Index, String, func
from sqlalchemy.dialects.postgresql import ARRAY, DATE, SMALLINT
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class VertexLabels(enum.IntEnum):
    ARTIST = 0
    COMPANY = 1
    MASTER = 2
    RELEASE = 3
    TRACK = 4


class EdgeLabels(enum.StrEnum):
    ALIAS_OF = "Alias Of"
    INCLUDED_ON = "Included On"
    MEMBER_OF = "Member Of"
    RELEASED_BY = "Released By"
    RELEASED_ON = "Released On"
    SUBRELEASE_OF = "Subrelease Of"
    SUBSIDIARY_OF = "Subsidiary Of"


"""
# OK, but what if it looked like this:
class Direction(enum.IntEnum):
    THIS_TO_THAT = -1
    BIDIRECTIONAL = 0
    THAT_TO_THIS = 1
"""


class Direction(enum.IntEnum):
    THIS_TO_THAT = -1
    BIDIRECTIONAL = 0
    THAT_TO_THIS = 1


class Base(MappedAsDataclass, DeclarativeBase):
    """
    Base for ORM models.
    """

    pass


class Vertex(Base):
    """
    A vertex.
    """

    __tablename__ = "vertices"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[VertexLabels] = mapped_column(SMALLINT, primary_key=True)
    index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)

    name: Mapped[str] = mapped_column(String)
    random: Mapped[float]
    dataset: Mapped[datetime.date] = mapped_column(DATE)

    country: Mapped[Optional[str]]
    formats: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    genres: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    position: Mapped[Optional[str]]
    primacy: Mapped[Optional[bool]]
    styles: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    videos: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    year: Mapped[Optional[int]]

    __table_args__ = (
        Index(
            "ix_vertices_name_ts_vector",
            func.to_tsvector("english", name),
            postgresql_using="gin",
        ),
    )


class Edge(Base):
    """
    An edge.
    """

    __tablename__ = "edges"

    this_id: Mapped[int] = mapped_column(primary_key=True)
    this_label: Mapped[VertexLabels] = mapped_column(SMALLINT, primary_key=True)
    this_index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)

    that_id: Mapped[int] = mapped_column(primary_key=True)
    that_label: Mapped[VertexLabels] = mapped_column(SMALLINT, primary_key=True)
    that_index: Mapped[int] = mapped_column(SMALLINT, primary_key=True)

    direction: Mapped[int] = mapped_column(SMALLINT, primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)

    dataset: Mapped[datetime.date] = mapped_column(DATE)


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
    videos: NotRequired[str | None]
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
