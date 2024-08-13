from typing import List, Tuple
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)



class RouteRequest(BaseModel):
    num_locations: int
    num_vehicles: int
    locations: List[Tuple[float,float]]
    depot: Tuple[float,float]