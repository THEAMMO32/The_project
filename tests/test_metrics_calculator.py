"""
Тесты для калькулятора метрик.
"""

import unittest
import tempfile
import os
from The_project.src.metrics_calculator import MetricsCalculator


class TestMetricsCalculator(unittest.TestCase):

    def test_halstead_metrics_simple(self):
        """Тест метрик Холстеда для простого кода."""
        simple_code = """
x = 1
y = 2
z = x + y
print(z)
"""

        metrics = MetricsCalculator.calculate_halstead_metrics(simple_code)

        # Проверяем наличие ключевых метрик
        self.assertIn("halstead_vocabulary", metrics)
        self.assertIn("halstead_volume", metrics)
        self.assertIn("halstead_effort", metrics)

        # Для простого кода объем должен быть небольшим
        self.assertLess(metrics["halstead_volume"], 100)

    def test_halstead_metrics_complex(self):
        """Тест метрик Холстеда для сложного кода."""
        complex_code = """
def calculate_stats(data):
    if not data:
        return {}
    
    total = sum(data)
    count = len(data)
    mean = total / count
    
    variance = sum((x - mean) ** 2 for x in data) / count
    std_dev = variance ** 0.5
    
    return {
        'mean': mean,
        'variance': variance,
        'std_dev': std_dev,
        'count': count
    }
"""

        metrics = MetricsCalculator.calculate_halstead_metrics(complex_code)

        # Сложный код должен иметь больший объем
        self.assertGreater(metrics.get("halstead_volume", 0), 10)

    def test_duplication_rate(self):
        """Тест расчета уровня дублирования."""
        # Код с дублированием
        duplicated_code = """
x = 1
y = 2
z = x + y
x = 1
y = 2
z = x + y
print(z)
"""

        rate = MetricsCalculator.calculate_duplication_rate(duplicated_code)

        # Должен быть положительный уровень дублирования
        self.assertGreater(rate, 0)
        self.assertLessEqual(rate, 100)

    def test_duplication_rate_no_duplicates(self):
        """Тест расчета уровня дублирования без дубликатов."""
        unique_code = """
def func1():
    return 1

def func2():
    return 2

def func3():
    return 3
"""

        rate = MetricsCalculator.calculate_duplication_rate(unique_code)
        self.assertEqual(rate, 0)

    def test_function_stats(self):
        """Тест статистики функций."""
        code_with_functions = """
def short_func():
    return 1

def long_func(x, y, z):
    result = x + y + z
    result *= 2
    result /= 3
    return result

def medium_func(a, b=10):
    return a * b
"""

        stats = MetricsCalculator.calculate_function_stats(code_with_functions)

        self.assertEqual(stats["num_functions"], 3)
        self.assertGreater(stats["avg_function_length"], 0)
        self.assertLess(stats["avg_function_params"], 3)

    def test_import_complexity(self):
        """Тест анализа импортов."""
        code_with_imports = """
import os
import sys
import json
from typing import List, Dict
from math import sqrt, pow
import numpy as np
"""

        import_stats = MetricsCalculator.calculate_import_complexity(code_with_imports)

        self.assertEqual(import_stats["total_imports"], 8)
        self.assertEqual(import_stats["unique_modules"], 6)

    def test_empty_code(self):
        """Тест с пустым кодом."""
        empty_code = ""

        # Все методы должны корректно обрабатывать пустой код
        halstead = MetricsCalculator.calculate_halstead_metrics(empty_code)
        self.assertEqual(halstead, {})

        duplication = MetricsCalculator.calculate_duplication_rate(empty_code)
        self.assertEqual(duplication, 0.0)

        func_stats = MetricsCalculator.calculate_function_stats(empty_code)
        self.assertEqual(func_stats, {})

        import_stats = MetricsCalculator.calculate_import_complexity(empty_code)
        # Исправлено: метод возвращает словарь со значениями 0
        expected = {"total_imports": 0, "unique_modules": 0, "most_used_module": 0}
        self.assertEqual(import_stats, expected)

    def test_invalid_syntax(self):
        """Тест с кодом с синтаксической ошибкой."""
        invalid_code = "def invalid syntax here"

        # Методы должны возвращать пустые словари при ошибках
        halstead = MetricsCalculator.calculate_halstead_metrics(invalid_code)
        self.assertEqual(halstead, {})

        # duplication_rate должен работать даже с ошибками
        duplication = MetricsCalculator.calculate_duplication_rate(invalid_code)
        self.assertIsInstance(duplication, float)


if __name__ == "__main__":
    unittest.main()
