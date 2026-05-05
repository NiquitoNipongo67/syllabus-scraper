from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://coursecatalogue.uva.nl/en/programmes/2025/1/5258')
time.sleep(6)

# Click Shared programme button
buttons = driver.find_elements(By.TAG_NAME, "button")
for btn in buttons:
    if "shared" in btn.text.lower():
        driver.execute_script("arguments[0].click();", btn)
        print("Clicked:", btn.text)
        time.sleep(4)
        break

# Now print ALL links on the page
links = driver.find_elements(By.TAG_NAME, "a")
print(f"Total links: {len(links)}")
for l in links:
    href = l.get_attribute("href") or ""
    text = l.text.strip()
    if "courses" in href or "Mathematics" in text or "Economics" in text:
        print(repr(text), "->", href)

driver.quit()