"""Order processing module with SRP violation."""

import sqlite3
import smtplib


class Order:
    """Handles everything related to orders - violates SRP!"""

    def __init__(self, order_id: str, items: list, customer_email: str):
        self.order_id = order_id
        self.items = items
        self.customer_email = customer_email
        self.total = 0

    def calculate_total(self) -> float:
        """Calculate order total - RESPONSIBILITY #1"""
        self.total = sum(item['price'] * item['quantity'] for item in self.items)
        return self.total

    def apply_discount(self, discount_code: str) -> None:
        """Apply discount logic - RESPONSIBILITY #2"""
        if discount_code == "SAVE10":
            self.total *= 0.9
        elif discount_code == "SAVE20":
            self.total *= 0.8

    def save_to_database(self) -> None:
        """Persist to database - RESPONSIBILITY #3"""
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (id, total, email) VALUES (?, ?, ?)",
            (self.order_id, self.total, self.customer_email)
        )
        conn.commit()
        conn.close()

    def send_confirmation_email(self) -> None:
        """Send email notification - RESPONSIBILITY #4"""
        smtp = smtplib.SMTP('localhost')
        message = f"Order {self.order_id} confirmed. Total: ${self.total}"
        smtp.sendmail('orders@example.com', self.customer_email, message)
        smtp.quit()

    def generate_invoice_pdf(self) -> bytes:
        """Generate PDF invoice - RESPONSIBILITY #5"""
        # PDF generation logic here
        return b"PDF content"


# Usage that shows all responsibilities mixed together
def process_order(order_data: dict) -> None:
    order = Order(
        order_data['id'],
        order_data['items'],
        order_data['email']
    )
    order.calculate_total()
    order.apply_discount(order_data.get('discount_code'))
    order.save_to_database()
    order.send_confirmation_email()
