from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    national_id = Column(String, unique=True, index=True, nullable=False)
    tickets = relationship("Ticket", back_populates="user")

class Stadium(Base):
    __tablename__ = "stadiums"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    num_gates = Column(Integer, nullable=False)
    num_seats = Column(Integer, nullable=False)
    tickets = relationship("Ticket", back_populates="stadium")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False)
    seat_number = Column(Integer, nullable=False)
    row_number = Column(Integer, nullable=False)
    col_number = Column(Integer, nullable=False)
    gate_number = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    stadium_id = Column(Integer, ForeignKey("stadiums.id"))
    user = relationship("User", back_populates="tickets")
    stadium = relationship("Stadium", back_populates="tickets")