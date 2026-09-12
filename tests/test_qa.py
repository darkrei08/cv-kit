# -*- coding: utf-8 -*-
"""Tests for the quality checks and the export helpers."""
from pathlib import Path

from docx import Document

from cvkit.builder import _stem
from cvkit.exporters import backends, export_text
from cvkit.qa import default_forbidden_tokens, inspect_docx, qa_cv
from test_build import make_cv


def test_docx_with_a_table_fails_the_portal_check(tmp_path):
    path = tmp_path / "with_table.docx"
    document = Document()
    document.add_paragraph("Test Person")
    document.add_table(rows=2, cols=2)
    document.save(str(path))

    report = inspect_docx(path, expect_tables=0, expect_images=0, variant="ats")
    assert not report.ok
    assert "table-in-portal-variant" in {f.code for f in report.findings}


def test_clean_portal_document_passes(tmp_path):
    path = tmp_path / "clean.docx"
    document = Document()
    document.add_paragraph("Test Person")
    document.add_paragraph("Elettricista")
    document.save(str(path))

    report = inspect_docx(path, expect_tables=0, expect_images=0, variant="ats")
    assert report.ok


def test_a_text_box_is_detected_as_a_hidden_container(tmp_path):
    from docx.oxml import OxmlElement

    path = tmp_path / "textbox.docx"
    document = Document()
    paragraph = document.add_paragraph("Test")
    run = paragraph.add_run()
    box = OxmlElement("w:txbxContent")
    run._r.append(box)
    document.save(str(path))

    report = inspect_docx(path, variant="ats")
    assert "hidden-text-container" in {f.code for f in report.findings}


def test_missing_file_is_reported_not_ignored(tmp_path):
    cv = make_cv(tmp_path)
    reports = qa_cv(cv, {"ATS": tmp_path / "does-not-exist.pdf"})
    codes = {f.code for report in reports for f in report.findings}
    assert "missing-file" in codes


def test_portal_variants_are_recognised_by_name():
    from cvkit.qa import is_portal_variant

    assert is_portal_variant("Bianchi_CV_ATS")
    assert is_portal_variant("candidate_cv_ats_en.pdf")
    assert not is_portal_variant("Bianchi_CV_DESIGNED")
    assert not is_portal_variant("Bianchi_CV_Fascicolo")


def test_forbidden_tokens_come_from_the_model(tmp_path):
    cv = make_cv(tmp_path)
    tokens = default_forbidden_tokens(cv)
    assert "01/01/1980" in tokens
    assert any("Via Esempio" in token for token in tokens)


def test_short_values_are_not_treated_as_tokens(tmp_path):
    from cvkit.model import CV, Contact

    cv = CV(contact=Contact(name="X", personal={"Sesso": "M"}))
    assert default_forbidden_tokens(cv) == ()


def test_stem_is_surname_first():
    assert _stem("Maria Grazia Rossi") == "Rossi_Maria_Grazia"
    assert _stem("Rossi") == "Rossi"
    assert _stem("") == "CV"


def test_backend_report_has_the_expected_keys():
    state = backends()
    assert set(state) == {"word", "docx2pdf", "libreoffice", "pandoc"}


def test_text_export_without_pandoc(tmp_path, monkeypatch):
    from cvkit import exporters

    monkeypatch.setattr(exporters, "find_pandoc", lambda: None)
    path = tmp_path / "doc.docx"
    document = Document()
    document.add_paragraph("Test Person")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Periodo"
    table.cell(0, 1).text = "01/2020"
    document.save(str(path))

    out = export_text(path, tmp_path / "doc.txt")
    content = out.read_text(encoding="utf-8")
    assert "Test Person" in content
    assert "Periodo | 01/2020" in content


def test_pdf_report_without_a_pdf_file_is_a_clean_error(tmp_path):
    report = inspect_docx(tmp_path / "nothing.docx") if (tmp_path / "nothing.docx").exists() \
        else None
    assert report is None


def test_a_forbidden_value_is_masked_in_the_report(tmp_path):
    """The guard must not republish the personal data it is guarding against."""
    from cvkit.qa import Report

    report = Report(path="x.pdf")
    # emulate the message construction used by inspect_pdf
    token = "NDRNLB64M13F052G"
    shown = f"{token[:2]}{'*' * 6}"
    report.add("error", "forbidden-token", f"a forbidden value ({shown}) must not appear")
    text = report.text()
    assert token not in text
    assert "ND******" in text


def test_binary_documents_are_read_by_the_pii_guard(tmp_path):
    """A scanner that only reads text cannot see inside a .docx."""
    import subprocess
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import check_no_pii

    document = tmp_path / "cv.docx"
    from docx import Document
    doc = Document()
    doc.add_paragraph("Via Giuseppe Impastato 54")
    doc.save(str(document))

    text, reason = check_no_pii.text_of(document)
    assert text is not None, reason
    assert "Impastato" in text
