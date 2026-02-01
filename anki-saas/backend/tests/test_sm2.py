"""
SM-2 Algorithm Unit Tests
"""
import pytest
from datetime import date, timedelta

from app.services.sm2 import calculate_sm2, SM2Result


class TestSM2Algorithm:
    """Test SM-2 spaced repetition algorithm"""

    def test_again_resets_interval(self):
        """Rating 0 (Again) should reset interval to 1"""
        result = calculate_sm2(
            rating=0,
            repetitions=5,
            ease_factor=2.5,
            interval=30
        )
        assert result.interval == 1
        assert result.repetitions == 0

    def test_hard_resets_interval(self):
        """Rating 1 (Hard) should reset interval to 1"""
        result = calculate_sm2(
            rating=1,
            repetitions=3,
            ease_factor=2.5,
            interval=15
        )
        assert result.interval == 1
        assert result.repetitions == 0

    def test_good_first_review(self):
        """First Good review should set interval to 1"""
        result = calculate_sm2(
            rating=2,
            repetitions=0,
            ease_factor=2.5,
            interval=0
        )
        assert result.interval == 1
        assert result.repetitions == 1

    def test_good_second_review(self):
        """Second Good review should set interval to 6"""
        result = calculate_sm2(
            rating=2,
            repetitions=1,
            ease_factor=2.5,
            interval=1
        )
        assert result.interval == 6
        assert result.repetitions == 2

    def test_good_subsequent_review(self):
        """Subsequent Good reviews should multiply interval by ease factor"""
        result = calculate_sm2(
            rating=2,
            repetitions=2,
            ease_factor=2.5,
            interval=6
        )
        assert result.interval == 15  # 6 * 2.5 = 15
        assert result.repetitions == 3

    def test_easy_bonus(self):
        """Easy rating should apply 1.3x bonus"""
        result = calculate_sm2(
            rating=3,
            repetitions=2,
            ease_factor=2.5,
            interval=6
        )
        # 6 * 2.5 * 1.3 = 19.5 -> 20
        assert result.interval == 20
        assert result.repetitions == 3

    def test_ease_factor_minimum(self):
        """Ease factor should not go below 1.3"""
        result = calculate_sm2(
            rating=0,
            repetitions=1,
            ease_factor=1.3,
            interval=1
        )
        assert result.ease_factor >= 1.3

    def test_ease_factor_increases_on_easy(self):
        """Ease factor should increase on Easy rating"""
        result = calculate_sm2(
            rating=3,
            repetitions=2,
            ease_factor=2.5,
            interval=6
        )
        assert result.ease_factor > 2.5

    def test_next_review_date(self):
        """Next review date should be today + interval"""
        result = calculate_sm2(
            rating=2,
            repetitions=1,
            ease_factor=2.5,
            interval=1
        )
        expected_date = date.today() + timedelta(days=6)
        assert result.next_review == expected_date

    def test_returns_sm2_result(self):
        """Function should return SM2Result dataclass"""
        result = calculate_sm2(
            rating=2,
            repetitions=0,
            ease_factor=2.5,
            interval=0
        )
        assert isinstance(result, SM2Result)
        assert hasattr(result, 'repetitions')
        assert hasattr(result, 'ease_factor')
        assert hasattr(result, 'interval')
        assert hasattr(result, 'next_review')
