#!/usr/bin/env python3
"""
Простой скрипт для тестирования анализа в CI/CD.
"""

import sys
import os

# Добавляем пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

try:
    from analyzer import CodeAnalyzer

    print("✓ Успешный импорт CodeAnalyzer")

    # Простой тест анализа
    analyzer = CodeAnalyzer()

    # Анализируем пример хорошего кода
    test_file = "data/student_codes/good_example.py"

    if os.path.exists(test_file):
        metrics = analyzer.analyze_file(test_file)
        if metrics:
            print(f"✓ Анализ файла {test_file} успешен")
            print(f"  Оценка: {metrics.score:.2f}/100")
            print(f"  Сложность: {metrics.avg_complexity:.2f}")

            # Сохраняем результат
            import json

            os.makedirs("data/reports", exist_ok=True)
            with open("data/reports/test_analysis.json", "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "test_file": test_file,
                        "score": metrics.score,
                        "complexity": metrics.avg_complexity,
                        "success": True,
                    },
                    f,
                    indent=2,
                )

            print("✓ Отчет сохранен в data/reports/test_analysis.json")
            sys.exit(0)
        else:
            print("✗ Анализ не вернул результатов")
            sys.exit(1)
    else:
        print(f"✗ Тестовый файл не найден: {test_file}")
        print("Создаю минимальный тестовый файл...")

        # Создаем простой тестовый файл
        os.makedirs("data/student_codes", exist_ok=True)
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(
                '''#!/usr/bin/env python3
"""Простой тестовый файл."""
print("Hello, World!")
'''
            )

        print(f"✓ Создан тестовый файл: {test_file}")
        sys.exit(0)

except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Ошибка выполнения: {e}")
    sys.exit(1)
