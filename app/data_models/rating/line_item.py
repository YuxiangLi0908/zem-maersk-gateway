from typing import Optional

from pydantic import BaseModel


class LineItem(BaseModel):
    description: str
    pieces: int
    height: int
    length: int
    width: int
    weight: int
