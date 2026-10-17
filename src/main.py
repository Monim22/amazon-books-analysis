import os
import sqlite3
import urllib.request
import pandas as pd


# ==========================================
# 1. INGESTION LAYER
# ==========================================
def fetch_raw_data(url: str, dest_path: str):
    """Downloads the raw dataset using proper HTTP headers."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if not os.path.exists(dest_path):
        print("📥 Fetching dataset from remote repository...")
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        )
        with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
            out_file.write(response.read())
        print("✔ Dataset downloaded successfully.")
    else:
        print("✔ Local dataset found. Skipping download.")


# ==========================================
# 2. EXTRACTION & CLEANING LAYER
# ==========================================
def load_data(file_path: str) -> pd.DataFrame:
    """Load raw dataset from CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File not found at '{file_path}'. Check your folder structure!")

    df = pd.read_csv(file_path)
    print(f"✔ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates, standardize column names, and enforce numerical data types."""
    # Drop exact row duplicates
    df = df.drop_duplicates()

    # Standardize column names to snake_case
    df = df.rename(
        columns={
            "Name": "title",
            "Author": "author",
            "User Rating": "user_rating",
            "Reviews": "reviews",
            "Price": "price",
            "Year": "year",
            "Genre": "genre",
        }
    )

    # Cast data types explicitly
    df["price"] = df["price"].astype(float)
    df["user_rating"] = df["user_rating"].astype(float)
    df["reviews"] = df["reviews"].astype(int)

    print("✔ Data cleaning complete.")
    return df


# ==========================================
# 3. ANALYTICAL AGGREGATION LAYER
# ==========================================
def generate_insights(df: pd.DataFrame) -> dict:
    """Perform data aggregations and extract key analytical metrics."""
    reports = {}

    # Report 1: Top 10 Authors by Bestseller Appearances
    reports["top_authors"] = (
        df.groupby("author")["title"]
        .count()
        .reset_index()
        .rename(columns={"title": "appearance_count"})
        .sort_values(by="appearance_count", ascending=False)
        .head(10)
    )

    # Report 2: Genre Metrics Summary (Rating, Price, Review Counts)
    reports["genre_summary"] = (
        df.groupby("genre")
        .agg(
            avg_rating=("user_rating", "mean"),
            avg_price=("price", "mean"),
            total_reviews=("reviews", "sum"),
            total_books=("title", "count"),
        )
        .round(2)
        .reset_index()
    )

    # Report 3: Highest Rated Books with >= 10,000 Reviews
    reports["top_rated_popular"] = (
        df[df["reviews"] >= 10000]
        .sort_values(by=["user_rating", "reviews"], ascending=[False, False])
        .drop_duplicates(subset=["title"])
        .head(10)[["title", "author", "user_rating", "reviews", "price", "genre"]]
    )

    print("✔ Analytical aggregations computed.")
    return reports


# ==========================================
# 4. STORAGE & EXPORT LAYER
# ==========================================
def save_to_database(df: pd.DataFrame, db_path: str = "data/processed/amazon_books.db"):
    """Saves the cleaned dataset directly into an SQLite database table."""
    conn = sqlite3.connect(db_path)
    df.to_sql("bestsellers", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✔ Cleaned dataset stored in SQLite database at '{db_path}'")


def export_outputs(cleaned_df: pd.DataFrame, reports: dict):
    """Exports processed data to CSV reports and SQLite storage."""
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Export master dataset & summary reports as CSVs
    cleaned_df.to_csv("data/processed/cleaned_bestsellers.csv", index=False)
    reports["top_authors"].to_csv("reports/top_10_authors.csv", index=False)
    reports["genre_summary"].to_csv("reports/genre_summary.csv", index=False)
    reports["top_rated_popular"].to_csv("reports/top_rated_books.csv", index=False)

    # Persist dataset in relational storage
    save_to_database(cleaned_df)

    print("✔ All CSV files and SQLite database tables exported successfully!")


# ==========================================
# 5. PIPELINE ORCHESTRATION
# ==========================================
def main():
    print("--- Starting Amazon Bestsellers End-to-End Pipeline ---")

    # Correct RAW CSV download URL
    DATA_URL = "https://raw.githubusercontent.com/aiplanethub/Datasets/master/Amazon%20Top%2050%20Bestselling%20Books%202009%20-%202019.csv"
    raw_path = "data/raw/bestsellers.csv"

    # Execute Pipeline Stages
    fetch_raw_data(DATA_URL, raw_path)       # Stage 1: Ingest
    df_raw = load_data(raw_path)             # Stage 2: Load
    df_cleaned = clean_data(df_raw)          # Stage 3: Clean
    reports = generate_insights(df_cleaned)  # Stage 4: Analyze
    export_outputs(df_cleaned, reports)      # Stage 5: Store & Export

    print("--- Pipeline Executed Successfully ---")


if __name__ == "__main__":
    main()