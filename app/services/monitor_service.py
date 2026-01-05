import httpx
import time
from sqlalchemy.orm import Session
from app.models.monitoring import MonitoringResult
from typing import Optional, Tuple
import math


class MonitorService:
    """
    Service class untuk handle monitoring logic.
    
    Kenapa dipisah ke service layer?
    - Separation of concerns (router cuma handle HTTP, service handle business logic)
    - Gampang di-test (bisa di-mock)
    - Reusable (bisa dipake di cronjob, CLI, etc)
    """
    
    @staticmethod
    async def check_url(url: str) -> Tuple[Optional[int], Optional[float], Optional[str]]:
        """
        Check URL dan return (status_code, response_time_ms, error_message).
        
        Menggunakan httpx AsyncClient untuk fully async operation.
        
        Args:
            url: URL yang mau di-check
            
        Returns:
            Tuple of (status_code, response_time_ms, error_message)
        """
        # httpx.AsyncClient untuk async HTTP requests
        # timeout 10 detik biar ga nunggu kelamaan
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Mulai timer
                start_time = time.perf_counter()
                
                # Kirim GET request (async)
                # follow_redirects=True untuk follow redirect (301, 302)
                response = await client.get(url, follow_redirects=True)
                
                # Stop timer
                end_time = time.perf_counter()
                
                # Hitung response time dalam milliseconds
                response_time_ms = (end_time - start_time) * 1000
                
                return response.status_code, response_time_ms, None
                
            except httpx.TimeoutException:
                # Request timeout (> 10 detik)
                return None, None, "Request timeout (> 10 seconds)"
                
            except httpx.RequestError as e:
                # Network error, DNS error, connection refused, etc
                return None, None, f"Request error: {str(e)}"
                
            except Exception as e:
                # Catch-all untuk error lainnya
                return None, None, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def is_healthy(status_code: Optional[int]) -> bool:
        """
        Tentukan apakah service healthy berdasarkan status code.
        
        Rules:
        - 2xx (200-299): Healthy ✅
        - 3xx (300-399): Healthy (redirect masih OK) ✅
        - 4xx, 5xx, None: Unhealthy ❌
        
        Args:
            status_code: HTTP status code
            
        Returns:
            True jika healthy, False jika unhealthy
        """
        if status_code is None:
            return False
        return 200 <= status_code < 400
    
    @staticmethod
    async def monitor_and_save(db: Session, url: str) -> MonitoringResult:
        """
        Monitor URL dan simpan hasilnya ke database.
        
        Args:
            db: Database session
            url: URL yang mau dimonitor
            
        Returns:
            MonitoringResult object yang sudah disimpan
        """
        # Check URL (async operation)
        status_code, response_time_ms, error_message = await MonitorService.check_url(url)
        
        # Tentukan health status
        is_healthy = MonitorService.is_healthy(status_code)
        
        # Bikin monitoring result object
        result = MonitoringResult(
            url=str(url),  # Convert HttpUrl to string
            status_code=status_code,
            response_time_ms=response_time_ms,
            is_healthy=is_healthy,
            error_message=error_message
        )
        
        # Save ke database
        db.add(result)
        db.commit()
        db.refresh(result)  # Refresh biar dapet ID yang auto-generated
        
        return result
    
    @staticmethod
    def get_all_results(
        db: Session, 
        page: int = 1, 
        page_size: int = 10
    ) -> Tuple[list[MonitoringResult], int]:
        """
        Get semua monitoring results dengan pagination.
        
        Args:
            db: Database session
            page: Halaman yang mau diambil (mulai dari 1)
            page_size: Jumlah item per halaman
            
        Returns:
            Tuple of (results, total_count)
        """
        # Hitung total records
        total = db.query(MonitoringResult).count()
        
        # Hitung offset untuk pagination
        # Contoh: page=2, page_size=10 -> offset=10 (skip 10 items)
        offset = (page - 1) * page_size
        
        # Query dengan limit & offset
        # order_by desc biar yang terbaru muncul duluan
        results = (
            db.query(MonitoringResult)
            .order_by(MonitoringResult.created_at.desc())
            .limit(page_size)
            .offset(offset)
            .all()
        )
        
        return results, total
    
    @staticmethod
    def get_result_by_id(db: Session, result_id: int) -> Optional[MonitoringResult]:
        """
        Get monitoring result by ID.
        
        Args:
            db: Database session
            result_id: ID monitoring result
            
        Returns:
            MonitoringResult object atau None kalau ga ketemu
        """
        return db.query(MonitoringResult).filter(MonitoringResult.id == result_id).first()