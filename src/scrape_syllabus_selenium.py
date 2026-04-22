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
DOCS_DOMAIN = "docs.ie.edu"


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
            degree_urls.append((text, href))
            print(f"  Found degree: {text or href}")

    print(f"\nTotal degrees found: {len(degree_urls)}")
    return degree_urls


def get_syllabus_links_for_degree(driver, degree_name, degree_url):
    """Go to the /the-program/#study-plan page and extract all docs.ie.edu PDF links."""
    study_plan_url = degree_url.rstrip("/") + "/the-program/#study-plan"
    print(f"\nScraping: {degree_name}")
    print(f"  URL: {study_plan_url}")

    links = get_links_from_page(driver, study_plan_url)

    syllabus_links = []
    seen = set()
    for text, href in links:
        if DOCS_DOMAIN in href and href.endswith(".pdf") and href not in seen:
            seen.add(href)
            syllabus_links.append({
    "degree": degree_name,
    "course_name": href.split("/")[-1].replace(".pdf", "").replace("_", " ").strip(),
    "syllabus_url": href,
})
            print(f"    Found: {text or href}")

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
    print(df[["degree", "course_name", "syllabus_url"]].to_string())


if __name__ == "__main__":
    main()