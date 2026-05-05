import pandas as pd

df = pd.read_csv('data/processed/combined_grading_dataset.csv')

# Degree name mapping
DEGREE_MAP = {
    # IE
    "BAM": "Applied Mathematics",
    "BCSAI": "Computer Science & AI",
    "BDBA": "Data & Business Analytics",
    "BBA": "Business Administration",
    "BIR": "International Relations",
    "LLB": "Law",
    "BHUM": "Humanities",
    "BAS": "Architecture",
    "BBSS": "Behavior & Social Sciences",
    "BEC": "Economics",
    "BPS": "Political Science",
    "PPLE": "Philosophy, Politics, Law & Economics",
    "BCDM": "Communication & Digital Media",
    "BDES": "Design",
    "BESS": "Environmental Sciences",
    "BFD": "Fashion Design",

    # UC3M
    "matematica-aplicada": "Applied Mathematics",
    "matematicas-computacion": "Mathematics & Computing",
    "informatica": "Computer Science",
    "ade": "Business Administration",
    "derecho": "Law",
    "economia": "Economics",
    "estadistica-empresa": "Statistics & Business",
    "electronica": "Electronic Engineering",
    "mecanica": "Mechanical Engineering",
    "comunicacion": "Communication",
    "periodismo": "Journalism",
    "historia-politica": "History & Politics",
    "fpe": "Philosophy, Politics & Economics",
    "relaciones-laborales": "Labor Relations",
    "ciencias-politicas": "Political Science",
    "turismo": "Tourism",
    "aeroespacial": "Aerospace Engineering",
    "datos": "Data Science",
    "telecomunicacion": "Telecommunications Engineering",
    "tecnologias-industriales": "Industrial Engineering",
    "biomedica": "Biomedical Engineering",
    "ingenieria-fisica": "Engineering Physics",
    "inteligencia-artificial": "Artificial Intelligence",
    "finanzas-contabilidad": "Finance & Accounting",
    "empresa-tecnologia": "Business & Technology",
    "estudios-internacionales": "International Studies",

    # UPM
    "matematicas": "Mathematics",
    "ciencia-datos": "Data Science & AI",
}

df['degree_clean'] = df['degree'].map(DEGREE_MAP).fillna(df['degree'])

df.to_csv('data/processed/combined_grading_dataset.csv', index=False)

print(df.groupby(['university', 'degree_clean'])['exam_weight'].mean().sort_values(ascending=False).round(1).to_string())
print(f'\nTotal courses: {len(df)}')
