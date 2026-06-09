from clothing_erp.repositories.json_repository import JSONRepository
from clothing_erp.config import TAX_RATE, CURRENCY


class ReportService:
    def __init__(self, repository: JSONRepository):
        self.repository = repository

    def get_all_products(self) -> list:
        return self.repository.get_all_products()

    def get_sales_summary(self) -> dict:
        """
        Returns a summary dict with:
          - total_sales  : number of sales transactions
          - total_items  : total units sold across all sales
          - revenue      : gross revenue (subtotal before tax)
          - tax_collected: total tax collected
          - grand_total  : revenue + tax
        """
        sales = self.repository.get_all_sales()
        total_items = 0
        revenue = 0.0
        tax_collected = 0.0

        for sale in sales:
            for item in sale.items:
                total_items += item.quantity
            revenue += sale.subtotal
            tax_collected += sale.tax

        return {
            "total_sales": len(sales),
            "total_items": total_items,
            "revenue": round(revenue, 2),
            "tax_collected": round(tax_collected, 2),
            "grand_total": round(revenue + tax_collected, 2),
        }