"""Unit tests for severity.py — run with: python -m pytest tests/ -q
No ML, no network, no weights needed. These test the standard table
and the heuristics, which are the parts a reviewer can check by hand.
"""
import numpy as np
from src.severity import d610_grade, box_union_area_pct, distribution_from_boxes


def test_d610_boundaries():
    # Exact D610 Table 1 boundaries (upper % inclusive).
    assert d610_grade(0.0) == 10
    assert d610_grade(0.01) == 10
    assert d610_grade(0.02) == 9
    assert d610_grade(0.03) == 9
    assert d610_grade(0.10) == 8
    assert d610_grade(0.30) == 7
    assert d610_grade(1.0) == 6
    assert d610_grade(3.0) == 5
    assert d610_grade(10.0) == 4
    assert d610_grade(16.0) == 3
    assert d610_grade(33.0) == 2
    assert d610_grade(50.0) == 1
    assert d610_grade(51.0) == 0
    assert d610_grade(100.0) == 0


def test_box_union_does_not_double_count_overlap():
    # Two identical 10x10 boxes on a 100x100 image = 1%, not 2%.
    assert box_union_area_pct([(0, 0, 10, 10), (0, 0, 10, 10)], 100, 100) == 1.0
    assert box_union_area_pct([], 100, 100) == 0.0


def test_distribution_heuristics():
    assert distribution_from_boxes([(0, 0, 10, 10)], 100, 100).startswith("S")
    tiny = [(i * 20, 0, i * 20 + 1, 1) for i in range(6)]
    assert distribution_from_boxes(tiny, 100, 100).startswith("P")
