import pytest
from maps.constants import Direction, EdgeLabel, VertexLabel
from maps.etl.entities import _compute_edge_id

ARTIST = int(VertexLabel.ARTIST)
COMPANY = int(VertexLabel.COMPANY)


def test_compute_edge_id_is_stable() -> None:
    """
    The ID is a fixed digest, not Python's per-process ``hash()``.
    """
    assert (
        _compute_edge_id(
            direction=Direction.BIDIRECTIONAL,
            name=EdgeLabel.ALIAS_OF,
            that=(ARTIST, 239, 0),
            this=(ARTIST, 1, 0),
        )
        == "ccda465ebf201c1ac0db4cec8940923a"
    )


@pytest.mark.parametrize(
    "direction",
    [Direction.THIS_TO_THAT, Direction.BIDIRECTIONAL, Direction.THAT_TO_THIS],
)
def test_compute_edge_id_ignores_which_end_is_this(direction: Direction) -> None:
    """
    Swapping the ends (and so the direction) describes the same edge.
    """
    a, b = (ARTIST, 1, 0), (COMPANY, 2, 0)
    assert _compute_edge_id(
        direction=direction, name=EdgeLabel.MEMBER_OF, that=b, this=a
    ) == _compute_edge_id(
        direction=-direction, name=EdgeLabel.MEMBER_OF, that=a, this=b
    )


def test_compute_edge_id_distinguishes_opposite_edges() -> None:
    """
    A to B and B to A are different edges, even though they share both ends.
    """
    a, b = (ARTIST, 1, 0), (COMPANY, 2, 0)
    forward = _compute_edge_id(
        direction=Direction.THIS_TO_THAT, name=EdgeLabel.MEMBER_OF, that=b, this=a
    )
    backward = _compute_edge_id(
        direction=Direction.THIS_TO_THAT, name=EdgeLabel.MEMBER_OF, that=a, this=b
    )
    assert forward != backward


@pytest.mark.parametrize(
    "changes",
    [
        {"name": EdgeLabel.ALIAS_OF},
        {"that": (ARTIST, 3, 0)},
        {"that": (ARTIST, 2, 1)},
        {"direction": Direction.THAT_TO_THIS},
    ],
    ids=["name", "eid", "index", "direction"],
)
def test_compute_edge_id_depends_on_every_field(changes: dict) -> None:
    base: dict = {
        "direction": Direction.THIS_TO_THAT,
        "name": EdgeLabel.MEMBER_OF,
        "that": (ARTIST, 2, 0),
        "this": (ARTIST, 1, 0),
    }
    assert _compute_edge_id(**base) != _compute_edge_id(**{**base, **changes})
