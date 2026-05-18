from datetime import datetime, timedelta, timezone
from models import Review


def calculate_next_review(
    quality: int,
    ease_factor: float = 2.5,
    interval: int = 1,
    repetitions: int = 0,
) -> dict:
    if quality < 0 or quality > 5:
        raise ValueError("Quality must be 0-5")

    if quality < 3:
        return {
            "interval": 1,
            "repetitions": 0,
            "ease_factor": max(1.3, ease_factor - 0.2),
        }

    new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(1.3, new_ease)

    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = round(interval * new_ease)

    return {
        "interval": new_interval,
        "repetitions": repetitions + 1,
        "ease_factor": new_ease,
    }


def schedule_review(db, note, quality: int):
    existing = db.query(Review).filter(Review.note_id == note.id).first()
    if existing:
        result = calculate_next_review(
            quality=quality,
            ease_factor=existing.ease_factor,
            interval=existing.interval,
            repetitions=existing.repetitions,
        )
        existing.ease_factor = result["ease_factor"]
        existing.interval = result["interval"]
        existing.repetitions = result["repetitions"]
        existing.reviewed_at = datetime.now(timezone.utc)
    else:
        result = calculate_next_review(quality=quality)
        existing = Review(
            note_id=note.id,
            ease_factor=result["ease_factor"],
            interval=result["interval"],
            repetitions=result["repetitions"],
            reviewed_at=datetime.now(timezone.utc),
        )

    existing.next_review_at = datetime.now(timezone.utc) + timedelta(days=result["interval"])
    db.add(existing)
    db.commit()
