from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


def scrape_all_links(url: str):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Give the page extra time to render dynamic content
        time.sleep(5)

        # Scroll so lazy-loaded sections appear
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        elements = driver.find_elements(By.TAG_NAME, "a")

        results = []
        for elem in elements:
            try:
                text = elem.text.strip()
                href = elem.get_attribute("href")
                if href:
                    results.append((text, href))
            except Exception:
                continue

        return results

    finally:
        driver.quit()


if __name__ == "__main__":
    url = input("Enter URL: ").strip()

    links = scrape_all_links(url)

    df = pd.DataFrame(links, columns=["text", "url"])
    df.to_csv("data/processed/all_rendered_links.csv", index=False)

    print(f"Saved {len(df)} rendered links to data/processed/all_rendered_links.csv")