
from typing import List
from pydantic import BaseModel

class Element(BaseModel):
    kind: int

class TextElement(BaseModel):
    kind: int
    text: str