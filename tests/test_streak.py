import pytest
from streak import longest_positive_streak

def test_empty_list():
    assert longest_positive_streak([]) == 0

def test_single_streak():
    assert longest_positive_streak([1, 1, 1]) == 3

def test_multiple_streaks():
    assert longest_positive_streak([2, 3, -1, 5, 6, 7, 0, 4]) == 3
    assert longest_positive_streak([1, 2, 0, 3, 4, -2, 5]) == 2

def test_with_zeros_and_negatives():
    assert longest_positive_streak([0, 0, 0]) == 0
    assert longest_positive_streak([-1, -2, -3]) == 0
    assert longest_positive_streak([1, 2, 3, 0, -1, 4, 5]) == 3
