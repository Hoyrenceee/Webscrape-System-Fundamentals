import streamlit as st
import pandas as pd
import os
from scraper import scrape_starlink_data


st.set_page_config(
    page_title="Starlink Terminal",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #000000 !important;
    color: #eeeeee !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] > div:first-child {
    background: #0a0a0a !important;
    border-right: 1px solid #222222;
    padding: 0 !important;
}

[data-testid="stSidebar"] .stButton > button {
    font-family: inherit;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #000000;
    background: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 15px 0;
    width: 100%;
    transition: all 0.2s ease;
    cursor: pointer;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #cccccc;
}
[data-testid="stSidebar"] .stButton > button:active { transform: scale(0.99); }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #222222;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 17px;
    font-weight: 400;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 14px 32px;
    color: #555555;
    margin-bottom: -1px;
    transition: color 0.2s;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #ffffff !important;
    border-bottom: 2px solid #ffffff !important;
    font-weight: 500 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 28px; }

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: #0a0a0a;
    border: 1px solid #222222;
    border-radius: 6px;
    padding: 22px 24px 18px;
    transition: border-color 0.2s;
}
div[data-testid="stMetric"]:hover { border-color: #444444; }
div[data-testid="stMetric"]::after { display: none !important; }

div[data-testid="stMetric"] label {
    font-size: 13px !important;
    font-weight: 400 !important;
    color: #666666 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}
div[data-testid="stMetricValue"] {
    font-size: 36px !important;
    font-weight: 500 !important;
    color: #ffffff !important;
    line-height: 1.15 !important;
    margin-top: 8px;
    letter-spacing: -1px;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] iframe {
    border-radius: 4px;
    border: 1px solid #222222;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    font-size: 16px;
    font-weight: 500;
    letter-spacing: 1px;
    color: #ffffff;
    background: #0a0a0a;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 15px 0;
    transition: all 0.2s ease;
    width: 100%;
}
[data-testid="stDownloadButton"] button:hover {
    background: #111111;
    border-color: #777777;
}

/* ── Text input ── */
[data-testid="stTextInput"] input {
    font-size: 15px;
    color: #eeeeee;
    background: #0a0a0a;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 10px 14px;
}
[data-testid="stTextInput"] input:focus {
    border-color: #ffffff;
    box-shadow: none;
}
[data-testid="stTextInput"] input::placeholder { color: #444444; }

/* ── Spinner & alerts ── */
[data-testid="stSpinner"] p { color: #aaaaaa; font-size: 16px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #000000; }
::-webkit-scrollbar-thumb { background: #333333; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #555555; }

hr { border: none; height: 1px; background: #1a1a1a; margin: 0; }

/* ── Caption / small text ── */
.stCaption, [data-testid="stCaptionContainer"] p {
    font-size: 13px !important;
    color: #555555 !important;
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────────────────────
def section_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h3 style="font-size: 24px; font-weight: 500; color: #ffffff;
                   letter-spacing: -0.4px; margin: 0 0 6px 0;">
            {title}
        </h3>
        {f'<p style="font-size: 15px; color: #555555; margin: 0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding: 36px 24px 24px; border-bottom: 1px solid #1a1a1a;">
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 6px;">
            <svg width="32" height="32" viewBox="0 0 28 28" fill="none">
                <circle cx="14" cy="14" r="12.5" stroke="#ffffff" stroke-width="1.5"/>
                <ellipse cx="14" cy="14" rx="12.5" ry="4.5" stroke="#ffffff" stroke-width="1"
                         transform="rotate(-30 14 14)"/>
                <circle cx="14" cy="14" r="2.5" fill="#ffffff"/>
            </svg>
            <div>
                <div style="font-size: 20px; font-weight: 600; color: #ffffff;
                            letter-spacing: 1px; text-transform: uppercase;">
                    Starlink
                </div>
                <div style="font-size: 12px; color: #555555; letter-spacing: 1.5px;
                            text-transform: uppercase; margin-top: 2px;">
                    Terminal Console
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Steps
    st.markdown("""
    <div style="padding: 26px 24px 18px;">
        <p style="font-size: 12px; color: #555555; text-transform: uppercase;
                  letter-spacing: 1.5px; margin-bottom: 16px;">How it works</p>
        <div style="display: flex; flex-direction: column; gap: 14px;">
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="min-width: 24px; height: 24px; border-radius: 50%;
                            background: #ffffff; color: #000000; font-size: 12px;
                            font-weight: 600; display: flex; align-items: center;
                            justify-content: center; flex-shrink: 0; margin-top: 1px;">
                    1
                </div>
                <p style="font-size: 15px; color: #888888; line-height: 1.5; padding-top: 2px; margin: 0;">
                    Click <strong style="color: #ffffff;">Run Sync</strong> below
                </p>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="min-width: 24px; height: 24px; border-radius: 50%;
                            background: #ffffff; color: #000000; font-size: 12px;
                            font-weight: 600; display: flex; align-items: center;
                            justify-content: center; flex-shrink: 0; margin-top: 1px;">
                    2
                </div>
                <p style="font-size: 15px; color: #888888; line-height: 1.5; padding-top: 2px; margin: 0;">
                    Browser connects to Starlink and pulls your usage data
                </p>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="min-width: 24px; height: 24px; border-radius: 50%;
                            background: #ffffff; color: #000000; font-size: 12px;
                            font-weight: 600; display: flex; align-items: center;
                            justify-content: center; flex-shrink: 0; margin-top: 1px;">
                    3
                </div>
                <p style="font-size: 15px; color: #888888; line-height: 1.5; padding-top: 2px; margin: 0;">
                    View your metrics and download the CSV
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sync button
    st.markdown('<div style="padding: 0 24px;">', unsafe_allow_html=True)
    run_scraper = st.button("Run Sync", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding: 10px 24px 0;">', unsafe_allow_html=True)
    st.caption("Launches a headless browser to extract usage data from your Starlink portal.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # System status
    csv_exists = os.path.exists("data_usage.csv")

    st.markdown(f"""
    <div style="padding: 20px 24px 28px;">
        <p style="font-size: 12px; color: #555555; text-transform: uppercase;
                  letter-spacing: 1.5px; margin-bottom: 16px;">System</p>
        <div style="display: flex; flex-direction: column; gap: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 15px; color: #555555;">Engine</span>
                <span style="font-size: 15px; color: #ffffff;">Playwright</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 15px; color: #555555;">Source</span>
                <span style="font-size: 15px; color: #ffffff;">Starlink Portal</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 15px; color: #555555;">Output</span>
                <span style="font-size: 15px; color: #ffffff;">CSV</span>
            </div>
            <div style="height: 1px; background: #1a1a1a; margin: 2px 0;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 15px; color: #555555;">Dataset</span>
                <span style="font-size: 14px; color: {'#ffffff' if csv_exists else '#444444'};
                             background: {'#1a1a1a' if csv_exists else '#0d0d0d'};
                             padding: 3px 10px; border-radius: 3px; border: 1px solid {'#333333' if csv_exists else '#1a1a1a'};">
                    {'Ready' if csv_exists else 'No data'}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── MAIN ─────────────────────────────────────────────────────────────────────
csv_file = "data_usage.csv"

# Large prominent header
st.markdown("""
<div style="padding: 32px 0 36px; border-bottom: 1px solid #1a1a1a; margin-bottom: 36px;">
    <div style="display: flex; align-items: flex-end;
                justify-content: space-between; flex-wrap: wrap; gap: 16px;">
        <div>
            <p style="font-size: 13px; color: #555555; text-transform: uppercase;
                      letter-spacing: 2px; margin: 0 0 10px 0;">
                Starlink · Network Analytics
            </p>
            <h1 style="font-size: 52px; font-weight: 500; color: #ffffff;
                       letter-spacing: -2px; line-height: 1; margin: 0;">
                Usage Dashboard
            </h1>
            <p style="font-size: 16px; color: #555555; margin: 12px 0 0 0; line-height: 1.5;">
                Automated data extraction &amp; visualization for your Starlink consumption metrics.
            </p>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;
                    padding: 10px 18px; border: 1px solid #222222; border-radius: 4px;">
            <span style="width: 7px; height: 7px; border-radius: 50%;
                         background: #ffffff; display: inline-block;
                         animation: blink 2s infinite;"></span>
            <span style="font-size: 13px; color: #888888; letter-spacing: 1px;
                         text-transform: uppercase;">Live Monitor</span>
        </div>
    </div>
</div>
<style>
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }
</style>
""", unsafe_allow_html=True)

# Scraper trigger
if run_scraper:
    with st.spinner("Connecting to Starlink portal · Extracting data..."):
        success, message = scrape_starlink_data()
    if success:
        st.success("Sync complete. Dashboard updated.")
        st.rerun()
    else:
        st.error(f"Sync failed: {message}")

# ── DATA VIEW ─────────────────────────────────────────────────────────────────
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)

    try:
        df["Data Usage (GB)"] = pd.to_numeric(df["Data Usage (GB)"], errors="coerce")
        total_gb  = df["Data Usage (GB)"].sum()
        avg_gb    = df["Data Usage (GB)"].mean()
        max_gb    = df["Data Usage (GB)"].max()
        min_gb    = df["Data Usage (GB)"].min()
        row_count = len(df)
    except Exception:
        total_gb = avg_gb = max_gb = min_gb = 0.0
        row_count = 0

    # KPI cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Consumed",  f"{total_gb:.1f} GB",  help="Total data used this cycle")
    with k2:
        st.metric("Daily Average",   f"{avg_gb:.2f} GB",    help="Mean daily consumption")
    with k3:
        st.metric("Peak Day",        f"{max_gb:.1f} GB",    help="Highest single-day usage")
    with k4:
        st.metric("Records",         str(row_count),        help="Total rows logged")

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    # Tabs
    tab_overview, tab_table, tab_export = st.tabs([
        "Overview",
        "Data Table",
        "Export",
    ])

    # ── OVERVIEW ─────────────────────────────────────────────
    with tab_overview:
        col_l, col_r = st.columns([3, 2], gap="large")

        with col_l:
            section_header("Daily Usage History", "Data consumed per day over time")

            try:
                import plotly.graph_objects as go

                date_col = next(
                    (c for c in df.columns
                     if any(k in c.lower() for k in ["date", "day", "time"])),
                    None
                )
                x_vals = df[date_col] if date_col else list(range(1, len(df) + 1))
                y_vals = df["Data Usage (GB)"].fillna(0)

                fig = go.Figure()
                fig.add_bar(
                    x=x_vals,
                    y=y_vals,
                    marker_color=[
                        "#ffffff" if v >= avg_gb * 1.4 else "#333333"
                        for v in y_vals
                    ],
                    marker_line_width=0,
                )
                fig.add_hline(
                    y=avg_gb,
                    line_dash="solid",
                    line_color="#444444",
                    line_width=1,
                    annotation_text=f"Avg  {avg_gb:.1f} GB",
                    annotation_font_color="#666666",
                    annotation_font_size=13,
                )
                fig.update_layout(
                    plot_bgcolor="#000000",
                    paper_bgcolor="#000000",
                    font=dict(family="inherit", size=13, color="#555555"),
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=280,
                    xaxis=dict(
                        gridcolor="#111111",
                        showline=False,
                        tickfont=dict(size=12, color="#555555"),
                    ),
                    yaxis=dict(
                        gridcolor="#111111",
                        showline=False,
                        ticksuffix=" GB",
                        tickfont=dict(size=12, color="#555555"),
                    ),
                    hoverlabel=dict(
                        bgcolor="#0a0a0a",
                        bordercolor="#333333",
                        font_color="#ffffff",
                        font_size=14,
                    ),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})
                st.caption("White bars = peak days (≥ 1.4× daily average)")

            except ImportError:
                st.bar_chart(df[["Data Usage (GB)"]], height=280, color="#ffffff")
                st.caption("Install plotly for an enhanced chart: pip install plotly")

        with col_r:
            section_header("Usage Breakdown", "Key consumption benchmarks")

            stats = [
                ("Highest Day",  f"{max_gb:.1f} GB",   "Peak consumption recorded"),
                ("Lowest Day",   f"{min_gb:.1f} GB",   "Minimum usage recorded"),
                ("Daily Mean",   f"{avg_gb:.2f} GB",   "Average per day"),
                ("Total Volume", f"{total_gb:.1f} GB", "All-time cumulative total"),
            ]
            for label, value, desc in stats:
                st.markdown(f"""
                <div style="display: flex; align-items: center;
                            justify-content: space-between;
                            background: #0a0a0a; border: 1px solid #1e1e1e;
                            border-radius: 4px; padding: 16px 20px;
                            margin-bottom: 10px; transition: border-color 0.2s;">
                    <div>
                        <p style="font-size: 15px; font-weight: 500;
                                  color: #ffffff; margin: 0 0 3px 0;">{label}</p>
                        <p style="font-size: 13px; color: #555555; margin: 0;">{desc}</p>
                    </div>
                    <span style="font-size: 20px; font-weight: 400;
                                 color: #ffffff; letter-spacing: -0.5px;">{value}</span>
                </div>
                """, unsafe_allow_html=True)

    # ── DATA TABLE ───────────────────────────────────────────
    with tab_table:
        section_header("Full Dataset", "All logged records")

        filter_col, _ = st.columns([2, 3])
        with filter_col:
            search = st.text_input(
                "Search",
                placeholder="Search any column...",
                label_visibility="collapsed",
            )

        display_df = df.copy()
        if search:
            mask = display_df.apply(
                lambda col: col.astype(str).str.contains(search, case=False, na=False)
            ).any(axis=1)
            display_df = display_df[mask]
            st.caption(f"Showing {len(display_df)} of {len(df)} rows")
        else:
            st.caption(f"{len(df)} rows · {len(df.columns)} columns")

        try:
            styled = (
                display_df.style
                .format({"Data Usage (GB)": "{:.2f} GB"})
                .background_gradient(
                    cmap="Greys",
                    subset=["Data Usage (GB)"],
                    vmin=0,
                    vmax=max_gb,
                )
                .set_properties(**{
                    "background-color": "#000000",
                    "color": "#eeeeee",
                    "border-color": "#1e1e1e",
                    "font-size": "15px",
                })
            )
            st.dataframe(styled, use_container_width=True, height=440)
        except Exception:
            st.dataframe(display_df, use_container_width=True, height=440)

        if len(display_df) == 0:
            st.info("No rows match your search.")

    # ── EXPORT ───────────────────────────────────────────────
    with tab_export:
        section_header("Export Data", "Download your dataset as a CSV file")

        exp_l, exp_r = st.columns([3, 2], gap="large")

        with exp_l:
            file_size_kb = round(os.path.getsize(csv_file) / 1024, 1)

            st.markdown(f"""
            <div style="background: #0a0a0a; border: 1px solid #1e1e1e;
                        border-radius: 6px; padding: 24px 26px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center;
                            gap: 16px; margin-bottom: 22px;">
                    <div style="width: 48px; height: 48px; border-radius: 6px;
                                background: #111111; border: 1px solid #222222;
                                display: flex; align-items: center;
                                justify-content: center; font-size: 22px;">
                        📄
                    </div>
                    <div>
                        <p style="font-size: 16px; color: #ffffff;
                                  margin: 0 0 3px 0; font-weight: 500;">
                            Starlink_Network_Telemetry.csv
                        </p>
                        <p style="font-size: 13px; color: #555555; margin: 0;">
                            Starlink usage data · Verified export
                        </p>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                    <div style="background: #111111; border-radius: 4px;
                                padding: 14px; text-align: center;">
                        <p style="font-size: 11px; color: #555555; letter-spacing: 1px;
                                  text-transform: uppercase; margin: 0 0 6px 0;">Rows</p>
                        <p style="font-size: 22px; color: #ffffff;
                                  font-weight: 500; margin: 0;">{row_count}</p>
                    </div>
                    <div style="background: #111111; border-radius: 4px;
                                padding: 14px; text-align: center;">
                        <p style="font-size: 11px; color: #555555; letter-spacing: 1px;
                                  text-transform: uppercase; margin: 0 0 6px 0;">Columns</p>
                        <p style="font-size: 22px; color: #ffffff;
                                  font-weight: 500; margin: 0;">{len(df.columns)}</p>
                    </div>
                    <div style="background: #111111; border-radius: 4px;
                                padding: 14px; text-align: center;">
                        <p style="font-size: 11px; color: #555555; letter-spacing: 1px;
                                  text-transform: uppercase; margin: 0 0 6px 0;">Size</p>
                        <p style="font-size: 22px; color: #ffffff;
                                  font-weight: 500; margin: 0;">{file_size_kb}
                            <span style="font-size: 13px; color: #555555;">KB</span>
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with open(csv_file, "rb") as f:
                st.download_button(
                    label="↓  Download CSV",
                    data=f,
                    file_name="Starlink_Network_Telemetry.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with exp_r:
            st.markdown("""
            <div style="background: #0a0a0a; border: 1px solid #1e1e1e;
                        border-radius: 6px; padding: 24px 26px;">
                <p style="font-size: 12px; color: #555555; text-transform: uppercase;
                          letter-spacing: 1.5px; margin: 0 0 18px 0;">What's included</p>
                <div style="display: flex; flex-direction: column; gap: 14px;">
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <span style="font-size: 16px; color: #ffffff; margin-top: 1px;">✓</span>
                        <span style="font-size: 15px; color: #888888; line-height: 1.5;">
                            Daily data usage records in GB
                        </span>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <span style="font-size: 16px; color: #ffffff; margin-top: 1px;">✓</span>
                        <span style="font-size: 15px; color: #888888; line-height: 1.5;">
                            Timestamped entries from Starlink portal
                        </span>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <span style="font-size: 16px; color: #ffffff; margin-top: 1px;">✓</span>
                        <span style="font-size: 15px; color: #888888; line-height: 1.5;">
                            Clean CSV — opens in Excel or Python
                        </span>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <span style="font-size: 16px; color: #ffffff; margin-top: 1px;">✓</span>
                        <span style="font-size: 15px; color: #888888; line-height: 1.5;">
                            Auto-updated every time you run a sync
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="background: #0a0a0a; border: 1px dashed #222222;
                border-radius: 6px; padding: 72px 32px; text-align: center;
                max-width: 520px; margin: 40px auto 0;">
        <svg width="44" height="44" viewBox="0 0 28 28" fill="none"
             style="margin-bottom: 20px; opacity: 0.2;">
            <circle cx="14" cy="14" r="12.5" stroke="#ffffff" stroke-width="1.5"/>
            <ellipse cx="14" cy="14" rx="12.5" ry="4.5" stroke="#ffffff" stroke-width="1"
                     transform="rotate(-30 14 14)"/>
            <circle cx="14" cy="14" r="2.5" fill="#ffffff"/>
        </svg>
        <h3 style="font-size: 22px; font-weight: 500; color: #ffffff; margin: 0 0 10px 0;">
            No data yet
        </h3>
        <p style="font-size: 16px; color: #555555; line-height: 1.6; margin: 0 0 32px 0;">
            Click <strong style="color: #ffffff;">Run Sync</strong> in the sidebar
            to launch the scraper and pull your Starlink usage data.
        </p>
        <div style="display: flex; justify-content: center;
                    align-items: center; gap: 24px;">
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: 500;
                             color: #ffffff; margin-bottom: 6px;">1</div>
                <div style="font-size: 13px; color: #444444;">Run Sync</div>
            </div>
            <div style="font-size: 20px; color: #222222;">→</div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: 500;
                             color: #ffffff; margin-bottom: 6px;">2</div>
                <div style="font-size: 13px; color: #444444;">Scrape data</div>
            </div>
            <div style="font-size: 20px; color: #222222;">→</div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: 500;
                             color: #ffffff; margin-bottom: 6px;">3</div>
                <div style="font-size: 13px; color: #444444;">View & export</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)