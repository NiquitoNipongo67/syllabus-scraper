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


# Maps a normalized label to a grading category.
# Returns None only for known header/non-data rows.
def map_label_to_category(label: str) -> str | None:
    label = normalize_label(label)
    # Strip leading "a.", "b.", etc. prefixes from lettered-section syllabuses
    label = re.sub(r"^[a-z]\.", "", label).strip()

    # Skip known header/metadata rows
    if label in ("criteria", "evaluation criteria", "percentage",
                 "learning objectives", "comments", ""):
        return None

    squished = label.replace(" ", "")

    # Final exam
    if ("final exam" in label or "final-exam" in label or "final test" in label
            or "finalexam" in squished):
        return "final_exam"

    # Midterm / intermediate tests
    if ("midterm" in label or "intermediate test" in label
            or "intermediate exam" in label or "midterm" in squished):
        return "midterm_tests"

    # Quizzes
    if "quiz" in label or "quiz" in squished:
        return "quizzes"

    # Group projects, presentations, any team/project work
    if (
        any(k in label for k in [
            "group project", "group work", "group presentation",
            "project report", "project presentation", "scientific writing",
            "final presentation",
        ])
        or any(k in squished for k in [
            "groupproject", "groupwork", "grouppresentation", "groupworkand",
        ])
        or label.startswith("project")
    ):
        return "project"

    # Class participation
    if "participation" in label or "participation" in squished:
        return "participation"

    # Individual work → other
    if ("individual work" in label or "individual contribution" in label
            or "individualwork" in squished):
        return "other"

    # Catch-all: any remaining row with a percentage goes to other
    return "other"


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
            # Find the first page that contains "evaluation criteria"
            criteria_page_idx = None
            for i, page in enumerate(pdf.pages):
                if "evaluation criteria" in (page.extract_text() or "").lower():
                    criteria_page_idx = i
                    break

            if criteria_page_idx is None:
                return results

            # Scan from criteria page through the next 3 pages to capture
            # split tables where the header and data land on different pages.
            for i in range(criteria_page_idx, min(criteria_page_idx + 4, len(pdf.pages))):
                page = pdf.pages[i]
                tables = page.extract_tables()
                if not tables:
                    continue

                for table in tables:
                    if not table:
                        continue

                    for row in table:
                        if not row:
                            continue

                        cleaned = [str(c).strip() if c is not None else "" for c in row]

                        if len(cleaned) < 2:
                            continue

                        label = normalize_label(cleaned[0])
                        pct_cell = cleaned[1].strip().lower()

                        if not label:
                            continue

                        # Skip column-header rows
                        if label in ("criteria", "evaluation criteria") and "percentage" in pct_cell:
                            continue

                        match = re.search(r"(\d{1,3})\s*%", pct_cell)
                        if not match:
                            continue

                        pct = int(match.group(1))
                        category = map_label_to_category(label)
                        if category:
                            results[category] += pct

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

        raw_label = None
        pct = None

        # Pattern 1: "Label NN%" (standard spaced format)
        m = re.search(r"(.+?)\s+(\d{1,3})\s*%", line, flags=re.IGNORECASE)
        if m:
            raw_label = m.group(1).strip().lower()
            pct = int(m.group(2))

        # Pattern 2: "Label[NN%]" (bracket format, e.g. file_45)
        if raw_label is None:
            m2 = re.search(r"(.+?)\[(\d{1,3})%\]", line, flags=re.IGNORECASE)
            if m2:
                raw_label = m2.group(1).strip().lower()
                pct = int(m2.group(2))

        if raw_label is None or pct is None:
            continue

        category = map_label_to_category(raw_label)

        # In text extraction use explicit categories only; skip catch-all
        # to avoid false positives from narrative sentences.
        if category and category != "other":
            results[category] += pct
        elif category == "other" and any(k in raw_label for k in [
            "individual work", "individual contribution", "individualwork",
        ]):
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

    # If both are valid, prefer table parsing (more structured)
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

    for filename in sorted(os.listdir(input_folder)):
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

        parse_status = "ok" if 90 <= total_weight <= 110 else "needs_review"

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
            "parse_status": parse_status,
        }

        rows.append(row)

        if parse_status == "needs_review":
            print(f"  [needs_review] {filename} | {course_name} | total={total_weight}")

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)

    print(f"\nSaved grading dataframe to {output_csv}")
    print("Total rows:", len(df))
    print()
    print(df[["filename", "course_name", "final_exam", "midterm_tests", "quizzes",
              "project", "participation", "other", "total_weight", "parse_status"]].to_string())

    clean_df = df[df["parse_status"] == "ok"].copy()
    clean_df.to_csv("data/processed/grading_dataframe_clean.csv", index=False)

    print(f"\nClean rows (total ~100%): {len(clean_df)}")


if __name__ == "__main__":
    main()
