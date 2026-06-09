"""
Amazon Orders Dashboard - Streamlit App
Visualizes 100K Amazon orders (2020-2024) with interactive filters and charts.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Amazon Orders Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

_qs = st.query_params
_theme = str(_qs.get("theme", "dark")).lower()
IS_LIGHT = (_theme == "light")

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

/* ════════════════════════════════════════════════════════
   DARK MODE TOKENS  (default / prefers-color-scheme:dark)
   ════════════════════════════════════════════════════════ */
:root,
[data-theme="dark"],
html[data-theme="dark"] {
    --amazon-orange:   #FF9900;
    --amazon-navy:     #232F3E;
    --bg-page:         #0F1117;
    --bg-card:         #1A1D27;
    --bg-card-hover:   #1F2235;
    --bg-input:        rgba(255,255,255,0.07);
    --border:          rgba(255,153,0,0.15);
    --border-hover:    rgba(255,153,0,0.40);
    --text-primary:    #F0F2F8;
    --text-secondary:  #8B91A7;
    --text-muted:      #555B70;
    --shadow:          0 4px 24px rgba(0,0,0,0.40);
    --shadow-glow:     0 0 0 1px rgba(255,153,0,0.20), 0 8px 32px rgba(255,153,0,0.08);
    --sidebar-bg:      #232F3E;
    --sidebar-border:  rgba(255,153,0,0.15);
    --table-row-hover: #1F2235;
    --table-border:    rgba(255,255,255,0.04);
    --h1-gradient:     linear-gradient(135deg, #FF9900 0%, #FFC940 60%, #FFFFFF 100%);
    --scrollbar-track: #0F1117;
    --scrollbar-thumb: #232F3E;
    --radius:          12px;
    --radius-sm:       8px;
}

/* ════════════════════════════════════════════════════════
   LIGHT MODE TOKENS
   Covers: OS preference, Streamlit data-theme attr,
   and Streamlit's own .st-emotion-cache light class.
   ════════════════════════════════════════════════════════ */
@media (prefers-color-scheme: light) {
    :root {
        --bg-page:         #F5F7FA;
        --bg-card:         #FFFFFF;
        --bg-card-hover:   #FFF8EE;
        --bg-input:        #FFFFFF;
        --border:          rgba(255,153,0,0.25);
        --border-hover:    rgba(255,153,0,0.55);
        --text-primary:    #111827;
        --text-secondary:  #4B5563;
        --text-muted:      #9CA3AF;
        --shadow:          0 2px 12px rgba(0,0,0,0.08);
        --shadow-glow:     0 0 0 1px rgba(255,153,0,0.30), 0 6px 24px rgba(255,153,0,0.12);
        --sidebar-bg:      #232F3E;
        --sidebar-border:  rgba(255,153,0,0.20);
        --table-row-hover: #FFF8EE;
        --table-border:    rgba(0,0,0,0.06);
        --h1-gradient:     linear-gradient(135deg, #CC7700 0%, #FF9900 60%, #232F3E 100%);
        --scrollbar-track: #F5F7FA;
        --scrollbar-thumb: #D1D5DB;
    }
}

[data-theme="light"],
html[data-theme="light"] {
    --bg-page:         #F5F7FA;
    --bg-card:         #FFFFFF;
    --bg-card-hover:   #FFF8EE;
    --bg-input:        #FFFFFF;
    --border:          rgba(255,153,0,0.25);
    --border-hover:    rgba(255,153,0,0.55);
    --text-primary:    #111827;
    --text-secondary:  #4B5563;
    --text-muted:      #9CA3AF;
    --shadow:          0 2px 12px rgba(0,0,0,0.08);
    --shadow-glow:     0 0 0 1px rgba(255,153,0,0.30), 0 6px 24px rgba(255,153,0,0.12);
    --sidebar-bg:      #232F3E;
    --sidebar-border:  rgba(255,153,0,0.20);
    --table-row-hover: #FFF8EE;
    --table-border:    rgba(0,0,0,0.06);
    --h1-gradient:     linear-gradient(135deg, #CC7700 0%, #FF9900 60%, #232F3E 100%);
    --scrollbar-track: #F5F7FA;
    --scrollbar-thumb: #D1D5DB;
}

/* ── Full-page background ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar (always dark — Amazon navy — regardless of page theme) ── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-border) !important;
}
[data-testid="stSidebar"] * { color: #F0F2F8 !important; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: var(--amazon-orange) !important;
    color: #000 !important;
    border-radius: 4px;
    font-weight: 600;
    font-size: 11px;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"] {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,153,0,0.25) !important;
    border-radius: var(--radius-sm) !important;
    color: #F0F2F8 !important;
}
[data-testid="stSidebar"] .stDateInput input {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,153,0,0.25) !important;
    border-radius: var(--radius-sm) !important;
    color: #F0F2F8 !important;
}
            
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
    color: #8B91A7 !important;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Page title ── */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    background: var(--h1-gradient);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.03em;
    padding: 4px 0 !important;
}

/* ── Section headings ── */
h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
    font-size: 1.05rem !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 20px 18px !important;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-glow) !important;
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: var(--amazon-orange) !important;
    line-height: 1.2 !important;
}

/* ── Chart containers ── */
[data-testid="stPlotlyChart"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 8px !important;
    box-shadow: var(--shadow) !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stPlotlyChart"]:hover {
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-glow) !important;
}

/* ── Horizontal rule ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 24px 0 !important;
}

/* ── Expander (Raw Data) ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    font-size: 0.95rem !important;
}
[data-testid="stExpander"] summary:hover { color: var(--amazon-orange) !important; }

/* ── Dataframe / table ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden;
}
[data-testid="stDataFrame"] th {
    background: #232F3E !important;
    color: var(--amazon-orange) !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    font-size: 13px !important;
    border-bottom: 1px solid var(--table-border) !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: var(--table-row-hover) !important;
}

/* ── Text inputs (search boxes) ── */
[data-testid="stTextInput"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-size: 13px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--amazon-orange) !important;
    box-shadow: 0 0 0 2px rgba(255,153,0,0.20) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label { color: var(--text-primary) !important; }
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-style: italic;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--amazon-orange); }

/* ── Orange accent divider ── */
.accent-divider {
    height: 3px;
    background: linear-gradient(90deg, var(--amazon-orange), transparent);
    border-radius: 2px;
    margin: 4px 0 20px 0;
    width: 60px;
}

/* ── Section label pill ── */
.section-pill {
    display: inline-block;
    background: rgba(255,153,0,0.12);
    border: 1px solid rgba(255,153,0,0.30);
    color: var(--amazon-orange);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 8px;
}

/* ── Toast / info boxes ── */
[data-testid="stInfo"] {
    background: rgba(59,130,246,0.10) !important;
    border: 1px solid rgba(59,130,246,0.30) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}
</style>
""", unsafe_allow_html=True)



