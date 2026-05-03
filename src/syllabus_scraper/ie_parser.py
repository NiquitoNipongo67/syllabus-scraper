from base_parser import BaseParser
import re


class IEParser(BaseParser):

    @property
    def university_name(self):
        return "IE"

    @property
    def section_keywords(self):
        return ["evaluation criteria"]

    @property
    def section_end_keywords(self):
        return ["re-sit", "re-take", "ai policy", "bibliography",
                "attendance policy", "ethical policy", "behavior rules"]

    def is_likely_syllabus(self, text: str) -> bool:
        text_lower = text.lower()
        return (
            "number of credits" in text_lower
            and "academic year" in text_lower
            and ("evaluation criteria" in text_lower or "criteria" in text_lower)
        )

    def map_label_to_category(self, label: str) -> str | None:
        label = self.normalize_label(label)
        label = re.sub(r"^[a-z]\.", "", label).strip()

        if label in ("criteria", "evaluation criteria", "percentage",
                     "learning objectives", "comments", ""):
            return None

        squished = label.replace(" ", "")

        if ("final exam" in label or "final test" in label or "finalexam" in squished):
            return "final_exam"

        if ("midterm" in label or "intermediate test" in label
                or "intermediate exam" in label):
            return "midterm_tests"

        if "quiz" in label:
            return "quizzes"

        if (any(k in label for k in [
                "group project", "group work", "group presentation",
                "project report", "project presentation", "final presentation"])
                or label.startswith("project")):
            return "project"

        if "participation" in label:
            return "participation"

        if "individual work" in label or "individual contribution" in label:
            return "other"

        return "other"


if __name__ == "__main__":
    parser = IEParser()
    parser.run()
    