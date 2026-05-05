# Syllabus Scraper

Automatically scrapes, downloads, and parses grading breakdowns from university course syllabuses across multiple institutions. Used to analyze whether grading structures differ systematically across degree types — specifically, whether mathematics degrees rely more heavily on exams than other degrees.

## Research Question

Do math students face unfair GPA comparisons in exchange programs because their courses are more exam-heavy than other degrees?

## Universities Supported

| University | Country | Degrees | Courses |
|------------|---------|---------|---------|
| IE University | Spain | 16 | ~700 |
| Universidad Carlos III (UC3M) | Spain | 26 | ~2248 |
| Universidad Politécnica de Madrid (UPM) | Spain | 3 | ~53 |
| University of Amsterdam (UvA) | Netherlands | 6 | In progress |

## Key Finding

Mathematics degrees consistently have the highest exam weight across all universities:
- IE Applied Mathematics: 65.4%
- UC3M Matemática Aplicada: 57.4%
- UPM Matemáticas: 51.7%

## Installation

```bash
git clone https://github.com/NiquitoNipongo67/syllabus-scraper
cd syllabus-scraper
pip install -e .
```

## Usage

### Scrape IE University syllabuses
```bash
python -m syllabus_scraper.ie_scraper
```

### Parse grading from downloaded PDFs
```bash
python -m syllabus_scraper.ie_parser
```

### Scrape UC3M
```bash
python src/syllabus_scraper/uc3m_scraper.py
```

### Scrape UPM
```bash
python src/syllabus_scraper/upm_scraper.py
```

### Run tests
```bash
pytest tests/
```

## Project Structure
syllabus-scraper/
├── src/syllabus_scraper/
│   ├── base_scraper.py       # Abstract base class for all university scrapers
│   ├── base_parser.py        # Abstract base class for all syllabus parsers
│   ├── ie_scraper.py         # IE University scraper
│   ├── ie_parser.py          # IE University PDF parser
│   ├── uc3m_scraper.py       # UC3M web scraper
│   ├── upm_scraper.py        # UPM PDF scraper
│   └── uva_scraper.py        # UvA scraper (in progress)
├── tests/                    # 37 unit tests
├── data/
│   ├── raw/                  # Downloaded PDFs
│   └── processed/            # CSV datasets
├── pyproject.toml
└── requirements.txt

## Output

Results saved to `data/processed/combined_grading_dataset.csv` with columns:
- `university`: IE, UC3M, UPM
- `degree`: degree code (e.g. BAM, LLB)
- `course_name`: name of the course
- `exam_weight`: percentage of grade from exams (final + midterm)

