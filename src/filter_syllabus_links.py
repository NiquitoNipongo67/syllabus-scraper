import pandas as pd


def filter_syllabus_links(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)

    include_keywords = [
        "pdf",
        "docs.ie.edu",
        "syllabus",
        "guide",
        "calculus",
        "discrete",
        "algebra",
        "mathematics",
        "statistics",
        "analysis",
        "geometry",
        "equations",
        "probability",
    ]

    exclude_keywords = [
        "calendar",
        "admission",
        "brochure",
        "privacy",
        "policy",
        "housing",
        "scholarship",
        "tuition",
        "fees",
        "apply",
    ]

    def is_candidate(row):
        text = str(row.get("text", "")).lower()
        url = str(row.get("url", "")).lower()
        combined = f"{text} {url}"

        has_include = any(word in combined for word in include_keywords)
        has_exclude = any(word in combined for word in exclude_keywords)

        return has_include and not has_exclude

    filtered = df[df.apply(is_candidate, axis=1)].copy()
    filtered.to_csv(output_csv, index=False)

    print(f"Saved {len(filtered)} candidate syllabus links to {output_csv}")


if __name__ == "__main__":
    filter_syllabus_links(
        "data/processed/all_rendered_links.csv",
        "data/processed/candidate_syllabus_links.csv"
    )