import requests
import re
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

GRAPHQL_URL = "https://api.studiegids.uva.nl/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://coursecatalogue.uva.nl",
    "Referer": "https://coursecatalogue.uva.nl/"
}

PROGRAMMES = {
    5248: "econometrics-data-science",
    5258: "economics-business",
    5271: "business-administration",
    5447: "political-science",
    5254: "pple",
    5212: "business-analytics",
}

GET_PAGES_QUERY = """
query getProgrammeById($academicYear: Int!, $id: Int!, $language: CourseCatalogLanguage!) {
  programmeById(academicYear: $academicYear, id: $id, language: $language) {
    id
    name
    pages {
      id
      name
      parentPageId
      hasContent
    }
  }
}
"""

GET_PAGE_CONTENT_QUERY = """query getProgrammePageById($academicYear: Int!, $id: Int!, $language: CourseCatalogLanguage!) {
  programmePageById(academicYear: $academicYear, id: $id, language: $language) {
    id
    name
    content
  }
}"""


def make_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def get_programme_pages(programme_id):
    resp = requests.post(
        GRAPHQL_URL,
        json={
            "operationName": "getProgrammeById",
            "variables": {"id": programme_id, "academicYear": 2025, "language": "ENGLISH"},
            "query": GET_PAGES_QUERY
        },
        headers=HEADERS
    )
    data = resp.json()
    return data["data"]["programmeById"]["pages"]


def get_page_content(page_id):
    resp = requests.post(
        GRAPHQL_URL,
        json={
            "operationName": "getProgrammePageById",
            "variables": {"id": page_id, "academicYear": 2025, "language": "ENGLISH"},
            "extensions": {"clientLibrary": {"name": "@apollo/client", "version": "4.1.9"}},
            "query": GET_PAGE_CONTENT_QUERY
        },
        headers=HEADERS
    )
    data = resp.json()
    return data["data"]["programmePageById"].get("content", "") or ""


def extract_course_ids_from_content(content):
    courses = []
    matches = re.findall(
        r'data-title="([^"]+)"[^>]*data-id="(\d+)"',
        content
    )
    for title, course_id in matches:
        courses.append((title, int(course_id)))
    return courses


def get_assessment_from_course(driver, course_id):
    url = f"https://coursecatalogue.uva.nl/en/courses/2025/1/{course_id}"
    try:
        driver.get(url)
        time.sleep(2.5)
        body = driver.find_element(By.TAG_NAME, "body").text

        # Find assessment section after Study materials
        if "Study materials" in body:
            start = body.find("Study materials")
            rest = body[start:]
            if "Assessment" in rest:
                start = start + rest.find("Assessment")
            else:
                return None
        elif "Assessment" in body:
            start = body.rfind("Assessment")
        else:
            return None

        assessment_text = body[start:start + 2000]

        results = {
            "final_exam": 0,
            "midterm_tests": 0,
            "project": 0,
            "participation": 0,
            "other": 0,
        }

        # Match percentage BEFORE label (UvA format: "30% midterm exam")
        matches = re.findall(
            r"(\d+)\s*%\s*([^\n•*]{5,80})",
            assessment_text,
            re.IGNORECASE
        )

        # Also match percentage AFTER label (other format: "midterm exam (30%)")
        matches += [(pct, ctx) for ctx, pct in re.findall(
            r"([^\n•*]{5,80}?)\s*[\(\,\:]\s*(\d+)\s*%",
            assessment_text,
            re.IGNORECASE
        )]

        total = 0
        for pct_str, context in matches:
            pct = int(pct_str)
            if pct > 100 or pct == 0:
                continue
            context_lower = context.lower()

            if any(k in context_lower for k in ["final exam", "endterm", "end-term", "final examination", "written exam"]):
                results["final_exam"] += pct
            elif any(k in context_lower for k in ["midterm", "mid-term", "partial"]):
                results["midterm_tests"] += pct
            elif any(k in context_lower for k in ["assignment", "project", "paper", "essay", "group", "thesis"]):
                results["project"] += pct
            elif any(k in context_lower for k in ["participation", "attendance", "tutorial test", "weekly test", "quiz"]):
                results["participation"] += pct
            else:
                results["other"] += pct

            total += pct

        if total < 50 or total > 150:
            return None

        return results, total

    except Exception:
        return None


def main():
    driver = make_driver()
    all_rows = []

    try:
        for programme_id, degree_slug in PROGRAMMES.items():
            print(f"\n{'='*50}")
            print(f"Degree: {degree_slug} (ID: {programme_id})")

            pages = get_programme_pages(programme_id)
            programme_page = next((p for p in pages if p["name"] == "Programme"), None)
            if not programme_page:
                print("  No Programme page found")
                continue

            programme_page_id = programme_page["id"]
            child_pages = [p for p in pages if p["parentPageId"] == programme_page_id]
            if programme_page["hasContent"]:
                child_pages.insert(0, programme_page)

            all_courses = []
            seen_ids = set()

            for page in child_pages:
                name_lower = page["name"].lower()
                if any(k in name_lower for k in ["elective", "honours", "transitional"]):
                    continue

                content = get_page_content(page["id"])
                courses = extract_course_ids_from_content(content)
                print(f"    {page['name']}: {len(courses)} courses")

                for course_name, course_id in courses:
                    if course_id not in seen_ids:
                        seen_ids.add(course_id)
                        all_courses.append((course_name, course_id))

                time.sleep(0.3)

            print(f"  Total unique courses: {len(all_courses)}")

            for course_name, course_id in all_courses:
                result = get_assessment_from_course(driver, course_id)
                if result is None:
                    continue

                grading, total = result
                row = {
                    "university": "UvA",
                    "degree": degree_slug,
                    "course_name": course_name,
                    **grading,
                    "total_weight": total,
                    "parse_status": "ok" if 90 <= total <= 110 else "needs_review",
                }
                all_rows.append(row)
                print(f"  {course_name}: final={grading['final_exam']}% midterm={grading['midterm_tests']}% total={total}%")

    finally:
        driver.quit()

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["degree", "course_name"])

    out_path = "data/processed/uva_grading_dataframe.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✅ Done! Scraped {len(df)} courses across {len(PROGRAMMES)} degrees.")

    if not df.empty:
        ok = df[df["parse_status"] == "ok"].copy()
        ok["exam_weight"] = ok["final_exam"] + ok["midterm_tests"]
        print("\nAverage exam weight by degree:")
        print(ok.groupby("degree")["exam_weight"].mean().sort_values(ascending=False).round(1))


if __name__ == "__main__":
    main()