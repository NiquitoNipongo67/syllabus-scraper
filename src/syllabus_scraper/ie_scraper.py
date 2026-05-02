from base_scraper import BaseScraper

class IEScraper(BaseScraper):

    DEGREE_NAME_MAP = {
        "bachelor-applied-mathematics": "BAM",
        "bachelor-computer-science": "BCSAI",
        "bachelor-data-business-analytics": "BDBA",
        "bachelor-business-administration": "BBA",
        "bachelor-international-relations": "BIR",
        "bachelor-laws": "LLB",
        "bachelor-humanities": "BHUM",
        "bachelor-architectural": "BAS",
        "bachelor-in-behavior": "BBSS",
        "bachelor-behavior": "BBSS",
        "bachelor-economics": "BEC",
        "bachelor-in-economics": "BEC",
        "bachelor-political": "BPS",
        "bachelor-pple": "PPLE",
        "bachelor-communication": "BCDM",
        "bachelor-in-communication": "BCDM",
        "bachelor-design": "BDES",
        "bachelor-in-design": "BDES",
        "bachelor-environmental": "BESS",
        "bachelor-fashion": "BFD",
        "dual-degree": "DOBLES",
    }

    @property
    def university_name(self):
        return "IE"

    @property
    def main_url(self):
        return "https://www.ie.edu/university/studies/academic-programs/"

    @property
    def syllabus_domains(self):
        return ["docs.ie.edu", "thesaurus.ie.edu", "files.thesaurus.ie.edu", "static.ie.edu"]

    def get_degree_urls(self, driver):
        print("Scanning main programs page for degree links...")
        links = self.get_links_from_page(driver, self.main_url)

        base_domain = "ie.edu/university/studies/academic-programs/"
        degree_urls = []
        seen = set()

        for text, href in links:
            if (
                base_domain in href
                and href.rstrip("/") != self.main_url.rstrip("/")
                and href not in seen
                and href.count("/") == self.main_url.count("/") + 1
            ):
                seen.add(href)
                slug = href.rstrip("/").split("/")[-1]
                degree_code = next(
                    (code for key, code in self.DEGREE_NAME_MAP.items() if key in slug),
                    slug
                )
                degree_urls.append((degree_code, href))
                print(f"  Found degree: {degree_code} → {slug}")

        print(f"\nTotal degrees found: {len(degree_urls)}")
        return degree_urls

    def get_study_plan_url(self, degree_url):
        return degree_url.rstrip("/") + "/the-program/#study-plan"

    def assign_degree(self, href, page_degree):
        url_parts = href.split("/")
        try:
            grados_idx = url_parts.index("Grados")
            url_degree = url_parts[grados_idx + 1]
            if url_degree == "DOBLES":
                return page_degree
            return url_degree
        except (ValueError, IndexError):
            return page_degree


if __name__ == "__main__":
    scraper = IEScraper()
    scraper.run()
    