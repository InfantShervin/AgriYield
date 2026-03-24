import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Provided PostgreSQL connection string with URL-encoded password
# Password: [REDACTED_PASSWORD] -> encoded: [REDACTED_PASSWORD_ENCODED]
DATABASE_URL = "postgresql://postgres:[REDACTED_PASSWORD_ENCODED]@db.rnxiwstzyhfirdixvlkf.supabase.co:5432/postgres"

# Replace 'postgres://' with 'postgresql://' if needed (SQLAlchemy 1.4+ requirement)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    class PredictionRecord(Base):
        __tablename__ = "predictions"
        
        id = Column(Integer, primary_key=True, index=True)
        temperature = Column(Float)
        humidity = Column(Float)
        precipitation = Column(Float)
        soil_ph = Column(Float)
        latitude = Column(Float)
        longitude = Column(Float)
        crop_type = Column(String)
        predicted_yield = Column(Float)
        created_at = Column(DateTime, default=datetime.utcnow)

    # In a real setup, you might run Base.metadata.create_all(bind=engine)
    # But for a Supabase project we might already have the tables or use migrations.
    
except Exception as e:
    print(f"Database connection error: {e}")
    engine = None

def save_prediction(data: dict):
    if not engine:
        return False
    try:
        db = SessionLocal()
        record = PredictionRecord(
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            precipitation=data.get('precipitation'),
            soil_ph=data.get('soil_ph'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            crop_type=data.get('crop_type', 'Unknown'),
            predicted_yield=data.get('predicted_yield')
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        db.close()
        return True
    except Exception as e:
        print(f"Error saving to DB: {e}")
        return False
