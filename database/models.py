from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, func
from database.connection import Base

class RawFare(Base):
    __tablename__ = 'raw_fares'
    id = Column(Integer, primary_key=True, index=True)
    scrape_timestamp = Column(DateTime(timezone=True), server_default=func.now(), primary_key=True)
    flight_date = Column(Date, nullable=False)
    route = Column(String(10), nullable=False)
    airline = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    lead_time = Column(String(10), nullable=False)
    base_fare = Column(Numeric(10, 2), nullable=False)
    taxes = Column(Numeric(10, 2), nullable=False)
    udf = Column(Numeric(10, 2), nullable=False)
    conv_fee = Column(Numeric(10, 2), nullable=False)
    total_fare = Column(Numeric(10, 2), nullable=False)

class CleanedFare(Base):
    __tablename__ = 'cleaned_fares'
    id = Column(Integer, primary_key=True, index=True)
    clean_timestamp = Column(DateTime(timezone=True), server_default=func.now(), primary_key=True)
    flight_date = Column(Date, nullable=False)
    route = Column(String(10), nullable=False)
    airline = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    lead_time = Column(String(10), nullable=False)
    total_fare = Column(Numeric(10, 2), nullable=False)

class APIxLog(Base):
    __tablename__ = 'apix_log'
    calculation_date = Column(Date, primary_key=True)
    apix_value = Column(Numeric(10, 4), nullable=False)
    weekly_moving_avg = Column(Numeric(10, 4), nullable=False)
