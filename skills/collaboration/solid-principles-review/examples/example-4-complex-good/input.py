"""Well-designed order processing system following SOLID principles."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol
from decimal import Decimal


# Domain models (SRP - just data structures)
@dataclass
class Product:
    """Product data structure."""
    id: str
    name: str
    price: Decimal


@dataclass
class OrderItem:
    """Order item data structure."""
    product: Product
    quantity: int


@dataclass
class Order:
    """Order data structure."""
    id: str
    items: list[OrderItem]
    customer_email: str
    total: Decimal = Decimal('0')


# Abstractions (DIP + ISP - small, focused interfaces)
class PriceCalculator(Protocol):
    """Protocol for price calculation (ISP - minimal interface)."""

    def calculate_total(self, items: list[OrderItem]) -> Decimal:
        """Calculate total price for items."""
        ...


class DiscountStrategy(ABC):
    """Abstract discount strategy (OCP - extensible via subclasses)."""

    @abstractmethod
    def calculate_discount(self, total: Decimal) -> Decimal:
        """Calculate discount amount."""
        pass


class OrderRepository(Protocol):
    """Protocol for order persistence (DIP + ISP)."""

    def save(self, order: Order) -> None:
        """Save order to storage."""
        ...

    def find_by_id(self, order_id: str) -> Order | None:
        """Find order by ID."""
        ...


class NotificationService(Protocol):
    """Protocol for notifications (DIP + ISP)."""

    def send_order_confirmation(self, order: Order) -> None:
        """Send order confirmation."""
        ...


# Implementations (SRP - each class has one responsibility)
class StandardPriceCalculator:
    """Calculates order total (SRP)."""

    def calculate_total(self, items: list[OrderItem]) -> Decimal:
        """Calculate total from items."""
        return sum(
            item.product.price * item.quantity
            for item in items
        )


class PercentageDiscount(DiscountStrategy):
    """Percentage-based discount (OCP - can add new strategies)."""

    def __init__(self, percentage: int):
        self.percentage = percentage

    def calculate_discount(self, total: Decimal) -> Decimal:
        """Calculate percentage discount."""
        return total * (Decimal(self.percentage) / Decimal('100'))


class VIPDiscount(DiscountStrategy):
    """VIP customer discount (OCP - another strategy)."""

    def calculate_discount(self, total: Decimal) -> Decimal:
        """Calculate VIP discount based on total."""
        if total > Decimal('1000'):
            return total * Decimal('0.20')
        elif total > Decimal('500'):
            return total * Decimal('0.15')
        else:
            return total * Decimal('0.10')


class InMemoryOrderRepository:
    """In-memory order storage (DIP - implements protocol)."""

    def __init__(self):
        self.orders: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        """Save order to memory."""
        self.orders[order.id] = order

    def find_by_id(self, order_id: str) -> Order | None:
        """Find order by ID."""
        return self.orders.get(order_id)


class EmailNotificationService:
    """Email notification service (SRP + DIP)."""

    def send_order_confirmation(self, order: Order) -> None:
        """Send confirmation email."""
        print(f"Sending confirmation to {order.customer_email}")
        print(f"Order {order.id}: Total ${order.total}")


# Application service (coordinates components)
class OrderService:
    """
    High-level order processing service.

    Demonstrates:
    - SRP: Only handles order workflow
    - DIP: Depends on abstractions (protocols)
    - OCP: Closed for modification (uses injected strategies)
    - LSP: All injected implementations are substitutable
    """

    def __init__(
        self,
        calculator: PriceCalculator,
        discount_strategy: DiscountStrategy,
        repository: OrderRepository,
        notifier: NotificationService
    ):
        """Initialize with injected dependencies (DIP)."""
        self.calculator = calculator
        self.discount_strategy = discount_strategy
        self.repository = repository
        self.notifier = notifier

    def create_order(
        self,
        order_id: str,
        items: list[OrderItem],
        customer_email: str
    ) -> Order:
        """Create and process a new order."""
        # Calculate total
        total = self.calculator.calculate_total(items)

        # Apply discount
        discount = self.discount_strategy.calculate_discount(total)
        final_total = total - discount

        # Create order
        order = Order(
            id=order_id,
            items=items,
            customer_email=customer_email,
            total=final_total
        )

        # Save order
        self.repository.save(order)

        # Send notification
        self.notifier.send_order_confirmation(order)

        return order

    def get_order(self, order_id: str) -> Order | None:
        """Retrieve an order."""
        return self.repository.find_by_id(order_id)


# Usage example showing dependency injection
def main() -> None:
    """Demonstrate the well-designed system."""
    # Create dependencies
    calculator = StandardPriceCalculator()
    discount = VIPDiscount()  # Could easily swap to PercentageDiscount(10)
    repository = InMemoryOrderRepository()
    notifier = EmailNotificationService()

    # Create service with injected dependencies (DIP)
    order_service = OrderService(
        calculator=calculator,
        discount_strategy=discount,
        repository=repository,
        notifier=notifier
    )

    # Create order
    laptop = Product("1", "Laptop", Decimal('1200'))
    items = [OrderItem(laptop, 1)]

    order = order_service.create_order(
        order_id="ORD-001",
        items=items,
        customer_email="customer@example.com"
    )

    print(f"Order created: {order.id}, Total: ${order.total}")
