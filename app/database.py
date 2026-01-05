from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file
# Ganti ke ":memory:" kalau mau in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///./monitoring.db"

# create_engine adalah factory untuk bikin koneksi database
# check_same_thread=False khusus untuk SQLite agar bisa dipake di multi-thread
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# SessionLocal adalah class untuk bikin database session
# autocommit=False: kita manual commit transaction
# autoflush=False: data ga auto flush ke DB sebelum commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk semua model SQLAlchemy
Base = declarative_base()


# Dependency untuk dapetin database session
def get_db():
    """
    Generator function yang yield database session.
    Setelah request selesai, session otomatis di-close.
    
    Ini pattern yang bagus karena:
    1. Session selalu di-close, ga ada memory leak
    2. Setiap request dapet session baru (isolated)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()