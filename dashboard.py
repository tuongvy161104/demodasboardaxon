import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────
if "spend_filter" not in st.session_state:
    st.session_state.spend_filter = None   # str | None: "Under-spent" / "Scale Signal" / "Scaling"

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Axon Ads Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Light background */
.stApp {
    background: linear-gradient(145deg, #f0f4ff 0%, #fafbff 50%, #f5f0ff 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f5f3ff 100%);
    border-right: 1px solid rgba(99, 102, 241, 0.15);
    box-shadow: 2px 0 12px rgba(99, 102, 241, 0.06);
}

/* KPI Cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(99, 102, 241, 0.08);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
    border-radius: 16px 16px 0 0;
}

.kpi-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(99, 102, 241, 0.15);
}

.kpi-label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: #1e1b4b;
    line-height: 1.2;
}

.kpi-sub {
    font-size: 12px;
    color: #9ca3af;
    margin-top: 4px;
}

/* ROAS Cards */
.roas-card-green {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(16, 185, 129, 0.1);
}

.roas-card-green::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #10b981, #34d399);
}

.roas-card-red {
    background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(239, 68, 68, 0.1);
}

.roas-card-red::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #ef4444, #f87171);
}

.roas-big-number {
    font-size: 52px;
    font-weight: 800;
    line-height: 1;
    margin: 8px 0;
}

.roas-label {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* Section headers */
.section-header {
    font-size: 16px;
    font-weight: 700;
    color: #312e81;
    letter-spacing: 0.5px;
    margin: 24px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.35), transparent);
    margin-left: 12px;
}

/* Hide streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Plotly chart wrapper */
.js-plotly-plot {
    border-radius: 12px;
}

/* Streamlit metric override */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 6px rgba(99,102,241,0.06);
}

/* Expander light */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 12px;
}

/* File uploader */
.uploadedFile {
    background: rgba(99, 102, 241, 0.05) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────
def format_number(n, prefix="", suffix="", decimals=0):
    """Format large numbers nicely."""
    if pd.isna(n):
        return "N/A"
    if abs(n) >= 1_000_000:
        return f"{prefix}{n/1_000_000:.1f}M{suffix}"
    elif abs(n) >= 1_000:
        return f"{prefix}{n/1_000:.1f}K{suffix}"
    else:
        return f"{prefix}{n:,.{decimals}f}{suffix}"

def get_plotly_layout(title=""):
    """Return a consistent light theme layout for Plotly."""
    return dict(
        title=dict(text=title, font=dict(color="#312e81", size=14, family="Inter"), x=0.0, xanchor="left"),
        paper_bgcolor="rgba(255,255,255,0.0)",
        plot_bgcolor="rgba(248,250,255,0.6)",
        font=dict(color="#374151", family="Inter", size=11),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            gridcolor="rgba(99,102,241,0.1)",
            linecolor="rgba(99,102,241,0.15)",
            tickfont=dict(color="#6b7280"),
        ),
        yaxis=dict(
            gridcolor="rgba(99,102,241,0.1)",
            linecolor="rgba(99,102,241,0.15)",
            tickfont=dict(color="#6b7280"),
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(99,102,241,0.2)",
            borderwidth=1,
            font=dict(color="#374151"),
        ),
    )

