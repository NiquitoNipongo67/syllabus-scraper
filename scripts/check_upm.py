import pandas as pd
df = pd.read_csv('data/processed/upm_grading_dataframe.csv')
print(f'Total courses: {len(df)}')
print(f'OK: {len(df[df["parse_status"]=="ok"])}')
print(f'Needs review: {len(df[df["parse_status"]=="needs_review"])}')
print()
print(df.groupby('degree')['midterm_tests'].mean().sort_values(ascending=False).round(1))
