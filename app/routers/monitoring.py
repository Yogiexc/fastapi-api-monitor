from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.monitoring import MonitorRequest, MonitorResponse, PaginatedMonitorResponse
from app.services.monitor_service import MonitorService
from typing import List
import math


router = APIRouter(
    prefix="/api/v1",
    tags=["monitoring"]
)


@router.post("/monitor", response_model=MonitorResponse, status_code=201)
async def monitor_url(
    request: MonitorRequest,
    db: Session = Depends(get_db)
):
    """
    Monitor sebuah URL dan simpan hasilnya.
    
    Request body:
```json
    {
        "url": "https://google.com"
    }
```
    
    Response:
    - 201: Monitoring berhasil
    - 422: Validation error (URL invalid)
    """
    # Service layer handle semua business logic
    result = await MonitorService.monitor_and_save(db, request.url)
    return result


@router.get("/results", response_model=PaginatedMonitorResponse)
async def get_monitoring_results(
    page: int = Query(1, ge=1, description="Halaman yang mau diambil (mulai dari 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Jumlah item per halaman (max 100)"),
    db: Session = Depends(get_db)
):
    """
    Get semua monitoring results dengan pagination.
    
    Query parameters:
    - page: Halaman yang mau diambil (default: 1)
    - page_size: Jumlah item per halaman (default: 10, max: 100)
    
    Response:
```json
    {
        "total": 100,
        "page": 1,
        "page_size": 10,
        "total_pages": 10,
        "results": [...]
    }
```
    """
    # Get results dari service layer
    results, total = MonitorService.get_all_results(db, page, page_size)
    
    # Hitung total pages
    # math.ceil buat bulatkan ke atas
    # Contoh: 25 items, page_size=10 -> 3 pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedMonitorResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=results
    )


@router.get("/results/{result_id}", response_model=MonitorResponse)
async def get_monitoring_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    Get monitoring result by ID.
    
    Path parameter:
    - result_id: ID monitoring result
    
    Response:
    - 200: Result ditemukan
    - 404: Result tidak ditemukan
    """
    result = MonitorService.get_result_by_id(db, result_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Monitoring result with ID {result_id} not found")

    @router.get("/results/filter/healthy", response_model=PaginatedMonitorResponse)
async def get_healthy_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get hanya monitoring results yang HEALTHY.
    """
    total = db.query(MonitoringResult).filter(MonitoringResult.is_healthy == True).count()
    offset = (page - 1) * page_size
    
    results = (
        db.query(MonitoringResult)
        .filter(MonitoringResult.is_healthy == True)
        .order_by(MonitoringResult.created_at.desc())
        .limit(page_size)
        .offset(offset)
        .all()
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedMonitorResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=results
    )


@router.get("/results/filter/unhealthy", response_model=PaginatedMonitorResponse)
async def get_unhealthy_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get hanya monitoring results yang UNHEALTHY.
    """
    total = db.query(MonitoringResult).filter(MonitoringResult.is_healthy == False).count()
    offset = (page - 1) * page_size
    
    results = (
        db.query(MonitoringResult)
        .filter(MonitoringResult.is_healthy == False)
        .order_by(MonitoringResult.created_at.desc())
        .limit(page_size)
        .offset(offset)
        .all()
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedMonitorResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=results
    )
    
    return result