from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Stadium, Ticket
from schemas import UserCreate, StadiumCreate, TicketCreate, VerifyRequest

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/stadiums/")
def create_stadium(stadium: StadiumCreate, db: Session = Depends(get_db)):
    new_stadium = Stadium(name=stadium.name)
    db.add(new_stadium)
    db.commit()
    db.refresh(new_stadium)
    return new_stadium

@app.post("/tickets/")
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = Ticket(number=ticket.number, user_id=ticket.user_id, stadium_id=ticket.stadium_id)
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@app.post("/verify/")
def verify_user(data: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.national_id == data.national_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ticket = db.query(Ticket).filter(Ticket.user_id == user.id, Ticket.number == data.ticket_number).first()
    if not ticket:
        raise HTTPException(status_code=401, detail="Invalid ticket number")
    return {"status": "success", "user": user.name}
