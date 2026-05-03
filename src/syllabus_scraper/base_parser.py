from abc import ABC, abstractmethod
import os
import re
import pandas as pd
import pdfplumber


class BaseParser(ABC):

    @property
    @abstractmethod
    def university_name(self) -> str:
        """Short name for the university, e.g. 'IE', 'UAM'"""
        pass

    @property
    @abstractmethod
    def section_keywords(self) -> list:
        """Keywords that mark the start of the grading section"""
        pass

    @property
    @abstractmethod
    def section_end_keywords(self) -> list:
        """Keywords that mark the end of the grading section"""
        pass

    @abstractmethod
    def is_likely_syllabus(self, text: str) -> bool:
        """Return True if the text looks like a syllabus from this university"""
        pass

    @abstractmethod
    def map_label_to_category(self, label: str) -> str | None:
        """Map a grading label to a category (final_exam, midterm_tests, etc.)"""
        pass

    def normalize_label(self, label: str) -> str:
        return " ".join(label.lower().strip().split())

    def compute_total_weight(self, grading: dict) -> int:
        return sum(grading.values())

    def empty_grading(self) -> dict:
        return {
            "final_exam": 0,
            "midterm_tests": 0,
            "quizzes": 0,
            "project": 0,
            "participation": 0,
            "other": 0,
        }

    def extract_pdf_text(self, pdf_path: str) -> str:
        parts = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        parts.append(text)
        except Exception as e:
            print(f"Failed to read {pdf_path}: {e}")
            return ""
        return "\n".join(parts)

    def extract_course_name(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[0] if lines else ""

    def extract_grading_from_tables(self, pdf_path: str) -> dict:
        results = self.empty_grading()
        try:
            with pdfplumber.open(pdf_path) as pdf:
                criteria_page_idx = None
                for i, page in enumerate(pdf.pages):
                    page_text = (page.extract_text() or "").lower()
                    if any(kw in page_text for kw in self.section_keywords):
                        criteria_page_idx = i
                        break

                if criteria_page_idx is None:
                    return results

                for i in range(criteria_page_idx, min(criteria_page_idx + 4, len(pdf.pages))):
                    page = pdf.pages[i]
                    tables = page.extract_tables()
                    if not tables:
                        continue

                    for table in tables:
                        if not table:
                            continue
                        for row in table:
                            if not row:
                                continue
                            cleaned = [str(c).strip() if c is not None else "" for c in row]
                            if len(cleaned) < 2:
                                continue

                            label = self.normalize_label(cleaned[0])
                            pct_cell = cleaned[1].strip().lower()

                            if not label:
                                continue

                            match = re.search(r"(\d{1,3})\s*%", pct_cell)
                            if not match:
                                continue

                            pct = int(match.group(1))
                            category = self.map_label_to_category(label)
                            if category:
                                results[category] += pct

        except Exception as e:
            print(f"Failed table extraction for {pdf_path}: {e}")
        return results

    def extract_grading_from_text(self, text: str) -> dict:
        results = self.empty_grading()
        text_lower = text.lower()

        start = None
        for kw in self.section_keywords:
            idx = text_lower.find(kw)
            if idx != -1:
                start = idx
                break

        if start is None:
            return results

        end_candidates = [text_lower.find(kw, start) for kw in self.section_end_keywords]
        end_candidates = [x for x in end_candidates if x != -1]
        end = min(end_candidates) if end_candidates else start + 2500
        section = text[start:end]

        for line in section.splitlines():
            line = line.strip()
            if "%" not in line:
                continue

            raw_label, pct = None, None

            m = re.search(r"(.+?)\s+(\d{1,3})\s*%", line, re.IGNORECASE)
            if m:
                raw_label = m.group(1).strip().lower()
                pct = int(m.group(2))

            if raw_label is None:
                m2 = re.search(r"(.+?)\[(\d{1,3})%\]", line, re.IGNORECASE)
                if m2:
                    raw_label = m2.group(1).strip().lower()
                    pct = int(m2.group(2))

            if raw_label is None or pct is None:
                continue

            category = self.map_label_to_category(raw_label)
            if category and category != "other":
                results[category] += pct

        return results

    def choose_best_grading(self, pdf_path: str, text: str) -> dict:
        table_grading = self.extract_grading_from_tables(pdf_path)
        text_grading = self.extract_grading_from_text(text)

        table_total = self.compute_total_weight(table_grading)
        text_total = self.compute_total_weight(text_grading)

        if 90 <= table_total <= 110 and not (90 <= text_total <= 110):
            return table_grading
        if 90 <= text_total <= 110 and not (90 <= table_total <= 110):
            return text_grading
        if 90 <= table_total <= 110 and 90 <= text_total <= 110:
            return table_grading
        if abs(table_total - 100) <= abs(text_total - 100):
            return table_grading
        return text_grading

    def run(self, input_folder: str = "data/raw", output_csv: str = None):
        if output_csv is None:
            output_csv = f"data/processed/{self.university_name.lower()}_grading_dataframe.csv"

        rows = []
        for filename in sorted(os.listdir(input_folder)):
            if not filename.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(input_folder, filename)
            print(f"Parsing: {filename}")

            text = self.extract_pdf_text(pdf_path)
            if not text:
                continue

            if not self.is_likely_syllabus(text):
                continue

            course_name = self.extract_course_name(text)
            grading = self.choose_best_grading(pdf_path, text)
            total_weight = self.compute_total_weight(grading)
            parse_status = "ok" if 90 <= total_weight <= 110 else "needs_review"

            row = {
                "university": self.university_name,
                "filename": filename,
                "course_name": course_name,
                **grading,
                "total_weight": total_weight,
                "parse_status": parse_status,
            }
            rows.append(row)

            if parse_status == "needs_review":
                print(f"  [needs_review] {filename} | total={total_weight}")

        df = pd.DataFrame(rows)
        df.to_csv(output_csv, index=False)
        print(f"\nSaved to {output_csv}")
        print(f"Total rows: {len(df)}")
        clean_df = df[df["parse_status"] == "ok"].copy()
        clean_df.to_csv(output_csv.replace(".csv", "_clean.csv"), index=False)
        print(f"Clean rows: {len(clean_df)}")
        return df
    