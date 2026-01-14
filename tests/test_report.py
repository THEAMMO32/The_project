"""
Тесты для генератора отчетов.
"""

import unittest
import tempfile
import os
import json
import pandas as pd
import sys

# Добавляем путь к src в sys.path для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.analyzer import CodeAnalyzer
    from src.report_generator import ReportGenerator
except ImportError:
    # Альтернативный импорт для локального запуска
    sys.path.append("src")
    from The_project.src.analyzer import CodeAnalyzer
    from The_project.src.report_generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.reporter = ReportGenerator()
        self.analyzer = CodeAnalyzer()

        # Создаем тестовый код с ASCII символами (без кириллицы)
        self.test_code = '''
def example_function(x):
    """Example function with docstring."""
    return x * 2

class ExampleClass:
    """Example class."""
    def method(self):
        return 42
'''

        # Сохраняем во временный файл с UTF-8 кодировкой
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        )
        self.temp_file.write(self.test_code)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_create_visualizations(self):
        """Тест создания визуализаций."""
        # Анализируем файл
        metrics = self.analyzer.analyze_file(self.temp_file.name)
        results = [metrics.__dict__]

        # Создаем временную директорию
        with tempfile.TemporaryDirectory() as temp_dir:
            self.reporter.create_visualizations(results, temp_dir)

            # Проверяем, что файлы созданы
            expected_files = ["score_distribution.png"]
            for file in expected_files:
                filepath = os.path.join(temp_dir, file)
                self.assertTrue(os.path.exists(filepath), f"Файл {file} не создан")

    def test_generate_recommendations(self):
        """Тест генерации рекомендаций."""
        # Тестируем с плохими метриками
        bad_metrics = {
            "score": 45,
            "pep8_errors": 10,
            "max_complexity": 15,
            "docstring_coverage": 20,
            "comment_density": 2,
        }

        recommendations = self.reporter.generate_recommendations(bad_metrics)

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        # Проверяем, что есть рекомендации по PEP8
        pep8_recommendations = [
            r for r in recommendations if "PEP8" in r or "black" in r
        ]
        self.assertGreater(len(pep8_recommendations), 0)

        # Тестируем с хорошими метриками
        good_metrics = {
            "score": 95,
            "pep8_errors": 0,
            "max_complexity": 3,
            "docstring_coverage": 100,
            "comment_density": 15,
        }

        good_recommendations = self.reporter.generate_recommendations(good_metrics)

        # Должна быть похвала для хорошего кода
        praise = [r for r in good_recommendations if "Отличный" in r or "Хороший" in r]
        self.assertGreater(len(praise), 0)

    def test_recommendations_edge_cases(self):
        """Тест граничных случаев для рекомендаций."""
        # Очень низкая оценка
        very_bad = {"score": 20}
        recs = self.reporter.generate_recommendations(very_bad)
        self.assertIn("🚨", "".join(recs))

        # Очень высокая оценка
        excellent = {"score": 98}
        recs = self.reporter.generate_recommendations(excellent)
        self.assertIn("🏆", "".join(recs))

    def test_empty_results_visualization(self):
        """Тест визуализации с пустыми результатами."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Пустой список результатов - не должно вызывать ошибок
            self.reporter.create_visualizations([], temp_dir)

            # Файлы могут не создаться для пустых данных
            # Главное - нет ошибок выполнения
            self.assertTrue(True)

    def test_single_result_visualization(self):
        """Тест визуализации с одним результатом."""
        metrics = self.analyzer.analyze_file(self.temp_file.name)
        results = [metrics.__dict__] * 3  # Дублируем для гистограммы

        with tempfile.TemporaryDirectory() as temp_dir:
            self.reporter.create_visualizations(results, temp_dir)

            score_file = os.path.join(temp_dir, "score_distribution.png")
            self.assertTrue(os.path.exists(score_file))

            # Проверяем размер файла
            self.assertGreater(os.path.getsize(score_file), 100)

    def test_correlation_heatmap_with_insufficient_data(self):
        """Тест создания heatmap с недостаточными данными."""
        # Создаем результаты только с одним числовым полем
        results = [{"score": 80}, {"score": 90}]

        with tempfile.TemporaryDirectory() as temp_dir:
            # Не должно вызывать ошибок
            self.reporter.create_visualizations(results, temp_dir)
            self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
