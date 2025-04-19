from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Stadium, Ticket
from schemas import UserCreate, StadiumCreate, TicketCreate, VerifyRequest
import random
import string

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_ticket_number(length=8):
    """Generate a random ticket number"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.national_id == user.national_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="National ID already exists")
    new_user = User(name=user.name, national_id=user.national_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/stadiums/")
def create_stadium(stadium: StadiumCreate, db: Session = Depends(get_db)):
    new_stadium = Stadium(
        name=stadium.name,
        num_gates=stadium.num_gates,
        num_seats=stadium.num_seats
    )
    db.add(new_stadium)
    db.commit()
    db.refresh(new_stadium)
    return new_stadium

@app.get("/stadiums/")
def get_all_stadiums(db: Session = Depends(get_db)):
    stadiums = db.query(Stadium).all()
    return stadiums

@app.post("/tickets/")
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    stadium = db.query(Stadium).filter(Stadium.id == ticket.stadium_id).first()
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")
    
    user = db.query(User).filter(User.id == ticket.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if ticket.gate_number <= 0 or ticket.gate_number > stadium.num_gates:
        raise HTTPException(status_code=400, detail="Invalid gate number")
    
    ticket_number = ticket.number if ticket.number else generate_ticket_number()
    
    new_ticket = Ticket(
        number=ticket_number,
        seat_number=ticket.seat_number,
        row_number=ticket.row_number,
        col_number=ticket.col_number,
        gate_number=ticket.gate_number,
        user_id=ticket.user_id,
        stadium_id=ticket.stadium_id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@app.get("/tickets/")
def get_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return tickets

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.post("/verify/")
def verify_user(data: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.national_id == data.national_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ticket = db.query(Ticket).filter(Ticket.user_id == user.id, Ticket.number == data.ticket_number).first()
    if not ticket:
        raise HTTPException(status_code=401, detail="Invalid ticket number")
    
    stadium = db.query(Stadium).filter(Stadium.id == ticket.stadium_id).first()
    
    return {
        "status": "success",
        "user": {
            "name": user.name,
            "national_id": user.national_id
        },
        "ticket": {
            "number": ticket.number,
            "seat_number": ticket.seat_number,
            "row_number": ticket.row_number,
            "col_number": ticket.col_number,
            "gate_number": ticket.gate_number,
            "stadium": stadium.name
        }
    }

@app.get("/users/by-national-id/{national_id}")
def get_user_by_national_id(national_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.national_id == national_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tickets = db.query(Ticket).filter(Ticket.user_id == user.id).all()
    ticket_details = []
    
    for ticket in tickets:
        stadium = db.query(Stadium).filter(Stadium.id == ticket.stadium_id).first()
        ticket_details.append({
            "number": ticket.number,
            "seat_number": ticket.seat_number,
            "row_number": ticket.row_number,
            "col_number": ticket.col_number,
            "gate_number": ticket.gate_number,
            "stadium": stadium.name
        })
    
    return {
        "id": user.id,
        "name": user.name,
        "national_id": user.national_id,
        "tickets": ticket_details
    }