if IS_LIGHT:
    _FONT_COLOR    = "#4B5563"
    _GRID_COLOR    = "rgba(0,0,0,0.07)"
    _ZEROLINE      = "rgba(0,0,0,0.12)"
    _PLOT_BG       = "rgba(0,0,0,0)"
    _BAR_STROKE    = "#FFFFFF"
    _PIE_STROKE    = "#F5F7FA"
else:
    _FONT_COLOR    = "#8B91A7"
    _GRID_COLOR    = "rgba(255,255,255,0.05)"
    _ZEROLINE      = "rgba(255,255,255,0.08)"
    _PLOT_BG       = "rgba(0,0,0,0)"
    _BAR_STROKE    = "#1A1D27"
    _PIE_STROKE    = "#1A1D27"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=_PLOT_BG,
    font=dict(family="Inter, sans-serif", color=_FONT_COLOR, size=12),
    colorway=["#FF9900", "#3B82F6", "#22C55E", "#FACC15", "#EF4444", "#A855F7"],
)

_AXIS_BASE = dict(
    gridcolor=_GRID_COLOR,
    zerolinecolor=_ZEROLINE,
    tickfont=dict(color=_FONT_COLOR),
    title_font=dict(color=_FONT_COLOR),
)

_LEGEND_BASE = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=_FONT_COLOR))


