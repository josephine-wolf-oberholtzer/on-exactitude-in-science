from urllib.parse import urlencode

from fastapi import Request

from ..constants import VertexLabel
from ..models import Vertex


def get_vertex_url(request: Request, vertex: Vertex) -> str:
    """
    Get the URL path of the entity endpoint for a vertex.
    """
    label = VertexLabel(vertex.label)
    params = {"id": vertex.id, "label": label.name.lower()}
    if vertex.index:
        params["index"] = vertex.index
    return f"{request.app.url_path_for('get_entity')}?{urlencode(params)}"
