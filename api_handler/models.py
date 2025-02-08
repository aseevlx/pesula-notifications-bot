from dataclasses import dataclass
import pydantic


@dataclass
class MessageColumn(pydantic.BaseModel):
    """
    Possible values for type (will use plain int, it's not needed in our case):
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


@dataclass
class MessageRow(pydantic.BaseModel):
    Columns2: MessageColumn  # TODO: doc says it will be renamed to Columns


class Message(pydantic.BaseModel):
    Name: str
    Title: str
    Description: list[str]
    Rows: list[MessageRow]
    Collapsed: bool
