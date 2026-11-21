"""
Stage 1: Dataset Inspection
File: src/01_inspect_data.py

This beginner-friendly script inspects both 'movies.csv' and 'ratings.csv':
- Displays shapes (rows and columns)
- Checks column data types
- Checks for missing/null values
- Checks for duplicate records
- Displays statistical summaries and sample rows
- Saves a summary report into the outputs/ folder
"""

import os
import pandas as pd


def inspect_dataset():
    # Define file paths safely
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    movies_path = os.path.join(base_dir, "Dataset", "movies.csv")
    ratings_path = os.path.join(base_dir, "Dataset", "ratings.csv")
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    summary_file = os.path.join(output_dir, "inspection_summary.txt")

    print("=" * 60)
    print("STAGE 1: DATASET INSPECTION")
    print("=" * 60)

    # 1. Load movies dataset
    print("\n[1] Loading movies.csv...")
    movies_df = pd.read_csv(movies_path)
    print(f"Movies dataset loaded successfully with {len(movies_df):,} rows.")

    # 2. Load ratings dataset
    print("\n[2] Loading ratings.csv...")
    ratings_df = pd.read_csv(ratings_path)
    print(f"Ratings dataset loaded successfully with {len(ratings_df):,} rows.")

    # Prepare summary report lines
    report = []
    report.append("=" * 60)
    report.append("STAGE 1: DATASET INSPECTION SUMMARY REPORT")
    report.append("=" * 60 + "\n")

    # --- MOVIES INSPECTION ---
    report.append("--- 1. MOVIES DATASET (movies.csv) ---")
    report.append(f"Dimensions: {movies_df.shape[0]} rows x {movies_df.shape[1]} columns")
    report.append(f"Columns: {list(movies_df.columns)}")
    report.append("\nData Types:")
    for col, dtype in movies_df.dtypes.items():
        report.append(f"  - {col}: {dtype}")

    report.append("\nMissing Values:")
    for col, nulls in movies_df.isnull().sum().items():
        report.append(f"  - {col}: {nulls} missing")

    duplicates_movie_id = movies_df["movieId"].duplicated().sum()
    report.append(f"\nDuplicate Movie IDs: {duplicates_movie_id}")
    report.append("\nSample 5 Rows:")
    report.append(movies_df.head().to_string())
    report.append("\n" + "-" * 50 + "\n")

    # --- RATINGS INSPECTION ---
    report.append("--- 2. RATINGS DATASET (ratings.csv) ---")
    report.append(f"Dimensions: {ratings_df.shape[0]} rows x {ratings_df.shape[1]} columns")
    report.append(f"Columns: {list(ratings_df.columns)}")
    report.append("\nData Types:")
    for col, dtype in ratings_df.dtypes.items():
        report.append(f"  - {col}: {dtype}")

    report.append("\nMissing Values:")
    for col, nulls in ratings_df.isnull().sum().items():
        report.append(f"  - {col}: {nulls} missing")

    duplicates_ratings = ratings_df.duplicated(subset=["userId", "movieId"]).sum()
    report.append(f"\nDuplicate User-Movie Rating Pairs: {duplicates_ratings}")

    report.append("\nRating Summary Statistics:")
    report.append(ratings_df["rating"].describe().to_string())

    report.append(f"\nUnique Users: {ratings_df['userId'].nunique():,}")
    report.append(f"Unique Rated Movies: {ratings_df['movieId'].nunique():,}")
    report.append("\nSample 5 Rows:")
    report.append(ratings_df.head().to_string())
    report.append("\n" + "=" * 60)

    # Print summary to console
    full_report = "\n".join(report)
    print(full_report)

    # Save summary report to outputs/
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(full_report)
    print(f"\nInspection summary successfully saved to: {summary_file}")


if __name__ == "__main__":
    inspect_dataset()
