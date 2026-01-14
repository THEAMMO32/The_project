"""Тесты для анализатора кода."""

import unittest
import tempfile
import os
import json
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


class TestCodeAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = CodeAnalyzer()
        self.test_dir = tempfile.mkdtemp()

        # Создаем тестовый файл с ASCII символами (без кириллицы)
        self.test_file = os.path.join(self.test_dir, "test_code.py")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(
                """
def simple_function(x):
    '''Simple function.'''
    return x * 2

class TestClass:
    '''Test class.'''
    def method(self):
        return 42
"""
            )

    def tearDown(self):
        # Очистка временных файлов
        import shutil

        shutil.rmtree(self.test_dir)

    def test_analyze_file(self):
        """Тест анализа одного файла."""
        metrics = self.analyzer.analyze_file(self.test_file)

        self.assertEqual(metrics.filename, "test_code.py")
        self.assertGreater(metrics.score, 0)
        self.assertLessEqual(metrics.score, 100)

    def test_analyze_directory(self):
        """Тест анализа директории."""
        # Создаем второй файл
        second_file = os.path.join(self.test_dir, "second.py")
        with open(second_file, "w", encoding="utf-8") as f:
            f.write("print('Hello')")

        results = self.analyzer.analyze_directory(self.test_dir)
        self.assertEqual(len(results), 2)

    def test_error_handling(self):
        """Тест обработки синтаксических ошибок."""
        error_file = os.path.join(self.test_dir, "error.py")
        with open(error_file, "w", encoding="utf-8") as f:
            f.write("def invalid syntax")

        metrics = self.analyzer.analyze_file(error_file)
        self.assertEqual(metrics.score, 0)

    def test_report_generation(self):
        """Тест генерации отчета."""
        results = self.analyzer.analyze_directory(self.test_dir)

        # Тест создания отчета
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            report_path = f.name

        try:
            self.analyzer.generate_report(results, report_path[:-5])  # Без .json

            # Проверяем, что файл создан
            self.assertTrue(os.path.exists(report_path))

            # Проверяем структуру JSON
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)

            self.assertIn("timestamp", report_data)
            self.assertIn("total_files", report_data)
            self.assertIn("files", report_data)
        finally:
            if os.path.exists(report_path):
                os.remove(report_path)

    def test_recommendations(self):
        """Тест генерации рекомендаций."""
        # Создаем файл с плохими метриками (только ASCII)
        bad_file = os.path.join(self.test_dir, "bad.py")
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("x=1+2  # Bad style\n" * 20)

        metrics = self.analyzer.analyze_file(bad_file)
        recommendations = ReportGenerator.generate_recommendations(
            {"score": metrics.score}
        )

        self.assertGreater(len(recommendations), 0)
        self.assertIsInstance(recommendations, list)


if __name__ == "__main__":
    unittest.main()
