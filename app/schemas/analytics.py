from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Sales Analytics
class SalesMetrics(BaseModel):
    total_sales: float
    total_transactions: int
    average_transaction_value: float
    wholesale_sales: float
    retail_sales: float

class DailySalesMetrics(BaseModel):
    date: datetime
    total_sales: float
    transaction_count: int

class ProductSales(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int
    total_revenue: float
    average_price: float

class ProductSalesResponse(BaseModel):
    period: str
    sales: List[ProductSales]
    total_products_sold: int
    total_revenue: float

# Employee Analytics
class EmployeeSalesMetrics(BaseModel):
    user_id: int
    username: str
    total_sales: float
    transaction_count: int
    average_transaction_value: float
    wholesale_sales: float
    retail_sales: float

class EmployeeSalesResponse(BaseModel):
    period: str
    employees: List[EmployeeSalesMetrics]

# Inventory Analytics
class InventoryStatus(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    low_stock_threshold: int
    is_low_stock: bool
    wholesale_price: float
    retail_price: float

class InventoryAnalytics(BaseModel):
    total_products: int
    low_stock_count: int
    average_stock_level: float
    products: List[InventoryStatus]

# Revenue Analytics
class RevenueBreakdown(BaseModel):
    wholesale_revenue: float
    retail_revenue: float
    total_revenue: float
    wholesale_percentage: float
    retail_percentage: float

class TopProduct(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int
    revenue: float

class DashboardAnalytics(BaseModel):
    date_range_start: datetime
    date_range_end: datetime
    total_revenue: float
    total_transactions: int
    average_transaction_value: float
    revenue_breakdown: RevenueBreakdown
    top_products: List[TopProduct]
    low_stock_products: List[InventoryStatus]
    employee_count: int
