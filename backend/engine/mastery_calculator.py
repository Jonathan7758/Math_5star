import math
from datetime import datetime, timezone


class MasteryCalculator:
    """Weighted mastery algorithm with forgetting curve decay."""

    HALF_LIFE_DAYS = 14.0

    @staticmethod
    def calculate(
        correct: int,
        total: int,
        last_practiced_at: datetime | None = None,
        first_seen_at: datetime | None = None,
    ) -> float:
        """Calculate weighted mastery score (0.0 to 1.0).

        Combines:
        - Accuracy: correct / total
        - Frequency: how recently practiced (exponential decay)
        - Consistency: ratio of days practiced
        """
        if total == 0:
            return 0.0

        accuracy = correct / total

        recency = 1.0
        if last_practiced_at is not None:
            now = datetime.now(timezone.utc)
            if last_practiced_at.tzinfo is None:
                last_practiced_at = last_practiced_at.replace(tzinfo=timezone.utc)
            days_since = (now - last_practiced_at).total_seconds() / 86400.0
            recency = math.exp(-days_since * math.log(2) / MasteryCalculator.HALF_LIFE_DAYS)
            recency = max(recency, 0.1)

        confidence = min(total / 10.0, 1.0)

        score = 0.5 * accuracy + 0.3 * recency + 0.2 * confidence

        return round(min(score, 1.0), 4)

    @staticmethod
    def decay(score: float, days_elapsed: float) -> float:
        """Apply exponential decay to a mastery score based on days since last practice."""
        decay_factor = math.exp(-days_elapsed * math.log(2) / MasteryCalculator.HALF_LIFE_DAYS)
        return round(score * max(decay_factor, 0.1), 4)
