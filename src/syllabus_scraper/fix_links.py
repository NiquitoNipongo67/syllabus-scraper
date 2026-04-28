import pandas as pd

# Load both files
links = pd.read_csv("data/processed/all_syllabus_links.csv")
grades = pd.read_csv("data/processed/grading_dataframe.csv")

# Extract degree from URL in links file
def extract_degree_from_url(url):
    parts = str(url).split("/")
    try:
        grados_idx = parts.index("Grados")
        return parts[grados_idx + 1]
    except (ValueError, IndexError):
        return None

links["degree"] = links["syllabus_url"].apply(extract_degree_from_url)
links = links[links["degree"].notna()].copy()

# Extract degree from filename in grades file
# Filenames look like: "BAM__Fall_CalculusI.pdf" or old ones like "file_38.pdf"
def extract_degree_from_filename(filename):
    name = str(filename).replace(".pdf", "")
    if "__" in name:
        return name.split("__")[0].strip()
    return None

grades["degree"] = grades["filename"].apply(extract_degree_from_filename)

# Save final dataset
output_path = "data/processed/final_grading_dataset.csv"
grades.to_csv(output_path, index=False)

print(f"Final dataset shape: {grades.shape}")
print(f"\nSample:")
print(grades[["degree", "course_name", "final_exam", "midterm_tests", "project", "participation", "total_weight", "parse_status"]].head(15).to_string())
print(f"\nCourses per degree:")
print(grades["degree"].value_counts())
print(f"\nRows with no degree: {grades['degree'].isna().sum()}")