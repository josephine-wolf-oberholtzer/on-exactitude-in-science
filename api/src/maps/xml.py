import datetime
import gzip
import re
import traceback
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Generator, Sequence, cast
from xml.dom import minidom

import lxml.etree

if TYPE_CHECKING:
    from .schema import Role

date_regex = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
date_no_dashes_regex = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
year_regex = re.compile(r"^\d\d\d\d$")


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


def get_xml_path(directory_path: Path, tag: str) -> Path:
    glob_string = f"discogs_*_{tag}s.xml.gz"
    file_paths = list(directory_path.glob(glob_string))
    if not file_paths:
        raise FileNotFoundError
    file_paths.sort(reverse=True)  # Sorting by timestamp descending
    return file_paths[0]


def build_test_files(source_path: Path, target_path: Path, n: int = 10) -> None:
    for tag in ["artist", "label", "master", "release"]:
        source_file_path = get_xml_path(source_path, tag)
        target_file_path = target_path / f"discogs_test_{tag}s.xml.gz"
        iterator = iterate_xml(source_file_path, tag)
        with gzip.GzipFile(target_file_path, "w") as gzip_file:
            gzip_file.write(b'<?xml version="1.0" ?>\n')
            gzip_file.write(f"<{tag}s>\n".encode())
            for _ in range(n):
                element = next(iterator)
                for line in prettify(element).splitlines()[1:]:  # strip <?xml>
                    gzip_file.write((line + "\n").encode())
            gzip_file.write(f"</{tag}s>\n".encode())


def find_list(element: lxml.etree._Element, name: str) -> Sequence[lxml.etree._Element]:
    if (elements := element.find(name)) is None:
        return []
    return list(elements)


def parse_roles(text: str) -> list["Role"]:
    from .schema import Role

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

    roles: list["Role"] = []
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


def parse_release_date(date_string: str) -> datetime.datetime | None:
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


def validate_release_date(year: str, month: str, day: str) -> datetime.datetime | None:
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
