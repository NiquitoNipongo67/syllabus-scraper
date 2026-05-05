import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from syllabus_scraper.download_pdfs import build_filename


# --- build_filename ---

def test_grados_url_uses_degree_from_url():
    row = {
        "syllabus_url": "https://docs.ie.edu/Grados/BAM/Fall_CalculusI.pdf",
        "degree": "BAM",
    }
    result = build_filename(row)
    assert result == "BAM__Fall_CalculusI.pdf"


def test_grados_dobles_uses_dobles_as_prefix():
    # DOBLES handling happens at scrape time; build_filename uses the URL degree as-is
    row = {
        "syllabus_url": "https://docs.ie.edu/Grados/DOBLES/SomeCourse.pdf",
        "degree": "BBA",
    }
    result = build_filename(row)
    assert result == "DOBLES__SomeCourse.pdf"


def test_non_grados_url_falls_back_to_degree_column():
    row = {
        "syllabus_url": "https://static.ie.edu/syllabuses/Calculus.pdf",
        "degree": "BAM",
    }
    result = build_filename(row)
    assert result == "BAM__Calculus.pdf"


def test_filename_ends_with_pdf():
    row = {
        "syllabus_url": "https://docs.ie.edu/Grados/BCSAI/Algorithms.pdf",
        "degree": "BCSAI",
    }
    result = build_filename(row)
    assert result.endswith(".pdf")


def test_degree_truncated_to_30_chars_in_fallback():
    long_degree = "A" * 50
    row = {
        "syllabus_url": "https://static.ie.edu/syllabuses/Course.pdf",
        "degree": long_degree,
    }
    result = build_filename(row)
    prefix = result.split("__")[0]
    assert len(prefix) <= 30
