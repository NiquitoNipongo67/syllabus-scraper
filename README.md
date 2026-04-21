# syllabus-scraper

A pipeline for scraping, downloading, and parsing grading information from university course syllabuses (IE University).

## Pipeline

The pipeline runs in five stages:

1. **Scrape links** — renders the university webpage with Selenium and extracts all anchor links.
2. **Filter links** — keeps only links that look like syllabuses based on URL/text keywords.
3. **Download PDFs** — downloads candidate syllabuses as PDFs.
4. **Analyze PDFs** — confirms each PDF is a syllabus by checking for key markers.
5. **Parse grading** — extracts percentage breakdowns (final exam, midterms, projects, participation, etc.) from each syllabus.

## Installation

```bash
# With pip
pip install -e .

# With conda
conda env create -f environment.yaml
conda activate syllabus-scraper
```

## Usage

Run each stage from the project root:

```bash
# 1. Scrape all links from the university page
python -m syllabus_scraper.scrape_syllabus_selenium

# 2. Filter for syllabus candidates
python -m syllabus_scraper.filter_syllabus_links

# 3. Download PDFs
python -m syllabus_scraper.download_pdfs

# 4. Analyze PDFs (confirm they are syllabuses)
python -m syllabus_scraper.extract_text

# 5. Parse grading breakdowns
python -m syllabus_scraper.parse_grading
```

Outputs are written to `data/processed/`. Raw PDFs are saved to `data/raw/`.

## Running tests

```bash
pytest tests/
```

## Project structure

```
syllabus-scraper/
├── src/syllabus_scraper/
│   ├── scrape_syllabus_selenium.py   # Stage 1: render page and collect links
│   ├── scrape_links.py               # Stage 1 (static fallback): scrape links without JS
│   ├── filter_syllabus_links.py      # Stage 2: filter candidate syllabus links
│   ├── download_pdfs.py              # Stage 3: download PDFs
│   ├── extract_text.py               # Stage 4: detect syllabuses from PDF text
│   ├── parse_grading.py              # Stage 5: extract grading percentages
│   └── inspect_syllabus_section.py   # Debug helper: inspect a page's syllabus section
├── tests/
│   └── test_parse_grading.py
├── data/
│   ├── raw/                          # Downloaded PDFs (not tracked in git)
│   └── processed/                    # CSV outputs (not tracked in git)
├── environment.yaml
├── setup.py
└── requirements.txt
```
