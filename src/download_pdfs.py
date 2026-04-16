import os
import requests
import pandas as pd


def download_pdfs(csv_path: str, output_folder: str):
    df = pd.read_csv(csv_path)

    # make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for i, row in df.iterrows():
        url = row["url"]

        # only keep PDF links
        if ".pdf" not in url.lower():
            continue

        try:
            print(f"Downloading: {url}")

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            # create filename
            filename = f"file_{i}.pdf"
            filepath = os.path.join(output_folder, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

        except Exception as e:
            print(f"Failed to download {url}: {e}")


if __name__ == "__main__":
    csv_path = "data/processed/candidate_syllabus_links.csv"
    output_folder = "data/raw"

    download_pdfs(csv_path, output_folder)

    print("Download process finished.")