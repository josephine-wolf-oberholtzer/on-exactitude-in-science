import datetime
import gzip
import json
import re
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, Generator, Optional, Sequence, cast
from xml.dom import minidom

import lxml.etree

date_regex = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
date_no_dashes_regex = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
year_regex = re.compile(r"^\d\d\d\d$")


@dataclass
class Role:
    name: str
    detail: str | None = None


@dataclass(unsafe_hash=True)
class Artist:
    entity_id: int
    name: str
    aliases: list["Artist"] = field(default_factory=list, compare=False, hash=False)
    groups: list["Artist"] = field(default_factory=list, compare=False, hash=False)
    members: list["Artist"] = field(default_factory=list, compare=False, hash=False)
    roles: list[Role] = field(default_factory=list, compare=False, hash=False)


@dataclass(unsafe_hash=True)
class Company:
    entity_id: int
    name: str
    parent_company: Optional["Company"] = field(default=None, compare=False, hash=False)
    roles: list[Role] = field(default_factory=list, compare=False, hash=False)
    subsidiaries: list["Company"] = field(
        default_factory=list, compare=False, hash=False
    )


@dataclass
class Master:
    entity_id: int
    main_release_id: int
    name: str


@dataclass
class Track:
    entity_id: str
    name: str
    position: str
    artists: list[Artist] = field(default_factory=list)
    extra_artists: list[Artist] = field(default_factory=list)


@dataclass
class Release:
    entity_id: int
    name: str
    artists: list[Artist] = field(default_factory=list)
    companies: list[Company] = field(default_factory=list)
    country: str | None = None
    extra_artists: list[Artist] = field(default_factory=list)
    formats: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    is_main_release: bool = field(default=False)
    labels: list[Company] = field(default_factory=list)
    master_id: int | None = None
    styles: list[str] = field(default_factory=list)
    tracks: list[Track] = field(default_factory=list)
    videos: str | None = None
    year: int | None = None


def get_xml_path(directory_path: Path, tag: str) -> Path:
    glob_string = "discogs_*_{}s.xml.gz".format(tag)
    file_paths = list(directory_path.glob(glob_string))
    if not file_paths:
        raise FileNotFoundError
    file_paths.sort(reverse=True)  # Sorting by timestamp descending
    return file_paths[0]


def iterate_xml(xml_path: Path, tag: str) -> Generator[lxml.etree._Element, None, None]:
    with gzip.GzipFile(xml_path, "r") as gzip_file:
        context = lxml.etree.iterparse(
            cast(IO[Any], gzip_file), events=["start", "end"]
        )
        _, root = next(context)
        depth = 0
        for event, element in context:
            if element.tag != tag:
                continue
            if event == "start":
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    yield element
                    root.clear()


def prettify(element: lxml.etree._Element) -> str:
    string = lxml.etree.tostring(element, encoding="utf-8")
    reparsed = minidom.parseString(string)
    return reparsed.toprettyxml(indent=" " * 4)


def build_test_files(source_path: Path, target_path: Path, n=10):
    for tag in ["artist", "label", "master", "release"]:
        source_file_path = get_xml_path(source_path, tag)
        target_file_path = target_path / "discogs_test_{}s.xml.gz".format(tag)
        iterator = iterate_xml(source_file_path, tag)
        with gzip.GzipFile(target_file_path, "w") as gzip_file:
            gzip_file.write(b'<?xml version="1.0" ?>\n')
            gzip_file.write("<{}s>\n".format(tag).encode())
            for _ in range(n):
                element = next(iterator)
                for line in prettify(element).splitlines()[1:]:  # strip <?xml>
                    gzip_file.write((line + "\n").encode())
            gzip_file.write("</{}s>\n".format(tag).encode())


def find_list(element: lxml.etree._Element, name: str) -> Sequence[lxml.etree._Element]:
    if (elements := element.find(name)) is None:
        return []
    return list(elements)


