from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

MAIN_URL = "https://www.ie.edu/university/studies/academic-programs/"
BASE_DOMAIN = "ie.edu/university/studies/academic-programs/"
DOCS_DOMAINS = ["docs.ie.edu", "thesaurus.ie.edu", "files.thesaurus.ie.edu", "static.ie.edu"]

DEGREE_NAME_MAP = {
    "bachelor-applied-mathematics": "BAM",
    "bachelor-computer-science": "BCSAI",
    "bachelor-data-business-analytics": "BDBA",
    "bachelor-business-administration": "BBA",
    "bachelor-international-relations": "BIR",
    "bachelor-laws": "LLB",
    "bachelor-humanities": "BHUM",
    "bachelor-architectural": "BAS",
    "bachelor-behavior": "BBSS",
    "bachelor-economics": "BEC",
    "bachelor-political": "BPS",
    "bachelor-pple": "PPLE",
    "bachelor-communication": "BCDM",
    "bachelor-design": "BDES",
    "bachelor-environmental": "BESS",
    "bachelor-fashion": "BFD",
}


def make_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def get_links_from_page(driver, url):
    driver.get(url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    links = []
    for elem in driver.find_elements(By.TAG_NAME, "a"):
        try:
            href = elem.get_attribute("href")
            text = elem.text.strip()
            if href:
                links.append((text, href))
        except Exception:
            continue
    return links


def get_degree_urls(driver):
    """Scrape the main programs page and return all individual degree URLs."""
    print("Scanning main programs page for degree links...")
    links = get_links_from_page(driver, MAIN_URL)

    degree_urls = []
    seen = set()
    for text, href in links:
        if (
            BASE_DOMAIN in href
            and href.rstrip("/") != MAIN_URL.rstrip("/")
            and href not in seen
            and href.count("/") == MAIN_URL.count("/") + 1
        ):
            seen.add(href)
            # Extract degree code from URL slug
            slug = href.rstrip("/").split("/")[-1]
            degree_code = next(
                (code for key, code in DEGREE_NAME_MAP.items() if key in slug),
                slug  # fallback to full slug if not in map
            )
            degree_urls.append((degree_code, href))
            print(f"  Found degree: {degree_code} → {slug}")

    print(f"\nTotal degrees found: {len(degree_urls)}")
    return degree_urls


def get_syllabus_links_for_degree(driver, degree_name, degree_url):
    """Go to the /the-program/#study-plan page and extract all PDF links."""
    study_plan_url = degree_url.rstrip("/") + "/the-program/#study-plan"
    print(f"\nScraping: {degree_name}")
    print(f"  URL: {study_plan_url}")

    links = get_links_from_page(driver, study_plan_url)

    syllabus_links = []
    seen = set()
    for text, href in links:
        if any(domain in href for domain in DOCS_DOMAINS) and href.endswith(".pdf") and href not in seen:
            seen.add(href)
            course_name = href.split("/")[-1].replace(".pdf", "").replace("_", " ").replace("-", " ").strip()
            syllabus_links.append({
                "degree": degree_name,
                "course_name": course_name,
                "syllabus_url": href,
            })
            print(f"    Found: {course_name}")

    print(f"  Syllabuses found: {len(syllabus_links)}")
    return syllabus_links


def main():
    driver = make_driver()
    all_syllabuses = []
    degree_urls = []

    try:
        degree_urls = get_degree_urls(driver)

        if not degree_urls:
            print("No degree URLs found.")
            return

        for degree_name, degree_url in degree_urls:
            try:
                syllabuses = get_syllabus_links_for_degree(driver, degree_name, degree_url)
                all_syllabuses.extend(syllabuses)
            except Exception as e:
                print(f"  Error scraping {degree_name}: {e}")
                continue

    finally:
        driver.quit()

    df = pd.DataFrame(all_syllabuses)
    out_path = "data/processed/all_syllabus_links.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✅ Done! Found {len(df)} syllabuses across {len(degree_urls)} degrees.")
    print(f"Saved to {out_path}")
    if not df.empty:
        print(df[["degree", "course_name", "syllabus_url"]].to_string())


if __name__ == "__main__":
    main()