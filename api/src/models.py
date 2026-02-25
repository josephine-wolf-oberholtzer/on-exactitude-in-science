from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""


class Vertex(Base):
    __tablename__ = "vertices"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    random: Mapped[float]
    created_on: Mapped[int]
    updated_on: Mapped[int]

    country: Mapped[Optional[str]]
    formats: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    genres: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    primacy: Mapped[Optional[bool]]
    styles: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    videos: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    year: Mapped[Optional[int]]


class Edge(Base):
    __tablename__ = "edges"

    this_id: Mapped[int] = mapped_column(primary_key=True)
    this_label: Mapped[str] = mapped_column(primary_key=True)
    that_id: Mapped[int] = mapped_column(primary_key=True)
    that_label: Mapped[str] = mapped_column(primary_key=True)
    direction: Mapped[bool] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    created_on: Mapped[int]
    updated_on: Mapped[int]
