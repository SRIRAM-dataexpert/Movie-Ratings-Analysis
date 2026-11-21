"""
Stage 2: Data Cleaning and Preprocessing
File: src/02_clean_data.py

This beginner-friendly script cleans and enriches the movie and ratings data:
- Keeps original files in Dataset/ untouched.
- Extracts 'year' from the movie title using regular expressions.
- Cleans movie titles by removing the trailing year.
- Standardizes '(no genres listed)' into 'Unknown' and creates a primary genre column.
- Converts rating timestamps into readable datetime, year, and month.
- Merges ratings with movie information for fast dashboard querying.
- Saves the cleaned datasets into outputs/.
"""

import os
import re
import pandas as pd


def clean_datasets():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    movies_path = os.path.join(base_dir, "Dataset", "movies.csv")
    ratings_path = os.path.join(base_dir, "Dataset", "ratings.csv")
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    cleaned_movies_file = os.path.join(output_dir, "cleaned_movies.csv")
    cleaned_ratings_file = os.path.join(output_dir, "cleaned_ratings.csv")

    print("=" * 60)
    print("STAGE 2: DATA CLEANING & PREPROCESSING")
    print("=" * 60)

    # 1. Load original data (read-only)
    print("\n[1] Reading raw data...")
    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)

    # 2. Clean Movies Data
    print("\n[2] Cleaning movies dataset...")

    # Extract 4-digit release year from title (e.g., "Toy Story (1995)" -> 1995)
    # Using regex to match 4 digits enclosed in parentheses at or near the end of the string
    extracted_years = movies_df["title"].str.extract(r"\((\d{4})\)\s*$", expand=False)
    movies_df["year"] = pd.to_numeric(extracted_years, errors="coerce").astype("Int64")

    # Clean the title by removing the (YYYY) suffix
    movies_df["clean_title"] = (
        movies_df["title"].str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True).str.strip()
    )

    # Standardize missing/unlisted genres
    movies_df["genres"] = movies_df["genres"].replace("(no genres listed)", "Unknown")

    # Extract primary genre (the first genre listed before the '|')
    movies_df["primary_genre"] = movies_df["genres"].apply(
        lambda g: g.split("|")[0] if isinstance(g, str) else "Unknown"
    )

    # Count number of genres associated with each movie
    movies_df["genre_count"] = movies_df["genres"].apply(
        lambda g: len(g.split("|")) if g != "Unknown" else 0
    )

    print(f"  - Extracted release years for {movies_df['year'].notnull().sum():,} movies.")
    print(f"  - Cleaned titles and identified {movies_df['primary_genre'].nunique()} primary genres.")

    # 3. Clean Ratings Data
    print("\n[3] Cleaning ratings dataset...")

    # Convert Unix timestamp to readable UTC datetime
    ratings_df["rating_datetime"] = pd.to_datetime(ratings_df["timestamp"], unit="s")
    ratings_df["rating_year"] = ratings_df["rating_datetime"].dt.year
    ratings_df["rating_month"] = ratings_df["rating_datetime"].dt.month

    # 4. Create an Enriched Ratings Dataset by merging with Movie details
    print("\n[4] Merging ratings with movie titles and genres...")
    enriched_ratings = pd.merge(
        ratings_df,
        movies_df[["movieId", "clean_title", "year", "genres", "primary_genre"]],
        on="movieId",
        how="inner",
    )
    print(f"  - Enriched dataset created with {len(enriched_ratings):,} records.")

    # 5. Save cleaned files to outputs/
    print("\n[5] Saving cleaned files into outputs/ folder...")
    movies_df.to_csv(cleaned_movies_file, index=False)
    enriched_ratings.to_csv(cleaned_ratings_file, index=False)

    print(f"  -> Cleaned movies saved: {cleaned_movies_file}")
    print(f"  -> Enriched ratings saved: {cleaned_ratings_file}")
    print("\nStage 2 completed successfully!")


if __name__ == "__main__":
    clean_datasets()
