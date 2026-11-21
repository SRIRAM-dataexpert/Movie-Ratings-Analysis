"""
Stage 3: Exploratory Data Analysis (EDA)
File: src/03_eda_analysis.py

This beginner-friendly script performs exploratory data analysis:
- Computes overall summary statistics (total movies, ratings, users, average rating)
- Analyzes rating distributions (0.5 to 5.0 stars)
- Finds top 10 most-rated movies
- Finds top 10 highest-rated movies (with >= 50 ratings threshold)
- Analyzes genre popularity and average rating per genre
- Analyzes rating activity trends across years
- Generates and saves 5 clean, publication-ready charts in outputs/
- Generates and saves a detailed text summary in outputs/eda_summary.txt
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Set visual style
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.size": 11, "figure.autolayout": True})


def perform_eda():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs")
    ratings_path = os.path.join(output_dir, "cleaned_ratings.csv")
    movies_path = os.path.join(output_dir, "cleaned_movies.csv")

    print("=" * 60)
    print("STAGE 3: EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 60)

    # 1. Load cleaned datasets
    print("\n[1] Loading cleaned data from outputs/...")
    ratings_df = pd.read_csv(ratings_path)
    movies_df = pd.read_csv(movies_path)

    # 2. Key Metrics
    total_ratings = len(ratings_df)
    total_movies = movies_df["movieId"].nunique()
    total_users = ratings_df["userId"].nunique()
    overall_mean_rating = ratings_df["rating"].mean()
    overall_median_rating = ratings_df["rating"].median()

    print(f"Total Movies: {total_movies:,}")
    print(f"Total Ratings: {total_ratings:,}")
    print(f"Total Users: {total_users:,}")
    print(f"Overall Average Rating: {overall_mean_rating:.2f} / 5.00")

    # 3. Chart 1: Rating Distribution
    print("\n[2] Generating Chart 1: Rating Distribution...")
    plt.figure(figsize=(9, 5))
    rating_counts = ratings_df["rating"].value_counts().sort_index()
    palette = sns.color_palette("Blues_d", len(rating_counts))
    ax = sns.barplot(x=rating_counts.index, y=rating_counts.values, palette=palette)
    plt.title("Distribution of Movie Ratings (0.5 - 5.0 Stars)", fontsize=14, weight="bold")
    plt.xlabel("Rating (Stars)", fontsize=12)
    plt.ylabel("Number of Ratings", fontsize=12)

    # Add count labels on top of each bar
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height()):,}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="bottom",
            fontsize=9,
            xytext=(0, 3),
            textcoords="offset points",
        )

    chart1_path = os.path.join(output_dir, "01_rating_distribution.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"  -> Saved: {chart1_path}")

    # 4. Chart 2: Top 10 Most-Rated Movies
    print("\n[3] Generating Chart 2: Top 10 Most-Rated Movies...")
    movie_stats = (
        ratings_df.groupby(["movieId", "clean_title"])
        .agg(rating_count=("rating", "count"), rating_mean=("rating", "mean"))
        .reset_index()
    )

    top_most_rated = movie_stats.sort_values(by="rating_count", ascending=False).head(10)

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=top_most_rated,
        x="rating_count",
        y="clean_title",
        palette="viridis",
        hue="clean_title",
        legend=False,
    )
    plt.title("Top 10 Most-Rated Movies (Review Count)", fontsize=14, weight="bold")
    plt.xlabel("Total Reviews", fontsize=12)
    plt.ylabel("Movie Title", fontsize=12)

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(
                f"{int(width):,}",
                (width, p.get_y() + p.get_height() / 2.0),
                ha="left",
                va="center",
                fontsize=10,
                xytext=(5, 0),
                textcoords="offset points",
            )

    chart2_path = os.path.join(output_dir, "02_top_10_most_rated_movies.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"  -> Saved: {chart2_path}")

    # 5. Chart 3: Top 10 Highest-Rated Movies (Minimum 50 Ratings)
    print("\n[4] Generating Chart 3: Top 10 Highest-Rated Movies (Min 50 Ratings)...")
    min_reviews = 50
    qualified_movies = movie_stats[movie_stats["rating_count"] >= min_reviews]
    top_highest_rated = (
        qualified_movies.sort_values(by=["rating_mean", "rating_count"], ascending=[False, False])
        .head(10)
    )

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=top_highest_rated,
        x="rating_mean",
        y="clean_title",
        palette="mako",
        hue="clean_title",
        legend=False,
    )
    plt.title(
        f"Top 10 Highest-Rated Movies (Minimum {min_reviews} Reviews)",
        fontsize=14,
        weight="bold",
    )
    plt.xlabel("Average Rating (Out of 5.0)", fontsize=12)
    plt.ylabel("Movie Title", fontsize=12)
    plt.xlim(3.5, 4.6)

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(
                f"{width:.2f} ★",
                (width, p.get_y() + p.get_height() / 2.0),
                ha="left",
                va="center",
                fontsize=10,
                xytext=(5, 0),
                textcoords="offset points",
            )

    chart3_path = os.path.join(output_dir, "03_top_10_highest_rated_movies.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"  -> Saved: {chart3_path}")

    # 6. Chart 4: Genre Popularity
    print("\n[5] Generating Chart 4: Top Genres by Rating Count...")
    # Unnest pipe-separated genres
    genre_series = (
        ratings_df[["genres", "rating"]]
        .assign(genre=ratings_df["genres"].str.split("|"))
        .explode("genre")
    )
    genre_series = genre_series[genre_series["genre"] != "Unknown"]

    genre_counts = genre_series["genre"].value_counts().head(12)

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        x=genre_counts.values,
        y=genre_counts.index,
        palette="rocket",
        hue=genre_counts.index,
        legend=False,
    )
    plt.title("Top 12 Most Popular Genres by Number of Ratings", fontsize=14, weight="bold")
    plt.xlabel("Total Ratings", fontsize=12)
    plt.ylabel("Genre", fontsize=12)

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(
                f"{int(width):,}",
                (width, p.get_y() + p.get_height() / 2.0),
                ha="left",
                va="center",
                fontsize=9,
                xytext=(5, 0),
                textcoords="offset points",
            )

    chart4_path = os.path.join(output_dir, "04_genre_distribution.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f"  -> Saved: {chart4_path}")

    # 7. Chart 5: Ratings Trend Over Years
    print("\n[6] Generating Chart 5: Ratings Activity Over Years...")
    ratings_by_year = ratings_df["rating_year"].value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    sns.lineplot(
        x=ratings_by_year.index,
        y=ratings_by_year.values,
        marker="o",
        color="#2b5c8f",
        linewidth=2.5,
    )
    plt.title("MovieLens Rating Activity by Year (1996 - 2018)", fontsize=14, weight="bold")
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Number of Ratings Submitted", fontsize=12)

    chart5_path = os.path.join(output_dir, "05_ratings_trend_by_year.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f"  -> Saved: {chart5_path}")

    # 8. Create and Save Text Summary Report
    print("\n[7] Generating EDA Summary Report...")
    summary_report = []
    summary_report.append("=" * 60)
    summary_report.append("STAGE 3: EXPLORATORY DATA ANALYSIS (EDA) REPORT")
    summary_report.append("=" * 60 + "\n")

    summary_report.append("--- 1. OVERALL DATASET METRICS ---")
    summary_report.append(f"Total Unique Movies: {total_movies:,}")
    summary_report.append(f"Total Ratings Logged: {total_ratings:,}")
    summary_report.append(f"Total Active Users: {total_users:,}")
    summary_report.append(f"Mean Rating Score: {overall_mean_rating:.2f} / 5.00")
    summary_report.append(f"Median Rating Score: {overall_median_rating:.2f} / 5.00")
    summary_report.append(f"Most Frequent Rating: {ratings_df['rating'].mode()[0]} stars\n")

    summary_report.append("--- 2. TOP 10 MOST-RATED MOVIES ---")
    for i, row in top_most_rated.reset_index(drop=True).iterrows():
        summary_report.append(
            f"  {i+1}. {row['clean_title']} — {row['rating_count']} reviews (Avg: {row['rating_mean']:.2f}★)"
        )
    summary_report.append("")

    summary_report.append(f"--- 3. TOP 10 HIGHEST-RATED MOVIES (>= {min_reviews} Reviews) ---")
    for i, row in top_highest_rated.reset_index(drop=True).iterrows():
        summary_report.append(
            f"  {i+1}. {row['clean_title']} — {row['rating_mean']:.2f}★ ({row['rating_count']} reviews)"
        )
    summary_report.append("")

    summary_report.append("--- 4. TOP 5 GENRES BY RATINGS VOLUME ---")
    for genre, count in genre_counts.head(5).items():
        summary_report.append(f"  - {genre}: {count:,} ratings")
    summary_report.append("")

    summary_report.append("--- 5. GENERATED VISUALIZATIONS ---")
    summary_report.append("  - outputs/01_rating_distribution.png")
    summary_report.append("  - outputs/02_top_10_most_rated_movies.png")
    summary_report.append("  - outputs/03_top_10_highest_rated_movies.png")
    summary_report.append("  - outputs/04_genre_distribution.png")
    summary_report.append("  - outputs/05_ratings_trend_by_year.png")
    summary_report.append("\n" + "=" * 60)

    report_text = "\n".join(summary_report)
    print("\n" + report_text)

    summary_file = os.path.join(output_dir, "eda_summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nEDA summary successfully saved to: {summary_file}")
    print("\nStage 3 completed successfully!")


if __name__ == "__main__":
    perform_eda()
