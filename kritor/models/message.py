
from typing import List
from pydantic import BaseModel

class SendMessageResponse(BaseModel):
    message_id: str
    message_time: int
