import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from syllabus_scraper.parse_grading import (
    map_label_to_category,
    compute_total_weight,
    extract_grading_items_from_text,
    normalize_label,
)


# --- map_label_to_category ---

def test_final_exam_variants():
    assert map_label_to_category("Final Exam") == "final_exam"
    assert map_label_to_category("final exam") == "final_exam"
    assert map_label_to_category("FINAL-EXAM") == "final_exam"
    # squished (no-space PDF artifact)
    assert map_label_to_category("A.Finalexam") == "final_exam"


def test_midterm_variants():
    assert map_label_to_category("Midterm") == "midterm_tests"
    assert map_label_to_category("Midterm Exam") == "midterm_tests"
    assert map_label_to_category("Intermediate tests") == "midterm_tests"
    assert map_label_to_category("Intermediate exams") == "midterm_tests"
    assert map_label_to_category("B.Midtermexams") == "midterm_tests"


def test_quiz_variants():
    assert map_label_to_category("Quizzes") == "quizzes"
    assert map_label_to_category("Quiz") == "quizzes"
    assert map_label_to_category("Exercises & Quizes") == "quizzes"


def test_project_variants():
    assert map_label_to_category("Group Projects") == "project"
    assert map_label_to_category("Group Work") == "project"
    assert map_label_to_category("Group Presentation") == "project"
    assert map_label_to_category("Project report and deliverables") == "project"
    assert map_label_to_category("Project presentation") == "project"
    assert map_label_to_category("Scientific writing project") == "project"
    assert map_label_to_category("Final presentation") == "project"
    assert map_label_to_category("D.Groupworkandpresentation") == "project"


def test_participation_variants():
    assert map_label_to_category("Class Participation") == "participation"
    assert map_label_to_category("Participation in class") == "participation"
    assert map_label_to_category("participation") == "participation"


def test_individual_work_is_other():
    assert map_label_to_category("Individual work") == "other"
    assert map_label_to_category("C.Individualwork") == "other"
    assert map_label_to_category("Final report on individual contribution") == "other"


def test_header_rows_return_none():
    assert map_label_to_category("criteria") is None
    assert map_label_to_category("Evaluation Criteria") is None
    assert map_label_to_category("percentage") is None
    assert map_label_to_category("") is None


# --- compute_total_weight ---

def test_compute_total_weight():
    grading = {
        "final_exam": 40,
        "midterm_tests": 30,
        "quizzes": 10,
        "project": 10,
        "participation": 10,
        "other": 0,
    }
    assert compute_total_weight(grading) == 100


def test_compute_total_weight_zeros():
    grading = {k: 0 for k in ["final_exam", "midterm_tests", "quizzes", "project", "participation", "other"]}
    assert compute_total_weight(grading) == 0


# --- extract_grading_items_from_text ---

SAMPLE_TEXT = """
ACADEMIC YEAR 2024-2025
NUMBER OF CREDITS 6
EVALUATION CRITERIA
Final Exam 40 %
Midterm Exam 30 %
Group Project 15 %
Class Participation 15 %
RE-SIT / RE-TAKE POLICY
Students who fail...
"""

def test_extract_from_standard_text():
    result = extract_grading_items_from_text(SAMPLE_TEXT)
    assert result["final_exam"] == 40
    assert result["midterm_tests"] == 30
    assert result["project"] == 15
    assert result["participation"] == 15
    assert compute_total_weight(result) == 100


BRACKET_TEXT = """
ACADEMIC YEAR 2024-2025
NUMBER OF CREDITS 6
EVALUATION CRITERIA
A.Finalexam[40%]
B.Midtermexams[30%]
C.Individualwork[15%]
D.Groupworkandpresentation[15%]
RE-SIT / RE-TAKE POLICY
"""

def test_extract_bracket_format():
    result = extract_grading_items_from_text(BRACKET_TEXT)
    assert result["final_exam"] == 40
    assert result["midterm_tests"] == 30
    assert result["project"] == 15


def test_no_criteria_section_returns_zeros():
    result = extract_grading_items_from_text("Some random text with no criteria section.")
    assert compute_total_weight(result) == 0
