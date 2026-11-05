import datetime
import gzip
import re
from collections.abc import Generator, Sequence
from pathlib import Path
from typing import IO, Any, cast
from xml.dom import minidom

import lxml.etree


def get_xml_path(data_directory_path: Path, tag: str) -> tuple[Path, datetime.date]:
    """
    Given a directory and an XML tag name, find a matching GZIP'd XML archive.
    """
    glob_string = f"discogs_*_{tag}s.xml.gz"
    if not (file_paths := list(data_directory_path.glob(glob_string))):
        raise FileNotFoundError
    file_path = max(file_paths)  # Sorting by timestamp descending
    if match := re.match(rf"discogs_(\d{{6}})_{tag}s.xml.gz", file_path.name):
        return file_path, datetime.date.fromisoformat(match.groups()[0])
    return file_path, datetime.date.today()


def iterate_xml(xml_path: Path, tag: str) -> Generator[lxml.etree._Element]:
    """
    Iterate elements with ``tag`` from a GZIP'd XML archive.

    Do not unpack the entire archive.
    """
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
    """
    Generate a pretty-printable representation of an XML element.
    """
    string = lxml.etree.tostring(element, encoding="utf-8")
    reparsed = minidom.parseString(string)
    return reparsed.toprettyxml(indent=" " * 4)


def build_test_files(source_path: Path, target_path: Path, n: int = 10) -> None:
    """
    Given a source path to real GZIP'd XML archives, generate test archives
    with up to ``n`` elements each.
    """
    for tag in ["artist", "label", "master", "release"]:
        source_file_path, _ = get_xml_path(source_path, tag)
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
    """
    For type-safety, return the children of a found element or an empty list.

    Reduces the number of ``is not None`` checks in our XML parsing.
    """
    if (elements := element.find(name)) is None:
        return []
    return list(elements)
