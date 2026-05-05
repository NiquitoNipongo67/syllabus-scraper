import pandas as pd

combined = pd.read_csv('data/processed/combined_grading_dataset.csv')
upm = pd.read_csv('data/processed/upm_grading_dataframe.csv')

# Keep only clean rows
upm = upm[upm['parse_status'] == 'ok'].copy()
upm['exam_weight'] = upm['midterm_tests']

# Add to combined
upm_clean = upm[['university', 'degree', 'course_name', 'exam_weight']]
combined = pd.concat([combined, upm_clean], ignore_index=True)
combined.to_csv('data/processed/combined_grading_dataset.csv', index=False)

print(combined.groupby(['university', 'degree'])['exam_weight'].mean().sort_values(ascending=False).round(1).to_string())
print(f'\nTotal courses: {len(combined)}')