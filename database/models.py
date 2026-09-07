from sqlalchemy import Column, Integer, String, Date, Numeric
from database.connection import Base, engine

class CleanedFare(Base):
    __tablename__ = 'cleaned_fares'
    id = Column(Integer, primary_key=True, index=True)
    flight_date = Column(String(10), nullable=False)
    route = Column(String(10), nullable=False)
    airline = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    lead_time = Column(String(10), nullable=False)
    total_fare = Column(Numeric(10, 2), nullable=False)

# Auto-create tables on launch (makes initial setup zero-config!)
Base.metadata.create_all(bind=engine)
