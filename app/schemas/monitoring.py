from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List


class MonitorRequest(BaseModel):
    """
    Schema untuk request monitoring.
    
    Pydantic bakal auto-validasi:
    - url harus format URL yang valid (http/https)
    """
    url: HttpUrl = Field(
        ..., 
        description="URL yang mau dimonitor",
        examples=["https://google.com"]
    )

    class Config:
        # Contoh yang muncul di Swagger docs
        json_schema_extra = {
            "example": {
                "url": "https://api.github.com"
            }
        }


class MonitorResponse(BaseModel):
    """
    Schema untuk response monitoring.
    
    Ini yang dikembalikan ke user setelah monitoring selesai.
    """
    id: int
    url: str
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    is_healthy: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        # Biar bisa convert dari SQLAlchemy model
        from_attributes = True


class PaginatedMonitorResponse(BaseModel):
    """
    Schema untuk response paginated.
    
    Contains:
    - total: total semua record di database
    - page: halaman saat ini
    - page_size: jumlah item per halaman
    - total_pages: total jumlah halaman
    - results: list monitoring results
    """
    total: int = Field(..., description="Total semua monitoring results")
    page: int = Field(..., description="Halaman saat ini")
    page_size: int = Field(..., description="Jumlah item per halaman")
    total_pages: int = Field(..., description="Total halaman")
    results: List[MonitorResponse] = Field(..., description="List monitoring results")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10,
                "results": []
            }
        }

    class MonitoringStats(BaseModel):
    """
    Schema untuk statistik monitoring.
    """
    total_checks: int
    healthy_count: int
    unhealthy_count: int
    uptime_percentage: float
    average_response_time_ms: Optional[float]
    fastest_response_ms: Optional[float]
    slowest_response_ms: Optional[float]
    most_monitored_url: Optional[str]

    class BatchMonitorRequest(BaseModel):
    """
    Schema untuk batch monitoring.
    """
    urls: List[HttpUrl] = Field(
        ..., 
        min_length=1, 
        max_length=10,
        description="List URLs yang mau dimonitor (max 10)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://google.com",
                    "https://github.com",
                    "https://stackoverflow.com"
                ]
            }
        }


class BatchMonitorResponse(BaseModel):
    """
    Schema untuk response batch monitoring.
    """
    total_monitored: int
    results: List[MonitorResponse]