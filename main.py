import streamlit as st
from tavily import TavilyClient
from dotenv import load_dotenv
import os 
# ------------------------ Tavily Setup ------------------------
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]  # ✅ fetch from Streamlit Secrets
client = TavilyClient(api_key=TAVILY_API_KEY)

# Initialize Tavily client
if not TAVILY_API_KEY:
    st.error("❌ Tavily API Key not found. Please set it in your .env file.")
else:
    client = TavilyClient(api_key=TAVILY_API_KEY)  # 🔑 Your Tavily API key here
client = TavilyClient(api_key=TAVILY_API_KEY)

# ------------------------ Session State ------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------ Authentication ------------------------
def auth_page():
    st.markdown("<h1 style='text-align:center; color:#00FFAA;'>🔒 Login to TruthLens</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:grey;'>Enter your credentials</p>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid credentials!")

# ------------------------ Tavily Search ------------------------
def search_query(query: str, max_results=10):
    try:
        results = client.search(query, search_depth="advanced", max_results=max_results)
        return [(r["title"], r["url"]) for r in results["results"]]
    except Exception as e:
        st.error(f"Error fetching sources: {e}")
        return []

# ------------------------ Main TruthLens Page ------------------------
def main_page():
    st.set_page_config(page_title="TruthLens", page_icon="🔍", layout="wide")

    # CSS for dark theme and cards
    st.markdown("""
        <style>
        body {background-color: #0e1117; color: #ffffff;}
        .stButton>button {background-color:#00FFAA; color:#000; border-radius:8px;}
        .result-card {background-color:#1e222b; padding:15px; margin:10px 0; border-radius:12px; box-shadow:0 0 10px rgba(0,255,170,0.2);}
        footer {visibility:hidden;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#00FFAA;'>🔍 TruthLens</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:grey;'>AI-powered Fact Checker (Source Finder)</p>", unsafe_allow_html=True)

    # Sidebar history
    st.sidebar.title("🕘 History")
    if st.session_state.history:
        for q in reversed(st.session_state.history[-10:]):
            st.sidebar.markdown(f"- **{q}**")
    else:
        st.sidebar.info("No queries yet.")

    # Query input
    query = st.text_input("Enter a claim or news headline:")
    max_results = st.slider("Number of sources to fetch:", 3, 15, 5)

    if st.button("Verify") and query:
        with st.spinner("🔎 Searching sources..."):
            articles = search_query(query, max_results=max_results)

        st.session_state.history.append(query)

        # Tabs for Trusted vs All sources
        trusted_sources_list = [
            "ndtv.com", "bbc.com", "reuters.com", "indiatimes.com",
            "thehindu.com", "indianexpress.com", "timesofindia.com",
            "cnn.com", "gov.in", "who.int", "un.org"
        ]
        trusted_articles = [a for a in articles if any(t in a[1] for t in trusted_sources_list)]

        tab1, tab2 = st.tabs(["✅ Trusted Sources", "⚠️ All Sources"])

        with tab1:
            if trusted_articles:
                for title, url in trusted_articles:
                    st.markdown(f"<div class='result-card'><b>{title}</b><br>🔗 <a href='{url}' target='_blank'>{url}</a> — ✅ Trusted</div>", unsafe_allow_html=True)
            else:
                st.info("No trusted sources found.")

        with tab2:
            if articles:
                for title, url in articles:
                    tag = "✅ Trusted" if any(t in url for t in trusted_sources_list) else "⚠️ Unknown"
                    st.markdown(f"<div class='result-card'><b>{title}</b><br>🔗 <a href='{url}' target='_blank'>{url}</a> — {tag}</div>", unsafe_allow_html=True)
            else:
                st.info("No sources found.")

# ------------------------ App Router ------------------------
def app():
    if not st.session_state.authenticated:
        auth_page()
    else:
        main_page()

# ------------------------ Run App ------------------------
if __name__ == "__main__":
    app()

