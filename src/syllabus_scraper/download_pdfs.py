import os
import requests
import pandas as pd


def build_filename(row):
    url = row["syllabus_url"]
    parts = url.split("/")
    try:
        grados_idx = parts.index("Grados")
        degree = parts[grados_idx + 1]
        pdf_name = parts[-1].replace(".pdf", "")
        return f"{degree}__{pdf_name}.pdf"
    except (ValueError, IndexError):
        # fallback to just the pdf filename
        return parts[-1]


def download_pdfs(csv_path: str, output_folder: str):
    df = pd.read_csv(csv_path)
    df = df[df["syllabus_url"].str.endswith(".pdf", na=False)]
    df = df[df["syllabus_url"].str.contains("Grados", na=False)]

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