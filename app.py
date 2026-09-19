import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Amazon Bestsellers Analytics",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM STYLING (CSS)
# ==========================================
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .footer {
        position: relative;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 20px;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid #e9ecef;
        margin-top: 50px;
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
    return "General / Other"

# ==========================================
# LOAD DATASET (ROBUST PATH + CACHED)
# ==========================================
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Checks if file is in main directory or data/ folder
    if os.path.exists(os.path.join(BASE_DIR, "amazon_books.csv")):
        file_path = os.path.join(BASE_DIR, "amazon_books.csv")
    else:
        file_path = os.path.join(BASE_DIR, "data", "amazon_books.csv")
        
    df = pd.read_csv(file_path)
    df["Sub-Genre"] = df["Name"].apply(detect_subgenre)
    return df

df = load_data()

# ==========================================
# SIDEBAR FILTERS
# ==========================================
st.sidebar.title("📚 Amazon Analytics")
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Options")

genres_available = df["Genre"].unique().tolist()
selected_genre = st.sidebar.multiselect(
    "Select Main Genre(s):",
    options=genres_available,
    default=genres_available
)

min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

min_price, max_price = float(df["Price"].min()), float(df["Price"].max())
selected_price = st.sidebar.slider(
    "Select Price Range ($):",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

filtered_df = df[
    (df["Genre"].isin(selected_genre)) &
    (df["Year"] >= selected_years[0]) & (df["Year"] <= selected_years[1]) &
    (df["Price"] >= selected_price[0]) & (df["Price"] <= selected_price[1])
]

if filtered_df.empty:
    st.warning("⚠️ No books match your selected filter criteria. Please adjust your sidebar settings.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Results", f"{len(filtered_df)} / {len(df)} Books")

# ==========================================
# HEADER & OVERVIEW
# ==========================================
st.title("📚 Amazon Bestselling Books Dashboard")
st.markdown("An interactive analytics dashboard exploring historical bestselling books data from Amazon (2009–2019).")

with st.expander("ℹ️ About this Dashboard & Dataset"):
    st.markdown("""
    * **Dataset Scope**: Contains 550 top-selling books on Amazon between 2009 and 2019.
    * **Key Variables**: Book Title, Author, User Rating, Number of Reviews, Price, Year, and Genre.
    * **Tech Stack**: Built using **Python**, **Pandas** for data aggregation, **Plotly Express** for dynamic charts, and **Streamlit** for front-end presentation.
    """)

st.divider()

# ==========================================
# KPI METRIC CARDS
# ==========================================
st.header("📊 Executive Overview")

overall_avg_rating = df["User Rating"].mean()
overall_avg_price = df["Price"].mean()

avg_rating = filtered_df["User Rating"].mean()
avg_price = filtered_df["Price"].mean()
total_reviews = filtered_df["Reviews"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📚 Books Shown", len(filtered_df), delta=f"{len(filtered_df) - len(df)} total")
with col2:
    rating_delta = round(avg_rating - overall_avg_rating, 2)
    st.metric("⭐ Average Rating", round(avg_rating, 2), delta=f"{rating_delta:+.2f} vs avg")
with col3:
    price_delta = round(avg_price - overall_avg_price, 2)
    st.metric("💰 Average Price", f"${avg_price:.2f}", delta=f"${price_delta:+.2f} vs avg")
with col4:
    st.metric("💬 Total Reviews", f"{total_reviews:,}")

st.divider()

# ==========================================
# PLOTLY CHARTS
# ==========================================
st.header("📈 Visual Trends & Distribution")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📚 Genre Distribution per Year")
    genre_year_counts = filtered_df.groupby(["Year", "Genre"]).size().reset_index(name="Count")
    
    fig_genre_year = px.bar(
        genre_year_counts,
        x="Year",
        y="Count",
        color="Genre",
        barmode="group",
        labels={"Count": "Number of Books"},
        color_discrete_map={"Fiction": "#1f77b4", "Non Fiction": "#ff7f0e"},
        template="plotly_white"
    )
    fig_genre_year.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_genre_year, use_container_width=True)

with col_chart2:
    st.subheader("💰 Average Price Trend ($)")
    yearly_price = filtered_df.groupby("Year")["Price"].mean().reset_index()
    
    fig_price_trend = px.line(
        yearly_price,
        x="Year",
        y="Price",
        markers=True,
        labels={"Price": "Avg Price ($)"},
        color_discrete_sequence=["#2ca02c"],
        template="plotly_white"
    )
    fig_price_trend.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_price_trend, use_container_width=True)

st.subheader("✍️ Top 10 Bestselling Authors")
top_authors_data = filtered_df["Author"].value_counts().head(10).reset_index()
top_authors_data.columns = ["Author", "Book Count"]

fig_authors = px.bar(
    top_authors_data,
    x="Book Count",
    y="Author",
    orientation="h",
    text="Book Count",
    color="Book Count",
    color_continuous_scale="Viridis",
    labels={"Book Count": "Bestsellers Count"},
    template="plotly_white"
)
fig_authors.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_authors, use_container_width=True)

st.divider()

# ==========================================
# TABLES & EXPORT
# ==========================================
st.header("📋 Filtered Dataset Explorer")

csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_amazon_bestsellers.csv",
    mime="text/csv"
)

st.dataframe(
    filtered_df[["Name", "Author", "Genre", "Sub-Genre", "User Rating", "Reviews", "Price", "Year"]],
    hide_index=True,
    use_container_width=True
)

st.markdown("""
    <div class="footer">
        <p>📚 <b>Amazon Best-Selling Books Analyzer</b> | Built with Python, Pandas & Streamlit</p>
    </div>
""", unsafe_allow_html=True)
