"""Shape area calculator with OCP violation."""

import math


class Shape:
    """Generic shape class - violates OCP!"""

    def __init__(self, shape_type: str, **dimensions):
        self.shape_type = shape_type
        self.dimensions = dimensions


class AreaCalculator:
    """Calculator that must be modified for each new shape type - violates OCP!"""

    def calculate_area(self, shape: Shape) -> float:
        """Calculate area based on shape type - requires modification for new shapes."""
        # This if-elif chain violates OCP
        if shape.shape_type == "circle":
            radius = shape.dimensions['radius']
            return math.pi * radius ** 2

        elif shape.shape_type == "rectangle":
            width = shape.dimensions['width']
            height = shape.dimensions['height']
            return width * height

        elif shape.shape_type == "triangle":
            base = shape.dimensions['base']
            height = shape.dimensions['height']
            return 0.5 * base * height

        elif shape.shape_type == "square":
            side = shape.dimensions['side']
            return side ** 2

        # Adding a hexagon would require modifying this method!
        # elif shape.shape_type == "hexagon":
        #     side = shape.dimensions['side']
        #     return (3 * math.sqrt(3) / 2) * side ** 2

        else:
            raise ValueError(f"Unknown shape type: {shape.shape_type}")


class ShapeProcessor:
    """Another class with type-checking - also violates OCP!"""

    def process_shape(self, shape: Shape) -> dict:
        """Process shape differently based on type - requires modification."""
        if isinstance(shape, Circle):
            return {"type": "curved", "perimeter": 2 * math.pi * shape.radius}
        elif isinstance(shape, Rectangle):
            return {"type": "angular", "perimeter": 2 * (shape.width + shape.height)}
        # More type checks would go here
        else:
            return {"type": "unknown", "perimeter": 0}


class Circle:
    def __init__(self, radius: float):
        self.radius = radius


class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height


# Usage showing the brittleness
def main() -> None:
    calculator = AreaCalculator()

    circle = Shape("circle", radius=5)
    rectangle = Shape("rectangle", width=10, height=5)

    print(f"Circle area: {calculator.calculate_area(circle)}")
    print(f"Rectangle area: {calculator.calculate_area(rectangle)}")

    # If we want to add a new shape, we must modify AreaCalculator!
