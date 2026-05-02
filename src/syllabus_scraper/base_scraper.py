from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


class BaseScraper(ABC):

    @property
    @abstractmethod
    def university_name(self) -> str:
        """Short name for the university, e.g. 'IE', 'UAM'"""
        pass

    @property
    @abstractmethod
    def main_url(self) -> str:
        """URL of the main programs/degrees page"""
        pass

    @property
    @abstractmethod
    def syllabus_domains(self) -> list:
        """List of domains where syllabus PDFs are hosted"""
        pass

    @abstractmethod
    def get_degree_urls(self, driver) -> list:
        """Return list of (degree_code, degree_url) tuples"""
        pass

    @abstractmethod
    def get_study_plan_url(self, degree_url: str) -> str:
        """Given a degree URL, return the URL of its study plan page"""
        pass

    @abstractmethod
    def assign_degree(self, href: str, page_degree: str) -> str:
        """Given a PDF link and the degree page it was found on, return the degree code"""
        pass

    def make_driver(self):
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def get_links_from_page(self, driver, url):
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

    def get_syllabus_links_for_degree(self, driver, degree_name, degree_url):
        study_plan_url = self.get_study_plan_url(degree_url)
        print(f"\nScraping: {degree_name}")
        print(f"  URL: {study_plan_url}")

        links = self.get_links_from_page(driver, study_plan_url)

        syllabus_links = []
        seen = set()
        for text, href in links:
            if (
                any(domain in href for domain in self.syllabus_domains)
                and href.endswith(".pdf")
                and href not in seen
            ):
                seen.add(href)
                course_name = href.split("/")[-1].replace(".pdf", "").replace("_", " ").replace("-", " ").strip()
                assigned_degree = self.assign_degree(href, degree_name)

                syllabus_links.append({
                    "university": self.university_name,
                    "degree": assigned_degree,
                    "course_name": course_name,
                    "syllabus_url": href,
                })
                print(f"    Found: {course_name}")

        print(f"  Syllabuses found: {len(syllabus_links)}")
        return syllabus_links

    def run(self, output_path: str = None):
        if output_path is None:
            output_path = f"data/processed/{self.university_name.lower()}_syllabus_links.csv"

        driver = self.make_driver()
        all_syllabuses = []
        degree_urls = []

        try:
            degree_urls = self.get_degree_urls(driver)

            if not degree_urls:
                print("No degree URLs found.")
                return

            for degree_name, degree_url in degree_urls:
                try:
                    syllabuses = self.get_syllabus_links_for_degree(driver, degree_name, degree_url)
                    all_syllabuses.extend(syllabuses)
                except Exception as e:
                    print(f"  Error scraping {degree_name}: {e}")
                    continue

        finally:
            driver.quit()

        df = pd.DataFrame(all_syllabuses)
        df.to_csv(output_path, index=False)

        print(f"\n✅ Done! Found {len(df)} syllabuses across {len(degree_urls)} degrees.")
        print(f"Saved to {output_path}")
        return df
    