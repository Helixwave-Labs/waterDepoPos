from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1 import deps
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    SalesMetrics,
    DailySalesMetrics,
    ProductSalesResponse,
    EmployeeSalesResponse,
    InventoryAnalytics,
    DashboardAnalytics,
)
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/sales-metrics", response_model=SalesMetrics)
def get_sales_metrics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
) -> SalesMetrics:
    """Get sales metrics for a specified period (default last 30 days)"""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    return AnalyticsService.get_sales_metrics(db, start_date, end_date)

@router.get("/daily-sales", response_model=list[DailySalesMetrics])
def get_daily_sales(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
) -> list[DailySalesMetrics]:
    """Get daily sales breakdown for the last N days"""
    return AnalyticsService.get_daily_sales(db, days)

@router.get("/product-sales", response_model=ProductSalesResponse)
def get_product_sales(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
) -> ProductSalesResponse:
    """Get sales analytics by product"""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    return AnalyticsService.get_product_sales(db, start_date, end_date)

@router.get("/employee-sales", response_model=EmployeeSalesResponse)
def get_employee_sales(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
) -> EmployeeSalesResponse:
    """Get sales analytics by employee"""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    return AnalyticsService.get_employee_sales(db, start_date, end_date)

@router.get("/inventory", response_model=InventoryAnalytics)
def get_inventory_analytics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> InventoryAnalytics:
    """Get current inventory status and low stock alerts"""
    return AnalyticsService.get_inventory_analytics(db)

@router.get("/dashboard", response_model=DashboardAnalytics)
def get_dashboard_analytics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
) -> DashboardAnalytics:
    """Get comprehensive dashboard analytics including sales, top products, and inventory"""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    return AnalyticsService.get_dashboard_analytics(db, start_date, end_date)

@router.get("/export/sales", response_class=StreamingResponse)
def export_sales_report(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(30, ge=1, le=365),
    format: str = Query("csv", regex="^(csv)$")
):
    """Export sales metrics as CSV"""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    metrics = AnalyticsService.get_sales_metrics(db, start_date, end_date)
    
    if format == "csv":
        csv_file = ReportService.generate_sales_csv(metrics)
        return StreamingResponse(
            iter([csv_file.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sales_report_{datetime.utcnow().date()}.csv"}
        )

@router.get("/export/inventory", response_class=StreamingResponse)
def export_inventory_report(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    format: str = Query("csv", regex="^(csv)$")
):
    """Export inventory status as CSV"""
    analytics = AnalyticsService.get_inventory_analytics(db)
    
    if format == "csv":
        csv_file = ReportService.generate_inventory_csv(analytics)
        return StreamingResponse(
            iter([csv_file.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=inventory_report_{datetime.utcnow().date()}.csv"}
        )

@router.get("/export/dashboard", response_class=StreamingResponse)
def export_dashboard_report(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    days: int = Query(30, ge=1, le=365),
    format: str = Query("pdf", regex="^(pdf)$")
):
    """Export dashboard analytics as PDF"""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    analytics = AnalyticsService.get_dashboard_analytics(db, start_date, end_date)
    
    if format == "pdf":
        pdf_file = ReportService.generate_dashboard_pdf(analytics)
        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=dashboard_report_{datetime.utcnow().date()}.pdf"}
        )
