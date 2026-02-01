from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class SM2Result:
    repetitions: int
    ease_factor: float
    interval: int
    next_review: date


def calculate_sm2(
    rating: int,
    repetitions: int,
    ease_factor: float,
    interval: int
) -> SM2Result:
    """
    SM-2 アルゴリズム実装

    rating: 0=Again, 1=Hard, 2=Good, 3=Easy
    repetitions: 連続正解回数
    ease_factor: 難易度係数 (1.3以上)
    interval: 次回までの日数

    Returns: SM2Result with updated values
    """
    if rating < 2:  # Again(0) or Hard(1) → リセット
        repetitions = 0
        interval = 1
    else:  # Good(2) or Easy(3)
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1

    # EF調整 (rating 0-3 を 2-5 にマッピング)
    q = rating + 2  # 2, 3, 4, 5
    ease_factor = max(1.3, ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))

    # Easy bonus
    if rating == 3:
        interval = round(interval * 1.3)

    next_review = date.today() + timedelta(days=interval)

    return SM2Result(
        repetitions=repetitions,
        ease_factor=round(ease_factor, 2),
        interval=interval,
        next_review=next_review
    )
