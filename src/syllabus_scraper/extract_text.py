import os
import re
import pandas as pd
import pdfplumber


def extract_pdf_text(pdf_path):
    text_parts = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        print(f"Failed to read {pdf_path}: {e}")
        return ""

    return "\n".join(text_parts)


def detect_syllabus_markers(text):
    markers = {
        "number_of_credits": "number of credits" in text,
        "academic_year": "academic year" in text,
        "semester": "semester" in text,
        "subject_description": "subject description" in text,
        "evaluation_criteria": "evaluation criteria" in text,
    }

    score = sum(markers.values())
    is_syllabus = score >= 3

    return markers, score, is_syllabus


def extract_percentages(text):
    matches = re.findall(r"([A-Za-z /&]+)\s+(\d{1,3})\s*%", text)
    return matches


def main():
    input_folder = "data/raw"
    output_csv = "data/processed/pdf_analysis.csv"

    results = []

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_folder, filename)
        print(f"Analyzing: {filename}")

        text = extract_pdf_text(pdf_path)
        text_lower = text.lower()

        markers, score, is_syllabus = detect_syllabus_markers(text_lower)
        percentages = extract_percentages(text)

        results.append({
            "filename": filename,
            "is_syllabus": is_syllabus,
            "marker_score": score,
            "number_of_credits_found": markers["number_of_credits"],
            "academic_year_found": markers["academic_year"],
            "semester_found": markers["semester"],
            "subject_description_found": markers["subject_description"],
            "evaluation_criteria_found": markers["evaluation_criteria"],
            "percentages_found": str(percentages[:10]),
        })

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)

    print(f"Saved analysis to {output_csv}")


if __name__ == "__main__":
    main()
    