import logging
from collections import deque

from aiogremlin.process.graph_traversal import __
from gremlin_python.process.traversal import P

from maps.graphutils import cleanup_edge, cleanup_vertex

logger = logging.getLogger(__name__)


def get_locality_center_projection():
    return (
        __.cap("center")
        .unfold()
        .project("in_roles", "kind", "out_roles", "pageable_edge_count")
        .by(__.inE("relationship").groupCount().by("name"))
        .by(__.constant("center"))
        .by(__.outE("relationship").groupCount().by("name"))
        .by(__.cap("pageableEdges").unfold().count())
    )


def get_locality_edge_projection():
    return (
        __.cap("filteredEdges")
        .unfold()
        .project("id", "kind", "label", "source", "target", "values")
        .by(__.id())
        .by(__.constant("edge"))
        .by(__.label())
        .by(__.outV().id())
        .by(__.inV().id())
        .by(__.valueMap())
    )


def get_locality_vertex_projection():
    return (
        __.cap("vertices")
        .unfold()
        .dedup()
        .project("id", "kind", "label", "values", "total_edge_count", "child_count")
        .by(__.id())
        .by(__.constant("vertex"))
        .by(__.label())
        .by(__.valueMap())
        .by(__.bothE().count())
        .by(
            __.inE("relationship")
            .has("name", P.within("Member Of", "Subsidiary Of", "Subrelease Of"))
            .count()
        )
    )


def get_primacy(labels, main_releases_only):
    primacy = (0, 1, 2)
    if main_releases_only:
        primacy = (0, 1)
    if labels:
        if "Track" not in labels and "Release" not in labels:
            primacy = (0,)
        elif (
            "Artist" not in labels
            and "Company" not in labels
            and "Master" not in labels
        ):
            primacy = (1, 2)
            if main_releases_only:
                primacy = (1,)
    return primacy


def get_locality_loop_traversal(
    countries=None,
    formats=None,
    formats_op="or",
    genres=None,
    labels=None,
    main_releases_only=True,
    offset=0,
    roles=None,
    styles=None,
    styles_op="or",
    years=None,
):
    primacy = get_primacy(labels, main_releases_only)
    traversal = (
        __.timeLimit(1000)
        .bothE("relationship")
        .dedup()
        .has("primacy", P.within(*primacy))
    )
    if roles:
        traversal = traversal.has("name", P.within(*roles))
    other_traversal = __.otherV()
    if labels:
        other_traversal = other_traversal.hasLabel(*(label.lower() for label in labels))
    if 1 in primacy or 2 in primacy:
        traversals = []
        # country, format, genre, style, year
        if countries:
            traversals.append(__.has("country", P.within(*countries)))
        if formats:
            if formats_op == "or":
                traversals.append(__.has("formats", P.within(*formats)))
            else:
                for format_ in formats:
                    traversals.append(__.has("formats", format_))
        if genres:
            traversals.append(__.has("genres", P.within(*genres)))
        if styles:
            if styles_op == "or":
                traversals.append(__.has("styles", P.within(*styles)))
            else:
                for style in styles:
                    traversals.append(__.has("styles", style))
        if years:
            traversals.append(__.has("year", P.within(*years)))
        if traversals:
            traversal = traversal.where(
                other_traversal.choose(
                    __.label().is_(P.within("release", "track")),
                    __.and_(*traversals),
                    __.identity(),
                )
            )
        elif labels:
            traversal = traversal.where(other_traversal)
    elif labels:
        traversal = traversal.where(other_traversal)
    traversal = traversal.choose(
        __.loops().is_(0),
        __.aggregate("pageableEdges").order().range(offset, offset + 50),
        __.limit(10),
    )
    return __.local(traversal).dedup().aggregate("edges").otherV().dedup()


