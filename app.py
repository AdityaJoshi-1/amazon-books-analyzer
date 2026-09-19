import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION (MEDIEVAL THEME)
# ==========================================
st.set_page_config(
    page_title="Grand Archives of Bestsellers",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# MEDIEVAL STYLING (CUSTOM CSS)
# ==========================================
st.markdown("""
    <style>
    /* Dark Oakwood & Parchment Palette */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=IM+Fell+English&display=swap');

    .stApp {
        background-color: #12100e;
        color: #e6dacb;
    }
    
    /* Headers & Typography */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #d4af37 !important; /* Gold header */
        letter-spacing: 1px;
    }
    
    body, p, span, label {
        font-family: 'IM Fell English', Georgia, serif !important;
    }

    /* Metric Cards styled like Ancient Plaques */
    div[data-testid="stMetric"] {
        background: radial-gradient(circle, #221d19 0%, #171412 100%);
        border: 1px solid #d4af37;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.7);
    }
    
    div[data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-family: 'Cinzel', serif !important;
    }

    /* Sidebar Medieval Styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1613;
        border-right: 1px solid #4a3b2c;
    }
    
    /* Buttons styled like Leather / Brass Badges */
    .stButton>button {
        background: linear-gradient(180deg, #6b1724 0%, #4a0e17 100%);
        color: #f4eae1 !important;
        border: 1px solid #d4af37 !important;
        border-radius: 6px;
        font-family: 'Cinzel', serif;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #d4af37 !important;
        color: #12100e !important;
        box-shadow: 0 0 10px #d4af37;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #12100e; 
    }
    ::-webkit-scrollbar-thumb {
        background: #4a3b2c; 
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SUB-GENRE KEYWORD MAPPING
# ==========================================
SUBGENRE_KEYWORDS = {
    "Self-Help & Mindset": ["habit", "subtle art", "mindset", "power", "secret", "think and grow", "attitude", "magic of thinking"],
    "Finance & Business": ["money", "rich dad", "invest", "millionaire", "capital", "business", "economy", "finance", "freakonomics", "zero to one"],
    "Cooking & Diet": ["cook", "diet", "food", "recipe", "keto", "baking", "kitchen", "meal", "salt fat acid"],
    "Children & YA": ["harry potter", "percy jackson", "dog man", "diary of a wimpy", "cat in the hat", "wonder", "dr. seuss", "hunger games"],
    "Biography & Memoir": ["memoir", "becoming", "unbroken", "steve jobs", "autobiography", "story of", "diary", "educated", "when breath becomes air"],
    "Thriller & Mystery": ["girl", "silent patient", "gone", "mystery", "murder", "detective", "shadow", "spy", "da vinci"],
    "Health & Fitness": ["body", "health", "sleep", "brain", "workout", "fitness", "healing", "vitality"],
    "History & Politics": ["war", "history", "freedom", "american", "world", "politics", "revolution", "sapiens", "civilization"],
    "Romance & Fiction": ["love", "heart", "beach", "romance", "kiss", "summer", "forever", "me before you"]
}

def detect_subgenre(title):
    title_lower = str(title).lower()
    for subgenre, keywords in SUBGENRE_KEYWORDS.items():
        if any(keyword in title_lower for keyword in keywords):
            return subgenre
    return "General Literature"

# ==========================================
# LOAD DATASET
# ==========================================
@st.cache_data
def load_data():
   df = pd.read_csv("amazon_books.csv")
    df["Sub-Genre"] = df["Name"].apply(detect_subgenre)
    return df

df = load_data()

# ==========================================
# SIDEBAR FILTERS & AMBIENCE
# ==========================================
st.sidebar.title("📜 Archives Control")
st.sidebar.markdown("---")

# Ambience Audio Player Feature
st.sidebar.subheader("🎶 Ambient Atmosphere")
ambient_choice = st.sidebar.selectbox(
    "Choose Background Ambiance:",
    ["None", "Quiet Rain & Fireplace", "Tavern Lute Music"]
)

if ambient_choice == "Quiet Rain & Fireplace":
    st.sidebar.audio("https://cdn.pixabay.com/download/audio/2022/05/16/audio_db65912089.mp3?filename=soft-rain-ambient-111154.mp3")
elif ambient_choice == "Tavern Lute Music":
    st.sidebar.audio("https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c87130b9.mp3?filename=medieval-fantasy-108102.mp3")

st.sidebar.markdown("---")
st.sidebar.header("🛡️ Search & Filter Manuscripts")

# Advanced Feature 1: Search Bar
search_query = st.sidebar.text_input("🔍 Search Title / Author:", "")

# Filters
genres_available = df["Genre"].unique().tolist()
selected_genre = st.sidebar.multiselect(
    "Select Realm (Genre):",
    options=genres_available,
    default=genres_available
)

min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
selected_years = st.sidebar.slider(
    "Select Eras (Years):",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

min_price, max_price = float(df["Price"].min()), float(df["Price"].max())
selected_price = st.sidebar.slider(
    "Select Cost (Gold Pieces / $):",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# Apply Search & Filter Conditions
filtered_df = df[
    (df["Genre"].isin(selected_genre)) &
    (df["Year"] >= selected_years[0]) & (df["Year"] <= selected_years[1]) &
    (df["Price"] >= selected_price[0]) & (df["Price"] <= selected_price[1])
]

if search_query:
    filtered_df = filtered_df[
        filtered_df["Name"].str.contains(search_query, case=False, na=False) |
        filtered_df["Author"].str.contains(search_query, case=False, na=False)
    ]

# ==========================================
# MAIN TITLE & HEADER
# ==========================================
st.title("🏛️ The Grand Archives of Bestsellers")
st.markdown("*A peaceful sanctuary for exploring historical literary tomes and market analytics (2009–2019).*")

st.divider()

# ==========================================
# KPI METRIC CARDS
# ==========================================
st.header("📊 Archives Summary")

col1, col2, col3, col4 = st.columns(4)

avg_rating = filtered_df["User Rating"].mean() if not filtered_df.empty else 0
avg_price = filtered_df["Price"].mean() if not filtered_df.empty else 0
total_reviews = filtered_df["Reviews"].sum() if not filtered_df.empty else 0

with col1:
    st.metric("📜 Tomes Preserved", len(filtered_df))
with col2:
    st.metric("⭐ Celestial Rating", f"{avg_rating:.2f} / 5.0")
with col3:
    st.metric("💰 Average Cost", f"${avg_price:.2f}")
with col4:
    st.metric("💬 Total Scribe Reviews", f"{total_reviews:,}")

st.divider()

# ==========================================
# ADVANCED FEATURE 2: SIDE-BY-SIDE DUAL COMPARE TOOL
# ==========================================
with st.expander("⚔️ Comparative Sanctuary (Compare Any Two Books Side-by-Side)"):
    st.subheader("Select Two Manuscripts to Compare:")
    comp_col1, comp_col2 = st.columns(2)
    
    book_list = df["Name"].unique().tolist()
    
    with comp_col1:
        book_a = st.selectbox("First Tome:", book_list, index=0)
        data_a = df[df["Name"] == book_a].iloc[0]
        st.markdown(f"""
        **Author**: {data_a['Author']}  
        **Genre**: {data_a['Genre']} ({data_a['Sub-Genre']})  
        **Rating**: ⭐ {data_a['User Rating']}  
        **Reviews**: 💬 {data_a['Reviews']:,}  
        **Price**: 💰 ${data_a['Price']}  
        **Year**: 📅 {data_a['Year']}
        """)

    with comp_col2:
        book_b = st.selectbox("Second Tome:", book_list, index=1 if len(book_list) > 1 else 0)
        data_b = df[df["Name"] == book_b].iloc[0]
        st.markdown(f"""
        **Author**: {data_b['Author']}  
        **Genre**: {data_b['Genre']} ({data_b['Sub-Genre']})  
        **Rating**: ⭐ {data_b['User Rating']}  
        **Reviews**: 💬 {data_b['Reviews']:,}  
        **Price**: 💰 ${data_b['Price']}  
        **Year**: 📅 {data_b['Year']}
        """)

st.divider()

# ==========================================
# CHARTS & VISUAL ANALYTICS
# ==========================================
st.header("📈 Visual Chronicles")

if not filtered_df.empty:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📜 Fiction vs Non-Fiction Distribution")
        genre_year_counts = filtered_df.groupby(["Year", "Genre"]).size().reset_index(name="Count")
        fig_genre = px.bar(
            genre_year_counts,
            x="Year",
            y="Count",
            color="Genre",
            barmode="group",
            color_discrete_map={"Fiction": "#6b1724", "Non Fiction": "#d4af37"},
            template="plotly_dark"
        )
        fig_genre.update_layout(paper_bgcolor="#12100e", plot_bgcolor="#171412")
        st.plotly_chart(fig_genre, use_container_width=True)

    with chart_col2:
        st.subheader("💰 Price Progression Over Eras")
        yearly_price = filtered_df.groupby("Year")["Price"].mean().reset_index()
        fig_price = px.line(
            yearly_price,
            x="Year",
            y="Price",
            markers=True,
            color_discrete_sequence=["#d4af37"],
            template="plotly_dark"
        )
        fig_price.update_layout(paper_bgcolor="#12100e", plot_bgcolor="#171412")
        st.plotly_chart(fig_price, use_container_width=True)

st.divider()

# ==========================================
# BOOK RANKINGS TABLE
# ==========================================
st.header("🏆 Legendary Rankings")

tab1, tab2 = st.tabs(["🔥 Most Acclaimed (Most Reviews)", "⭐ Highest Renown (Top Rated)"])

with tab1:
    top_reviewed = filtered_df.sort_values("Reviews", ascending=False).head(10)
    st.dataframe(
        top_reviewed[["Name", "Author", "Genre", "Sub-Genre", "Reviews", "User Rating", "Price", "Year"]],
        hide_index=True,
        use_container_width=True
    )

with tab2:
    top_rated = filtered_df.sort_values(by=["User Rating", "Reviews"], ascending=[False, False]).head(10)
    st.dataframe(
        top_rated[["Name", "Author", "Genre", "Sub-Genre", "User Rating", "Reviews", "Price", "Year"]],
        hide_index=True,
        use_container_width=True
    )

st.divider()

# ==========================================
# EXPORT DATA SECTION
# ==========================================
st.header("📋 The Full Scrolls")

csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📜 Download Filtered Scrolls (CSV)",
    data=csv_data,
    file_name="bestsellers_archives.csv",
    mime="text/csv"
)

st.dataframe(
    filtered_df[["Name", "Author", "Genre", "Sub-Genre", "User Rating", "Reviews", "Price", "Year"]],
    hide_index=True,
    use_container_width=True
)

st.markdown("""
    <hr style="border:1px solid #4a3b2c;">
    <div style="text-align: center; color: #8c7a6b; padding: 10px;">
        📜 <i>Grand Archives of Bestsellers — Crafted with Python, Pandas & Streamlit</i>
    </div>
""", unsafe_allow_html=True)
