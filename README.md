# syllabus-scraper

Scrapes, downloads, and parses grading breakdowns from IE University course syllabuses.

## Install

```bash
pip install -e .
```

## Pipeline

Run each step from the project root:

```bash
python -m syllabus_scraper.scrape_syllabus_selenium  # scrape links from university page
python -m syllabus_scraper.filter_syllabus_links      # filter for syllabus candidates
python -m syllabus_scraper.download_pdfs              # download PDFs
python -m syllabus_scraper.extract_text               # confirm PDFs are syllabuses
python -m syllabus_scraper.parse_grading              # extract grading percentages
```

Outputs land in `data/processed/`. Raw PDFs go to `data/raw/`.

## Tests

```bash
pytest tests/
```
