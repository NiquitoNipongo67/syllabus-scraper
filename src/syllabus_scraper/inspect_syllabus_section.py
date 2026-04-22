import requests
from bs4 import BeautifulSoup

url = input("Enter URL: ").strip()

response = requests.get(url, timeout=20)
response.raise_for_status()

print("Page downloaded.")
print("Final URL:", response.url)
print("HTML length:", len(response.text))

soup = BeautifulSoup(response.text, "lxml")

matches = soup.find_all(string=lambda s: s and "syllabus" in s.lower())

print(f"\nFound {len(matches)} matches containing 'syllabus'.\n")

for i, match in enumerate(matches[:10], start=1):
    print(f"Match {i}:")
    print(match.strip())

    parent = match.parent
    print("Parent tag:", parent.name)
    print("Parent HTML:")
    print(parent)

    print("-" * 80)