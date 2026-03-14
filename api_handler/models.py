import pydantic


class MessageColumn(pydantic.BaseModel):
    """
    Represents a single column in a Nortec message row.

    Type is an integer that encodes how the text should be rendered.
    Common values:
        1 (CenterHead)
        2 (Center)
        3 (CenterBold)
        4 (CenterAuto)
        5 (CenterItalic)
        11 (LineHead)
        12 (Line)
        13 (LineBullet)
        14 (LineHTML)
    """

    Cells: list[str]
    Type: int


class MessageRow(pydantic.BaseModel):
    """
    Represents a logical row in a Nortec message, with the full textual payload
    stored under Columns2.
    """

    Columns2: MessageColumn  # TODO: doc says it will be renamed to Columns


class Message(pydantic.BaseModel):
    """
    Top-level Nortec message as returned by the API.
    """

    Name: str
    Title: str
    Description: list[str]
    Rows: list[MessageRow]
    Collapsed: bool
