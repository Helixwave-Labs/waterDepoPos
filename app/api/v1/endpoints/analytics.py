from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
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
