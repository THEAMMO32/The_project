"""
Пример хорошо написанного кода с хорошими метриками.
"""

import math
from typing import List, Optional


class GeometryCalculator:
    """Класс для геометрических расчетов."""

    def __init__(self, precision: int = 2):
        self.precision = precision

    def circle_area(self, radius: float) -> float:
        """Вычисляет площадь круга.

        Args:
            radius: Радиус круга

        Returns:
            Площадь круга с заданной точностью
        """
        area = math.pi * radius ** 2
        return round(area, self.precision)

    def rectangle_area(self, width: float, height: float) -> float:
        """Вычисляет площадь прямоугольника."""
        return round(width * height, self.precision)

    def triangle_area(self, base: float, height: float) -> float:
        """Вычисляет площадь треугольника."""
        return round(0.5 * base * height, self.precision)


def filter_even_numbers(numbers: List[int]) -> List[int]:
    """Фильтрует четные числа из списка.

    Args:
        numbers: Список целых чисел

    Returns:
        Список четных чисел
    """
    return [num for num in numbers if num % 2 == 0]


def main():
    """Основная функция для демонстрации."""
    calculator = GeometryCalculator()

    # Вычисляем площади
    circle_area = calculator.circle_area(5.0)
    rectangle_area = calculator.rectangle_area(4.0, 6.0)

    print(f"Площадь круга: {circle_area}")
    print(f"Площадь прямоугольника: {rectangle_area}")

    # Фильтруем числа
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_numbers = filter_even_numbers(numbers)
    print(f"Четные числа: {even_numbers}")


if __name__ == "__main__":
    main()
