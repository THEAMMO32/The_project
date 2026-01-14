"""
Расчет дополнительных метрик для анализа кода.
"""

import ast
import math
from typing import Dict, List, Tuple
from collections import Counter


class MetricsCalculator:
    """Калькулятор дополнительных метрик качества кода."""

    @staticmethod
    def calculate_halstead_metrics(code: str) -> Dict[str, float]:
        """Рассчитывает метрики Холстеда."""
        try:
            tree = ast.parse(code)

            operators = []
            operands = []

            # Собираем операторы и операнды
            for node in ast.walk(tree):
                # Операторы
                if isinstance(
                    node,
                    (
                        ast.Add,
                        ast.Sub,
                        ast.Mult,
                        ast.Div,
                        ast.FloorDiv,
                        ast.Mod,
                        ast.Pow,
                        ast.LShift,
                        ast.RShift,
                        ast.BitOr,
                        ast.BitXor,
                        ast.BitAnd,
                        ast.MatMult,
                        ast.And,
                        ast.Or,
                        ast.Not,
                        ast.Invert,
                        ast.UAdd,
                        ast.USub,
                        ast.Eq,
                        ast.NotEq,
                        ast.Lt,
                        ast.LtE,
                        ast.Gt,
                        ast.GtE,
                        ast.Is,
                        ast.IsNot,
                        ast.In,
                        ast.NotIn,
                    ),
                ):
                    operators.append(node.__class__.__name__)

                # Операнды (имена переменных, константы)
                if isinstance(node, ast.Name):
                    operands.append(node.id)
                elif isinstance(node, ast.Constant):
                    operands.append(str(node.value))

            # Уникальные операторы и операнды
            n1 = len(set(operators))  # Количество уникальных операторов
            n2 = len(set(operands))  # Количество уникальных операндов
            N1 = len(operators)  # Общее количество операторов
            N2 = len(operands)  # Общее количество операндов

            if n1 == 0 or n2 == 0:
                return {}

            # Расчет метрик Холстеда
            vocabulary = n1 + n2
            length = N1 + N2
            volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
            difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
            effort = difficulty * volume
            time_required = effort / 18  # Стандартное предположение

            return {
                "halstead_vocabulary": vocabulary,
                "halstead_length": length,
                "halstead_volume": round(volume, 2),
                "halstead_difficulty": round(difficulty, 2),
                "halstead_effort": round(effort, 2),
                "halstead_time": round(time_required, 2),
            }
        except:
            return {}

    @staticmethod
    def calculate_duplication_rate(code: str) -> float:
        """Рассчитывает уровень дублирования кода."""
        lines = code.strip().split("\n")
        cleaned_lines = []

        # Убираем комментарии и пустые строки
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                # Убираем лишние пробелы
                cleaned = " ".join(stripped.split())
                cleaned_lines.append(cleaned)

        if len(cleaned_lines) < 2:
            return 0.0

        # Поиск дубликатов строк
        line_counter = Counter(cleaned_lines)
        duplicate_lines = sum(
            count for line, count in line_counter.items() if count > 1
        )

        return (duplicate_lines / len(cleaned_lines)) * 100

    @staticmethod
    def calculate_function_stats(code: str) -> Dict[str, float]:
        """Статистика по функциям."""
        try:
            tree = ast.parse(code)

            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Считаем строки в теле функции
                    func_lines = ast.get_source_segment(code, node).split("\n")
                    body_lines = len([l for l in func_lines if l.strip()])

                    # Считаем параметры
                    num_args = len(node.args.args)
                    num_defaults = len(node.args.defaults)

                    functions.append(
                        {
                            "name": node.name,
                            "lines": body_lines,
                            "params": num_args,
                            "defaults": num_defaults,
                        }
                    )

            if not functions:
                return {}

            # Сводная статистика
            avg_lines = sum(f["lines"] for f in functions) / len(functions)
            avg_params = sum(f["params"] for f in functions) / len(functions)

            return {
                "num_functions": len(functions),
                "avg_function_length": round(avg_lines, 2),
                "avg_function_params": round(avg_params, 2),
                "longest_function": (
                    max(f["lines"] for f in functions) if functions else 0
                ),
                "max_params": max(f["params"] for f in functions) if functions else 0,
            }
        except:
            return {}

    @staticmethod
    def calculate_import_complexity(code: str) -> Dict[str, float]:
        """Анализ импортов."""
        try:
            tree = ast.parse(code)

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            {
                                "module": alias.name,
                                "alias": alias.asname,
                                "type": "import",
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append(
                            {
                                "module": node.module or "",
                                "name": alias.name,
                                "alias": alias.asname,
                                "type": "from_import",
                            }
                        )

            # Группировка по модулям
            modules = {}
            for imp in imports:
                module = imp.get("module", imp.get("name", ""))
                if module:
                    if module not in modules:
                        modules[module] = 0
                    modules[module] += 1

            return {
                "total_imports": len(imports),
                "unique_modules": len(modules),
                "most_used_module": max(modules.values()) if modules else 0,
            }
        except:
            return {}
