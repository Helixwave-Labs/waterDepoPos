import csv
import io
from typing import Any
from app.schemas.analytics import SalesMetrics, InventoryAnalytics, DashboardAnalytics

class ReportService:
    @staticmethod
    def generate_sales_csv(data: SalesMetrics) -> io.StringIO:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Sales", f"{data.total_sales:.2f}"])
        writer.writerow(["Total Transactions", data.total_transactions])
        writer.writerow(["Average Transaction Value", f"{data.average_transaction_value:.2f}"])
        writer.writerow(["Wholesale Sales", f"{data.wholesale_sales:.2f}"])
        writer.writerow(["Retail Sales", f"{data.retail_sales:.2f}"])
        output.seek(0)
        return output

    @staticmethod
    def generate_inventory_csv(data: InventoryAnalytics) -> io.StringIO:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Product Name", "Current Stock", "Low Stock Threshold", "Status", "Wholesale Price", "Retail Price"])
        for product in data.products:
            status = "Low Stock" if product.is_low_stock else "OK"
            writer.writerow([
                product.product_name,
                product.current_stock,
                product.low_stock_threshold,
                status,
                f"{product.wholesale_price:.2f}",
                f"{product.retail_price:.2f}"
            ])
        output.seek(0)
        return output

    @staticmethod
    def generate_dashboard_pdf(data: DashboardAnalytics) -> io.BytesIO:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            raise ImportError("reportlab is required for PDF generation. Install it with `pip install reportlab`.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph(f"Dashboard Report ({data.date_range_start.date()} - {data.date_range_end.date()})", styles['Title']))
        elements.append(Spacer(1, 12))

        # Summary Table
        summary_data = [
            ["Metric", "Value"],
            ["Total Revenue", f"${data.total_revenue:,.2f}"],
            ["Total Transactions", str(data.total_transactions)],
            ["Avg Transaction", f"${data.average_transaction_value:,.2f}"],
            ["Employee Count", str(data.employee_count)]
        ]
        t = Table(summary_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # Revenue Breakdown
        elements.append(Paragraph("Revenue Breakdown", styles['Heading2']))
        rev_data = [
            ["Type", "Revenue", "Percentage"],
            ["Wholesale", f"${data.revenue_breakdown.wholesale_revenue:,.2f}", f"{data.revenue_breakdown.wholesale_percentage:.1f}%"],
            ["Retail", f"${data.revenue_breakdown.retail_revenue:,.2f}", f"{data.revenue_breakdown.retail_percentage:.1f}%"]
        ]
        t_rev = Table(rev_data)
        t_rev.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t_rev)
        elements.append(Spacer(1, 24))

        # Top Products
        elements.append(Paragraph("Top Products", styles['Heading2']))
        top_products_data = [["Product", "Quantity Sold", "Revenue"]]
        for p in data.top_products:
            top_products_data.append([p.product_name, str(p.quantity_sold), f"${p.revenue:,.2f}"])
        
        t2 = Table(top_products_data)
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t2)

        doc.build(elements)
        buffer.seek(0)
        return buffer