CHART_COLORS = {
    "primary": "#6366f1",
    "secondary": "#8b5cf6",
    "accent": "#a78bfa",
    "green": "#10b981",
    "red": "#ef4444",
    "orange": "#f59e0b",
    "blue": "#3b82f6",
    "teal": "#14b8a6",
}

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 30px 0;">
        <div style="font-size:36px; margin-bottom:8px;">🚀</div>
        <div style="font-size:20px; font-weight:800; color:#312e81; letter-spacing:1px;">AXON ADS</div>
        <div style="font-size:11px; color:#6366f1; font-weight:600; letter-spacing:2px;">DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Data Source")
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        help="Upload your Axon Ads export CSV",
    )

    # Default file path
    DEFAULT_PATH = "axon-ads-2026-05-20_to_2026-05-20.csv"

    st.markdown("---")
    st.markdown("### ⏱ Time Period")
    time_period = st.selectbox(
        "Select period",
        options=["Today", "Yesterday", "Last 7 Days", "This Week", "Last 30 Days", "This Month", "All Time"],
        index=6,
        help="Filters the time-series chart",
    )

    st.markdown("---")
    st.markdown("### 🏆 Chart Settings")
    top_n = st.slider("Top / Bottom N campaigns", min_value=3, max_value=15, value=8)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; font-size:11px; color:#9ca3af; padding-top:10px;">
        Powered by Streamlit + Plotly
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
@st.cache_data
def load_data(path=None, file_obj=None):
    if file_obj is not None:
        df = pd.read_csv(file_obj)
    elif path and os.path.exists(path):
        df = pd.read_csv(path)
    else:
        return None

    # Rename columns for clarity
    rename_map = {
        "shopifyOrders": "sOrders",
        "shopifyRevenue": "sRevenue",
        "roas": "sROAS",
        "beRoas": "beROAS",
        "profit": "sProfit",
    }
    df.rename(columns=rename_map, inplace=True)

    # Extract date from campaignName (format: ...- DDMMYYYY -)
    def extract_date(name):
        import re
        match = re.search(r"(\d{2})(\d{2})(\d{4})", str(name))
        if match:
            try:
                return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1))).date()
            except:
                pass
        return None

    df["campaign_date"] = df["campaignName"].apply(extract_date)

    # Short campaign name (first segment before " - ")
    df["campaignShort"] = df["campaignName"].apply(lambda x: str(x).split(" - ")[0])

    return df


if uploaded_file is not None:
    df = load_data(file_obj=uploaded_file)
else:
    df = load_data(path=DEFAULT_PATH)

if df is None:
    st.error("⚠️ Could not load data. Please upload a CSV file or verify the default path.")
    st.stop()

# ─────────────────────────────────────────────
# Date filtering for time-series
# ─────────────────────────────────────────────
today = datetime.today().date()

def get_date_range(period):
    if period == "Today":
        return today, today
    elif period == "Yesterday":
        return today - timedelta(days=1), today - timedelta(days=1)
    elif period == "Last 7 Days":
        return today - timedelta(days=6), today
    elif period == "This Week":
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == "Last 30 Days":
        return today - timedelta(days=29), today
    elif period == "This Month":
        return today.replace(day=1), today
    else:  # All Time
        return None, None

date_start, date_end = get_date_range(time_period)

df_time = df.copy()
if date_start and date_end:
    mask = df_time["campaign_date"].notna()
    df_time = df_time[mask]
    df_time = df_time[(df_time["campaign_date"] >= date_start) & (df_time["campaign_date"] <= date_end)]

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div style="padding: 8px 0 24px 0;">
    <div style="font-size:28px; font-weight:800; color:#1e1b4b; line-height:1.2;">
        🚀 Axon Ads Performance Dashboard
    </div>
    <div style="font-size:14px; color:#6b7280; margin-top:6px;">
        Axon AppLovin Account &nbsp;·&nbsp; Real-time campaign intelligence
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI Cards – Row 1
# ─────────────────────────────────────────────
total_campaigns = len(df)
total_cost = df["cost"].sum()
total_revenue = df["sRevenue"].sum()
total_profit = df["sProfit"].sum()
total_orders = df["sOrders"].sum()
# True Account sROAS = Total Shopify Revenue / Total Cost
account_sroas = total_revenue / total_cost if total_cost > 0 else 0
# True Account beROAS (weighted average based on cost spend)
account_beroas = (df["beROAS"] * df["cost"]).sum() / total_cost if total_cost > 0 else df["beROAS"].mean()

kpis = [
    ("🎯 Total Campaigns", f"{total_campaigns:,}", "campaigns"),
    ("💰 Total Cost", f"${total_cost:,.0f}", "ad spend"),
    ("📈 sRevenue", f"${total_revenue:,.0f}", "shopify revenue"),
    ("💎 sProfit", f"${total_profit:,.0f}", "net profit"),
    ("🛒 sOrders", f"{total_orders:,.0f}", "shopify orders"),
    ("⚡ sROAS", f"{account_sroas:.2f}", "account sROAS"),
]

