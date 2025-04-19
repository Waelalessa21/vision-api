from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    national_id: str

class StadiumCreate(BaseModel):
    name: str
    num_gates: int
    num_seats: int

class TicketCreate(BaseModel):
    number: Optional[str] = None  
    seat_number: int
    row_number: int
    col_number: int
    gate_number: int
    user_id: int
    stadium_id: int

class VerifyRequest(BaseModel):
    national_id: str
    ticket_number: str