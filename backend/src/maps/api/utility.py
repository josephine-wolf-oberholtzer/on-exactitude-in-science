from fastapi import Request

from ..models import Vertex, VertexLabels


def get_vertex_url(request: Request, vertex: Vertex) -> str:
    """
    Get the URL path of the entity endpoint for a vertex.
    """
    label = VertexLabels(vertex.label)
    params = {"id": vertex.id}
    if label == VertexLabels.TRACK:
        params["index"] = vertex.index
    return str(request.app.url_path_for(f"entity_{label.name.lower()}", **params))