@st.cache_data
def load_data():
    df = pd.read_csv(
        r"Amazon.csv",
        encoding="latin-1",
        on_bad_lines="skip",
    )
    cols = [
        "OrderID", "OrderDate", "CustomerID", "CustomerName",
        "ProductID", "ProductName", "Category", "Brand",
        "Quantity", "UnitPrice", "Discount", "Tax",
        "ShippingCost", "TotalAmount", "PaymentMethod",
        "OrderStatus", "City", "State", "Country", "SellerID",
    ]
    df = df[cols]
    df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")
    df = df.dropna(subset=["OrderDate"])
    df["Year"] = df["OrderDate"].dt.year
    df["Month"] = df["OrderDate"].dt.month
    df["YearMonth"] = df["OrderDate"].dt.to_period("M").astype(str)
    df["DayOfWeek"] = df["OrderDate"].dt.day_name()
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["Profit"] = df["Revenue"] - (df["Discount"] + df["Tax"] + df["ShippingCost"])
    return df


df = load_data()


st.sidebar.markdown(
    "<div style='padding:16px 0 8px;'>"
    "<span style='font-family:Space Grotesk,sans-serif;font-size:1.2rem;"
    "font-weight:700;color:#FF9900;letter-spacing:-0.02em;'>📦 Amazon</span>"
    "<span style='font-family:Space Grotesk,sans-serif;font-size:1.2rem;"
    "font-weight:300;color:#8B91A7;'> Dashboard</span>"
    "</div>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

min_date = df["OrderDate"].min().date()
max_date = df["OrderDate"].max().date()
date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

all_categories = sorted(df["Category"].unique())
selected_categories = st.sidebar.multiselect("📂 Categories", all_categories, default=all_categories)

all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect("🌍 Countries", all_countries, default=all_countries)

all_statuses = sorted(df["OrderStatus"].unique())
selected_statuses = st.sidebar.multiselect("📋 Order Status", all_statuses, default=all_statuses)

filtered = df[
    (df["OrderDate"].dt.date >= date_range[0])
    & (df["OrderDate"].dt.date <= date_range[1])
    & (df["Category"].isin(selected_categories))
    & (df["Country"].isin(selected_countries))
    & (df["OrderStatus"].isin(selected_statuses))
]


st.title("📦 Amazon Orders Analytics Dashboard")
st.markdown("---")


st.markdown("<div class='section-pill'>Overview</div>", unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("💰 Total Revenue", f"${filtered['TotalAmount'].sum():,.0f}")
with col2:
    st.metric("📋 Total Orders", f"{len(filtered):,}")
with col3:
    st.metric("🧾 Avg Order Value", f"${filtered['TotalAmount'].mean():,.2f}")
with col4:
    st.metric("👤 Unique Customers", f"{filtered['CustomerID'].nunique():,}")
with col5:
    st.metric("📦 Avg Items/Order", f"{filtered['Quantity'].mean():.1f}")
with col6:
    delivered_pct = (
        len(filtered[filtered["OrderStatus"] == "Delivered"]) / len(filtered) * 100
        if len(filtered) > 0 else 0
    )
    st.metric("✅ Delivery Rate", f"{delivered_pct:.1f}%")

st.markdown("---")


st.markdown("<div class='section-pill'>Time Series</div>", unsafe_allow_html=True)
row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    st.subheader("📈 Revenue & Orders Trend (Monthly)")
    monthly = (
        filtered.groupby("YearMonth")
        .agg(Revenue=("TotalAmount", "sum"), Orders=("OrderID", "count"))
        .reset_index()
        .sort_values("YearMonth")
    )
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(
        go.Scatter(
            x=monthly["YearMonth"], y=monthly["Revenue"],
            name="Revenue ($)", mode="lines+markers",
            line=dict(color="#FF9900", width=2.5),
            marker=dict(size=5, color="#FF9900"),
            fill="tozeroy",
            fillcolor="rgba(255,153,0,0.07)",
        ),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Bar(
            x=monthly["YearMonth"], y=monthly["Orders"],
            name="Orders", marker_color="rgba(59,130,246,0.45)",
            marker_line_color="rgba(59,130,246,0.80)",
            marker_line_width=1,
        ),
        secondary_y=True,
    )
    fig_trend.update_layout(
        **PLOTLY_LAYOUT,
        height=400, hovermode="x unified",
        legend=dict(**_LEGEND_BASE, orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=_AXIS_BASE,
    )
    fig_trend.update_yaxes(title_text="Revenue ($)", secondary_y=False,
                           gridcolor=_GRID_COLOR, tickfont=dict(color=_FONT_COLOR))
    fig_trend.update_yaxes(title_text="Order Count", secondary_y=True,
                           gridcolor=_GRID_COLOR, tickfont=dict(color=_FONT_COLOR))
    st.plotly_chart(fig_trend, use_container_width=True)

with row1_col2:
    st.subheader("📋 Order Status")
    status_counts = filtered["OrderStatus"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    colors_map = {
        "Delivered": "#22C55E", "Shipped": "#3B82F6", "Pending": "#FACC15",
        "Returned": "#EF4444", "Cancelled": "#6B7280",
    }
    fig_status = px.pie(
        status_counts, names="Status", values="Count", hole=0.5,
        color="Status",
        color_discrete_map={s: colors_map.get(s, "#999") for s in status_counts["Status"]},
    )
    fig_status.update_traces(textinfo="percent+label", textfont_size=11,
                             marker=dict(line=dict(color=_PIE_STROKE, width=2)))
    fig_status.update_layout(**PLOTLY_LAYOUT, legend=_LEGEND_BASE, height=400, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")


st.markdown("<div class='section-pill'>Breakdown</div>", unsafe_allow_html=True)
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("📂 Revenue by Category")
    cat_rev = (
        filtered.groupby("Category")["TotalAmount"]
        .sum().sort_values(ascending=True).reset_index()
    )
    _cat_scale = [[0, "#E8F0FE"], [0.5, "#FF6600"], [1, "#FF9900"]] if IS_LIGHT else [[0, "#232F3E"], [0.5, "#FF6600"], [1, "#FF9900"]]
    fig_cat = px.bar(
        cat_rev, x="TotalAmount", y="Category", orientation="h",
        color="TotalAmount", text_auto=".2s",
        color_continuous_scale=_cat_scale,
    )
    fig_cat.update_traces(textfont=dict(color="#111827" if IS_LIGHT else "#F0F2F8", size=11))
    fig_cat.update_layout(
        **PLOTLY_LAYOUT, height=400, showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(**_AXIS_BASE, title="Total Revenue ($)"),
        yaxis=_AXIS_BASE,
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with row2_col2:
    st.subheader("🌍 Revenue by Country")
    country_rev = (
        filtered.groupby("Country")["TotalAmount"]
        .sum().sort_values(ascending=True).reset_index()
    )
    _country_scale = [[0, "#EFF6FF"], [0.5, "#3B5BDB"], [1, "#4DABF7"]] if IS_LIGHT else [[0, "#232F3E"], [0.5, "#3B5BDB"], [1, "#4DABF7"]]
    fig_country = px.bar(
        country_rev, x="TotalAmount", y="Country", orientation="h",
        color="TotalAmount", text_auto=".2s",
        color_continuous_scale=_country_scale,
    )
    fig_country.update_traces(textfont=dict(color="#111827" if IS_LIGHT else "#F0F2F8", size=11))
    fig_country.update_layout(
        **PLOTLY_LAYOUT, height=400, showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(**_AXIS_BASE, title="Total Revenue ($)"),
        yaxis=_AXIS_BASE,
    )
    st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")


st.markdown("<div class='section-pill'>Products & Payments</div>", unsafe_allow_html=True)
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("💳 Payment Methods")
    pay_counts = filtered["PaymentMethod"].value_counts().reset_index()
    pay_counts.columns = ["Method", "Count"]
    fig_pay = px.pie(
        pay_counts, names="Method", values="Count", hole=0.5,
        color_discrete_sequence=["#FF9900", "#3B82F6", "#22C55E", "#FACC15", "#A855F7"],
    )
    fig_pay.update_traces(textinfo="percent+label", textfont_size=11,
                          marker=dict(line=dict(color=_PIE_STROKE, width=2)))
    fig_pay.update_layout(**PLOTLY_LAYOUT, legend=_LEGEND_BASE, height=400, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_pay, use_container_width=True)

with row3_col2:
    st.subheader("🏷️ Top 10 Products by Revenue")
    top_products = (
        filtered.groupby("ProductName")["TotalAmount"]
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    _prod_scale = [[0, "#FEF3C7"], [0.5, "#EA580C"], [1, "#FF9900"]] if IS_LIGHT else [[0, "#7C2D12"], [0.5, "#EA580C"], [1, "#FF9900"]]
    fig_prod = px.bar(
        top_products, x="TotalAmount", y="ProductName", orientation="h",
        color="TotalAmount", text_auto=".2s",
        color_continuous_scale=_prod_scale,
    )
    fig_prod.update_traces(textfont=dict(color="#111827" if IS_LIGHT else "#F0F2F8", size=11))
    fig_prod.update_layout(
        **PLOTLY_LAYOUT, height=400, showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(**_AXIS_BASE, title="Revenue ($)"),
        yaxis=dict(**_AXIS_BASE, categoryorder="total ascending"),
    )
    st.plotly_chart(fig_prod, use_container_width=True)

st.markdown("---")


st.markdown("<div class='section-pill'>Geography & Brand</div>", unsafe_allow_html=True)
row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    st.subheader("🗺️ Revenue by US State")
    us_data = filtered[filtered["Country"] == "United States"]
    state_rev = us_data.groupby("State")["TotalAmount"].sum().reset_index()
    _choro_scale = [[0, "#E8F4FD"], [0.4, "#FDBA74"], [1, "#FF9900"]] if IS_LIGHT else [[0, "#131921"], [0.4, "#7C3700"], [1, "#FF9900"]]
    fig_state = px.choropleth(
        state_rev, locations="State", locationmode="USA-states",
        color="TotalAmount", scope="usa",
        color_continuous_scale=_choro_scale,
        labels={"TotalAmount": "Revenue ($)"},
    )
    _geo_land  = "#E5E7EB" if IS_LIGHT else "#1A1D27"
    _geo_lake  = "#DBEAFE" if IS_LIGHT else "#131921"
    _geo_sub   = "#9CA3AF" if IS_LIGHT else "#232F3E"
    fig_state.update_layout(
        **PLOTLY_LAYOUT,
        height=400, margin=dict(l=10, r=10, t=10, b=10),
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor=_geo_lake,
                 landcolor=_geo_land, subunitcolor=_geo_sub),
        coloraxis_colorbar=dict(tickfont=dict(color=_FONT_COLOR),
                                title=dict(text="Revenue", font=dict(color=_FONT_COLOR))),
    )
    st.plotly_chart(fig_state, use_container_width=True)

with row4_col2:
    st.subheader("🏭 Revenue by Brand")
    brand_rev = (
        filtered.groupby("Brand")["TotalAmount"]
        .sum().sort_values(ascending=True).reset_index()
    )
    _brand_scale = [[0, "#EFF6FF"], [0.5, "#2563EB"], [1, "#60A5FA"]] if IS_LIGHT else [[0, "#1E3A5F"], [0.5, "#2563EB"], [1, "#60A5FA"]]
    fig_brand = px.bar(
        brand_rev, x="TotalAmount", y="Brand", orientation="h",
        color="TotalAmount", text_auto=".2s",
        color_continuous_scale=_brand_scale,
    )
    fig_brand.update_traces(textfont=dict(color="#111827" if IS_LIGHT else "#F0F2F8", size=11))
    fig_brand.update_layout(
        **PLOTLY_LAYOUT, height=400, showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(**_AXIS_BASE, title="Total Revenue ($)"),
        yaxis=_AXIS_BASE,
    )
    st.plotly_chart(fig_brand, use_container_width=True)

st.markdown("---")


st.markdown("<div class='section-pill'>Discount Analysis</div>", unsafe_allow_html=True)
st.subheader("🏷️ Discount Impact Analysis")
disc_cat = (
    filtered.groupby("Category")
    .agg(
        Avg_Discount=("Discount", "mean"),
        Total_Revenue=("TotalAmount", "sum"),
        Order_Count=("OrderID", "count"),
    )
    .reset_index()
)
fig_disc = px.scatter(
    disc_cat, x="Avg_Discount", y="Total_Revenue",
    size="Order_Count", color="Category",
    text="Category", size_max=55,
    color_discrete_sequence=["#FF9900", "#3B82F6", "#22C55E", "#FACC15",
                              "#EF4444", "#A855F7", "#06B6D4", "#F97316"],
)
fig_disc.update_traces(
    textposition="top center",
    textfont=dict(color=_FONT_COLOR, size=11),
    marker=dict(line=dict(color=_BAR_STROKE, width=1.5)),
)
fig_disc.update_layout(
    **PLOTLY_LAYOUT,
    legend=_LEGEND_BASE,
    xaxis=_AXIS_BASE,
    yaxis=_AXIS_BASE,
    height=440,
    margin=dict(l=20, r=20, t=40, b=20),
    title=dict(
        text="Category: Avg Discount vs Total Revenue  (bubble size = order volume)",
        font=dict(color=_FONT_COLOR, size=12),
        x=0,
    ),
)
st.plotly_chart(fig_disc, use_container_width=True)

st.markdown("---")


with st.expander("🔍 Raw Data Explorer", expanded=False):
    st.subheader("Filter & Explore Raw Data")

    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        search_product = st.text_input("🔎 Search Product Name", "")
    with ec2:
        search_city = st.text_input("🏙️ Search City", "")
    with ec3:
        sort_col = st.selectbox("Sort By", ["OrderDate", "TotalAmount", "Quantity", "Category"])
    with ec4:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

    explorer_df = filtered.copy()
    if search_product:
        explorer_df = explorer_df[
            explorer_df["ProductName"].str.contains(search_product, case=False, na=False)
        ]
    if search_city:
        explorer_df = explorer_df[
            explorer_df["City"].str.contains(search_city, case=False, na=False)
        ]

    explorer_df = explorer_df.sort_values(
        sort_col, ascending=(sort_order == "Ascending")
    ).head(500)

    st.dataframe(
        explorer_df[[
            "OrderID", "OrderDate", "CustomerName", "ProductName",
            "Category", "Quantity", "UnitPrice", "TotalAmount",
            "PaymentMethod", "OrderStatus", "City", "Country",
        ]],
        use_container_width=True,
        hide_index=True,
        height=420,
    )
    st.caption(f"Showing up to 500 of {len(filtered):,} filtered records")
