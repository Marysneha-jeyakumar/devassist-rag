from app.ingestion.section_detector import (
    SectionDetector,
)


def test_detect_introduction():

    detector = SectionDetector()

    result = detector.detect(
        "1. INTRODUCTION"
    )

    assert result is not None
    assert result.section_type == "introduction"


def test_detect_methodology():

    detector = SectionDetector()

    result = detector.detect(
        "III. MATERIALS AND METHODS"
    )

    assert result is not None
    assert result.section_type == "methodology"


def test_detect_study_area():

    detector = SectionDetector()

    result = detector.detect(
        "2.1 Study Area"
    )

    assert result is not None
    assert result.section_type == "study_area"


def test_normal_sentence_is_not_heading():

    detector = SectionDetector()

    result = detector.detect(
        "Flood prediction is important for disaster management."
    )

    assert result is None