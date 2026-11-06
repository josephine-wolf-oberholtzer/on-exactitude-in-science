import enum


class Direction(enum.IntEnum):
    THIS_TO_THAT = -1
    BIDIRECTIONAL = 0
    THAT_TO_THIS = 1


class EdgeLabel(enum.StrEnum):
    ALIAS_OF = "Alias Of"
    INCLUDED_ON = "Included On"
    MEMBER_OF = "Member Of"
    RELEASED_BY = "Released By"
    RELEASED_ON = "Released On"
    SUBRELEASE_OF = "Subrelease Of"
    SUBSIDIARY_OF = "Subsidiary Of"


class VertexLabelName(enum.StrEnum):
    """
    The names of the vertex labels, as they appear in URLs.
    """

    ARTIST = "artist"
    COMPANY = "company"
    MASTER = "master"
    RELEASE = "release"
    TRACK = "track"


class VertexLabel(enum.IntEnum):
    ARTIST = 0
    COMPANY = 1
    MASTER = 2
    RELEASE = 3
    TRACK = 4
