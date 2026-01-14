"""
Генерация визуальных отчетов и рекомендаций.
"""

import pandas as pd
import matplotlib

# Устанавливаем неинтерактивный бэкенд ДО импорта pyplot
matplotlib.use("Agg")  # Важно: должно быть перед импортом pyplot
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
import os


# Seaborn уже использует стиль, поэтому оставляем как есть


class ReportGenerator:
    """Генерирует визуальные отчеты по результатам анализа."""

    @staticmethod
    def create_visualizations(results: List[Dict[str, Any]], output_dir: str):
        """Создает визуализации метрик."""
        # Проверяем, что есть данные для визуализации
        if not results or len(results) == 0:
            return

        df = pd.DataFrame(results)

        # Проверяем, что есть столбец 'score' и данные не пустые
        if "score" not in df.columns or df.empty:
            return

        # Создаем директорию, если её нет
        os.makedirs(output_dir, exist_ok=True)

        try:
            # 1. Гистограмма оценок
            plt.figure(figsize=(10, 6))
            plt.hist(df["score"], bins=20, edgecolor="black", alpha=0.7)
            plt.title("Распределение оценок по файлам")
            plt.xlabel("Оценка")
            plt.ylabel("Количество файлов")
            plt.grid(True, alpha=0.3)

            score_path = os.path.join(output_dir, "score_distribution.png")
            plt.savefig(score_path, dpi=150, bbox_inches="tight", format="png")
            plt.close()

            # 2. Scatter plot: сложность vs оценка
            if "avg_complexity" in df.columns and "score" in df.columns:
                plt.figure(figsize=(10, 6))
                plt.scatter(df["avg_complexity"], df["score"], alpha=0.6)
                plt.title("Сложность кода vs Оценка")
                plt.xlabel("Средняя цикломатическая сложность")
                plt.ylabel("Оценка")
                plt.grid(True, alpha=0.3)

                scatter_path = os.path.join(output_dir, "complexity_vs_score.png")
                plt.savefig(scatter_path, dpi=150, bbox_inches="tight", format="png")
                plt.close()

            # 3. Heatmap корреляций (только если есть несколько числовых колонок)
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 1:
                try:
                    plt.figure(figsize=(12, 8))
                    correlation = df[numeric_cols].corr()
                    sns.heatmap(correlation, annot=True, cmap="coolwarm", center=0)
                    plt.title("Корреляция между метриками")

                    heatmap_path = os.path.join(output_dir, "correlation_heatmap.png")
                    plt.savefig(
                        heatmap_path, dpi=150, bbox_inches="tight", format="png"
                    )
                    plt.close()
                except Exception:
                    # Игнорируем ошибки при создании heatmap
                    pass

        except Exception as e:
            # Логируем ошибку, но не падаем
            print(f"Warning: Error creating visualizations: {e}")

    @staticmethod
    def generate_recommendations(metrics: Dict[str, Any]) -> List[str]:
        """Генерирует рекомендации по улучшению кода."""
        recommendations = []

        # PEP8 рекомендации
        if metrics.get("pep8_errors", 0) > 5:
            recommendations.append(
                "⚠️ Много ошибок PEP8. Используйте `black` для автоматического форматирования: "
                "`black ваш_файл.py`"
            )

        # Сложность
        if metrics.get("max_complexity", 0) > 10:
            recommendations.append(
                "🔄 Высокая цикломатическая сложность. Разбейте сложные функции на более простые."
            )

        # Docstring
        if metrics.get("docstring_coverage", 0) < 50:
            recommendations.append(
                "📝 Добавьте docstring к функциям и классам для лучшей документации."
            )

        # Комментарии
        comment_density = metrics.get("comment_density", 0)
        if comment_density < 5:
            recommendations.append("💭 Добавьте комментарии к сложным участкам кода.")
        elif comment_density > 30:
            recommendations.append(
                "💭 Слишком много комментариев. Некоторые из них могут быть избыточными."
            )

        # Общая оценка
        score = metrics.get("score", 0)
        if score < 50:
            recommendations.append("🚨 Необходимо серьезное улучшение кода!")
        elif score < 70:
            recommendations.append(
                "📈 Есть куда улучшать. Обратите внимание на рекомендации выше."
            )
        elif score < 85:
            recommendations.append("✅ Хороший код! Небольшие улучшения возможны.")
        else:
            recommendations.append("🏆 Отличный код! Продолжайте в том же духе.")

        return recommendations
