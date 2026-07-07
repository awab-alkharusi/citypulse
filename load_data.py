import pandas as pd
import sqlite3
import os

def load_data_to_sqlite(csv_path="data/nyc311_sample.csv", db_path="citypulse.db"):
    print("Loading data into SQLite...")
    
    # Load CSV into Pandas DataFrame
    df = pd.read_csv(csv_path)
    
    # Clean column names using Pandas: remove spaces, lowercase everything
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Keep only the columns we care about
    columns_to_keep = [
        "unique_key",
        "created_date",
        "closed_date", 
        "agency",
        "agency_name",
        "complaint_type",
        "descriptor",
        "status",
        "borough",
        "city"
    ]
    
    # Only keep columns that actually exist in the dataset
    columns_to_keep = [col for col in columns_to_keep if col in df.columns]
    df = df[columns_to_keep]
    
    # Drop rows where borough is missing
    df = df.dropna(subset=["borough"])
    
    # Connect to SQLite and write the data
    conn = sqlite3.connect(db_path)
    df.to_sql("complaints", conn, if_exists="replace", index=False)
    conn.close()
    
    print(f"Done. {len(df)} rows loaded into {db_path}")
    print(f"Columns: {list(df.columns)}")

if __name__ == "__main__":
    load_data_to_sqlite()