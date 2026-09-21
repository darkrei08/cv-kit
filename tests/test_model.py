"""Tests for the data model and its validation rules."""
from cvkit.model import CV, LABELS, Contact, Education, Job, Language, validate


def minimal(**overrides) -> CV:
    values = dict(
        contact=Contact(name="Test Person", email="test@example.com",
                        phone="+39 000 000 0000", headline="Elettricista"),
        profile="Elettricista industriale con esperienza su quadri di automazione.",
        experience=[Job(period="01/2020 - 12/2024", employer="Azienda",
                        role="Elettricista", duties=["Manutenzione dei quadri."])],
    )
    values.update(overrides)
    return CV(**values)


def codes(findings) -> set[str]:
    return {f.code for f in findings}


def test_a_clean_cv_has_no_errors():
    findings = validate(minimal(), "ats")
    assert not [f for f in findings if f.level == "error"]


def test_missing_name_and_email_are_errors():
    cv = minimal(contact=Contact(name="", email=""))
    assert {"missing-name", "missing-email"} <= codes(validate(cv, "ats"))


def test_malformed_email_is_an_error():
    cv = minimal(contact=Contact(name="Test", email="not-an-address"))
    assert "bad-email" in codes(validate(cv, "ats"))


def test_a_job_without_dates_is_an_error():
    cv = minimal(experience=[Job(period="", employer="Azienda", role="Ruolo")])
    assert "job-without-dates" in codes(validate(cv, "ats"))


def test_personal_data_in_a_portal_variant_is_flagged():
    cv = minimal(contact=Contact(name="Test Person", email="test@example.com",
                                 personal={"Data di nascita": "01/01/1980"}))
    assert "personal-data-in-portal-variant" in codes(validate(cv, "ats"))


def test_personal_data_is_acceptable_in_the_designed_variant():
    cv = minimal(contact=Contact(name="Test Person", email="test@example.com",
                                 personal={"Data di nascita": "01/01/1980"}))
    findings = codes(validate(cv, "designed"))
    assert "personal-data-in-portal-variant" not in findings


def test_a_photo_is_flagged_for_portals_only():
    cv = minimal(contact=Contact(name="Test Person", email="test@example.com",
                                 photo="assets/photo.jpg"))
    assert "photo-in-portal-variant" in codes(validate(cv, "ats"))
    assert "photo-in-portal-variant" not in codes(validate(cv, "designed"))


def test_age_cues_are_flagged():
    cv = minimal(profile="Oltre 40 anni di esperienza nel settore elettrico.")
    assert "age-cue" in codes(validate(cv, "ats"))


def test_generic_phrases_are_flagged():
    cv = minimal(profile="Hard worker, dynamic and reliable.")
    assert "generic-phrase" in codes(validate(cv, "ats"))


def test_missing_keywords_is_flagged_for_portals():
    assert "no-keywords" in codes(validate(minimal(), "ats"))


def test_too_many_duties_is_flagged():
    job = Job(period="01/2020 - 12/2024", employer="Azienda", role="Ruolo",
              duties=[f"Compito {i}" for i in range(7)])
    assert "too-many-duties" in codes(validate(minimal(experience=[job]), "ats"))


def test_long_profile_is_flagged():
    cv = minimal(profile=" ".join(["parola"] * 140))
    assert "profile-too-long" in codes(validate(cv, "ats"))


def test_labels_fall_back_to_the_language_and_can_be_overridden():
    cv = minimal()
    assert cv.label("profile") == LABELS["it"]["profile"]
    cv.lang = "en"
    assert cv.label("profile") == LABELS["en"]["profile"]
    cv.labels = {"profile": "Custom heading"}
    assert cv.label("profile") == "Custom heading"


def test_languages_are_frozen_only_by_convention():
    cv = minimal(languages=[Language(name="Italiano", level="Madrelingua")])
    assert cv.languages[0].name == "Italiano"


def test_education_year_can_be_hidden_from_portal_variants():
    cv = minimal(education=[Education(year="1978", title="Licenza media",
                                      where="Scuola")])
    assert cv.hide_education_years_in_ats is True
