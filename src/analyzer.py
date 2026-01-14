"""
Анализатор качества Python кода с метриками для оценивания студенческих работ.
"""

import ast
import subprocess
import json
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import pandas as pd
from radon.complexity import cc_visit
from radon.metrics import h_visit, mi_visit


@dataclass
class CodeMetrics:
    """Хранение метрик для одного файла."""

    filename: str
    lines_of_code: int
    num_functions: int
    num_classes: int
    avg_complexity: float
    max_complexity: int
    maintainability_index: float
    pep8_errors: int
    pep8_warnings: int
    docstring_coverage: float  # % функций/классов с docstring
    comment_density: float  # % строк с комментариями
    score: float  # Общая оценка 0-100


class CodeAnalyzer:
    """Основной класс для анализа Python кода."""

    def __init__(self):
        self.metrics_weights = {
            "pep8": 0.25,
            "complexity": 0.25,
            "maintainability": 0.20,
            "docstrings": 0.15,
            "comments": 0.15,
        }

    def analyze_file(self, filepath: str) -> CodeMetrics:
        """Анализирует один Python файл."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, "r", encoding="cp1251") as f:
                    code = f.read()
            except Exception as e:
                return self._create_error_metrics(filepath, f"Encoding Error: {str(e)}")
        except FileNotFoundError:
            return self._create_error_metrics(filepath, "File Not Found")
        except Exception as e:
            return self._create_error_metrics(filepath, f"Read Error: {str(e)}")

        try:
            tree = ast.parse(code)
        except (SyntaxError, ValueError) as e:
            return self._create_error_metrics(filepath, f"Syntax Error: {str(e)}")

        # Базовые метрики из AST
        loc = len(code.split("\n"))
        num_funcs = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        num_classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

        # Цикломатическая сложность через radon
        try:
            complexity_results = cc_visit(code)
            complexities = [c.complexity for c in complexity_results]
            avg_complexity = (
                sum(complexities) / len(complexities) if complexities else 0
            )
            max_complexity = max(complexities) if complexities else 0
        except Exception:
            avg_complexity = 0
            max_complexity = 0

        # Индекс поддерживаемости
        try:
            mi_score = mi_visit(code, multi=True)
            if isinstance(mi_score, (int, float)):
                mi_score = float(mi_score)
            else:
                mi_score = 0.0
        except Exception:
            mi_score = 0.0

        # Проверка PEP8
        pep8_errors, pep8_warnings = self._run_pep8_check(filepath)

        # Docstring coverage
        docstring_coverage = self._calculate_docstring_coverage(
            tree, num_funcs, num_classes
        )

        # Comment density
        comment_density = self._calculate_comment_density(code)

        # Общая оценка
        score = self._calculate_score(
            {
                "pep8_errors": pep8_errors,
                "pep8_warnings": pep8_warnings,
                "avg_complexity": avg_complexity,
                "max_complexity": max_complexity,
                "maintainability": mi_score,
                "docstring_coverage": docstring_coverage,
                "comment_density": comment_density,
            }
        )

        return CodeMetrics(
            filename=os.path.basename(filepath),
            lines_of_code=loc,
            num_functions=num_funcs,
            num_classes=num_classes,
            avg_complexity=round(avg_complexity, 2),
            max_complexity=max_complexity,
            maintainability_index=round(mi_score, 2),
            pep8_errors=pep8_errors,
            pep8_warnings=pep8_warnings,
            docstring_coverage=round(docstring_coverage, 2),
            comment_density=round(comment_density, 2),
            score=round(score, 2),
        )

    def analyze_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Анализирует все Python файлы в директории."""
        results = []

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    metrics = self.analyze_file(filepath)
                    results.append(asdict(metrics))

        return results

    def _run_pep8_check(self, filepath: str) -> Tuple[int, int]:
        """Запускает проверку PEP8 через flake8."""
        try:
            errors = 0
            warnings = 0

            # Подсчитываем ошибки (E, F)
            result_errors = subprocess.run(
                ["flake8", "--select=E,F", "--count", "--max-line-length=88", filepath],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result_errors.stdout.strip().isdigit():
                errors = int(result_errors.stdout.strip())

            # Подсчитываем предупреждения (W)
            result_warnings = subprocess.run(
                ["flake8", "--select=W", "--count", "--max-line-length=88", filepath],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result_warnings.stdout.strip().isdigit():
                warnings = int(result_warnings.stdout.strip())

            return errors, warnings

        except subprocess.TimeoutExpired:
            print(f"Timeout при проверке {filepath}")
            return 0, 0
        except FileNotFoundError:
            print("flake8 не установлен. Установите: pip install flake8")
            return 0, 0
        except Exception as e:
            print(f"Ошибка при проверке PEP8: {str(e)}")
            return 0, 0

    def _calculate_docstring_coverage(
        self, tree: ast.AST, num_funcs: int, num_classes: int
    ) -> float:
        """Рассчитывает покрытие docstring."""
        total_entities = num_funcs + num_classes
        if total_entities == 0:
            return 100.0

        entities_with_doc = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring and len(docstring.strip()) > 0:
                    entities_with_doc += 1

        return (entities_with_doc / total_entities) * 100

    def _calculate_comment_density(self, code: str) -> float:
        """Рассчитывает плотность комментариев."""
        lines = code.split("\n")
        total_lines = len(lines)
        if total_lines == 0:
            return 0.0

        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        return (comment_lines / total_lines) * 100

    def _calculate_score(self, metrics: Dict[str, float]) -> float:
        """Рассчитывает общую оценку 0-100 на основе метрик."""
        score = 100

        # Штрафы за ошибки (с ограничением)
        score -= min(metrics["pep8_errors"] * 2, 30)  # Макс 30 баллов штрафа
        score -= min(metrics["pep8_warnings"] * 0.5, 10)  # Макс 10 баллов

        # Штрафы за сложность
        if metrics["max_complexity"] > 10:
            score -= min((metrics["max_complexity"] - 10) * 2, 20)
        if metrics["avg_complexity"] > 5:
            score -= min((metrics["avg_complexity"] - 5) * 1, 10)

        # Бонус/штраф за поддерживаемость
        if metrics["maintainability"] > 80:
            score += 5
        elif metrics["maintainability"] < 40:
            score -= 10

        # Бонус за docstring (макс 15 баллов)
        score += min(metrics["docstring_coverage"] * 0.15, 15)

        # Бонус за комментарии (но не слишком много)
        if 5 <= metrics["comment_density"] <= 20:
            score += 5
        elif metrics["comment_density"] < 2:
            score -= 5

        return max(0, min(100, score))

    def _create_error_metrics(self, filename: str, error_msg: str) -> CodeMetrics:
        """Создает метрики для файла с ошибкой."""
        print(f"Ошибка при анализе {filename}: {error_msg}")
        return CodeMetrics(
            filename=os.path.basename(filename),
            lines_of_code=0,
            num_functions=0,
            num_classes=0,
            avg_complexity=0,
            max_complexity=0,
            maintainability_index=0,
            pep8_errors=100,
            pep8_warnings=0,
            docstring_coverage=0,
            comment_density=0,
            score=0,
        )

    def generate_report(self, results: List[Dict[str, Any]], output_path: str) -> str:
        """Генерирует отчет в формате JSON и CSV."""
        if not results:
            print("Нет результатов для генерации отчета")
            return ""

        # Сохраняем в JSON
        json_path = output_path + ".json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": pd.Timestamp.now().isoformat(),
                        "total_files": len(results),
                        "average_score": round(
                            sum(r["score"] for r in results) / len(results), 2
                        ),
                        "files": results,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except Exception as e:
            print(f"Ошибка при сохранении JSON: {str(e)}")

        # Сохраняем в CSV
        csv_path = output_path + ".csv"
        try:
            df = pd.DataFrame(results)
            df.to_csv(csv_path, index=False, encoding="utf-8")
        except Exception as e:
            print(f"Ошибка при сохранении CSV: {str(e)}")

        # Генерируем сводную статистику
        try:
            df = pd.DataFrame(results)
            summary = {
                "📊 Статистика анализа": {
                    "Всего файлов": len(results),
                    "Средняя оценка": round(df["score"].mean(), 2),
                    "Лучший результат": round(df["score"].max(), 2),
                    "Худший результат": round(df["score"].min(), 2),
                    "Средняя сложность": round(df["avg_complexity"].mean(), 2),
                    "Средний индекс поддерживаемости": round(
                        df["maintainability_index"].mean(), 2
                    ),
                    "Среднее покрытие docstring": round(
                        df["docstring_coverage"].mean(), 2
                    ),
                    "Средняя плотность комментариев": round(
                        df["comment_density"].mean(), 2
                    ),
                }
            }

            summary_path = output_path + "_summary.txt"
            with open(summary_path, "w", encoding="utf-8") as f:
                for section, data in summary.items():
                    f.write(f"{section}\n")
                    f.write("=" * 40 + "\n")
                    for key, value in data.items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
        except Exception as e:
            print(f"Ошибка при генерации сводки: {str(e)}")

        return json_path


# Пример использования
if __name__ == "__main__":
    analyzer = CodeAnalyzer()
