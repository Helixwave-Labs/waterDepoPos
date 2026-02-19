from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.transaction import Transaction, TransactionItem, SaleType
from app.models.product import Product
from app.models.user import User
from app.schemas.analytics import (
    SalesMetrics,
    DailySalesMetrics,
    ProductSales,
    ProductSalesResponse,
    EmployeeSalesMetrics,
    EmployeeSalesResponse,
    InventoryStatus,
    InventoryAnalytics,
    RevenueBreakdown,
    TopProduct,
    DashboardAnalytics,
)

class AnalyticsService:
    @staticmethod
    def get_sales_metrics(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> SalesMetrics:
        """Get overall sales metrics for a period"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        query = db.query(Transaction).filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )

        wholesale = query.filter(Transaction.sale_type == SaleType.WHOLESALE)
        retail = query.filter(Transaction.sale_type == SaleType.RETAIL)

        total_sales = query.with_entities(func.sum(Transaction.total_amount)).scalar() or 0.0
        total_transactions = query.count()
        wholesale_sales = wholesale.with_entities(func.sum(Transaction.total_amount)).scalar() or 0.0
        retail_sales = retail.with_entities(func.sum(Transaction.total_amount)).scalar() or 0.0

        return SalesMetrics(
            total_sales=float(total_sales),
            total_transactions=total_transactions,
            average_transaction_value=float(total_sales) / total_transactions if total_transactions > 0 else 0.0,
            wholesale_sales=float(wholesale_sales),
            retail_sales=float(retail_sales),
        )

    @staticmethod
    def get_daily_sales(db: Session, days: int = 30) -> List[DailySalesMetrics]:
        """Get daily sales metrics for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        daily_sales = db.query(
            func.date(Transaction.created_at).label('date'),
            func.sum(Transaction.total_amount).label('total_sales'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            Transaction.created_at >= start_date
        ).group_by(
            func.date(Transaction.created_at)
        ).order_by(
            func.date(Transaction.created_at)
        ).all()

        return [
            DailySalesMetrics(
                date=day.date,
                total_sales=float(day.total_sales or 0),
                transaction_count=day.transaction_count or 0
            )
            for day in daily_sales
        ]

    @staticmethod
    def get_product_sales(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> ProductSalesResponse:
        """Get product sales analytics"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        product_stats = db.query(
            Product.id,
            Product.name,
            func.sum(TransactionItem.quantity).label('quantity_sold'),
            func.sum(TransactionItem.quantity * TransactionItem.price_at_sale).label('total_revenue'),
            func.avg(TransactionItem.price_at_sale).label('average_price')
        ).join(
            TransactionItem, Product.id == TransactionItem.product_id
        ).join(
            Transaction, TransactionItem.transaction_id == Transaction.id
        ).filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        ).group_by(
            Product.id, Product.name
        ).order_by(
            func.sum(TransactionItem.quantity * TransactionItem.price_at_sale).desc()
        ).all()

        sales = [
            ProductSales(
                product_id=str(stat.id),
                product_name=stat.name,
                quantity_sold=stat.quantity_sold or 0,
                total_revenue=float(stat.total_revenue or 0),
                average_price=float(stat.average_price or 0),
            )
            for stat in product_stats
        ]

        total_quantity = sum(s.quantity_sold for s in sales)
        total_revenue = sum(s.total_revenue for s in sales)

        return ProductSalesResponse(
            period=f"{start_date.date()} to {end_date.date()}",
            sales=sales,
            total_products_sold=total_quantity,
            total_revenue=total_revenue,
        )

    @staticmethod
    def get_employee_sales(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> EmployeeSalesResponse:
        """Get sales metrics by employee"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        employee_stats = db.query(
            User.id,
            User.username,
            func.sum(Transaction.total_amount).label('total_sales'),
            func.count(Transaction.id).label('transaction_count'),
            func.sum(
                func.case(
                    (Transaction.sale_type == SaleType.WHOLESALE, Transaction.total_amount),
                    else_=0
                )
            ).label('wholesale_sales'),
            func.sum(
                func.case(
                    (Transaction.sale_type == SaleType.RETAIL, Transaction.total_amount),
                    else_=0
                )
            ).label('retail_sales'),
        ).join(
            Transaction, User.id == Transaction.user_id
        ).filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        ).group_by(
            User.id, User.username
        ).order_by(
            func.sum(Transaction.total_amount).desc()
        ).all()

        employees = [
            EmployeeSalesMetrics(
                user_id=str(stat.id),
                username=stat.username,
                total_sales=float(stat.total_sales or 0),
                transaction_count=stat.transaction_count or 0,
                average_transaction_value=float(stat.total_sales or 0) / (stat.transaction_count or 1),
                wholesale_sales=float(stat.wholesale_sales or 0),
                retail_sales=float(stat.retail_sales or 0),
            )
            for stat in employee_stats
        ]

        return EmployeeSalesResponse(
            period=f"{start_date.date()} to {end_date.date()}",
            employees=employees,
        )

    @staticmethod
    def get_inventory_analytics(db: Session) -> InventoryAnalytics:
        """Get inventory status and low stock alerts"""
        products = db.query(Product).filter(Product.is_active == True).all()

        inventory_items = [
            InventoryStatus(
                product_id=str(p.id),
                product_name=getattr(p, "name", ""),
                current_stock=getattr(p, "stock_quantity", 0),
                low_stock_threshold=getattr(p, "low_stock_threshold", 0),
                is_low_stock=(getattr(p, "stock_quantity", 0) <= getattr(p, "low_stock_threshold", 0)),
                wholesale_price=getattr(p, "wholesale_price", 0.0),
                retail_price=getattr(p, "retail_price", 0.0),
            )
            for p in products
        ]

        low_stock = [item for item in inventory_items if item.is_low_stock]
        avg_stock = sum(item.current_stock for item in inventory_items) / len(inventory_items) if inventory_items else 0

        return InventoryAnalytics(
            total_products=len(inventory_items),
            low_stock_count=len(low_stock),
            average_stock_level=avg_stock,
            products=inventory_items,
        )

    @staticmethod
    def get_dashboard_analytics(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> DashboardAnalytics:
        """Get comprehensive dashboard analytics"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        query = db.query(Transaction).filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )

        total_transactions = query.count()
        total_revenue = query.with_entities(func.sum(Transaction.total_amount)).scalar() or 0.0
        avg_transaction = float(total_revenue) / total_transactions if total_transactions > 0 else 0.0

        wholesale_revenue = query.filter(
            Transaction.sale_type == SaleType.WHOLESALE
        ).with_entities(func.sum(Transaction.total_amount)).scalar() or 0.0

        retail_revenue = query.filter(
            Transaction.sale_type == SaleType.RETAIL
        ).with_entities(func.sum(Transaction.total_amount)).scalar() or 0.0

        if total_revenue > 0:
            wholesale_pct = (float(wholesale_revenue) / float(total_revenue)) * 100
            retail_pct = (float(retail_revenue) / float(total_revenue)) * 100
        else:
            wholesale_pct = 0.0
            retail_pct = 0.0

        top_products_data = db.query(
            Product.id,
            Product.name,
            func.sum(TransactionItem.quantity).label('quantity_sold'),
            func.sum(TransactionItem.quantity * TransactionItem.price_at_sale).label('revenue')
        ).join(
            TransactionItem, Product.id == TransactionItem.product_id
        ).join(
            Transaction, TransactionItem.transaction_id == Transaction.id
        ).filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        ).group_by(
            Product.id, Product.name
        ).order_by(
            func.sum(TransactionItem.quantity * TransactionItem.price_at_sale).desc()
        ).limit(5).all()

        top_products = [
            TopProduct(
                product_id=str(p.id),
                product_name=p.name,
                quantity_sold=p.quantity_sold or 0,
                revenue=float(p.revenue or 0),
            )
            for p in top_products_data
        ]

        # Get low stock products
        low_stock_products = db.query(Product).filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.low_stock_threshold
        ).all()

        low_stock_list = [
            InventoryStatus(
                product_id=str(p.id),
                product_name=getattr(p, "name", ""),
                current_stock=getattr(p, "stock_quantity", 0),
                low_stock_threshold=getattr(p, "low_stock_threshold", 0),
                is_low_stock=True,
                wholesale_price=getattr(p, "wholesale_price", 0.0),
                retail_price=getattr(p, "retail_price", 0.0),
            )
            for p in low_stock_products
        ]

        # Get employee count
        employee_count = db.query(User).filter(User.is_active == True).count()

        return DashboardAnalytics(
            date_range_start=start_date,
            date_range_end=end_date,
            total_revenue=float(total_revenue),
            total_transactions=total_transactions,
            average_transaction_value=avg_transaction,
            revenue_breakdown=RevenueBreakdown(
                wholesale_revenue=float(wholesale_revenue),
                retail_revenue=float(retail_revenue),
                total_revenue=float(total_revenue),
                wholesale_percentage=wholesale_pct,
                retail_percentage=retail_pct,
            ),
            top_products=top_products,
            low_stock_products=low_stock_list,
            employee_count=employee_count,
        )
