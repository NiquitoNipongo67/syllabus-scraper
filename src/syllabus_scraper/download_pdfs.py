import os
import requests
import pandas as pd


def build_filename(row):
    url = row["syllabus_url"]
    parts = url.split("/")
    
    # Try to extract degree from Grados-style URLs
    try:
        grados_idx = parts.index("Grados")
        degree = parts[grados_idx + 1]
        pdf_name = parts[-1].replace(".pdf", "")
        return f"{degree}__{pdf_name}.pdf"
    except (ValueError, IndexError):
        pass
    
    # Fallback: use degree from the degree column + filename from URL
    degree = str(row.get("degree", "UNKNOWN")).replace(" ", "_")[:30]
    pdf_name = parts[-1].replace(".pdf", "")
    if not pdf_name:
        pdf_name = f"file_{hash(url) % 100000}"
    return f"{degree}__{pdf_name}.pdf"


def download_pdfs(csv_path: str, output_folder: str):
    df = pd.read_csv(csv_path)
    df = df[df["syllabus_url"].str.endswith(".pdf", na=False)]

    os.makedirs(output_folder, exist_ok=True)

    success = 0
    failed = 0

    for i, row in df.iterrows():
        url = row["syllabus_url"]
        filename = build_filename(row)
        filepath = os.path.join(output_folder, filename)

        if os.path.exists(filepath):
            print(f"Skipping (already exists): {filename}")
            continue

        try:
            print(f"Downloading: {filename}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(response.content)

            success += 1

        except Exception as e:
            print(f"Failed: {url} → {e}")
            failed += 1

    print(f"\n✅ Done! Downloaded {success} new PDFs, {failed} failed.")


if __name__ == "__main__":
    csv_path = "data/processed/all_syllabus_links.csv"
    output_folder = "data/raw"

    download_pdfs(csv_path, output_folder)