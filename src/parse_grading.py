import os
import re
import pandas as pd
import pdfplumber


def extract_pdf_text(pdf_path: str) -> str:
    parts = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    parts.append(text)
    except Exception as e:
        print(f"Failed to read {pdf_path}: {e}")
        return ""

    return "\n".join(parts)


def extract_course_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        return lines[0]
    return ""


def is_likely_syllabus(text: str) -> bool:
    text_lower = text.lower()
    return (
        "number of credits" in text_lower
        and "academic year" in text_lower
        and ("evaluation criteria" in text_lower or "criteria" in text_lower)
    )


def normalize_label(label: str) -> str:
    return " ".join(label.lower().strip().split())


def compute_total_weight(grading: dict) -> int:
    return (
        grading["final_exam"]
        + grading["midterm_tests"]
        + grading["quizzes"]
        + grading["project"]
        + grading["participation"]
        + grading["other"]
    )


def extract_grading_items_from_pdf(pdf_path: str) -> dict:
    results = {
        "final_exam": 0,
        "midterm_tests": 0,
        "quizzes": 0,
        "project": 0,
        "participation": 0,
        "other": 0,
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                page_text_lower = page_text.lower()

                if "evaluation criteria" not in page_text_lower and "criteria" not in page_text_lower:
                    continue

                tables = page.extract_tables()
                if not tables:
                    continue

                for table in tables:
                    if not table:
                        continue

                    for row in table:
                        if not row:
                            continue

                        cleaned = []
                        for cell in row:
                            if cell is None:
                                cleaned.append("")
                            else:
                                cleaned.append(str(cell).strip())

                        if len(cleaned) < 2:
                            continue

                        label = normalize_label(cleaned[0])
                        pct_cell = cleaned[1].strip().lower()

                        if not label:
                            continue

                        if "criteria" in label and "percentage" in pct_cell:
                            continue

                        match = re.search(r"(\d{1,3})\s*%", pct_cell)
                        if not match:
                            continue

                        pct = int(match.group(1))

                        if label.startswith("final exam"):
                            results["final_exam"] += pct
                        elif (
                            label.startswith("midterm + quizzes")
                            or label.startswith("midterm and quizzes")
                            or label.startswith("intermediate tests")
                            or label.startswith("intermediate test")
                            or label.startswith("midterm")
                        ):
                            results["midterm_tests"] += pct
                        elif label.startswith("quizzes") or label.startswith("quiz"):
                            results["quizzes"] += pct
                        elif (
                            label.startswith("group project")
                            or label.startswith("group projects")
                            or label.startswith("group work")
                            or label.startswith("project")
                        ):
                            results["project"] += pct
                        elif (
                            label.startswith("class participation")
                            or label.startswith("participation")
                        ):
                            results["participation"] += pct
                        elif label.startswith("individual work"):
                            results["other"] += pct

        return results

    except Exception as e:
        print(f"Failed table extraction for {pdf_path}: {e}")
        return results


def extract_grading_items_from_text(text: str) -> dict:
    text_lower = text.lower()

    results = {
        "final_exam": 0,
        "midterm_tests": 0,
        "quizzes": 0,
        "project": 0,
        "participation": 0,
        "other": 0,
    }

    if "evaluation criteria" not in text_lower:
        return results

    start = text_lower.find("evaluation criteria")

    end_candidates = [
        text_lower.find("re-sit", start),
        text_lower.find("re-take", start),
        text_lower.find("ai policy", start),
        text_lower.find("bibliography", start),
        text_lower.find("attendance policy", start),
        text_lower.find("ethical policy", start),
        text_lower.find("behavior rules", start),
    ]
    end_candidates = [x for x in end_candidates if x != -1]

    if end_candidates:
        end = min(end_candidates)
        section = text[start:end]
    else:
        section = text[start:start + 2500]

    lines = [line.strip() for line in section.splitlines() if line.strip()]

    for line in lines:
        if "%" not in line:
            continue

        match = re.search(r"(.+?)\s+(\d{1,3})\s*%", line, flags=re.IGNORECASE)
        if not match:
            continue

        raw_label = match.group(1).strip().lower()
        pct = int(match.group(2))

        if raw_label.startswith("final exam"):
            results["final_exam"] += pct
        elif (
            raw_label.startswith("midterm + quizzes")
            or raw_label.startswith("midterm and quizzes")
            or raw_label.startswith("intermediate tests")
            or raw_label.startswith("intermediate test")
            or raw_label.startswith("midterm")
        ):
            results["midterm_tests"] += pct
        elif raw_label.startswith("quizzes") or raw_label.startswith("quiz"):
            results["quizzes"] += pct
        elif (
            raw_label.startswith("group project")
            or raw_label.startswith("group projects")
            or raw_label.startswith("group work")
            or raw_label.startswith("project")
        ):
            results["project"] += pct
        elif raw_label.startswith("class participation") or raw_label.startswith("participation"):
            results["participation"] += pct
        elif raw_label.startswith("individual work"):
            results["other"] += pct

    return results


def choose_best_grading(pdf_path: str, text: str) -> dict:
    table_grading = extract_grading_items_from_pdf(pdf_path)
    text_grading = extract_grading_items_from_text(text)

    table_total = compute_total_weight(table_grading)
    text_total = compute_total_weight(text_grading)

    # Prefer valid totals near 100
    if 90 <= table_total <= 110 and not (90 <= text_total <= 110):
        return table_grading
    if 90 <= text_total <= 110 and not (90 <= table_total <= 110):
        return text_grading

    # If both are valid, prefer table parsing
    if 90 <= table_total <= 110 and 90 <= text_total <= 110:
        return table_grading

    # Otherwise choose whichever is closer to 100
    if abs(table_total - 100) <= abs(text_total - 100):
        return table_grading
    return text_grading


def main():
    input_folder = "data/raw"
    output_csv = "data/processed/grading_dataframe.csv"

    rows = []

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_folder, filename)
        print(f"Parsing: {filename}")

        text = extract_pdf_text(pdf_path)
        if not text:
            continue

        if not is_likely_syllabus(text):
            continue

        course_name = extract_course_name(text)
        grading = choose_best_grading(pdf_path, text)
        total_weight = compute_total_weight(grading)

        row = {
            "filename": filename,
            "course_name": course_name,
            "final_exam": grading["final_exam"],
            "midterm_tests": grading["midterm_tests"],
            "quizzes": grading["quizzes"],
            "project": grading["project"],
            "participation": grading["participation"],
            "other": grading["other"],
            "total_weight": total_weight,
        }

        # Keep only plausible grading structures
        if 90 <= total_weight <= 110:
            rows.append(row)
        else:
            print(f"Skipping suspicious row: {filename} | {course_name} | total={total_weight}")

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)

    print(f"Saved grading dataframe to {output_csv}")
    print("Number of rows:", len(df))
    print(df[["filename", "course_name", "total_weight"]].to_string())


if __name__ == "__main__":
    main()