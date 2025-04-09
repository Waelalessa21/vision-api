from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    national_id: str

class StadiumCreate(BaseModel):
    name: str

class TicketCreate(BaseModel):
    number: str
    user_id: int
    stadium_id: int

class VerifyRequest(BaseModel):
    national_id: str
    ticket_number: str
