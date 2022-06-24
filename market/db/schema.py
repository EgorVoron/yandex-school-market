from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ShopUnit(Base):
    __tablename__ = "ShopUnit"

    unit_id = Column(String, primary_key=True)
    name = Column(String)
    parent_id = Column(String)
    type = Column(String)
    price = Column(Integer)
    date = Column(DateTime)
    level = Column(Integer)

    def __repr__(self):
        return f"{self.unit_id} {self.name}, price: {self.price}"
