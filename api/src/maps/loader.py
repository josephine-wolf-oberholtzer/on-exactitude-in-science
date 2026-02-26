from sqlalchemy.dialects.postgresql import insert

from .models import Edge, EdgeDict, Vertex, VertexDict


def upsert_vertices(values: list[VertexDict]) -> None:
    insert_statement = insert(Vertex).values(values)
    update_columns = {
        column.name: column
        for column in insert_statement.excluded
        if column.name not in ["id", "label"]
    }
    update_statement = insert_statement.on_conflict_do_update(
        index_elements=["id", "label"], set_=update_columns
    )
    print(update_statement)


def upsert_edges(values: list[EdgeDict]) -> None:
    insert_statement = insert(Edge).values(values)
    update_columns = {
        column.name: column
        for column in insert_statement.excluded
        if column.name not in ["id", "label"]
    }
    update_statement = insert_statement.on_conflict_do_update(
        index_elements=["id", "label"], set_=update_columns
    )
    print(update_statement)
