import json

from aiogremlin.process.graph_traversal import __
from gremlin_python.process.traversal import Cardinality, P


def cleanup_edge(result):
    result["id"] = result["id"]["@value"]["relationId"]
    result.update(result.pop("values", {}))
    if "role" not in result:
        result["role"] = result["label"].replace("_", " ").title()
    return result


def cleanup_values(label, values, goblin_app):
    vertex = goblin_app.vertices[label]
    for key, value in values.items():
        cardinality = Cardinality.single
        prop = vertex.__properties__.get(key)
        if prop is not None:
            cardinality = getattr(prop, "cardinality", Cardinality.single)
        if value and cardinality == Cardinality.single:
            values[key] = value[0]
        if key == "videos" and values[key]:
            values[key] = json.loads(values[key])


def cleanup_vertex(result, goblin_app):
    cleanup_values(result["label"], result["values"], goblin_app)
    result["eid"] = result["values"].pop(result["label"] + "_id")
    result.update(result.pop("values"))
    if extra := result.pop("extra", None):
        cleanup_values("release", extra, goblin_app)
        for key, value in extra.items():
            if key.endswith("_id"):
                continue
            elif key == "name":
                key = f"release_{key}"
            result[key] = value
    if in_roles := sorted(result.pop("in_roles", {})):
        result["in_roles"] = in_roles
    if out_roles := sorted(result.pop("out_roles", {})):
        result["out_roles"] = out_roles
    return result


def project_vertex(traversal, **extra_traversals):
    traversal = (
        traversal.project(
            "id",
            "label",
            "values",
            "total_edge_count",
            "child_count",
            "extra",
            "in_roles",
            "out_roles",
            *sorted(extra_traversals.keys()),
        )
        .by(__.id())
        .by(__.label())
        .by(__.valueMap())
        .by(__.bothE().count())
        .by(make_child_count_traversal())
        .by(make_track_extras_traversal())
        .by(__.inE("relationship").groupCount().by("name"))
        .by(__.outE("relationship").groupCount().by("name"))
    )
    for _, extra_traversal in sorted(extra_traversals.items()):
        traversal = traversal.by(extra_traversal)
    return traversal


def make_child_count_traversal():
    return (
        __.inE("relationship")
        .has("name", P.within("Member Of", "Subsidiary Of", "Subrelease Of"))
        .count()
    )


def make_track_extras_traversal():
    return __.choose(
        __.inE("relationship").has("name", "Includes").count().is_(P.gt(0)),
        __.inE("relationship").has("name", "Includes").otherV().valueMap(),
        __.constant(False),
    )
