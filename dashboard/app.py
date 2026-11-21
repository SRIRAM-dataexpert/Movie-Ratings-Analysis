"""
Movie Ratings Analysis Dashboard
File: dashboard/app.py

Interactive Streamlit web dashboard for exploring MovieLens data.
Features:
- Executive KPI Metrics (Total Movies, Total Ratings, Users, Average Rating)
- Interactive Plotly Charts (Rating distributions, trends over time)
- Leaderboards (Highest-rated movies with review threshold, most popular movies)
- Genre Breakdown (Volume and rating quality by genre)
- Search & Exploration (Search any movie by title, view rating stats & rating breakdown)
- Gallery of Generated Analytical Visualizations
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure page layout and branding
st.set_page_config(
    page_title="Movie Ratings Analysis Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .kpi-container {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    """Load cleaned datasets and precompute movie aggregations for peak performance."""
    # Handle both being run from root or dashboard/ directory
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(curr_dir) if os.path.basename(curr_dir) == "dashboard" else curr_dir

    ratings_path = os.path.join(project_root, "outputs", "cleaned_ratings.csv")
    movies_path = os.path.join(project_root, "outputs", "cleaned_movies.csv")

    if not os.path.exists(ratings_path) or not os.path.exists(movies_path):
        import importlib
        clean_module = importlib.import_module("src.02_clean_data")
        clean_module.clean_datasets()

    ratings = pd.read_csv(ratings_path)
    movies = pd.read_csv(movies_path)

    # Compute movie-level aggregates
    stats = (
        ratings.groupby("movieId")
        .agg(
            rating_count=("rating", "count"),
            rating_mean=("rating", "mean"),
        )
        .reset_index()
    )

    movies_with_stats = pd.merge(movies, stats, on="movieId", how="left")
    movies_with_stats["rating_count"] = movies_with_stats["rating_count"].fillna(0).astype(int)
    movies_with_stats["rating_mean"] = movies_with_stats["rating_mean"].fillna(0.0)

    return ratings, movies_with_stats, project_root


ratings_df, movies_df, project_root = load_data()

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.image("https://img.icons8.com/color/96/movie-projector.png", width=70)
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("Filter data and customize dashboard views.")

# Genre filter
all_genres = sorted(
    list(
        set(
            g
            for sublist in movies_df["genres"].dropna().str.split("|")
            for g in sublist
            if g and g != "Unknown"
        )
    )
)
selected_genre = st.sidebar.selectbox("Filter by Genre:", ["All Genres"] + all_genres)

# Release year filter
min_yr = int(movies_df["year"].dropna().min()) if movies_df["year"].notnull().any() else 1900
max_yr = int(movies_df["year"].dropna().max()) if movies_df["year"].notnull().any() else 2020
year_range = st.sidebar.slider(
    "Release Year Range:",
    min_value=min_yr,
    max_value=max_yr,
    value=(1980, max_yr),
)

# Minimum rating votes threshold for leaderboards
min_votes = st.sidebar.slider(
    "Min. Review Count for Top-Rated:",
    min_value=5,
    max_value=200,
    value=50,
    step=5,
)

# Apply filters
filtered_movies = movies_df.copy()
if selected_genre != "All Genres":
    filtered_movies = filtered_movies[
        filtered_movies["genres"].str.contains(selected_genre, na=False, regex=False)
    ]

# Filter year
filtered_movies = filtered_movies[
    (filtered_movies["year"] >= year_range[0]) & (filtered_movies["year"] <= year_range[1])
]

filtered_ratings = ratings_df[ratings_df["movieId"].isin(filtered_movies["movieId"])]

# ----------------- MAIN HEADER -----------------
st.markdown('<div class="main-title">🎬 Movie Ratings Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Explore audience ratings, genre trends, and movie performance powered by the MovieLens dataset.</div>',
    unsafe_allow_html=True,
)

# ----------------- KPI METRIC CARDS -----------------
col1, col2, col3, col4 = st.columns(4)

total_movies_count = len(filtered_movies)
total_ratings_count = len(filtered_ratings)
total_unique_users = filtered_ratings["userId"].nunique() if total_ratings_count > 0 else 0
avg_rating_score = filtered_ratings["rating"].mean() if total_ratings_count > 0 else 0.0

col1.metric("🎥 Total Movies", f"{total_movies_count:,}")
col2.metric("⭐ Total Ratings", f"{total_ratings_count:,}")
col3.metric("👥 Active Users", f"{total_unique_users:,}")
col4.metric("📈 Avg Rating Score", f"{avg_rating_score:.2f} / 5.0")

st.markdown("---")

# ----------------- TABS NAVIGATION -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Ratings Distribution & Trends",
        "🏆 Top Rated & Popular Movies",
        "🎭 Genre Insights",
        "🔍 Movie Search & Lookup",
        "🖼️ Precomputed Visualizations",
    ]
)

# ================= TAB 1: RATINGS DISTRIBUTION & TRENDS =================
with tab1:
    st.subheader("Rating Distribution & Review Activity Over Time")

    if total_ratings_count > 0:
        c1, c2 = st.columns(2)

        with c1:
            # Distribution of star ratings
            dist = (
                filtered_ratings["rating"]
                .value_counts()
                .reset_index()
                .rename(columns={"count": "Rating Count", "rating": "Rating (Stars)"})
                .sort_values(by="Rating (Stars)")
            )

            fig_dist = px.bar(
                dist,
                x="Rating (Stars)",
                y="Rating Count",
                text="Rating Count",
                title="<b>Star Rating Distribution (0.5 to 5.0)</b>",
                color="Rating (Stars)",
                color_continuous_scale="Blues",
            )
            fig_dist.update_traces(textposition="outside")
            fig_dist.update_layout(xaxis=dict(tickmode="linear", tick0=0.5, dtick=0.5))
            st.plotly_chart(fig_dist, use_container_width=True)

        with c2:
            # Activity trend over time
            trend = (
                filtered_ratings["rating_year"]
                .value_counts()
                .reset_index()
                .rename(columns={"count": "Number of Reviews", "rating_year": "Year"})
                .sort_values(by="Year")
            )

            fig_trend = px.line(
                trend,
                x="Year",
                y="Number of Reviews",
                markers=True,
                title="<b>Review Volume Submitted Over Time</b>",
                color_discrete_sequence=["#1E3A8A"],
            )
            fig_trend.update_layout(hovermode="x unified")
            st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No ratings match the selected filters. Please adjust the sidebar controls.")

# ================= TAB 2: TOP RATED & POPULAR MOVIES =================
with tab2:
    st.subheader("Leaderboards: Highest-Rated & Most Popular Titles")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"#### 🌟 Top 10 Highest-Rated (Min. {min_votes} Reviews)")
        eligible = filtered_movies[filtered_movies["rating_count"] >= min_votes]

        if not eligible.empty:
            top_rated = (
                eligible.sort_values(
                    by=["rating_mean", "rating_count"],
                    ascending=[False, False],
                )
                .head(10)
                .copy()
            )

            fig_top_rated = px.bar(
                top_rated,
                x="rating_mean",
                y="clean_title",
                orientation="h",
                text=top_rated["rating_mean"].apply(lambda x: f"{x:.2f} ★"),
                color="rating_mean",
                color_continuous_scale="Tealgrn",
                labels={"rating_mean": "Average Rating", "clean_title": "Movie"},
            )
            fig_top_rated.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_range=[3.0, 5.0],
                showlegend=False,
            )
            st.plotly_chart(fig_top_rated, use_container_width=True)
        else:
            st.info(f"No movies have at least {min_votes} reviews within the current filter.")

    with c2:
        st.markdown("#### 🔥 Top 10 Most-Reviewed Movies")
        if not filtered_movies.empty:
            most_reviewed = (
                filtered_movies.sort_values(by="rating_count", ascending=False).head(10).copy()
            )

            fig_popular = px.bar(
                most_reviewed,
                x="rating_count",
                y="clean_title",
                orientation="h",
                text="rating_count",
                color="rating_count",
                color_continuous_scale="Sunset",
                labels={"rating_count": "Total Reviews", "clean_title": "Movie"},
            )
            fig_popular.update_layout(
                yaxis={"categoryorder": "total ascending"},
                showlegend=False,
            )
            st.plotly_chart(fig_popular, use_container_width=True)

# ================= TAB 3: GENRE INSIGHTS =================
with tab3:
    st.subheader("Genre Breakdown & Popularity")

    if total_ratings_count > 0:
        genre_expanded = (
            filtered_ratings[["genres", "rating"]]
            .assign(genre=filtered_ratings["genres"].str.split("|"))
            .explode("genre")
        )
        genre_expanded = genre_expanded[
            (genre_expanded["genre"] != "Unknown") & (genre_expanded["genre"].notnull())
        ]

        genre_agg = (
            genre_expanded.groupby("genre")
            .agg(
                Rating_Count=("rating", "count"),
                Average_Rating=("rating", "mean"),
            )
            .reset_index()
            .sort_values(by="Rating_Count", ascending=False)
        )

        c1, c2 = st.columns(2)

        with c1:
            fig_genre_vol = px.bar(
                genre_agg.head(12),
                x="genre",
                y="Rating_Count",
                text="Rating_Count",
                color="Rating_Count",
                color_continuous_scale="Purples",
                title="<b>Top 12 Genres by Review Volume</b>",
                labels={"Rating_Count": "Total Ratings", "genre": "Genre"},
            )
            fig_genre_vol.update_traces(textposition="outside")
            st.plotly_chart(fig_genre_vol, use_container_width=True)

        with c2:
            fig_genre_score = px.bar(
                genre_agg.sort_values(by="Average_Rating", ascending=True),
                x="Average_Rating",
                y="genre",
                orientation="h",
                text=genre_agg.sort_values(by="Average_Rating", ascending=True)[
                    "Average_Rating"
                ].apply(lambda x: f"{x:.2f}★"),
                color="Average_Rating",
                color_continuous_scale="Viridis",
                title="<b>Average Rating Score by Genre</b>",
                labels={"Average_Rating": "Avg Rating", "genre": "Genre"},
            )
            fig_genre_score.update_layout(xaxis_range=[2.5, 4.5])
            st.plotly_chart(fig_genre_score, use_container_width=True)

# ================= TAB 4: MOVIE SEARCH & LOOKUP =================
with tab4:
    st.subheader("🔍 Movie Search & Individual Details")

    search_query = st.text_input(
        "Enter movie title to search:",
        placeholder="e.g. Inception, Matrix, Toy Story, Godfather...",
    )

    if search_query:
        matches = movies_df[
            movies_df["clean_title"].str.contains(search_query, case=False, na=False)
        ]

        if not matches.empty:
            st.success(f"Found {len(matches)} matching movie(s):")

            display_cols = [
                "movieId",
                "clean_title",
                "year",
                "genres",
                "rating_mean",
                "rating_count",
            ]
            display_df = matches[display_cols].copy()
            display_df.rename(
                columns={
                    "movieId": "ID",
                    "clean_title": "Title",
                    "year": "Release Year",
                    "genres": "Genres",
                    "rating_mean": "Avg Rating",
                    "rating_count": "Total Reviews",
                },
                inplace=True,
            )
            display_df["Avg Rating"] = display_df["Avg Rating"].round(2)

            st.dataframe(
                display_df.sort_values(by="Total Reviews", ascending=False),
                width="stretch",
                hide_index=True,
            )

            # Deep dive on first selected match
            selected_movie_title = st.selectbox(
                "Select a movie for detailed rating breakdown:",
                matches["clean_title"].tolist(),
            )

            chosen_movie = matches[matches["clean_title"] == selected_movie_title].iloc[0]
            chosen_ratings = ratings_df[ratings_df["movieId"] == chosen_movie["movieId"]]

            m_col1, m_col2, m_col3 = st.columns([1, 1, 2])
            m_col1.metric("Average Rating", f"{chosen_movie['rating_mean']:.2f} ★")
            m_col2.metric("Total Reviews", f"{chosen_movie['rating_count']} reviews")
            m_col3.write(
                f"**Release Year:** {chosen_movie['year'] if pd.notnull(chosen_movie['year']) else 'N/A'}\n\n**Genres:** {chosen_movie['genres']}"
            )

            if not chosen_ratings.empty:
                r_dist = chosen_ratings["rating"].value_counts().reset_index()
                r_dist.columns = ["Rating", "Count"]
                r_dist = r_dist.sort_values("Rating")

                fig_single = px.bar(
                    r_dist,
                    x="Rating",
                    y="Count",
                    text="Count",
                    title=f"Rating Distribution for '{chosen_movie['clean_title']}'",
                    color_discrete_sequence=["#3B82F6"],
                )
                fig_single.update_layout(xaxis=dict(tickmode="linear", tick0=0.5, dtick=0.5))
                st.plotly_chart(fig_single, use_container_width=True)
        else:
            st.warning(f"No movies found matching '{search_query}'. Try another search term.")
    else:
        st.info("Type a movie title above to instantly search through 9,700+ movies.")

# ================= TAB 5: PRECOMPUTED VISUALIZATIONS =================
with tab5:
    st.subheader("🖼️ Generated Analytical Visualizations Gallery")
    st.markdown("These high-resolution charts were created during the Exploratory Data Analysis phase:")

    img_dir = os.path.join(project_root, "outputs")

    img_files = [
        ("01_rating_distribution.png", "1. Overall Rating Distribution (0.5 to 5.0 Stars)"),
        ("02_top_10_most_rated_movies.png", "2. Top 10 Most-Rated Movies"),
        ("03_top_10_highest_rated_movies.png", "3. Top 10 Highest-Rated Movies (Min 50 Votes)"),
        ("04_genre_distribution.png", "4. Top 12 Genres by Rating Volume"),
        ("05_ratings_trend_by_year.png", "5. Review Volume Trend Over Years"),
    ]

    for img_name, caption in img_files:
        full_img_path = os.path.join(img_dir, img_name)
        if os.path.exists(full_img_path):
            st.markdown(f"#### {caption}")
            st.image(full_img_path, use_container_width=True)
            st.markdown("---")