async def get_locality_traversal(
    session,
    vertex_id,
    vertex_label=None,
    limit=200,
    offset=0,
    countries=None,
    formats=None,
    formats_op="or",
    genres=None,
    labels=None,
    main_releases_only=True,
    roles=None,
    styles=None,
    styles_op="or",
    years=None,
):
    traversal = session.g.V(vertex_id)
    if vertex_label:
        traversal = session.g.V().has(vertex_label, f"{vertex_label}_id", vertex_id)
    traversal = traversal.aggregate("center")
    traversal = (
        traversal.aggregate("vertices")
        .repeat(
            get_locality_loop_traversal(
                countries=countries,
                formats=formats,
                formats_op=formats_op,
                genres=genres,
                labels=labels,
                main_releases_only=main_releases_only,
                offset=offset,
                roles=roles,
                styles=styles,
                styles_op=styles_op,
                years=years,
            ),
        )
        .until(
            __.or_(
                __.cap("edges").unfold().count().is_(P.gt(limit)),
                __.loops().is_(10),
            )
        )
        .cap("edges")
        .unfold()
        .limit(limit)
        .aggregate("filteredEdges")
        .bothV()
        .aggregate("vertices")
        .barrier(0)
        .inject(1)
        .union(
            get_locality_edge_projection(),
            get_locality_vertex_projection(),
            get_locality_center_projection(),
        )
    )
    return await traversal.toList()


async def get_locality(
    goblin_app,
    vertex_id,
    vertex_label=None,
    countries=None,
    formats=None,
    formats_op="or",
    genres=None,
    labels=None,
    limit=200,
    main_releases_only=True,
    offset=0,
    roles=None,
    styles=None,
    styles_op="or",
    years=None,
):
    session = await goblin_app.session()
    result = await get_locality_traversal(
        session,
        vertex_id,
        vertex_label=vertex_label,
        countries=countries,
        formats=formats,
        formats_op=formats_op,
        genres=genres,
        labels=labels,
        limit=limit,
        main_releases_only=main_releases_only,
        offset=offset,
        roles=roles,
        styles=styles,
        styles_op=styles_op,
        years=years,
    )
    if not result:
        return None
    return cleanup_locality(goblin_app, vertex_id, vertex_label, result)


def cleanup_locality(goblin_app, vertex_id, vertex_label, result):
    edges = []
    vertices = {}
    center = {}
    for x in result:
        kind = x.pop("kind")
        if kind == "edge":
            edges.append(cleanup_edge(x))
        elif kind == "vertex":
            vertex = cleanup_vertex(x, goblin_app)
            vertices[vertex["id"]] = vertex
        elif kind == "center":
            center = {
                "in_roles": sorted(x["in_roles"]),
                "out_roles": sorted(x["out_roles"]),
                "pageable_edge_count": x["pageable_edge_count"],
            }
    for vertex in vertices.values():
        if (
            vertex_label
            and vertex_label == vertex["label"]
            and vertex["eid"] == vertex_id
        ):
            vertex["depth"] = 0
            vertex.update(center)
        elif vertex_label is None and vertex_id == vertex["id"]:
            vertex["depth"] = 0
            vertex.update(center)
    for edge in edges:
        source = vertices[edge["source"]]
        target = vertices[edge["target"]]
        source["edge_count"] = source.get("edge_count", 0) + 1
        target["edge_count"] = target.get("edge_count", 0) + 1
    edge_deque = deque(edges)
    maximum_depth = 1
    while edge_deque:
        edge = edge_deque.popleft()
        source = vertices[edge["source"]]
        target = vertices[edge["target"]]
        if "depth" in source and "depth" in target:
            continue
        elif "depth" in source:
            target["depth"] = source["depth"] + 1
            if target["depth"] > maximum_depth:
                maximum_depth = target["depth"]
        elif "depth" in target:
            source["depth"] = target["depth"] + 1
            if source["depth"] > maximum_depth:
                maximum_depth = source["depth"]
        else:
            edge_deque.append(edge)
    for vertex in vertices.values():
        vertex["maximum_depth"] = maximum_depth
    return {
        "center": [vertex for vertex in vertices.values() if vertex["depth"] == 0][0],
        "edges": edges,
        "vertices": [vertex for _, vertex in sorted(vertices.items())],
    }
