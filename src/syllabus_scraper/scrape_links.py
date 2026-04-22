import requests
from bs4 import BeautifulSoup

url = input("Enter URL: ").strip()

response = requests.get(url, timeout=15)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

matches = soup.find_all(string=lambda s: s and "syllabus" in s.lower())

for m in matches:
    print("FOUND:", m.strip())
    parent = m.parent
    print("PARENT TAG:", parent.name)
    print(parent)
    print("-" * 80)