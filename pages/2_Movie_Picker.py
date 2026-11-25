# Lab 4: Agent page
# TODO: Rename this file to fit your page. Keep the number at the front.
#
# Your chatbot again, but now the agent can call your own Python functions as tools
# (see "Giving Your Agent Tools" on Canvas).
# It should:
#   - include at least 2 data-processing functions for your API, written by you, with type
#     hints and docstrings (the agent reads these to decide when to use each tool)
#   - include at least 2 extra tools, which you may build with help from AI. Base these tools
#     on the "cool things to do" in your Dream Project Plan (see "Building Tools for Your Plan" on Canvas)
#   - leave a comment on each tool, and any other code, that AI helped you write
#   - give your tools to a Pydantic AI Agent with tools=[...]
#   - use Streamlit's chat elements, remember the conversation, and use try/except
#   - show what the agent did: which tools it called, and a display of their results
#     (see "Displaying What the Agent Does" on Canvas)

import requests
import streamlit as st
from pydantic_ai import Agent
import csv
import re
from collections import Counter
from pathlib import Path
import altair as alt


# Your tools go here (You must define your tools before your agent!):

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_movies():
    totals = Counter()
    counts = Counter()
    with (DATA_DIR / "ratings.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            movie_id = row["movieId"]
            totals[movie_id] += float(row["rating"])
            counts[movie_id] += 1
    movies = []
    with (DATA_DIR / "movies.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            release_year = re.search(r"\((\d{4})\)\s*$", row["title"])
            if release_year is None:
                continue

            movie_id = row["movieId"]
            count = counts[movie_id]
            movies.append({
                "Movie": row["title"].strip(),
                "Genres": row["genres"].split("|"),
                "Year": int(release_year.group(1)),
                "Average rating": totals[movie_id] / count if count else None,
                "Ratings": count,
            })
    return movies
st.title("Pick a Movie")
movies = load_movies()
genres = sorted({
    genre for movie in movies for genre in movie["Genres"]
    if genre != "(no genres listed)"
})
decades = sorted({movie["Year"] // 10 * 10 for movie in movies}, reverse=True)

left, right = st.columns(2)
with left:
    genre = st.selectbox("Genre", genres, index=genres.index("Comedy"))
with right:
    decade = st.selectbox("Decade", decades, index=decades.index(2000),
                          format_func=lambda year: f"{year}s")
matches = [
    movie for movie in movies
    if genre in movie["Genres"] and decade <= movie["Year"] < decade + 10
]
if not matches:
    st.info("No movies match. Try a different genre or decade.")
    st.stop()
ranked = sorted(
    (movie for movie in matches if movie["Ratings"] >= 10),
    key=lambda movie: (-movie["Average rating"], -movie["Ratings"], movie["Movie"]),
)
st.subheader("Highest-ratd movies")
st.caption("Top 10 matches with at least 10 MovieLens ratings. Ratings are out of 5.")
if ranked:
    rating_chart = alt.Chart(alt.Data(values=ranked[:10])).mark_bar().encode(
        x=alt.X("Average rating:Q", scale=alt.Scale(domain=[0, 5])),
        y=alt.Y("Movie:N", sort=[movie["Movie"] for movie in ranked[:10]],
                axis=alt.Axis(labelLimit=220)),
        tooltip=["Movie:N", alt.Tooltip("Average rating:Q", format=".2f"), "Ratings:Q"],
    )
    st.altair_chart(rating_chart, width="stretch")
else:
    st.info("None of the matches have at least 10 ratings.")
st.subheader("Movies by release year")
year_counts = Counter(movie["Year"] for movie in matches)
year_data = [
    {"Year": str(year), "Movies": year_counts[year]}
    for year in range(decade, decade + 10)
]
year_chart = alt.Chart(alt.Data(values=year_data)).mark_bar().encode(
    x=alt.X("Year:O", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Movies:Q", axis=alt.Axis(tickMinStep=1)),
    tooltip=["Year:O", "Movies:Q"],
)
st.altair_chart(year_chart, width="stretch")
st.caption("Source: [MovieLens Latest Small](https://grouplens.org/datasets/movielens/latest/), "
           "GroupLens. Counts reflect titles in this dataset.")
