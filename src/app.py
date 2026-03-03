import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="NYC Restaurant Search", layout="wide")

# --- Custom styling ---
st.markdown("""
<style>
    /* White top header row */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    /* Light yellow page background */
    .stApp {
        background-color: #fce8b2;
    }
    /* Slightly darker yellow/orange input fields */
    .stTextInput input, .stSelectbox select {
        background-color: #fff9e6 !important;
    }
    div[data-baseweb="input"] {
        background-color: #fff9e6 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #fff9e6 !important;
    }
    /* Title banner – more red than pink */
    .title-banner {
        background-color: #e86060;
        padding: 1rem 2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .title-banner h1 {
        margin: 0;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-banner"><h1>NYC Restaurant Vector Search</h1></div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Filters")
online_order_only = st.sidebar.checkbox("Online Ordering Available")
min_reviews = st.sidebar.slider("Minimum Reviews", 0, 5000, 0, 50)
top_k = st.sidebar.radio("Number of results", [5, 10, 25], index=1)

# Mode selection
mode = st.radio("Search Mode", ["Natural Language Search", "Find Similar Restaurants"], horizontal=True)

search_q = None
search_id = None

if mode == "Natural Language Search":
    search_q = st.text_input("Describe the restaurant you are looking for...", "great pizza with outdoor seating")
else:
    try:
        init_res = requests.get(f"{API_URL}/api/restaurants")
        if init_res.status_code == 200:
            options = {r["title"]: r["id"] for r in init_res.json()}
            selected_title = st.selectbox("Select a restaurant to find similar ones", list(options.keys()))
            search_id = options[selected_title] if selected_title else None
        else:
            st.error("Fetched empty restaurant list. Is data processed?")
    except Exception:
        st.error("Could not connect to the API. Is FastAPI running?")

if st.button("Search", type="primary"):
    # Validate that we have a search query or restaurant ID
    if not search_q and not search_id:
        st.error("Please enter a search query or select a restaurant to find similar ones.")
    else:
        with st.spinner("Searching vectors..."):
            try:
                params = {
                    "online_order_only": online_order_only,
                    "min_reviews": min_reviews,
                    "limit": top_k,
                }
                if search_q:
                    params["q"] = search_q
                if search_id:
                    params["restaurant_id"] = search_id

                res = requests.get(f"{API_URL}/api/search", params=params)

                if res.status_code == 200:
                    results = res.json()
                    if not results:
                        st.warning("No matching restaurants found. Try adjusting your filters.")
                    else:
                        st.write(f"### Found {len(results)} matches:")

                        for row in results:
                            left, right = st.columns([3, 2])
                            with left:
                                st.markdown(f"**{row['title']}** — `{row['similarity']:.4f} cosine similarity`")
                                st.write(f"**Category:** {row['category']} · **Reviews:** {row['number_of_reviews']} · **Online Order:** {'🟢 Yes' if row['online_order'] else '🔴 No'}")
                                if row['popular_food'] and row['popular_food'] != 'No':
                                    st.write(f"**Popular Food:** {row['popular_food']}")
                            with right:
                                st.info(f"{row['review_comment']}")
                            st.markdown("---")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Failed to fetch results: {e}")
