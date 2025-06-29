# Before this script I had medicare and patent import scripts split but decided to combine them in one script here instead:
# imports
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# MySQL connection setup
# (Replace with database credentials)
user = ''
password = ''
host = ''
db = 'Patent_Expiration'
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db}')

# Load raw Orange Book files
# (Replace with a file path to each .txt file)
patent_path = 'path/to/patent.txt'
product_path = 'path/to/products.txt'

df_patents = pd.read_csv(patent_path, sep='~', dtype=str)
df_products = pd.read_csv(product_path, sep='~', dtype=str)

# Clean up string columns in both datasets
for df in [df_patents, df_products]:
    str_cols = df.select_dtypes(include='object').columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

# Merge patents and products on Appl_No and Product_No
merged = pd.merge(
    df_patents,
    df_products,
    on=['Appl_No', 'Product_No'],
    how='inner',
    suffixes=('_patent', '_product')
)

# --Rename and clean important columns for clarity
merged = merged.rename(columns={
    'Patent_No': 'patent_no',
    'Patent_Expire_Date_Text': 'patent_expire_date_text',
    'Patent_Use_Code': 'patent_use_code',
    'Submission_Date': 'submission_date',
    'Delist_Flag': 'delist_flag',
    'Appl_No': 'appl_no',
    'Product_No': 'product_no',
    'Ingredient': 'ingredient',
    'DF;Route': 'route',
    'Trade_Name': 'trade_name',
    'Applicant': 'applicant',
    'Strength': 'strength',
    'Approval_Date': 'approval_date',
    'TE_Code': 'te_code',
    'RLD': 'rld',
    'RS': 'rs',
    'Type': 'product_type',
    'Applicant_Full_Name': 'applicant_full_name',
})

print("Columns after cleaning and renaming:")
print(merged.columns.tolist())

# Convert relevant columns to datetime
date_cols = ['patent_expire_date_text', 'submission_date', 'approval_date']
merged['patent_expire_date'] = pd.to_datetime(merged['patent_expire_date_text'], errors='coerce')
for col in ['submission_date', 'approval_date']:
    merged[col] = pd.to_datetime(merged[col], errors='coerce')

# Upload cleaned Orange Book data to MySQL
merged.to_sql('patent_product_cleaned', con=engine, if_exists='replace', index_label='id')
print("Orange Book data loaded into `patent_product_cleaned` table.")

# Load Medicare Part D spending data
# (Replace with path to Medicare Part D file)
medicare_path = 'path/to/medicare_part_d.csv'
df_medicare = pd.read_csv(medicare_path)

# Clean column names and strip whitespace from string values
df_medicare.columns = df_medicare.columns.str.strip().str.replace(' ', '_')
df_medicare = df_medicare.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Upload Medicare data to MySQL
df_medicare.to_sql('medicare_part_d', con=engine, if_exists='replace', index=False)
print("Medicare Part D data loaded into `medicare_part_d` table.")