"""
Code Quality Assessment Tool - инструмент для автоматического оценивания качества Python кода.
"""

from .analyzer import CodeAnalyzer, CodeMetrics
from .report_generator import ReportGenerator
from .metrics_calculator import MetricsCalculator

__version__ = "1.0.0"
__author__ = "Student Project"
__all__ = ["CodeAnalyzer", "CodeMetrics", "ReportGenerator", "MetricsCalculator"]
