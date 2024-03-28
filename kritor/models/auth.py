
from typing import List
from pydantic import BaseModel

class GetTicketResponse(BaseModel):
    code: int
    msg: str
    tickets: List[str]

class AddTicketResponse(BaseModel):
    code: int
    msg: str

class DeleteTicketResponse(BaseModel):
    code: int
    msg: str

class GetAuthenticationStateResponse(BaseModel):
    is_required: bool

class AuthenticateResponse(BaseModel):
    code: int
    msg: str