cols = st.columns(6)
for col, (label, value, sub) in zip(cols, kpis):
    with col:
        if "Profit" in label:
            color = "#059669" if total_profit > 0 else "#dc2626"
        elif "sROAS" in label:
            color = "#059669" if account_sroas >= account_beroas else "#dc2626"
        else:
            color = "#1e1b4b"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{color};">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROAS Status – Row 2
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📊 ROAS Performance</div>', unsafe_allow_html=True)

df_valid = df.dropna(subset=["sROAS", "beROAS"])
above_roas = int((df_valid["sROAS"] > df_valid["beROAS"]).sum())
below_roas = int((df_valid["sROAS"] <= df_valid["beROAS"]).sum())
pct_above = above_roas / len(df_valid) * 100 if len(df_valid) > 0 else 0

col1, col_mid, col2 = st.columns([5, 1, 5])

with col1:
    st.markdown(f"""
    <div class="roas-card-green">
        <div class="roas-label" style="color:#059669;">✅ sROAS &gt; beROAS</div>
        <div class="roas-big-number" style="color:#059669;">{above_roas}</div>
        <div style="font-size:13px; color:#047857; font-weight:500;">{pct_above:.1f}% of campaigns</div>
        <div style="font-size:11px; color:#6ee7b7; margin-top:6px;">Above breakeven ROAS</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="roas-card-red">
        <div class="roas-label" style="color:#dc2626;">❌ sROAS &lt; beROAS</div>
        <div class="roas-big-number" style="color:#dc2626;">{below_roas}</div>
        <div style="font-size:13px; color:#b91c1c; font-weight:500;">{100-pct_above:.1f}% of campaigns</div>
        <div style="font-size:11px; color:#fca5a5; margin-top:6px;">Below breakeven ROAS</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Spend Category pre-computation
# ─────────────────────────────────────────────
N_camp = len(df)
total_spend_all = df["cost"].sum()

if N_camp > 0 and total_spend_all > 0:
    _eq_share = 1.0 / N_camp
    df["pct_spend"] = df["cost"] / total_spend_all
    thresh_low = 1.5 * _eq_share
    thresh_high = 2.0 * _eq_share

    def categorize_spend(pct):
        if pct < thresh_low:
            return "Under-spent"
        elif pct < thresh_high:
            return "Scale Signal"
        else:
            return "Scaling"

    df["spend_category"] = df["pct_spend"].apply(categorize_spend)
else:
    thresh_low = thresh_high = 0.0
    df["spend_category"] = "Under-spent"


# ─────────────────────────────────────────────
# Time-series chart: sOrders + sROAS
# ─────────────────────────────────────────────
st.markdown(f'<div class="section-header">📅 sOrders & sROAS by Time Period — {time_period}</div>', unsafe_allow_html=True)

if len(df_time) > 0 and df_time["campaign_date"].notna().any():
    ts = df_time.groupby("campaign_date").agg(
        sOrders=("sOrders", "sum"),
        sRevenue=("sRevenue", "sum"),
        cost=("cost", "sum"),
    ).reset_index().sort_values("campaign_date")
    ts["sROAS"] = ts["sRevenue"] / ts["cost"]

    fig_ts = make_subplots(specs=[[{"secondary_y": True}]])

    fig_ts.add_trace(
        go.Bar(
            x=ts["campaign_date"].astype(str),
            y=ts["sOrders"],
            name="sOrders",
            marker=dict(
                color=ts["sOrders"],
                colorscale=[[0, "rgba(99,102,241,0.4)"], [1, "rgba(139,92,246,0.9)"]],
                line=dict(color="rgba(99,102,241,0.8)", width=1),
            ),
        ),
        secondary_y=False,
    )

    fig_ts.add_trace(
        go.Scatter(
            x=ts["campaign_date"].astype(str),
            y=ts["sROAS"],
            name="sROAS",
            mode="lines+markers",
            line=dict(color="#10b981", width=2.5),
            marker=dict(size=7, color="#10b981", line=dict(color="#fff", width=1.5)),
        ),
        secondary_y=True,
    )

    layout = get_plotly_layout()
    fig_ts.update_layout(**layout)
    fig_ts.update_yaxes(title_text="sOrders", secondary_y=False, title_font=dict(color="#8b9abc", size=11))
    fig_ts.update_yaxes(title_text="sROAS", secondary_y=True, title_font=dict(color="#10b981", size=11))
    fig_ts.update_layout(height=340, legend=dict(orientation="h", yanchor="bottom", y=1.02))

    st.plotly_chart(fig_ts, use_container_width=True)
else:
    # Show aggregate bar chart when there's only one date or no date range
    agg = df.groupby("campaign_date").agg(
        sOrders=("sOrders", "sum"),
        sRevenue=("sRevenue", "sum"),
        cost=("cost", "sum"),
    ).reset_index().sort_values("campaign_date")
    agg["sROAS"] = agg["sRevenue"] / agg["cost"]

    if len(agg) > 0:
        fig_ts = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ts.add_trace(
            go.Bar(x=agg["campaign_date"].astype(str), y=agg["sOrders"], name="sOrders",
                   marker=dict(color="rgba(99,102,241,0.7)", line=dict(color="rgba(99,102,241,1)", width=1))),
            secondary_y=False,
        )
        fig_ts.add_trace(
            go.Scatter(x=agg["campaign_date"].astype(str), y=agg["sROAS"], name="sROAS",
                       mode="lines+markers", line=dict(color="#10b981", width=2.5),
                       marker=dict(size=8, color="#10b981")),
            secondary_y=True,
        )
        layout = get_plotly_layout()
        fig_ts.update_layout(**layout, height=340)
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        # Single-date fallback – show total as a single bar
        st.markdown("""
        <div style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.3);
                    border-radius:12px; padding:32px; text-align:center; color:#94a3b8;">
            📊 Only one date in dataset — showing account totals below.<br>
            <b style="color:#1e1b4b;">sOrders: {:.0f} &nbsp;|&nbsp; account sROAS: {:.2f}</b>
        </div>
        """.format(df["sOrders"].sum(), account_sroas), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Total Campaigns by Spend
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Total Campaigns by Spend</div>', unsafe_allow_html=True)

if N_camp > 0 and total_spend_all > 0:
    category_counts = df["spend_category"].value_counts().reindex(
        ["Under-spent", "Scale Signal", "Scaling"], fill_value=0
    ).reset_index()
    category_counts.columns = ["Category", "Count"]
    category_counts["Percentage"] = (category_counts["Count"] / N_camp) * 100
    category_counts["Condition"] = [
        f"< {thresh_low*100:.2f}% of total spend",
        f"{thresh_low*100:.2f}% to {thresh_high*100:.2f}% of total spend",
        f"≥ {thresh_high*100:.2f}% of total spend",
    ]

    _cat_color_map = {
        "Under-spent": "#ef4444",
        "Scale Signal": "#f59e0b",
        "Scaling": "#10b981",
    }

    # Visual dimming: dim non-selected bars when a spend filter is active
    _bar_colors = [
        "rgba(190,190,200,0.30)" if (st.session_state.spend_filter and cat != st.session_state.spend_filter)
        else _cat_color_map[cat]
        for cat in category_counts["Category"]
    ]

    fig_spend = go.Figure()
    fig_spend.add_trace(go.Bar(
        x=category_counts["Category"],
        y=category_counts["Count"],
        customdata=category_counts["Condition"],
        marker=dict(
            color=_bar_colors,
            line=dict(color="rgba(255,255,255,0.6)", width=1.5),
        ),
        text=category_counts.apply(
            lambda r: f"{r['Count']} camps ({r['Percentage']:.1f}%)" if r["Count"] > 0 else "", axis=1
        ),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Condition: %{customdata}<br>Count: %{y} campaigns<extra></extra>",
    ))

    layout_spend = get_plotly_layout("")
    fig_spend.update_layout(**layout_spend, height=320, yaxis_title="Campaigns Count")

    st.caption("💡 Click a bar to view campaigns list · click again to close")
    _ev_spend = st.plotly_chart(
        fig_spend,
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        key="spend_chart",
    )

    # Update state based on click
    _new_spend = None
    if _ev_spend.selection.points:
        _new_spend = _ev_spend.selection.points[0].get("x")
    if _new_spend != st.session_state.spend_filter:
        st.session_state.spend_filter = _new_spend
        st.rerun()

    # Drilldown table for selected spend category
    if st.session_state.spend_filter:
        st.markdown(f'<div style="font-size:14px; font-weight:600; color:#312e81; margin: 16px 0 8px 0;">📋 Campaigns in: <span style="color:#6366f1;">{st.session_state.spend_filter}</span></div>', unsafe_allow_html=True)
        df_drill = df[df["spend_category"] == st.session_state.spend_filter].copy()
        df_drill = df_drill[["campaignShort", "cost", "pct_spend", "sROAS", "sOrders", "sProfit"]].copy()
        df_drill = df_drill.rename(columns={
            "campaignShort": "Campaign",
            "cost": "Spend ($)",
            "pct_spend": "% Spend",
            "sROAS": "sROAS",
            "sOrders": "sPurchase",
            "sProfit": "sMargin ($)"
        })
        st.dataframe(
            df_drill.style.format({
                "Spend ($)": "${:,.2f}",
                "% Spend": "{:.2%}",
                "sROAS": "{:.3f}",
                "sPurchase": "{:,.0f}",
                "sMargin ($)": "${:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("⚠️ Not enough data to calculate spend classification.")

# ─────────────────────────────────────────────
# Top campaigns – Row
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 Top Campaigns</div>', unsafe_allow_html=True)

col_tl, col_tr = st.columns(2)

# Top by sOrders
with col_tl:
    df_top_orders = (
        df.nlargest(top_n, "sOrders")[["campaignShort", "sOrders", "sROAS", "beROAS"]].copy()
    )
    df_top_orders = df_top_orders.sort_values("sOrders", ascending=True)

    colors_orders = [
        CHART_COLORS["green"] if r > b else CHART_COLORS["red"]
        for r, b in zip(df_top_orders["sROAS"], df_top_orders["beROAS"])
    ]

    fig_top_orders = go.Figure(go.Bar(
        x=df_top_orders["sOrders"],
        y=df_top_orders["campaignShort"],
        orientation="h",
        marker=dict(
            color=colors_orders,
            opacity=0.85,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5),
        ),
        text=df_top_orders["sOrders"].apply(lambda v: f"{v:,.0f}"),
        textposition="outside",
        textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{y}</b><br>sOrders: %{x:,.0f}<extra></extra>",
    ))
    layout = get_plotly_layout(f"Top {top_n} by sOrders")
    fig_top_orders.update_layout(**layout, height=max(300, top_n * 42), xaxis_title="sOrders")
    st.plotly_chart(
        fig_top_orders, use_container_width=True,
    )
    st.caption("🟢 sROAS > beROAS &nbsp;&nbsp; 🔴 sROAS ≤ beROAS")

# Top by profit
with col_tr:
    df_top_profit = (
        df.nlargest(top_n, "sProfit")[["campaignShort", "sProfit", "sROAS", "beROAS"]].copy()
    )
    df_top_profit = df_top_profit.sort_values("sProfit", ascending=True)

    colors_profit = [
        CHART_COLORS["green"] if r > b else CHART_COLORS["red"]
        for r, b in zip(df_top_profit["sROAS"], df_top_profit["beROAS"])
    ]

    fig_top_profit = go.Figure(go.Bar(
        x=df_top_profit["sProfit"],
        y=df_top_profit["campaignShort"],
        orientation="h",
        marker=dict(
            color=colors_profit,
            opacity=0.85,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5),
        ),
        text=df_top_profit["sProfit"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{y}</b><br>sProfit: $%{x:,.0f}<extra></extra>",
    ))
    layout = get_plotly_layout(f"Top {top_n} by sProfit")
    fig_top_profit.update_layout(**layout, height=max(300, top_n * 42), xaxis_title="sProfit ($)")
    st.plotly_chart(
        fig_top_profit, use_container_width=True,
    )
    st.caption("🟢 sROAS > beROAS &nbsp;&nbsp; 🔴 sROAS ≤ beROAS")


# ─────────────────────────────────────────────
# Bottom campaigns – Row
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📉 Bottom Campaigns</div>', unsafe_allow_html=True)

col_bl, col_br = st.columns(2)

# Bottom by sOrders
with col_bl:
    df_bot_orders = (
        df.nsmallest(top_n, "sOrders")[["campaignShort", "sOrders", "sROAS", "beROAS"]].copy()
    )
    df_bot_orders = df_bot_orders.sort_values("sOrders", ascending=False)

    colors_bot_orders = [
        CHART_COLORS["green"] if r > b else CHART_COLORS["red"]
        for r, b in zip(df_bot_orders["sROAS"], df_bot_orders["beROAS"])
    ]

    fig_bot_orders = go.Figure(go.Bar(
        x=df_bot_orders["sOrders"],
        y=df_bot_orders["campaignShort"],
        orientation="h",
        marker=dict(
            color=colors_bot_orders,
            opacity=0.85,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5),
        ),
        text=df_bot_orders["sOrders"].apply(lambda v: f"{v:,.0f}"),
        textposition="outside",
        textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{y}</b><br>sOrders: %{x:,.0f}<extra></extra>",
    ))
    layout = get_plotly_layout(f"Bottom {top_n} by sOrders")
    fig_bot_orders.update_layout(**layout, height=max(300, top_n * 42), xaxis_title="sOrders")
    st.plotly_chart(
        fig_bot_orders, use_container_width=True,
    )
    st.caption("🟢 sROAS > beROAS &nbsp;&nbsp; 🔴 sROAS ≤ beROAS")

# Bottom by profit
with col_br:
    df_bot_profit = (
        df.nsmallest(top_n, "sProfit")[["campaignShort", "sProfit", "sROAS", "beROAS"]].copy()
    )
    df_bot_profit = df_bot_profit.sort_values("sProfit", ascending=False)

    colors_bot_profit = [
        CHART_COLORS["green"] if r > b else CHART_COLORS["red"]
        for r, b in zip(df_bot_profit["sROAS"], df_bot_profit["beROAS"])
    ]

    fig_bot_profit = go.Figure(go.Bar(
        x=df_bot_profit["sProfit"],
        y=df_bot_profit["campaignShort"],
        orientation="h",
        marker=dict(
            color=colors_bot_profit,
            opacity=0.85,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5),
        ),
        text=df_bot_profit["sProfit"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{y}</b><br>sProfit: $%{x:,.0f}<extra></extra>",
    ))
    layout = get_plotly_layout(f"Bottom {top_n} by sProfit")
    fig_bot_profit.update_layout(**layout, height=max(300, top_n * 42), xaxis_title="sProfit ($)")
    st.plotly_chart(
        fig_bot_profit, use_container_width=True,
    )
    st.caption("🟢 sROAS > beROAS &nbsp;&nbsp; 🔴 sROAS ≤ beROAS")

# ─────────────────────────────────────────────
# Raw data expander
# ─────────────────────────────────────────────
with st.expander("📋 Full Campaign List", expanded=False):
    st.info(f"🔍 Showing all **{len(df)}** campaigns")

    display_cols = ["campaignName", "cost", "sOrders", "sRevenue", "sProfit", "sROAS", "beROAS"]
    df_display = df[display_cols].copy()
    df_display["ROAS Status"] = df_display.apply(
        lambda r: "✅ Above" if r["sROAS"] > r["beROAS"] else "❌ Below", axis=1
    )
    df_display = df_display.rename(columns={
        "campaignName": "Campaign",
        "cost": "Cost ($)",
        "sOrders": "sOrders",
        "sRevenue": "sRevenue ($)",
        "sProfit": "sProfit ($)",
        "sROAS": "sROAS",
        "beROAS": "beROAS",
    })

    st.dataframe(
        df_display.style.format({
            "Cost ($)": "${:,.2f}",
            "sRevenue ($)": "${:,.2f}",
            "sProfit ($)": "${:,.2f}",
            "sROAS": "{:.3f}",
            "beROAS": "{:.2f}",
        }).map(
            lambda v: "color: #10b981" if v == "✅ Above" else "color: #ef4444" if v == "❌ Below" else "",
            subset=["ROAS Status"]
        ),
        use_container_width=True,
        height=400,
    )
