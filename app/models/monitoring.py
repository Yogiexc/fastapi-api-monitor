from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class MonitoringResult(Base):
    """
    Model untuk menyimpan hasil monitoring.
    
    Setiap row di tabel ini adalah 1x monitoring check.
    """
    __tablename__ = "monitoring_results"

    # Primary key auto-increment
    id = Column(Integer, primary_key=True, index=True)
    
    # URL yang dimonitor
    url = Column(String, nullable=False, index=True)
    
    # HTTP status code (200, 404, 500, etc)
    status_code = Column(Integer, nullable=True)
    
    # Response time dalam milliseconds
    response_time_ms = Column(Float, nullable=True)
    
    # Status kesehatan: True = Healthy, False = Unhealthy
    is_healthy = Column(Boolean, default=False)
    
    # Error message kalau ada masalah (timeout, connection error, etc)
    error_message = Column(String, nullable=True)
    
    # Timestamp otomatis pake server time
    # func.now() adalah fungsi SQL untuk current timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<MonitoringResult(id={self.id}, url={self.url}, status={self.status_code})>"