def get_artist_iterator(xml_path: Path) -> Generator[Artist, None, None]:
    for element in iterate_xml(xml_path, "artist"):
        artist = Artist(
            entity_id=int(element.findtext("id", "")), name=element.findtext("name", "")
        )
        for subelement in find_list(element, "aliases"):
            alias = Artist(
                entity_id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            artist.aliases.append(alias)
        for subelement in find_list(element, "groups"):
            group = Artist(
                entity_id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            artist.groups.append(group)
        for subelement in find_list(element, "members"):
            if subelement.tag == "id":
                continue
            member = Artist(
                entity_id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            artist.members.append(member)
        artist.aliases.sort(key=lambda x: x.entity_id)
        artist.groups.sort(key=lambda x: x.entity_id)
        artist.members.sort(key=lambda x: x.entity_id)
        yield artist


def get_company_iterator(xml_path: Path) -> Generator[Company, None, None]:
    for element in iterate_xml(xml_path, "label"):
        company = Company(
            entity_id=int(element.findtext("id", "")), name=element.findtext("name", "")
        )
        if (parent_company := element.find("parentLabel")) is not None:
            company.parent_company = Company(
                entity_id=int(parent_company.get("id") or ""),
                name=parent_company.text or "",
            )
        for subelement in find_list(element, "sublabels"):
            subsidiary = Company(
                entity_id=int(subelement.get("id") or ""), name=subelement.text or ""
            )
            company.subsidiaries.append(subsidiary)
        company.subsidiaries.sort(key=lambda x: x.entity_id)
        yield company


def get_master_iterator(xml_path: Path) -> Generator[Master, None, None]:
    for element in iterate_xml(xml_path, "master"):
        master = Master(
            entity_id=int(element.get("id") or ""),
            name=element.findtext("title") or "",
            main_release_id=int(element.findtext("main_release") or ""),
        )
        yield master


def get_release_iterator(xml_path: Path):
    def get_artists(element) -> list[Artist]:
        artists: set[Artist] = set()
        for artist in find_list(element, "artists"):
            artists.add(
                Artist(
                    entity_id=int(artist.findtext("id") or ""),
                    name=artist.findtext("name") or "",
                )
            )
        return sorted(artists, key=lambda x: x.entity_id)

    def get_companies(element) -> list[Company]:
        companies: list[Company] = []
        for company in find_list(element, "companies"):
            companies.append(
                Company(
                    entity_id=int(company.findtext("id") or ""),
                    name=company.findtext("name") or "",
                    roles=parse_roles(company.findtext("entity_type_name") or ""),
                )
            )
        return sorted(companies, key=lambda x: x.entity_id)

    def get_country(element) -> str | None:
        if (country := element.find("country")) is not None:
            return country.text
        return None

    def get_extra_artists(element) -> list[Artist]:
        extra_artists: list[Artist] = []
        for extra_artist in find_list(element, "extraartists"):
            extra_artists.append(
                Artist(
                    entity_id=int(extra_artist.findtext("id") or ""),
                    name=extra_artist.findtext("name") or "",
                    roles=parse_roles(extra_artist.findtext("role") or ""),
                )
            )
        return sorted(extra_artists, key=lambda x: x.entity_id)

    def get_formats(element) -> list[str]:
        formats: set[str] = set()
        for format_ in find_list(element, "formats"):
            formats.add(format_.get("name") or "")
            for description in find_list(format_, "descriptions"):
                formats.add(description.text or "")
        return sorted(formats)

    def get_genres(element) -> list[str]:
        result = []
        for genre in find_list(element, "genres"):
            if genre.text:
                result.append(genre.text)
        return sorted(set(result))

    def get_labels(element) -> list[Company]:
        labels: set[Company] = set()
        for label in find_list(element, "labels"):
            labels.add(
                Company(
                    entity_id=int(label.get("id") or ""), name=label.get("name") or ""
                )
            )
        return sorted(labels, key=lambda x: x.entity_id)

    def get_master_id(element) -> int | None:
        if (master_id := element.find("master_id")) is not None:
            return int(master_id.text)
        return None

    def get_is_main_release(element) -> bool | None:
        if (master_id := element.find("master_id")) is not None:
            return master_id.get("is_main_release") == "true"
        return None

    def get_styles(element) -> list[str]:
        result = []
        for style in find_list(element, "styles"):
            result.append(style.text or "")
        return sorted(set(result))

    def get_tracks(element, release_id) -> list[Track]:
        tracks: list[Track] = []
        for i, track in enumerate(find_list(element, "tracklist"), 1):
            position = (track.findtext("position") or "").strip() or str(i)
            tracks.append(
                Track(
                    entity_id="{}-{}".format(release_id, position),
                    name=track.findtext("title") or "",
                    position=position,
                    artists=get_artists(track),
                    extra_artists=get_extra_artists(track),
                )
            )
        return tracks

    def get_videos(element) -> str | None:
        videos: list[dict] = []
        for video in find_list(element, "videos"):
            title = video.findtext("title") or ""
            url = video.get("src")
            videos.append({"title": title, "url": url})
        if videos:
            return json.dumps(videos)
        return None

    def get_year(element) -> int | None:
        element = element.find("released")
        if element is not None:
            date = parse_release_date(element.text)
            if date:
                return date.year
        return None

    for element in iterate_xml(xml_path, "release"):
        release = Release(
            artists=get_artists(element),
            companies=get_companies(element),
            country=get_country(element),
            extra_artists=get_extra_artists(element),
            formats=get_formats(element),
            genres=get_genres(element),
            entity_id=int(element.get("id") or ""),
            is_main_release=bool(get_is_main_release(element)),
            labels=get_labels(element),
            master_id=get_master_id(element),
            name=element.findtext("title") or "",
            styles=get_styles(element),
            tracks=get_tracks(element, int(element.get("id") or "")),
            videos=get_videos(element),
            year=get_year(element),
        )
        yield release


def parse_roles(text):
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

    roles = []
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
            current_text = current_text.strip()
            if current_text:
                roles.append(from_text(current_text))
            current_text = ""
            continue
        current_text += character
    current_text = current_text.strip()
    if current_text:
        roles.append(from_text(current_text))
    return roles


def parse_release_date(date_string):
    # empty string
    if not date_string:
        return None
    # yyyy-mm-dd
    match = date_regex.match(date_string)
    if match:
        year, month, day = match.groups()
        return validate_release_date(year, month, day)
    # yyyymmdd
    match = date_no_dashes_regex.match(date_string)
    if match:
        year, month, day = match.groups()
        return validate_release_date(year, month, day)
    # yyyy
    match = year_regex.match(date_string)
    if match:
        year, month, day = match.group(), "1", "1"
        return validate_release_date(year, month, day)
    # other: "?", "????", "None", "Unknown"
    return None


def validate_release_date(year, month, day):
    try:
        year = int(year)
        if month.isdigit():
            month = int(month)
        if month < 1:
            month = 1
        if day.isdigit():
            day = int(day)
        if day < 1:
            day = 1
        if 12 < month:
            day, month = month, day
        date = datetime.datetime(year, month, 1, 0, 0)
        day_offset = day - 1
        date = date + datetime.timedelta(days=day_offset)
    except ValueError:
        traceback.print_exc()
        print("BAD DATE:", year, month, day)
        date = None
    return date
