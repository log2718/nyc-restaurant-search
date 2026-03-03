import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="NYC Restaurant Search", layout="wide")
st.title("🍕 NYC Restaurant Vector Search")

# Sidebar for filters
st.sidebar.header("Filters")
online_order_only = st.sidebar.checkbox("Online Ordering Available")
min_reviews = st.sidebar.slider("Minimum Reviews", 0, 5000, 0, 50)

# Mode selection
mode = st.radio("Search Mode", ["Natural Language Search", "Find Similar Restaurants"], horizontal=True)

search_q = None
search_id = None

if mode == "Natural Language Search":
    search_q = st.text_input("Describe the restaurant you are looking for...", "great pizza with outdoor seating")
else:
    # Fetch restaurants for dropdown
    try:
        init_res = requests.get(f"{API_URL}/api/restaurants")
        if init_res.status_code == 200:
            options = {r["title"]: r["id"] for r in init_res.json()}
            selected_title = st.selectbox("Select a restaurant to find similar ones", list(options.keys()))
            search_id = options[selected_title] if selected_title else None
        else:
            st.error("Fetched empty restaurant list. Is data processed?")
    except Exception as e:
        st.error("Could not connect to the API. Is FastAPI running?")

if st.button("Search", type="primary"):
    with st.spinner("Searching vectors..."):
        try:
            params = {
                "online_order_only": online_order_only,
                "min_reviews": min_reviews,
                "limit": 10
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
                    df = pd.DataFrame(results)
                    
                    for _, row in df.iterrows():
                        st.markdown(f"#### {row['title']} `({row['similarity']:.2f} score)`")
                        st.write(f"**Category:** {row['category']} | **Reviews:** {row['number_of_reviews']} | **Online Order:** {'🟢 Yes' if row['online_order'] else '🔴 No'}")
                        st.info(f"**Reviews:** {row['review_comment']}")
                        st.write(f"**Popular Food:** {row['popular_food']}")
                        st.markdown("---")
            else:
                st.error(f"API Error: {res.text}")
        except Exception as e:
            st.error(f"Failed to fetch results: {e}")
