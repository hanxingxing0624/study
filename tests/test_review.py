from datetime import datetime, timedelta, timezone
from services.review_service import calculate_next_review


def test_sm2_quality_0_resets():
    result = calculate_next_review(quality=0, ease_factor=2.5, interval=10, repetitions=5)
    assert result["interval"] == 1
    assert result["repetitions"] == 0


def test_sm2_quality_3_first_review():
    result = calculate_next_review(quality=3, ease_factor=2.5, interval=1, repetitions=0)
    assert result["repetitions"] == 1
    assert result["interval"] == 1


def test_sm2_quality_4_second_review():
    result = calculate_next_review(quality=4, ease_factor=2.5, interval=1, repetitions=1)
    assert result["repetitions"] == 2
    assert result["interval"] == 6


def test_sm2_quality_5():
    result = calculate_next_review(quality=5, ease_factor=2.5, interval=6, repetitions=2)
    assert result["repetitions"] == 3
    assert result["interval"] > 6


def test_sm2_ease_factor_never_below_1_3():
    result = calculate_next_review(quality=0, ease_factor=1.3, interval=1, repetitions=0)
    assert result["ease_factor"] >= 1.3


def test_review_page(client):
    resp = client.get("/review")
    assert resp.status_code == 200


def test_submit_review(client, db_session):
    from models import Note, Review
    from datetime import datetime, timezone
    note = Note(title="Review Note", content="test")
    db_session.add(note)
    db_session.flush()
    review = Review(
        note_id=note.id,
        next_review_at=datetime.now(timezone.utc) - timedelta(days=1),
        ease_factor=2.5,
        interval=1,
        repetitions=0,
    )
    db_session.add(review)
    db_session.commit()
    resp = client.post(f"/review/{note.id}", data={"quality": "4"}, follow_redirects=True)
    assert resp.status_code == 200
    db_session.refresh(review)
    assert review.repetitions == 1
