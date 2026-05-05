import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from syllabus_scraper.ie_parser import IEParser

parser = IEParser()


def test_university_name():
    assert parser.university_name == "IE"


def test_section_keywords():
    assert "evaluation criteria" in parser.section_keywords


def test_section_end_keywords():
    assert "re-sit" in parser.section_end_keywords
    assert "bibliography" in parser.section_end_keywords


# --- is_likely_syllabus ---

def test_is_likely_syllabus_valid():
    text = "Number of Credits 6 Academic Year 2024 Evaluation Criteria Final Exam 60%"
    assert parser.is_likely_syllabus(text) is True


def test_is_likely_syllabus_missing_credits():
    text = "Academic Year 2024 Evaluation Criteria Final Exam 60%"
    assert parser.is_likely_syllabus(text) is False


def test_is_likely_syllabus_missing_year():
    text = "Number of Credits 6 Evaluation Criteria Final Exam 60%"
    assert parser.is_likely_syllabus(text) is False


def test_is_likely_syllabus_empty():
    assert parser.is_likely_syllabus("") is False


# --- map_label_to_category ---

def test_final_exam():
    assert parser.map_label_to_category("Final Exam") == "final_exam"
    assert parser.map_label_to_category("Final Test") == "final_exam"
    assert parser.map_label_to_category("A.Finalexam") == "final_exam"


def test_midterm():
    assert parser.map_label_to_category("Midterm") == "midterm_tests"
    assert parser.map_label_to_category("Intermediate tests") == "midterm_tests"
    assert parser.map_label_to_category("Intermediate exam") == "midterm_tests"


def test_quizzes():
    assert parser.map_label_to_category("Quiz") == "quizzes"
    assert parser.map_label_to_category("Quizzes") == "quizzes"


def test_project():
    assert parser.map_label_to_category("Group Project") == "project"
    assert parser.map_label_to_category("Group Work") == "project"
    assert parser.map_label_to_category("Final presentation") == "project"
    assert parser.map_label_to_category("Project report") == "project"


def test_participation():
    assert parser.map_label_to_category("Class Participation") == "participation"
    assert parser.map_label_to_category("participation") == "participation"


def test_individual_work():
    assert parser.map_label_to_category("Individual work") == "other"
    assert parser.map_label_to_category("Individual contribution") == "other"


def test_header_rows_return_none():
    assert parser.map_label_to_category("criteria") is None
    assert parser.map_label_to_category("Evaluation Criteria") is None
    assert parser.map_label_to_category("percentage") is None
    assert parser.map_label_to_category("") is None


# --- normalize_label ---

def test_normalize_label():
    assert parser.normalize_label("  Final  Exam  ") == "final exam"
    assert parser.normalize_label("PARTICIPATION") == "participation"
    assert parser.normalize_label("Group   Work") == "group work"
