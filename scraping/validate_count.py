import pandas as pd

df = pd.read_csv("data/processed/shl_catalog_clean.csv")

count = len(df)
print("Total assessments scraped:", count)

if count >= 377:
    print("Requirement satisfied")
else:
    print("Less than required 377 tests")
