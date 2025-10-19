"""User service with DIP violation - hard-coded dependencies."""

import sqlite3
import smtplib
from datetime import datetime


class UserService:
    """User management service - violates DIP!"""

    def __init__(self):
        # Hard-coded concrete dependencies - violates DIP!
        self.db = sqlite3.connect('users.db')
        self.smtp = smtplib.SMTP('mail.example.com', 587)

    def register_user(self, name: str, email: str, password: str) -> dict:
        """Register a new user - impossible to test without real database and SMTP."""
        # Validation
        if not email or '@' not in email:
            raise ValueError("Invalid email")

        # Check if user exists - tightly coupled to SQLite
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            raise ValueError("User already exists")

        # Hash password - at least this is separate!
        hashed_password = self._hash_password(password)

        # Save to database - tightly coupled to SQLite
        user_id = self._generate_user_id()
        cursor.execute(
            "INSERT INTO users (id, name, email, password, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, hashed_password, datetime.now())
        )
        self.db.commit()

        # Send welcome email - tightly coupled to SMTP
        message = f"Welcome {name}! Your account has been created."
        self.smtp.sendmail('noreply@example.com', email, message)

        return {"id": user_id, "name": name, "email": email}

    def _hash_password(self, password: str) -> str:
        """Hash password - good, this is separate."""
        # Simplified for example
        return f"hashed_{password}"

    def _generate_user_id(self) -> str:
        """Generate unique user ID."""
        return f"user_{datetime.now().timestamp()}"


class OrderService:
    """Another service with the same problem - also violates DIP!"""

    def __init__(self):
        # Hard-coded dependencies again!
        self.db = sqlite3.connect('orders.db')
        self.email_client = smtplib.SMTP('mail.example.com', 587)

    def create_order(self, user_id: str, items: list) -> dict:
        """Create order - can't test without real database and email."""
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in items)

        # Save to database
        cursor = self.db.cursor()
        order_id = f"order_{datetime.now().timestamp()}"
        cursor.execute(
            "INSERT INTO orders (id, user_id, total) VALUES (?, ?, ?)",
            (order_id, user_id, total)
        )
        self.db.commit()

        # Send confirmation email
        cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        user_email = cursor.fetchone()[0]
        self.email_client.sendmail(
            'orders@example.com',
            user_email,
            f"Order {order_id} confirmed. Total: ${total}"
        )

        return {"id": order_id, "total": total}


# Usage - impossible to test without real infrastructure
def main() -> None:
    user_service = UserService()
    user = user_service.register_user("Alice", "alice@example.com", "password123")

    order_service = OrderService()
    order = order_service.create_order(
        user['id'],
        [{"price": 10.0, "quantity": 2}]
    )
