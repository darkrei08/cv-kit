"""Tests for the command line interface.

These run the real command in a subprocess, because the usage that broke in CI was
exactly this: the package imported fine and the console script existed, but
``python -m cvkit`` had no module to execute.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True, timeout=300)


def test_module_entry_point_reports_a_version():
    result = run("-m", "cvkit", "--version")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()


def test_doctor_runs_and_names_the_backends():
    result = run("-m", "cvkit", "doctor")
    assert result.returncode == 0, result.stderr
    for backend in ("word", "docx2pdf", "libreoffice", "pandoc"):
        assert backend in result.stdout


def test_help_lists_every_command():
    result = run("-m", "cvkit", "--help")
    assert result.returncode == 0
    for command in ("init", "build", "qa", "diagram", "html", "single", "doctor"):
        assert command in result.stdout


def test_init_then_build_then_qa(tmp_path):
    project = tmp_path / "my-cv"
    assert run("-m", "cvkit", "init", str(project)).returncode == 0
    assert (project / "cv_data.py").exists()
    assert (project / "assets").is_dir()

    out = tmp_path / "out"
    built = run("-m", "cvkit", "build", str(project), "-o", str(out), "--no-pdf",
                "--prefix", "Test_Person")
    assert built.returncode == 0, built.stderr
    assert (out / "Test_Person_CV_ATS.docx").exists()
    assert (out / "Test_Person_CV_Master.docx").exists()

    checked = run("-m", "cvkit", "qa", str(out), "--directory", str(project))
    # The scaffold is deliberately incomplete, so warnings are expected; what matters
    # is that the command runs, finds the files and reports something readable.
    assert "checked" in checked.stdout


def test_init_refuses_to_overwrite_without_force(tmp_path):
    project = tmp_path / "again"
    assert run("-m", "cvkit", "init", str(project)).returncode == 0
    second = run("-m", "cvkit", "init", str(project))
    assert second.returncode == 1
    assert "already exists" in second.stdout


def test_build_without_a_data_file_explains_itself(tmp_path):
    result = run("-m", "cvkit", "build", str(tmp_path), "-o", str(tmp_path / "out"))
    assert result.returncode != 0
    assert "cv_data.py" in (result.stdout + result.stderr)


def test_qa_on_an_empty_directory_reports_nothing_to_check(tmp_path):
    result = run("-m", "cvkit", "qa", str(tmp_path))
    assert result.returncode == 1
    assert "nothing to check" in result.stdout


@pytest.mark.parametrize("part", ["ats", "designed", "motivation"])
def test_single_parts_build_on_their_own(tmp_path, part):
    project = tmp_path / "proj"
    run("-m", "cvkit", "init", str(project))
    out = tmp_path / "out"
    result = run("-m", "cvkit", "single", part, str(project), "-o", str(out))
    assert result.returncode == 0, result.stderr
    assert (out / f"cv-{part}.docx").exists()
