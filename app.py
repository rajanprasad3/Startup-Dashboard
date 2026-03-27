import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="Startup Funding Analysis",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #2e3250;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label { color: #8b92b8 !important; font-size: 13px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e0e4ff !important; font-size: 26px !important; font-weight: 700 !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12151f 0%, #1a1d2e 100%);
        border-right: 1px solid #2e3250;
    }
    .section-header {
        background: linear-gradient(90deg, #1e2130, #252840);
        border-left: 4px solid #6c7ae0;
        border-radius: 0 8px 8px 0;
        padding: 10px 16px;
        margin: 20px 0 12px 0;
        color: #c8ccee;
        font-size: 16px;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1d2e; border-radius: 10px; padding: 4px; gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; color: #8b92b8; font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6c7ae0, #4c5ec7) !important;
        color: white !important;
    }
    hr { border-color: #2e3250; }
    h1, h2, h3 { color: #d0d4f0 !important; }
    p, li { color: #9ba3c8; }
</style>
""", unsafe_allow_html=True)


# Load Data
@st.cache_data
def load_data():
    data = pd.read_csv("cleaned_data.csv")
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['Amount_in_Cr'] = pd.to_numeric(data['Amount_in_Cr'], errors='coerce')

    round_map = {
        'seed round': 'Seed',
        'seed funding': 'Seed',
        'seed': 'Seed',
        'seed funding round': 'Seed',
        'seed\nfunding': 'Seed',
        'seed/ angel funding': 'Seed/Angel',
        'seed / angel funding': 'Seed/Angel',
        'seed/angel funding': 'Seed/Angel',
        'seed / angle funding': 'Seed/Angel',
        'angel / seed funding': 'Seed/Angel',
        'angel round': 'Angel',
        'angel': 'Angel',
        'pre-series a': 'Pre-Series A',
        'pre series a': 'Pre-Series A',
        'privateequity': 'Private Equity',
        'private equity round': 'Private Equity',
        'private equity': 'Private Equity',
        'private\nequity': 'Private Equity',
        'debt funding': 'Debt Funding',
        'debt-funding': 'Debt Funding',
        'debt and preference capital': 'Debt Funding',
        'funding round': 'Funding Round',
        'venture round': 'Venture Round',
        'venture - series unknown': 'Venture Round',
        'crowd funding': 'Crowd Funding',
        'crowdfunding': 'Crowd Funding',
    }
    data['round_clean'] = data['round'].str.lower().str.strip().map(round_map)
    data['round_clean'] = data['round_clean'].fillna(data['round'])
    return data


main_df = load_data()

# Sidebar
with st.sidebar:
    st.markdown("## 🚀 Startup Funding")
    st.markdown("---")

    page = st.selectbox("📌 Select View", [
        "📊 Overview Dashboard",
        "🏢 Startup Analysis",
        "👥 Investor Analysis",
        "🌍 City Analysis",
        "📈 Trend Analysis",
        "🔍 Raw Data Explorer"
    ])

    st.markdown("---")
    st.markdown("### 🎛️ Filters")

    years = sorted(main_df['year'].dropna().unique().astype(int).tolist(), reverse=True)
    selected_years = st.multiselect("📅 Year", years, default=years)

    verticals = sorted(main_df['vertical'].dropna().unique().tolist())
    selected_verticals = st.multiselect("🏭 Vertical (Industry)", verticals[:10],
                                        placeholder="All industries")

    cities = sorted(main_df['city'].dropna().unique().tolist())
    selected_cities = st.multiselect("🏙️ City", cities, placeholder="All cities")

    st.markdown("---")
    st.caption("Data: Indian Startup Funding 2015-2020")

# Apply Filters
fdf = main_df[main_df['year'].isin(selected_years)] if selected_years else main_df.copy()
if selected_verticals:
    fdf = fdf[fdf['vertical'].isin(selected_verticals)]
if selected_cities:
    fdf = fdf[fdf['city'].isin(selected_cities)]

# Plotly theme constants
PLOT_BG  = "#12151f"
PAPER_BG = "#1a1d2e"
GRID_CLR = "#2a2e45"
FONT_CLR = "#c0c6e8"
PALETTE  = px.colors.qualitative.Plotly


def style_fig(chart, height=380):
    chart.update_layout(
        height=height,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_CLR, family="Inter, sans-serif", size=12),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_CLR)),
        xaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(color=FONT_CLR)),
        yaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(color=FONT_CLR)),
    )
    return chart


# ==============================================================================
# PAGE 1 — OVERVIEW DASHBOARD
# ==============================================================================
if page == "📊 Overview Dashboard":
    st.title("📊 Overview Dashboard")
    st.caption(f"Showing {len(fdf):,} deals after filters")

    total_funding   = fdf['Amount_in_Cr'].sum()
    avg_deal        = fdf['Amount_in_Cr'].mean()
    total_deals     = len(fdf)
    uniq_startups   = fdf['startup'].nunique()
    uniq_investors  = fdf['investor'].nunique()
    uniq_cities     = fdf['city'].nunique()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Funding (Cr)", f"Rs {total_funding:,.0f}")
    c2.metric("Total Deals", f"{total_deals:,}")
    c3.metric("Startups", f"{uniq_startups:,}")
    c4.metric("Investors", f"{uniq_investors:,}")
    c5.metric("Cities", f"{uniq_cities:,}")
    c6.metric("Avg Deal (Cr)", f"Rs {avg_deal:,.1f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">Funding by Year</div>', unsafe_allow_html=True)
        yearly = fdf.groupby('year')['Amount_in_Cr'].sum().reset_index()
        chart1 = px.bar(yearly, x='year', y='Amount_in_Cr',
                        color='Amount_in_Cr', color_continuous_scale='Blues',
                        labels={'Amount_in_Cr': 'Funding (Cr)', 'year': 'Year'})
        chart1.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(chart1), use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Deals by Funding Round</div>', unsafe_allow_html=True)
        round_count = fdf['round_clean'].value_counts().head(10).reset_index()
        round_count.columns = ['Round', 'Count']
        chart2 = px.pie(round_count, names='Round', values='Count',
                        hole=0.45, color_discrete_sequence=PALETTE)
        chart2.update_traces(textinfo='percent+label', textfont_size=11)
        st.plotly_chart(style_fig(chart2), use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-header">Top 10 Verticals by Funding</div>', unsafe_allow_html=True)
        top_vert = fdf.groupby('vertical')['Amount_in_Cr'].sum().nlargest(10).reset_index()
        chart3 = px.bar(top_vert, x='Amount_in_Cr', y='vertical', orientation='h',
                        color='Amount_in_Cr', color_continuous_scale='Purples',
                        labels={'Amount_in_Cr': 'Funding (Cr)', 'vertical': ''})
        chart3.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(style_fig(chart3, 420), use_container_width=True)

    with col_d:
        st.markdown('<div class="section-header">Top 10 Cities by Deals</div>', unsafe_allow_html=True)
        top_city = fdf['city'].value_counts().head(10).reset_index()
        top_city.columns = ['City', 'Deals']
        chart4 = px.bar(top_city, x='Deals', y='City', orientation='h',
                        color='Deals', color_continuous_scale='Teal',
                        labels={'City': ''})
        chart4.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(style_fig(chart4, 420), use_container_width=True)


# ==============================================================================
# PAGE 2 — STARTUP ANALYSIS
# ==============================================================================
elif page == "🏢 Startup Analysis":
    st.title("🏢 Startup Analysis")

    tab1, tab2 = st.tabs(["Top Startups", "Individual Startup"])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-header">Top 15 by Total Funding</div>', unsafe_allow_html=True)
            top_by_fund = fdf.groupby('startup')['Amount_in_Cr'].sum().nlargest(15).reset_index()
            chart1 = px.bar(top_by_fund, x='Amount_in_Cr', y='startup', orientation='h',
                            color='Amount_in_Cr', color_continuous_scale='Viridis',
                            labels={'Amount_in_Cr': 'Total Funding (Cr)', 'startup': ''})
            chart1.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(style_fig(chart1, 500), use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">Top 15 by Number of Deals</div>', unsafe_allow_html=True)
            top_by_deals = fdf['startup'].value_counts().head(15).reset_index()
            top_by_deals.columns = ['Startup', 'Deals']
            chart2 = px.bar(top_by_deals, x='Deals', y='Startup', orientation='h',
                            color='Deals', color_continuous_scale='Magma',
                            labels={'Startup': ''})
            chart2.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(style_fig(chart2, 500), use_container_width=True)

        st.markdown('<div class="section-header">Vertical Distribution of Deals</div>', unsafe_allow_html=True)
        vert_dist = fdf['vertical'].value_counts().head(15).reset_index()
        vert_dist.columns = ['Vertical', 'Deals']
        chart3 = px.treemap(vert_dist, path=['Vertical'], values='Deals',
                            color='Deals', color_continuous_scale='RdBu')
        st.plotly_chart(style_fig(chart3, 400), use_container_width=True)

    with tab2:
        startup_list = sorted(fdf['startup'].dropna().unique().tolist())
        sel_startup = st.selectbox("Select a Startup", startup_list)

        startup_df = fdf[fdf['startup'] == sel_startup]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Raised (Cr)", f"Rs {startup_df['Amount_in_Cr'].sum():,.1f}")
        m2.metric("Funding Rounds", str(len(startup_df)))
        m3.metric("Vertical", startup_df['vertical'].mode()[0] if not startup_df['vertical'].isna().all() else "N/A")
        m4.metric("City", startup_df['city'].mode()[0] if not startup_df['city'].isna().all() else "N/A")

        st.markdown('<div class="section-header">Funding Timeline</div>', unsafe_allow_html=True)
        startup_sorted = startup_df.sort_values('date')
        chart4 = px.scatter(startup_sorted, x='date', y='Amount_in_Cr',
                            size='Amount_in_Cr', color='round_clean',
                            hover_data=['investor', 'round'],
                            labels={'Amount_in_Cr': 'Amount (Cr)', 'date': 'Date', 'round_clean': 'Round'})
        chart4.update_traces(marker=dict(line=dict(width=1, color='white')))
        st.plotly_chart(style_fig(chart4, 350), use_container_width=True)

        st.markdown('<div class="section-header">All Deals</div>', unsafe_allow_html=True)
        st.dataframe(
            startup_df[['date', 'round', 'Amount_in_Cr', 'investor', 'city']].sort_values('date', ascending=False),
            use_container_width=True, hide_index=True
        )


# ==============================================================================
# PAGE 3 — INVESTOR ANALYSIS
# ==============================================================================
elif page == "👥 Investor Analysis":
    st.title("👥 Investor Analysis")

    inv_df = fdf.copy()
    inv_df['investor'] = inv_df['investor'].str.split(',')
    inv_df = inv_df.explode('investor')
    inv_df['investor'] = inv_df['investor'].str.strip()
    inv_df = inv_df[inv_df['investor'].notna() & (inv_df['investor'] != '')]

    tab1, tab2 = st.tabs(["Top Investors", "Individual Investor"])

    with tab1:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-header">Most Active Investors (by deals)</div>', unsafe_allow_html=True)
            top_inv = inv_df['investor'].value_counts().head(15).reset_index()
            top_inv.columns = ['Investor', 'Deals']
            chart1 = px.bar(top_inv, x='Deals', y='Investor', orientation='h',
                            color='Deals', color_continuous_scale='Blues',
                            labels={'Investor': ''})
            chart1.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(style_fig(chart1, 500), use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">Top Investors by Funding (Cr)</div>', unsafe_allow_html=True)
            top_inv_amt = inv_df.groupby('investor')['Amount_in_Cr'].sum().nlargest(15).reset_index()
            chart2 = px.bar(top_inv_amt, x='Amount_in_Cr', y='investor', orientation='h',
                            color='Amount_in_Cr', color_continuous_scale='Oranges',
                            labels={'Amount_in_Cr': 'Total Invested (Cr)', 'investor': ''})
            chart2.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(style_fig(chart2, 500), use_container_width=True)

        st.markdown('<div class="section-header">Investor Sector Preferences (Top 10 investors)</div>', unsafe_allow_html=True)
        top10_inv = inv_df['investor'].value_counts().head(10).index.tolist()
        heat_data = inv_df[inv_df['investor'].isin(top10_inv)]
        heat_pivot = heat_data.groupby(['investor', 'vertical'])['Amount_in_Cr'].sum().unstack(fill_value=0)
        top_verts = heat_pivot.sum().nlargest(10).index
        heat_pivot = heat_pivot[top_verts]
        chart3 = px.imshow(heat_pivot, color_continuous_scale='YlOrRd',
                           labels=dict(x='Vertical', y='Investor', color='Amount (Cr)'),
                           aspect='auto')
        st.plotly_chart(style_fig(chart3, 420), use_container_width=True)

    with tab2:
        inv_list = sorted(inv_df['investor'].dropna().unique().tolist())
        sel_inv = st.selectbox("Select an Investor", inv_list)

        inv_detail = inv_df[inv_df['investor'] == sel_inv]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Invested (Cr)", f"Rs {inv_detail['Amount_in_Cr'].sum():,.1f}")
        m2.metric("Total Deals", str(len(inv_detail)))
        m3.metric("Startups Backed", str(inv_detail['startup'].nunique()))
        m4.metric("Fav Round", inv_detail['round_clean'].mode()[0] if not inv_detail['round_clean'].isna().all() else "N/A")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-header">Sectors Invested In</div>', unsafe_allow_html=True)
            sec_data = inv_detail['vertical'].value_counts().head(8).reset_index()
            sec_data.columns = ['Vertical', 'Deals']
            chart4 = px.pie(sec_data, names='Vertical', values='Deals', hole=0.4,
                            color_discrete_sequence=PALETTE)
            st.plotly_chart(style_fig(chart4, 350), use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">Investment Over Time</div>', unsafe_allow_html=True)
            yr_data = inv_detail.groupby('year')['Amount_in_Cr'].sum().reset_index()
            chart5 = px.line(yr_data, x='year', y='Amount_in_Cr', markers=True,
                             labels={'Amount_in_Cr': 'Amount (Cr)', 'year': 'Year'})
            chart5.update_traces(line_color='#6c7ae0', marker=dict(size=8, color='#a0a8ff'))
            st.plotly_chart(style_fig(chart5, 350), use_container_width=True)

        st.markdown('<div class="section-header">Portfolio</div>', unsafe_allow_html=True)
        st.dataframe(
            inv_detail[['date', 'startup', 'vertical', 'city', 'round', 'Amount_in_Cr']].sort_values('date', ascending=False),
            use_container_width=True, hide_index=True
        )


# ==============================================================================
# PAGE 4 — CITY ANALYSIS
# ==============================================================================
elif page == "🌍 City Analysis":
    st.title("🌍 City Analysis")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">Top Cities by Total Funding</div>', unsafe_allow_html=True)
        city_fund = fdf.groupby('city')['Amount_in_Cr'].sum().nlargest(15).reset_index()
        chart1 = px.bar(city_fund, x='Amount_in_Cr', y='city', orientation='h',
                        color='Amount_in_Cr', color_continuous_scale='Teal',
                        labels={'Amount_in_Cr': 'Funding (Cr)', 'city': ''})
        chart1.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(style_fig(chart1, 480), use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Top Cities by Number of Deals</div>', unsafe_allow_html=True)
        city_deals = fdf['city'].value_counts().head(15).reset_index()
        city_deals.columns = ['City', 'Deals']
        chart2 = px.bar(city_deals, x='Deals', y='City', orientation='h',
                        color='Deals', color_continuous_scale='Mint',
                        labels={'City': ''})
        chart2.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(style_fig(chart2, 480), use_container_width=True)

    st.markdown('<div class="section-header">Top Sectors per City (Top 8 cities)</div>', unsafe_allow_html=True)
    top8_cities = fdf['city'].value_counts().head(8).index.tolist()
    city_vert = fdf[fdf['city'].isin(top8_cities)].groupby(['city', 'vertical'])['Amount_in_Cr'].sum().reset_index()
    city_vert = city_vert.sort_values('Amount_in_Cr', ascending=False).groupby('city').head(5)
    chart3 = px.bar(city_vert, x='city', y='Amount_in_Cr', color='vertical',
                    barmode='stack',
                    labels={'Amount_in_Cr': 'Funding (Cr)', 'city': 'City', 'vertical': 'Vertical'})
    st.plotly_chart(style_fig(chart3, 420), use_container_width=True)

    st.markdown('<div class="section-header">City Deep Dive</div>', unsafe_allow_html=True)
    sel_city = st.selectbox("Select City", sorted(fdf['city'].dropna().unique().tolist()))
    city_detail = fdf[fdf['city'] == sel_city]

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Funding (Cr)", f"Rs {city_detail['Amount_in_Cr'].sum():,.1f}")
    m2.metric("Deals", str(len(city_detail)))
    m3.metric("Startups", str(city_detail['startup'].nunique()))

    col_c, col_d = st.columns(2)
    with col_c:
        city_top_s = city_detail['startup'].value_counts().head(8).reset_index()
        city_top_s.columns = ['Startup', 'Deals']
        chart4 = px.bar(city_top_s, x='Deals', y='Startup', orientation='h',
                        title="Top Startups", color='Deals', color_continuous_scale='Blues',
                        labels={'Startup': ''})
        chart4.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(style_fig(chart4, 350), use_container_width=True)
    with col_d:
        city_top_v = city_detail['vertical'].value_counts().head(8).reset_index()
        city_top_v.columns = ['Vertical', 'Count']
        chart5 = px.pie(city_top_v, names='Vertical', values='Count', hole=0.4,
                        title="Sectors", color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(chart5, 350), use_container_width=True)


# ==============================================================================
# PAGE 5 — TREND ANALYSIS
# ==============================================================================
elif page == "📈 Trend Analysis":
    st.title("📈 Trend Analysis")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">Monthly Funding Over Years</div>', unsafe_allow_html=True)
        monthly = fdf.groupby(['year', 'month'])['Amount_in_Cr'].sum().reset_index()
        monthly['period'] = monthly['year'].astype(str) + '-' + monthly['month'].astype(str).str.zfill(2)
        monthly = monthly.sort_values('period')
        chart1 = px.line(monthly, x='period', y='Amount_in_Cr', color='year',
                         markers=False, labels={'Amount_in_Cr': 'Funding (Cr)', 'period': 'Month'})
        chart1.update_xaxes(tickangle=45)
        st.plotly_chart(style_fig(chart1, 380), use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Round Type Trends by Year</div>', unsafe_allow_html=True)
        round_year = fdf.groupby(['year', 'round_clean']).size().reset_index(name='Deals')
        top_rounds = fdf['round_clean'].value_counts().head(6).index.tolist()
        round_year = round_year[round_year['round_clean'].isin(top_rounds)]
        chart2 = px.line(round_year, x='year', y='Deals', color='round_clean',
                         markers=True, labels={'round_clean': 'Round', 'year': 'Year'})
        st.plotly_chart(style_fig(chart2, 380), use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-header">Deal Size Distribution</div>', unsafe_allow_html=True)
        chart3 = px.histogram(fdf[fdf['Amount_in_Cr'] < 500], x='Amount_in_Cr',
                              nbins=50, color_discrete_sequence=['#6c7ae0'],
                              labels={'Amount_in_Cr': 'Deal Size (Cr)', 'count': 'Deals'})
        chart3.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(chart3, 350), use_container_width=True)

    with col_d:
        st.markdown('<div class="section-header">Avg Deal Size by Year</div>', unsafe_allow_html=True)
        avg_year = fdf.groupby('year')['Amount_in_Cr'].mean().reset_index()
        chart4 = px.area(avg_year, x='year', y='Amount_in_Cr',
                         color_discrete_sequence=['#6c7ae0'],
                         labels={'Amount_in_Cr': 'Avg Deal (Cr)', 'year': 'Year'})
        chart4.update_traces(fill='tozeroy', line_color='#a0a8ff')
        st.plotly_chart(style_fig(chart4, 350), use_container_width=True)

    st.markdown('<div class="section-header">Emerging Verticals (Year-over-Year)</div>', unsafe_allow_html=True)
    vert_year = fdf.groupby(['year', 'vertical']).size().reset_index(name='Deals')
    top15v = fdf['vertical'].value_counts().head(15).index.tolist()
    vert_year = vert_year[vert_year['vertical'].isin(top15v)]
    chart5 = px.line(vert_year, x='year', y='Deals', color='vertical',
                     markers=True, labels={'vertical': 'Vertical', 'year': 'Year'})
    st.plotly_chart(style_fig(chart5, 420), use_container_width=True)


# ==============================================================================
# PAGE 6 — RAW DATA EXPLORER
# ==============================================================================
elif page == "🔍 Raw Data Explorer":
    st.title("🔍 Raw Data Explorer")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        search = st.text_input("Search startup / investor", "")
    with col_b:
        round_filter = st.multiselect("Round", sorted(fdf['round_clean'].dropna().unique().tolist()))
    with col_c:
        amount_range = st.slider(
            "Amount Range (Cr)",
            float(fdf['Amount_in_Cr'].min()),
            float(fdf['Amount_in_Cr'].max()),
            (float(fdf['Amount_in_Cr'].min()), float(fdf['Amount_in_Cr'].max()))
        )

    display_df = fdf.copy()
    if search:
        mask = (
            display_df['startup'].str.contains(search, case=False, na=False) |
            display_df['investor'].str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]
    if round_filter:
        display_df = display_df[display_df['round_clean'].isin(round_filter)]
    display_df = display_df[
        (display_df['Amount_in_Cr'] >= amount_range[0]) &
        (display_df['Amount_in_Cr'] <= amount_range[1])
    ]

    st.caption(f"Showing {len(display_df):,} records")
    st.dataframe(
        display_df[['date', 'startup', 'vertical', 'subvertical', 'city', 'investor', 'round', 'Amount_in_Cr']]
        .sort_values('date', ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=520
    )

    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data as CSV", csv_data, "filtered_data.csv", "text/csv")