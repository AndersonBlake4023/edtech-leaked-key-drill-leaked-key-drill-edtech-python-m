from datetime import date

from src.leaked_key_drill import CourseDelivery, LearnerDeadline, educator_report


def test_learner_before_course_deadline_is_at_risk() -> None:
    delivery = CourseDelivery("biology-101", date(2026, 11, 10), LearnerDeadline("learner-17", date(2026, 11, 8)))
    assert educator_report(delivery)["at_risk"] is True
