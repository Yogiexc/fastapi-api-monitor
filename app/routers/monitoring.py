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

    from sqlalchemy import func

@router.get("/stats", response_model=MonitoringStats)
async def get_monitoring_stats(db: Session = Depends(get_db)):
    """
    Get statistik monitoring secara keseluruhan.
    """
    total_checks = db.query(MonitoringResult).count()
    
    if total_checks == 0:
        return MonitoringStats(
            total_checks=0,
            healthy_count=0,
            unhealthy_count=0,
            uptime_percentage=0.0,
            average_response_time_ms=None,
            fastest_response_ms=None,
            slowest_response_ms=None,
            most_monitored_url=None
        )
    
    healthy_count = db.query(MonitoringResult).filter(MonitoringResult.is_healthy == True).count()
    unhealthy_count = total_checks - healthy_count
    uptime_percentage = (healthy_count / total_checks) * 100
    
    # Average response time (exclude None values)
    avg_response = db.query(func.avg(MonitoringResult.response_time_ms)).filter(
        MonitoringResult.response_time_ms.isnot(None)
    ).scalar()
    
    # Fastest response time
    fastest = db.query(func.min(MonitoringResult.response_time_ms)).filter(
        MonitoringResult.response_time_ms.isnot(None)
    ).scalar()
    
    # Slowest response time
    slowest = db.query(func.max(MonitoringResult.response_time_ms)).filter(
        MonitoringResult.response_time_ms.isnot(None)
    ).scalar()
    
    # Most monitored URL
    most_monitored = db.query(
        MonitoringResult.url,
        func.count(MonitoringResult.url).label('count')
    ).group_by(MonitoringResult.url).order_by(func.count(MonitoringResult.url).desc()).first()
    
    return MonitoringStats(
        total_checks=total_checks,
        healthy_count=healthy_count,
        unhealthy_count=unhealthy_count,
        uptime_percentage=round(uptime_percentage, 2),
        average_response_time_ms=round(avg_response, 2) if avg_response else None,
        fastest_response_ms=round(fastest, 2) if fastest else None,
        slowest_response_ms=round(slowest, 2) if slowest else None,
        most_monitored_url=most_monitored[0] if most_monitored else None
    )
    @router.delete("/results/{result_id}", status_code=204)
async def delete_monitoring_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete monitoring result by ID.
    
    Response:
    - 204: Successfully deleted
    - 404: Result not found
    """
    result = MonitorService.get_result_by_id(db, result_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Monitoring result with ID {result_id} not found")
    
    db.delete(result)
    db.commit()

    @router.get("/results/search", response_model=PaginatedMonitorResponse)
async def search_results_by_url(
    url: str = Query(..., description="URL untuk dicari (partial match)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search monitoring results berdasarkan URL (partial match).
    
    Example: 
    - url="google" akan match "https://www.google.com"
    """
    total = db.query(MonitoringResult).filter(MonitoringResult.url.contains(url)).count()
    offset = (page - 1) * page_size
    
    results = (
        db.query(MonitoringResult)
        .filter(MonitoringResult.url.contains(url))
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
