# Adult Income dataset

import pandas as pd
from sklearn.datasets import fetch_openml

def fetch_and_save():
    print("Fetching Adult Income dataset from OpenML...")
    data = fetch_openml(name="adult", version=2, as_frame=True)

    df = data.frame

    df = df.rename(columns={"class": "income"})

    df["income"] = df["income"].apply(
        lambda x: 1 if str(x).strip() in (">50K", ">50K.") else 0
    )

    df = df.dropna()

    out_path = "adult_income.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")
    print(f"Columns: {list(df.columns)}")
    print(f"Sensitive attribute candidates: sex, race")

if __name__ == "__main__":
    fetch_and_save()