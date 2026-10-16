
import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from upstash_redis import Redis

load_dotenv()

st.set_page_config(
    page_title="Redis Database Explorer",
    layout="wide"
)

st.title("Redis Database Explorer")
st.caption("Read-only browser for your DSA question database")

@st.cache_data(ttl=60)
def load_questions():
    redis = Redis(
        url=os.getenv("UPSTASH_REDIS_REST_URL"),
        token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
    )

    raw_data = redis.get("coding_questions:legacy")

    if not raw_data:
        return []

    return json.loads(raw_data)

try:
    questions = load_questions()

    if not questions:
        st.warning("No question records found.")
        st.stop()

    rows = []

    for question in questions:
        payload = question.get("question_payload", "{}")

        if isinstance(payload, str):
            payload = json.loads(payload)

        rows.append({
            "ID": question.get("id"),
            "Title": payload.get("title", "Untitled"),
            "Topic": question.get("topic"),
            "Subtopic": question.get("subtopic"),
            "Difficulty": question.get("difficulty"),
            "Status": question.get("status")
        })

    df = pd.DataFrame(rows)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", len(df))
    col2.metric("Topics", df["Topic"].nunique())
    col3.metric("Difficulties", df["Difficulty"].nunique())

    st.subheader("Browse Questions")

    search = st.text_input("Search by title, ID, or topic")

    topics = ["All"] + sorted(
        df["Topic"].dropna().unique().tolist()
    )
    selected_topic = st.selectbox("Filter by topic", topics)

    filtered = df.copy()

    if search:
        mask = filtered.astype(str).apply(
            lambda col: col.str.contains(
                search, case=False, na=False
            )
        ).any(axis=1)
        filtered = filtered[mask]

    if selected_topic != "All":
        filtered = filtered[
            filtered["Topic"] == selected_topic
        ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Inspect a Question")

    selected_id = st.selectbox(
        "Select question",
        filtered["ID"].tolist(),
        format_func=lambda qid: (
            f"{filtered.loc[filtered['ID'] == qid, 'Title'].iloc[0]}"
            f" — {qid}"
        )
    )

    if selected_id:
        selected = next(
            q for q in questions if q.get("id") == selected_id
        )

        st.json(selected)

except Exception as e:
    st.error(f"Could not load Redis data: {e}")
    st.caption(
        "Check that your .env file contains valid credentials "
        "and that your Redis database is accessible."
    )