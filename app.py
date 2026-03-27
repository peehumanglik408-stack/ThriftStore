import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Thrift Fashion Analytics · Peehu",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px; border-radius: 8px 8px 0 0;
        font-size: 13px; font-weight: 500;
    }
    .metric-card {
        background: #F8FAF9; border-radius: 12px;
        padding: 1rem 1.2rem; border: 1px solid #E0EDE8;
        text-align: center;
    }
    .metric-val { font-size: 28px; font-weight: 600; color: #1D9E75; line-height: 1.1; }
    .metric-label { font-size: 12px; color: #5F5E5A; margin-top: 4px; }
    .insight-box {
        background: #F0FAF6; border-left: 4px solid #1D9E75;
        border-radius: 0 8px 8px 0; padding: 1rem 1.2rem;
        margin: 0.8rem 0; font-size: 14px; line-height: 1.7; color: #2C2C2A;
    }
    .warning-box {
        background: #FFFBF0; border-left: 4px solid #BA7517;
        border-radius: 0 8px 8px 0; padding: 1rem 1.2rem;
        margin: 0.8rem 0; font-size: 14px; line-height: 1.7; color: #2C2C2A;
    }
    .info-box {
        background: #EEF5FE; border-left: 4px solid #378ADD;
        border-radius: 0 8px 8px 0; padding: 1rem 1.2rem;
        margin: 0.8rem 0; font-size: 14px; line-height: 1.7; color: #2C2C2A;
    }
    .section-header {
        font-size: 18px; font-weight: 600; color: #1D9E75;
        margin: 1.5rem 0 0.5rem; padding-bottom: 6px;
        border-bottom: 2px solid #E0EDE8;
    }
    .tag { display:inline-block; padding: 2px 10px; border-radius: 99px;
           font-size: 11px; font-weight: 600; margin: 2px; }
    .tag-green { background: #E1F5EE; color: #0F6E56; }
    .tag-purple { background: #EEEDFE; color: #534AB7; }
    .tag-amber { background: #FAEEDA; color: #854F0B; }
    .tag-blue { background: #E6F1FB; color: #185FA5; }
    .tag-coral { background: #FAECE7; color: #993C1D; }
    h1, h2, h3 { color: #2C2C2A; }
    .stDataFrame { font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ─── Colour Palette ───────────────────────────────────────────────────────────
BRAND_GREEN   = "#1D9E75"
TEAL_LIGHT    = "#E1F5EE"
AMBER         = "#BA7517"
CORAL         = "#D85A30"
PURPLE        = "#534AB7"
BLUE          = "#378ADD"
GRAY          = "#888780"
PERSONA_COLORS = {
    "Aesthetic Chaser":  "#7F77DD",
    "Conscious Spender": "#1D9E75",
    "Bargain Hunter":    "#D85A30",
    "Fence-Sitter":      "#378ADD",
    "Occasional Gifter": "#BA7517",
    "Skeptic":           "#888780",
}
INTENT_COLORS = {
    "Interested":     "#1D9E75",
    "Maybe":          "#BA7517",
    "Not Interested": "#E24B4A",
}

# ─── Data Loading & Cleaning ──────────────────────────────────────────────────
@st.cache_data
def load_raw():
    df = pd.read_csv("data.csv")
    return df

@st.cache_data
def load_cleaned():
    df = pd.read_csv("data.csv")

    # Ordinal encodings
    age_order = ["Under 18","18-22","23-27","28-34","35-44","45+"]
    income_order = ["Below 10k","10k-25k","25k-50k","50k-1L","Above 1L"]
    spend_order = ["Under 500","500-1000","1000-2500","2500-5000","Above 5000"]
    outfit_order = ["Under 300","300-700","700-1500","1500-3000","Above 3000"]
    mbox_order = ["Under 500","500-800","800-1200","1200-1800","Would not buy"]
    freq_order = ["Multiple times a month","Once a month","Once every 2-3 months","Few times a year","Rarely"]
    city_order = ["Metro","Tier 2","Tier 3 / Small town","Rural"]
    thrift_exp_order = ["Yes regularly","Yes a few times","No but open","No and unlikely"]
    upc_order = ["Very interested","Interested if priced right","Curious but unsure","Not interested"]
    disc_order = ["Definitely yes","Likely yes","Unsure","Probably not","No"]
    size_order = ["Very confident","Somewhat confident","Unsure - it concerns me","Not confident at all"]
    trust_order = ["Reviews and tagged photos","Clear size guide and photos","COD/Easy return","Follower count/Brand credibility"]
    sub_order = ["Would subscribe immediately","Maybe after first box","Prefer one-off","No interest"]
    return_order = ["Would stop me","Makes me hesitate","Comfortable with it","Depends on price"]
    ugc_order = ["Yes regularly","Occasionally","Engage but rarely post","No"]
    gifting_order = ["Yes frequently","Yes occasionally","Rarely","Never"]
    intent_order = ["Interested","Maybe","Not Interested"]
    bundle_order = ["Prefer complete looks","Sometimes if it appeals","Prefer to mix myself","No preference"]

    ordinal_maps = {
        "age_group": {v:i for i,v in enumerate(age_order)},
        "monthly_income_band": {v:i for i,v in enumerate(income_order)},
        "monthly_fashion_spend": {v:i for i,v in enumerate(spend_order)},
        "max_outfit_spend": {v:i for i,v in enumerate(outfit_order)},
        "mystery_box_wtp": {v:i for i,v in enumerate(mbox_order)},
        "shop_frequency": {v:i for i,v in enumerate(freq_order)},
        "city_tier": {v:i for i,v in enumerate(city_order)},
        "prior_thrift_experience": {v:i for i,v in enumerate(thrift_exp_order)},
        "upcycle_interest": {v:i for i,v in enumerate(upc_order)},
        "discount_sensitivity": {v:i for i,v in enumerate(disc_order)},
        "size_confidence": {v:i for i,v in enumerate(size_order)},
        "digital_trust_score": {v:i for i,v in enumerate(trust_order)},
        "subscription_intent": {v:i for i,v in enumerate(sub_order)},
        "return_policy_sensitivity": {v:i for i,v in enumerate(return_order)},
        "ugc_propensity": {v:i for i,v in enumerate(ugc_order)},
        "gifting_behaviour": {v:i for i,v in enumerate(gifting_order)},
        "purchase_intent": {v:i for i,v in enumerate(intent_order)},
        "bundle_preference": {v:i for i,v in enumerate(bundle_order)},
    }
    df_clean = df.copy()
    for col, mapping in ordinal_maps.items():
        if col in df_clean.columns:
            df_clean[col+"_encoded"] = df_clean[col].map(mapping)

    # Fill missing binary columns with 0
    binary_cols = [c for c in df_clean.columns if c.startswith(("clothing_","colour_","accessory_","occasion_"))]
    for col in binary_cols:
        df_clean[col] = df_clean[col].fillna(0).astype(int)

    # Mid-point spend numeric approximation
    spend_mid = {"Under 500":250,"500-1000":750,"1000-2500":1750,"2500-5000":3750,"Above 5000":6000}
    outfit_mid = {"Under 300":150,"300-700":500,"700-1500":1100,"1500-3000":2250,"Above 3000":4000}
    income_mid = {"Below 10k":5000,"10k-25k":17500,"25k-50k":37500,"50k-1L":75000,"Above 1L":125000}
    df_clean["spend_numeric"] = df_clean["monthly_fashion_spend"].map(spend_mid)
    df_clean["outfit_spend_numeric"] = df_clean["max_outfit_spend"].map(outfit_mid)
    df_clean["income_numeric"] = df_clean["monthly_income_band"].map(income_mid)

    return df_clean

raw_df = load_raw()
df = load_cleaned()
N = len(df)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ♻️ Thrift Analytics")
    st.markdown("**Peehu's Thrift Fashion Brand**")
    st.markdown("---")
    st.markdown("### Dataset")
    st.markdown(f"- **Respondents:** {N:,}")
    st.markdown(f"- **Features:** {raw_df.shape[1]}")
    st.markdown(f"- **Personas:** 6")
    st.markdown(f"- **Missing cells:** {raw_df.isnull().sum().sum()}")
    st.markdown("---")
    st.markdown("### Quick Filters")
    city_filter = st.multiselect("City Tier", options=df["city_tier"].dropna().unique().tolist(),
                                 default=df["city_tier"].dropna().unique().tolist())
    gender_filter = st.multiselect("Gender", options=df["gender"].dropna().unique().tolist(),
                                   default=df["gender"].dropna().unique().tolist())
    intent_filter = st.multiselect("Purchase Intent", options=["Interested","Maybe","Not Interested"],
                                   default=["Interested","Maybe","Not Interested"])
    st.markdown("---")
    st.caption("Dashboard · Phase 1 — Descriptive & Diagnostic Analysis")

# Apply sidebar filters
mask = (
    df["city_tier"].isin(city_filter) &
    df["gender"].isin(gender_filter) &
    df["purchase_intent"].isin(intent_filter)
)
dff = df[mask].copy()
st.sidebar.markdown(f"**Filtered rows: {len(dff):,}**")

# ─── Tab Layout ───────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Business Overview",
    "📋 Raw Data",
    "🔧 Cleaned Data",
    "👥 Demographics",
    "👗 Fashion Behaviour",
    "💰 Budget & Spend",
    "🛍️ Product Preferences",
    "♻️ Thrift Attitudes",
    "📊 Correlations",
    "🎯 Customer Segments",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — BUSINESS OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("## ♻️ Thrift Fashion Brand — Business Intelligence Dashboard")
    st.markdown(
        "This dashboard powers data-driven decision making for a curated thrift fashion brand "
        "targeting Gen Z and millennial buyers across India. All analysis is based on a "
        "2,000-respondent synthetic consumer survey designed to capture demographics, fashion "
        "preferences, spending behaviour, and purchase intent."
    )

    c1,c2,c3,c4,c5 = st.columns(5)
    metrics = [
        (c1, f"{N:,}", "Survey Respondents"),
        (c2, f"{df['purchase_intent'].eq('Interested').sum():,}", "Likely Buyers"),
        (c3, f"{df['purchase_intent'].eq('Maybe').sum():,}", "Nurture Pipeline"),
        (c4, f"₹{int(dff['spend_numeric'].median()):,}", "Median Monthly Spend"),
        (c5, "6", "Distinct Personas"),
    ]
    for col, val, label in metrics:
        col.markdown(f"""<div class="metric-card">
            <div class="metric-val">{val}</div>
            <div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns([1,1])

    with col_a:
        st.markdown('<div class="section-header">Brand Strategy</div>', unsafe_allow_html=True)
        st.markdown("""
**Mission:** Build India's most recognisable curated thrift brand — affordable, unique, and sustainability-first.

**Core pillars:**
- 🎨 **Aesthetic curation** — Y2K, streetwear, minimal, cottagecore drops
- ♻️ **Sustainability narrative** — circular fashion, trade-in programme
- 📱 **Digital-first** — Instagram-led, community-driven
- 📊 **Data-driven** — personalised recs, targeted discounts, smart bundling

**Growth target:** 20%+ year-on-year, scaling from Instagram to multi-channel.
        """)

        st.markdown('<div class="section-header">7 Product Offerings</div>', unsafe_allow_html=True)
        products = [
            ("01", "Aesthetic-curated outfit drops", "High demand · 60–80% margin"),
            ("02", "Upcycled & reworked originals", "Highest margin · Brand differentiator"),
            ("03", "Mystery thrift boxes", "Viral potential · Subscription path"),
            ("04", "Style profile & personal styling", "Premium · Data engine for ML"),
            ("05", "Trade-in & community sourcing", "Solves inventory · Loyalty loop"),
            ("06", "Digital lookbooks", "95%+ margin · Brand authority"),
            ("07", "Thrift event & pop-up drops", "UGC flywheel · Community anchor"),
        ]
        for num, name, tag in products:
            st.markdown(f"**{num}.** {name}  \n<small style='color:#5F5E5A'>{tag}</small>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-header">Purchase Intent Distribution</div>', unsafe_allow_html=True)
        intent_counts = df["purchase_intent"].value_counts().reset_index()
        intent_counts.columns = ["Intent","Count"]
        intent_counts["Pct"] = (intent_counts["Count"]/N*100).round(1)
        fig_intent = px.pie(intent_counts, values="Count", names="Intent",
                            color="Intent", color_discrete_map=INTENT_COLORS,
                            hole=0.55)
        fig_intent.update_traces(textinfo="label+percent", textfont_size=13)
        fig_intent.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10),
                                  showlegend=False)
        st.plotly_chart(fig_intent, use_container_width=True)

        st.markdown('<div class="insight-box">📌 <strong>Key insight:</strong> '
                    '57% of respondents are likely to purchase from a curated thrift brand — '
                    'a strong conversion base. 35% are in the nurture pipeline (Maybe), '
                    'representing a large opportunity for targeted discounts and social proof. '
                    'Only 8% are firmly Not Interested, validating strong market demand.</div>',
                    unsafe_allow_html=True)

        st.markdown('<div class="section-header">Persona Distribution</div>', unsafe_allow_html=True)
        persona_counts = df["persona"].value_counts().reset_index()
        persona_counts.columns = ["Persona","Count"]
        fig_p = px.bar(persona_counts, x="Count", y="Persona", orientation="h",
                       color="Persona", color_discrete_map=PERSONA_COLORS,
                       text="Count")
        fig_p.update_traces(textposition="outside", textfont_size=11)
        fig_p.update_layout(height=260, showlegend=False,
                             margin=dict(t=10,b=10,l=10,r=60),
                             yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Dashboard Navigation Guide</div>', unsafe_allow_html=True)
    guide_cols = st.columns(4)
    guides = [
        ("📋 Raw & Cleaned Data", "Explore the unprocessed survey responses, missing value map, encoding transformations, and data quality summary."),
        ("👥 Demographics", "Age, gender, city tier, occupation, and income distributions — who is your customer base in India?"),
        ("👗 Fashion Behaviour", "Style identity, sustainability attitudes, shopping frequency, and platform preferences."),
        ("💰 Budget & Spend", "Monthly fashion spend, outfit WTP, mystery box pricing, and income-spend correlation analysis."),
    ]
    for col, (title, desc) in zip(guide_cols, guides):
        col.markdown(f"**{title}**  \n{desc}")
    guide_cols2 = st.columns(4)
    guides2 = [
        ("🛍️ Product Preferences", "Clothing types, colour palettes, accessories, and upcycling interest — feeds association rule mining."),
        ("♻️ Thrift Attitudes", "Prior experience, purchase barriers, discovery channels, and motivators — your conversion funnel."),
        ("📊 Correlations", "Heatmaps and cross-tabs revealing relationships between spend, intent, style, and demographics."),
        ("🎯 Customer Segments", "Deep persona profiling with spider charts and segment-level behavioural comparisons."),
    ]
    for col, (title, desc) in zip(guide_cols2, guides2):
        col.markdown(f"**{title}**  \n{desc}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("## 📋 Raw Survey Data")
    st.markdown("This tab displays the unprocessed dataset exactly as generated — before any encoding, imputation, or transformation. Use this to understand the raw structure and identify data quality issues.")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Rows", f"{raw_df.shape[0]:,}")
    c2.metric("Total Columns", raw_df.shape[1])
    c3.metric("Missing Cells", raw_df.isnull().sum().sum())
    c4.metric("Missing %", f"{raw_df.isnull().sum().sum()/(raw_df.shape[0]*raw_df.shape[1])*100:.2f}%")

    st.markdown("---")
    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown("### 🔍 Dataset Preview")
        n_rows = st.slider("Rows to display", 5, 100, 20)
        st.dataframe(raw_df.head(n_rows), use_container_width=True, height=400)

    with col2:
        st.markdown("### 📊 Column Data Types")
        dtype_df = pd.DataFrame({
            "Column": raw_df.dtypes.index,
            "Type": raw_df.dtypes.astype(str).values,
            "Nulls": raw_df.isnull().sum().values,
            "Unique": [raw_df[c].nunique() for c in raw_df.columns]
        })
        st.dataframe(dtype_df, use_container_width=True, height=400)

    st.markdown("---")
    st.markdown("### 🕳️ Missing Value Map")
    missing = raw_df.isnull().sum()
    missing = missing[missing > 0].reset_index()
    missing.columns = ["Column","Missing Count"]
    missing["Missing %"] = (missing["Missing Count"]/N*100).round(2)
    if len(missing) > 0:
        fig_miss = px.bar(missing, x="Column", y="Missing Count",
                          color="Missing %", color_continuous_scale="Oranges",
                          text="Missing Count",
                          title="Columns with missing values")
        fig_miss.update_traces(textposition="outside")
        fig_miss.update_layout(height=350, margin=dict(t=40,b=60))
        st.plotly_chart(fig_miss, use_container_width=True)
        st.dataframe(missing, use_container_width=True)
        st.markdown('<div class="warning-box">⚠️ Missing values are confined to binary columns '
                    '(colour preferences, accessory choices, travel occasions) — injected as '
                    'deliberate noise (~2% of rows) to simulate real survey skip patterns. '
                    'These will be imputed with 0 in the cleaned dataset, which is '
                    'analytically appropriate since absence of selection = not chosen.</div>',
                    unsafe_allow_html=True)
    else:
        st.success("No missing values detected in this view.")

    st.markdown("---")
    st.markdown("### 📈 Categorical Value Distribution Preview")
    cat_col = st.selectbox("Select column to inspect", options=[c for c in raw_df.select_dtypes("object").columns])
    vc = raw_df[cat_col].value_counts().reset_index()
    vc.columns = ["Value","Count"]
    vc["Pct"] = (vc["Count"]/N*100).round(1)
    fig_vc = px.bar(vc, x="Value", y="Count", text="Pct",
                    color_discrete_sequence=[BRAND_GREEN])
    fig_vc.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_vc.update_layout(height=350, margin=dict(t=10,b=80),
                         xaxis_tickangle=-30)
    st.plotly_chart(fig_vc, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CLEANED DATA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("## 🔧 Cleaned & Encoded Dataset")
    st.markdown("The cleaned dataset applies ordinal encoding, missing value imputation, and numeric approximation for spend/income bands. This is the version used for all EDA and modelling.")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Rows (after cleaning)", f"{df.shape[0]:,}")
    c2.metric("Original Columns", raw_df.shape[1])
    c3.metric("Engineered Columns", df.shape[1] - raw_df.shape[1])
    c4.metric("Total Columns", df.shape[1])

    st.markdown("---")
    st.markdown("### 🔄 Transformation Log")
    transformations = [
        ("Ordinal Encoding", "18 categorical columns encoded to integer scale preserving order (e.g. age_group: Under 18=0 → 45+=5; income: Below 10k=0 → Above 1L=4)", "tag-green"),
        ("Binary Imputation", "All multi-select binary columns (clothing, colour, accessory, occasion) filled with 0 where missing — absence = not selected", "tag-amber"),
        ("Numeric Spend Midpoints", "Monthly fashion spend, outfit spend, mystery box WTP mapped to midpoint INR values for regression-ready numeric features", "tag-blue"),
        ("Income Numeric", "Income band mapped to midpoint INR (e.g. 10k-25k → ₹17,500) for correlation analysis", "tag-blue"),
        ("Encoded Column Naming", "All encoded columns appended with _encoded suffix to preserve original labels alongside", "tag-purple"),
    ]
    for name, desc, tag_class in transformations:
        st.markdown(f'<span class="tag {tag_class}">{name}</span> — {desc}', unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")
    encoded_cols = [c for c in df.columns if c.endswith("_encoded")]
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("### 🔍 Cleaned Data Preview")
        show_cols = st.radio("Show columns", ["All columns", "Encoded only", "Numeric features only"], horizontal=True)
        if show_cols == "Encoded only":
            display_df = df[["respondent_id","persona"] + encoded_cols + ["spend_numeric","outfit_spend_numeric","income_numeric"]].head(50)
        elif show_cols == "Numeric features only":
            display_df = df[["respondent_id","persona","spend_numeric","outfit_spend_numeric","income_numeric","sustainability_score"] + encoded_cols].head(50)
        else:
            display_df = df.head(50)
        st.dataframe(display_df, use_container_width=True, height=400)

    with col2:
        st.markdown("### 📊 Encoded Column Summary")
        enc_summary = pd.DataFrame({
            "Encoded Column": encoded_cols,
            "Min": [df[c].min() for c in encoded_cols],
            "Max": [df[c].max() for c in encoded_cols],
            "Mean": [round(df[c].mean(),2) for c in encoded_cols],
            "Null": [df[c].isnull().sum() for c in encoded_cols],
        })
        st.dataframe(enc_summary, use_container_width=True, height=400)

    st.markdown("---")
    st.markdown("### 📐 Numeric Feature Distributions")
    num_col = st.selectbox("Select numeric feature", ["spend_numeric","outfit_spend_numeric","income_numeric","sustainability_score"])
    fig_hist = px.histogram(df, x=num_col, color="purchase_intent",
                            color_discrete_map=INTENT_COLORS, nbins=30, barmode="overlay",
                            opacity=0.75, marginal="box",
                            labels={num_col: num_col.replace("_"," ").title()})
    fig_hist.update_layout(height=380, margin=dict(t=20,b=40))
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('<div class="insight-box">📌 The overlaid histograms split by purchase intent reveal '
                'whether higher spend/income segments skew toward "Interested". The box plot '
                'in the margin shows outliers and spread — useful for regression preprocessing.</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DEMOGRAPHICS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("## 👥 Demographic Analysis")
    st.markdown("Understanding who your potential customers are is the foundation of every business decision — from product pricing to marketing channels. This section maps the demographic landscape of your 2,000 survey respondents.")

    # Row 1: Age & Gender
    st.markdown('<div class="section-header">Age & Gender Profile</div>', unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        age_order = ["Under 18","18-22","23-27","28-34","35-44","45+"]
        age_counts = dff["age_group"].value_counts().reindex(age_order).fillna(0).reset_index()
        age_counts.columns = ["Age Group","Count"]
        age_counts["Pct"] = (age_counts["Count"]/len(dff)*100).round(1)
        fig_age = px.bar(age_counts, x="Age Group", y="Count",
                         color_discrete_sequence=[BRAND_GREEN], text="Pct",
                         title="Age group distribution")
        fig_age.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_age.update_layout(height=360, margin=dict(t=40,b=40),
                               xaxis_categoryorder="array",
                               xaxis_categoryarray=age_order)
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>18–27 year olds dominate</strong> the survey '
                    '(~65% combined), which maps precisely to India\'s Gen Z and early millennial cohort — '
                    'the thrift fashion early adopter base. The 18–22 segment is your core Instagram audience. '
                    'The 23–27 group has higher income and thus higher spend potential. '
                    'Design your first drops and Instagram content specifically for this 18–27 window.</div>',
                    unsafe_allow_html=True)

    with r1c2:
        gender_counts = dff["gender"].value_counts().reset_index()
        gender_counts.columns = ["Gender","Count"]
        fig_gender = px.pie(gender_counts, values="Count", names="Gender",
                            color_discrete_sequence=[BRAND_GREEN,"#534AB7","#BA7517","#888780"],
                            hole=0.5, title="Gender breakdown")
        fig_gender.update_traces(textinfo="label+percent")
        fig_gender.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_gender, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Female respondents lead at ~57%</strong>, '
                    'consistent with industry data showing women drive thrift and resale fashion. '
                    'However, male interest at ~37% is significant — streetwear and vintage athleisure '
                    'for men is an underserved niche in Indian thrift. Non-binary/gender-fluid at ~5% '
                    'is notable and correlates strongly with the Y2K aesthetic segment.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    # Row 2: City Tier & Occupation
    st.markdown('<div class="section-header">Geography & Occupation</div>', unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        city_order = ["Metro","Tier 2","Tier 3 / Small town","Rural"]
        city_counts = dff["city_tier"].value_counts().reindex(city_order).fillna(0).reset_index()
        city_counts.columns = ["City Tier","Count"]
        city_counts["Pct"] = (city_counts["Count"]/len(dff)*100).round(1)
        colors_city = [BRAND_GREEN,"#5DCAA5","#9FE1CB","#E1F5EE"]
        fig_city = px.funnel(city_counts, y="City Tier", x="Count",
                             color_discrete_sequence=colors_city,
                             title="Geographic reach by city tier")
        fig_city.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_city, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Metro cities account for ~56% of respondents</strong>, '
                    'which makes sense for a digital-first, Instagram-led business in its early phase. '
                    'However, Tier-2 cities at ~32% represent a significant and fast-growing opportunity — '
                    'especially for mystery boxes and drop shipping. Tier-3 shows meaningful interest '
                    'driven by price sensitivity, making the Bargain Hunter persona relevant beyond metros.</div>',
                    unsafe_allow_html=True)

    with r2c2:
        occ_counts = dff["occupation"].value_counts().reset_index()
        occ_counts.columns = ["Occupation","Count"]
        occ_counts["Pct"] = (occ_counts["Count"]/len(dff)*100).round(1)
        fig_occ = px.bar(occ_counts, x="Pct", y="Occupation", orientation="h",
                         color_discrete_sequence=[PURPLE], text="Pct",
                         title="Occupation breakdown")
        fig_occ.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_occ.update_layout(height=360, margin=dict(t=40,b=10,r=50),
                               yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_occ, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Students (45%) and working professionals (37%)</strong> '
                    'dominate, together accounting for 82% of respondents. Students are price-sensitive '
                    'but highly style-conscious and socially active — perfect for mystery boxes and UGC '
                    'campaigns. Working professionals have higher disposable income — target them with '
                    'premium curated drops and styling services.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    # Row 3: Income + Age × Intent heatmap
    st.markdown('<div class="section-header">Income Profile & Age × Intent Cross-Analysis</div>', unsafe_allow_html=True)
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        inc_order = ["Below 10k","10k-25k","25k-50k","50k-1L","Above 1L"]
        inc_counts = dff["monthly_income_band"].value_counts().reindex(inc_order).fillna(0).reset_index()
        inc_counts.columns = ["Income Band","Count"]
        inc_counts["Pct"] = (inc_counts["Count"]/len(dff)*100).round(1)
        fig_inc = px.bar(inc_counts, x="Income Band", y="Count", text="Pct",
                         color="Count", color_continuous_scale="Greens",
                         title="Monthly income distribution (INR)")
        fig_inc.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_inc.update_layout(height=360, margin=dict(t=40,b=60), showlegend=False,
                               xaxis_categoryorder="array",
                               xaxis_categoryarray=inc_order)
        st.plotly_chart(fig_inc, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>58% earn below ₹25,000/month</strong> — '
                    'confirming price sensitivity as a critical design constraint. Your pricing '
                    'strategy (mystery boxes at ₹499–₹1,799; outfits at ₹800–₹3,500) fits this '
                    'income curve well. The 25k–50k band (~25%) is your sweet spot for premium '
                    'curated drops. Above ₹1L is a small but high-value styling service audience.</div>',
                    unsafe_allow_html=True)

    with r3c2:
        age_intent = dff.groupby(["age_group","purchase_intent"]).size().reset_index(name="Count")
        age_intent_piv = age_intent.pivot(index="age_group", columns="purchase_intent", values="Count").fillna(0)
        age_intent_piv = age_intent_piv.reindex(age_order)
        age_intent_pct = age_intent_piv.div(age_intent_piv.sum(axis=1), axis=0).round(3)*100
        fig_hm = px.imshow(age_intent_pct.T,
                           color_continuous_scale="Greens",
                           aspect="auto", text_auto=".1f",
                           title="Purchase intent % by age group",
                           labels=dict(color="% of age group"))
        fig_hm.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_hm, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>18–22 year olds show the highest "Interested" %</strong>, '
                    'making them both your most interested and most reachable segment via Instagram. '
                    'The 23–27 cohort has a large "Maybe" segment — these are convertible with the '
                    'right social proof or one-time discount offer. Older segments (35+) skew toward '
                    '"Maybe" or "Not Interested", suggesting limited ROI for broad-age targeting.</div>',
                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — FASHION BEHAVIOUR
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("## 👗 Fashion Behaviour Analysis")
    st.markdown("This section explores how respondents currently engage with fashion — their style identity, shopping frequency, sustainability attitudes, and channel preferences. These are the primary clustering variables that define your customer segments.")

    st.markdown('<div class="section-header">Style Identity & Fashion Psychographics</div>', unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        style_counts = dff["style_primary"].value_counts().reset_index()
        style_counts.columns = ["Style","Count"]
        style_counts["Pct"] = (style_counts["Count"]/len(dff)*100).round(1)
        style_colors = {"Y2K / Retro":"#D85A30","Streetwear":"#534AB7","Minimal / Clean girl":"#1D9E75",
                        "Cottagecore / Boho":"#BA7517","Sporty / Athleisure":"#378ADD",
                        "Formal / Classic":"#888780","Dark academia":"#3C3489"}
        fig_style = px.bar(style_counts, y="Style", x="Count", orientation="h",
                           color="Style", color_discrete_map=style_colors,
                           text="Pct", title="Primary style preferences")
        fig_style.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_style.update_layout(height=380, showlegend=False,
                                 margin=dict(t=40,b=10,r=60),
                                 yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_style, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Y2K/Retro and Streetwear together account for ~28% each</strong> of '
                    'primary styles — making them the top priority for your first inventory builds. '
                    'Minimal/Clean girl is your third segment and represents higher-income buyers '
                    'with larger spend capacity. Cottagecore/Boho is an emerging trend with low '
                    'competition in the Indian thrift space — a differentiation opportunity.</div>',
                    unsafe_allow_html=True)

    with r1c2:
        fi_counts = dff["fashion_identity"].value_counts().reset_index()
        fi_counts.columns = ["Identity","Count"]
        fig_fi = px.pie(fi_counts, values="Count", names="Identity",
                        color_discrete_sequence=[BRAND_GREEN,PURPLE,CORAL,AMBER,BLUE],
                        hole=0.45, title="Fashion identity / motivation")
        fig_fi.update_traces(textinfo="label+percent", textfont_size=11)
        fig_fi.update_layout(height=380, margin=dict(t=40,b=10))
        st.plotly_chart(fig_fi, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>"Fashion as self-expression" is the dominant identity (~30%)</strong>, '
                    'directly validating the brand\'s positioning around unique, curated aesthetics. '
                    'The "Avoid fast fashion actively" cohort (~18%) aligns with your sustainability '
                    'narrative. Together these two groups (~48%) represent the highest-intent buyers — '
                    'they BUY thrift because of what it stands for, not just the price.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Sustainability & Shopping Frequency</div>', unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        sust_labels_order = ["Very important","Somewhat important","Occasionally consider","Not a priority"]
        sust_counts = dff["sustainability_score"].value_counts().reset_index()
        # sustainability_score is 1-4, map back
        sust_map = {1:"Not a priority",2:"Occasionally consider",3:"Somewhat important",4:"Very important"}
        dff_tmp = dff.copy()
        dff_tmp["sust_label"] = dff_tmp["sustainability_score"].map(sust_map)
        sust_counts2 = dff_tmp["sust_label"].value_counts().reindex(sust_labels_order[::-1]).fillna(0).reset_index()
        sust_counts2.columns = ["Sustainability","Count"]
        sust_counts2["Pct"] = (sust_counts2["Count"]/len(dff)*100).round(1)
        colors_sust = ["#E24B4A","#BA7517","#5DCAA5","#1D9E75"]
        fig_sust = px.bar(sust_counts2, y="Sustainability", x="Count", orientation="h",
                          color="Sustainability",
                          color_discrete_sequence=colors_sust,
                          text="Pct", title="Sustainability importance to respondents")
        fig_sust.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_sust.update_layout(height=360, showlegend=False,
                                margin=dict(t=40,b=10,r=60))
        st.plotly_chart(fig_sust, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~52% consider sustainability at least "somewhat important"</strong>, '
                    'and ~22% say it actively drives their decisions. This is a strong foundation '
                    'for your brand\'s sustainability narrative — but note that ~28% are indifferent. '
                    'For the price-sensitive majority, lead with affordability and uniqueness; '
                    'layer the sustainability story as a brand differentiator, not the lead hook.</div>',
                    unsafe_allow_html=True)

    with r2c2:
        freq_order = ["Multiple times a month","Once a month","Once every 2-3 months","Few times a year","Rarely"]
        freq_counts = dff["shop_frequency"].value_counts().reindex(freq_order).fillna(0).reset_index()
        freq_counts.columns = ["Frequency","Count"]
        freq_counts["Pct"] = (freq_counts["Count"]/len(dff)*100).round(1)
        fig_freq = px.bar(freq_counts, x="Frequency", y="Count", text="Pct",
                          color_discrete_sequence=[BLUE],
                          title="Shopping frequency")
        fig_freq.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_freq.update_layout(height=360, margin=dict(t=40,b=100),
                                xaxis_tickangle=-20)
        st.plotly_chart(fig_freq, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~42% shop "Once a month" or more frequently</strong>, '
                    'suggesting a regular buying cadence that can be captured with monthly drops '
                    'and subscription boxes. The 35% "Once every 2–3 months" cohort is ideal '
                    'for seasonal push notifications and festival-themed drops. Only ~15% shop '
                    'rarely — these are your hardest targets for repeat purchase.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Purchase Influences & Discovery Channels</div>', unsafe_allow_html=True)
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        inf_counts = dff["purchase_influence"].value_counts().reset_index()
        inf_counts.columns = ["Influence","Count"]
        inf_counts["Pct"] = (inf_counts["Count"]/len(dff)*100).round(1)
        fig_inf = px.treemap(inf_counts, path=["Influence"], values="Count",
                             color="Count", color_continuous_scale="Greens",
                             title="What influences purchase decisions")
        fig_inf.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_inf, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Price/Affordability and Social Media Trends '
                    'are the top two influences</strong> — a direct signal to keep your Instagram '
                    'content trend-forward and price messaging transparent. Personal Expression is '
                    'the third driver, validating the aesthetic-curation approach. Brand reputation '
                    'matters less early on — focus on community trust over brand prestige.</div>',
                    unsafe_allow_html=True)

    with r3c2:
        disc_counts = dff["discovery_channel"].value_counts().reset_index()
        disc_counts.columns = ["Channel","Count"]
        disc_counts["Pct"] = (disc_counts["Count"]/len(dff)*100).round(1)
        fig_disc = px.bar(disc_counts, x="Pct", y="Channel", orientation="h",
                          color_discrete_sequence=[AMBER], text="Pct",
                          title="Preferred discovery channels")
        fig_disc.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_disc.update_layout(height=360, showlegend=False,
                                margin=dict(t=40,b=10,r=60),
                                yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_disc, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Instagram/Reels dominates at ~42%</strong> — '
                    'perfectly validating your Instagram-first strategy. WhatsApp drops at ~20% '
                    'suggest a strong community group / broadcast channel strategy should run '
                    'in parallel. Website/online store at ~17% shows a segment ready for direct '
                    'checkout — a Shopify or Instamojo store is worth building by Month 3–6.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Style × Purchase Intent Cross-Analysis</div>', unsafe_allow_html=True)
    style_intent = dff.groupby(["style_primary","purchase_intent"]).size().reset_index(name="Count")
    style_intent_piv = style_intent.pivot(index="style_primary", columns="purchase_intent", values="Count").fillna(0)
    style_intent_pct = style_intent_piv.div(style_intent_piv.sum(axis=1),axis=0)*100
    fig_si = px.bar(style_intent_pct.reset_index().melt(id_vars="style_primary"),
                    x="style_primary", y="value", color="purchase_intent",
                    color_discrete_map=INTENT_COLORS, barmode="stack",
                    labels={"value":"% of style group","style_primary":"Style"},
                    title="Purchase intent breakdown by primary style")
    fig_si.update_layout(height=380, margin=dict(t=40,b=80),
                          xaxis_tickangle=-15, yaxis_title="% within style group")
    st.plotly_chart(fig_si, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>Y2K/Retro and Streetwear show the highest "Interested" proportions</strong>, '
                'confirming these are your highest-converting style segments and should be prioritised '
                'in early inventory sourcing. Minimal/Clean girl has a higher "Maybe" share — this '
                'segment needs stronger social proof (reviews, styled photos) to convert. Formal/Classic '
                'skews toward "Not Interested", suggesting lower ROI for formal workwear drops early on.</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — BUDGET & SPEND
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("## 💰 Budget & Spending Analysis")
    st.markdown("Spend capacity and willingness to pay (WTP) analysis directly informs your pricing architecture. This tab maps income distribution against spending behaviour and reveals pricing sweet spots for each product offering.")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Median Monthly Spend", f"₹{int(dff['spend_numeric'].median()):,}")
    c2.metric("Mean Outfit WTP", f"₹{int(dff['outfit_spend_numeric'].mean()):,}")
    c3.metric("High-spend Segment (>₹2,500/mo)", f"{(dff['monthly_fashion_spend'].isin(['2500-5000','Above 5000'])).sum()}")
    c4.metric("Would Buy Mystery Box", f"{(~dff['mystery_box_wtp'].eq('Would not buy')).sum()}")

    st.markdown("---")
    st.markdown('<div class="section-header">Monthly Fashion Spend & Outfit WTP</div>', unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        spend_order = ["Under 500","500-1000","1000-2500","2500-5000","Above 5000"]
        spend_intent = dff.groupby(["monthly_fashion_spend","purchase_intent"]).size().reset_index(name="Count")
        spend_intent_piv = spend_intent.pivot(index="monthly_fashion_spend", columns="purchase_intent", values="Count").fillna(0)
        spend_intent_piv = spend_intent_piv.reindex([s for s in spend_order if s in spend_intent_piv.index])
        spend_pct = spend_intent_piv.div(spend_intent_piv.sum(axis=1),axis=0)*100
        fig_sp = px.bar(spend_pct.reset_index().melt(id_vars="monthly_fashion_spend"),
                        x="monthly_fashion_spend", y="value", color="purchase_intent",
                        color_discrete_map=INTENT_COLORS, barmode="stack",
                        title="Purchase intent by monthly spend band",
                        labels={"value":"% of spend group","monthly_fashion_spend":"Monthly Spend"})
        fig_sp.update_layout(height=370, margin=dict(t=40,b=60), xaxis_tickangle=-15)
        st.plotly_chart(fig_sp, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>"Interested" grows steadily with monthly spend</strong>, '
                    'confirming that higher-spending buyers are more likely to try thrift. This counter-intuitive '
                    'finding (affluent buyers choosing thrift) is well-documented globally — it\'s driven by '
                    'uniqueness-seeking, not just price. Your premium drops and styling service should explicitly '
                    'target the ₹2,500–₹5,000/month segment, while mystery boxes serve the ₹500–₹1,000 cohort.</div>',
                    unsafe_allow_html=True)

    with r1c2:
        outfit_order = ["Under 300","300-700","700-1500","1500-3000","Above 3000"]
        outfit_counts = dff["max_outfit_spend"].value_counts().reindex(outfit_order).fillna(0).reset_index()
        outfit_counts.columns = ["Max Outfit Spend","Count"]
        outfit_counts["Pct"] = (outfit_counts["Count"]/len(dff)*100).round(1)
        fig_out = px.bar(outfit_counts, x="Max Outfit Spend", y="Count", text="Pct",
                         color="Count", color_continuous_scale="Greens",
                         title="Max willingness to pay for one thrifted outfit")
        fig_out.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_out.update_layout(height=370, showlegend=False,
                               margin=dict(t=40,b=60),
                               xaxis_categoryorder="array",
                               xaxis_categoryarray=outfit_order)
        st.plotly_chart(fig_out, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>₹700–₹1,500 is the modal WTP for a single outfit (~35%)</strong>, '
                    'perfectly aligning with your planned pricing of ₹800–₹3,500 for curated outfit drops. '
                    'The ₹1,500–₹3,000 band captures ~25% — this is your premium audience. Price your '
                    'upcycled originals toward ₹1,500–₹3,000 and curated drops at ₹800–₹1,500 to maximise '
                    'addressable market coverage.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Mystery Box WTP & Subscription Intent</div>', unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        mbox_order = ["Under 500","500-800","800-1200","1200-1800","Would not buy"]
        mbox_counts = dff["mystery_box_wtp"].value_counts().reindex(mbox_order).fillna(0).reset_index()
        mbox_counts.columns = ["WTP","Count"]
        mbox_counts["Pct"] = (mbox_counts["Count"]/len(dff)*100).round(1)
        colors_mbox = [BRAND_GREEN,BRAND_GREEN,BRAND_GREEN,BRAND_GREEN,"#E24B4A"]
        fig_mb = px.bar(mbox_counts, x="WTP", y="Count", text="Pct",
                        color="WTP", color_discrete_sequence=colors_mbox,
                        title="Mystery box WTP per box (4–6 items)")
        fig_mb.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_mb.update_layout(height=370, showlegend=False,
                              margin=dict(t=40,b=60),
                              xaxis_categoryorder="array",
                              xaxis_categoryarray=mbox_order)
        st.plotly_chart(fig_mb, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~78% are willing to pay something for a mystery box</strong> — '
                    'strong validation for this product. The ₹500–₹800 band is the volume sweet spot (~32%), '
                    'confirming your planned entry price of ₹499–₹799. The 22% who "wouldn\'t buy" likely '
                    'have size or trust concerns — address these with a "build your box" feature that lets '
                    'customers specify size and aesthetic before purchase.</div>',
                    unsafe_allow_html=True)

    with r2c2:
        sub_order = ["Would subscribe immediately","Maybe after first box","Prefer one-off","No interest"]
        sub_counts = dff["subscription_intent"].value_counts().reindex(sub_order).fillna(0).reset_index()
        sub_counts.columns = ["Subscription Intent","Count"]
        sub_counts["Pct"] = (sub_counts["Count"]/len(dff)*100).round(1)
        colors_sub = [BRAND_GREEN,"#5DCAA5","#BA7517","#E24B4A"]
        fig_sub = px.bar(sub_counts, y="Subscription Intent", x="Count",
                         orientation="h", text="Pct",
                         color="Subscription Intent", color_discrete_sequence=colors_sub,
                         title="Subscription box intent")
        fig_sub.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_sub.update_layout(height=370, showlegend=False,
                               margin=dict(t=40,b=10,r=60))
        st.plotly_chart(fig_sub, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~18% would subscribe immediately</strong> and another '
                    '~33% would subscribe after a good first experience — together ~51% are subscription-receptive. '
                    'This is a massive LTV opportunity. Design your subscription funnel: sell the first box '
                    'at ₹499 with free personalisation, then offer ₹599–₹799/month recurring. '
                    'Focus on "first box experience" quality as your primary conversion lever.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Income vs Spend Correlation</div>', unsafe_allow_html=True)
    fig_scatter = px.scatter(dff.dropna(subset=["income_numeric","spend_numeric"]),
                             x="income_numeric", y="spend_numeric",
                             color="purchase_intent", color_discrete_map=INTENT_COLORS,
                             size_max=8, opacity=0.6,
                             facet_col="city_tier",
                             labels={"income_numeric":"Monthly Income (₹)","spend_numeric":"Monthly Fashion Spend (₹)"},
                             title="Income vs Fashion Spend by city tier and purchase intent",
                             trendline="ols")
    fig_scatter.update_layout(height=420, margin=dict(t=50,b=40))
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>Positive income-spend correlation is clearest in Metro respondents</strong>, '
                'while Tier-2 and Tier-3 show flatter slopes — indicating that in smaller cities, fashion spend '
                'is relatively fixed regardless of income. The "Interested" dots (green) cluster at higher spend '
                'levels across all tiers, confirming spend propensity as a strong purchase intent predictor. '
                'This validates including both income and spend in your regression model for spend estimation.</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Discount Sensitivity by Persona</div>', unsafe_allow_html=True)
    disc_persona = dff.groupby(["persona","discount_sensitivity"]).size().reset_index(name="Count")
    disc_order = ["Definitely yes","Likely yes","Unsure","Probably not","No"]
    disc_persona_piv = disc_persona.pivot(index="persona",columns="discount_sensitivity",values="Count").fillna(0)
    disc_persona_pct = disc_persona_piv.div(disc_persona_piv.sum(axis=1),axis=0)*100
    disc_colors = {k:v for k,v in zip(disc_order,[BRAND_GREEN,"#5DCAA5","#BA7517","#D85A30","#E24B4A"])}
    fig_disc2 = px.bar(disc_persona_pct.reset_index().melt(id_vars="persona"),
                       x="persona", y="value", color="variable",
                       color_discrete_map=disc_colors, barmode="stack",
                       title="Discount sensitivity distribution by persona",
                       labels={"value":"% of persona","variable":"Response"})
    fig_disc2.update_layout(height=380, margin=dict(t=40,b=60), xaxis_tickangle=-15)
    st.plotly_chart(fig_disc2, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>Bargain Hunters are overwhelmingly discount-driven (~55% "Definitely yes")</strong> '
                '— serve them with flash sales, first-purchase coupons, and bundle deals. '
                'Aesthetic Chasers and Conscious Spenders are less discount-motivated, '
                'responding more to curation quality and brand values. Avoid training '
                'premium segments to expect discounts — it erodes perceived brand value.</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — PRODUCT PREFERENCES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("## 🛍️ Product Preference Analysis")
    st.markdown("This section analyses multi-select responses for clothing types, colour palettes, accessories, and occasion drivers — the raw material for Association Rule Mining. These patterns reveal natural product bundles and co-purchase tendencies.")

    st.markdown('<div class="section-header">Clothing Type Preferences</div>', unsafe_allow_html=True)
    clothing_cols = [c for c in dff.columns if c.startswith("clothing_")]
    clothing_sums = dff[clothing_cols].fillna(0).sum().sort_values(ascending=True)
    clothing_labels = [c.replace("clothing_","").replace("_"," ").title() for c in clothing_sums.index]
    clothing_pct = (clothing_sums / len(dff) * 100).round(1)
    fig_cloth = px.bar(x=clothing_pct.values, y=clothing_labels, orientation="h",
                       color=clothing_pct.values, color_continuous_scale="Greens",
                       text=clothing_pct.values,
                       title="% of respondents selecting each clothing type")
    fig_cloth.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_cloth.update_layout(height=400, showlegend=False,
                             coloraxis_showscale=False,
                             margin=dict(t=40,b=20,r=60))
    st.plotly_chart(fig_cloth, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>Oversized tees and baggy jeans lead by a wide margin (~55–60%)</strong>, '
                'confirming streetwear and casual aesthetics as your highest-volume inventory categories. '
                'Jackets/blazers and crop tops are strong across multiple aesthetics (Y2K, minimal, streetwear) — '
                'these are "cross-aesthetic" items that serve multiple customer types and reduce inventory risk. '
                'Kurtis/ethnic tops show lower thrift interest, suggesting ethnic wear remains primarily a '
                'new-purchase category for most respondents — consider excluding from early drops.</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Colour Palette Preferences</div>', unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        colour_cols = [c for c in dff.columns if c.startswith("colour_")]
        colour_sums = dff[colour_cols].fillna(0).sum().sort_values(ascending=False)
        colour_labels = [c.replace("colour_","").replace("_"," ").title() for c in colour_sums.index]
        colour_pct = (colour_sums/len(dff)*100).round(1)
        colour_display_colors = {
            "Neutrals": "#D3D1C7", "Earthy Tones": "#BA7517",
            "Pastels": "#F4C0D1", "Bold Neon": "#E24B4A",
            "Vintage Washed": "#9FE1CB", "Prints Patterns": "#7F77DD",
            "Monochrome": "#444441"
        }
        bar_colors = [colour_display_colors.get(lbl, BRAND_GREEN) for lbl in colour_labels]
        fig_col = px.bar(x=colour_labels, y=colour_pct.values,
                         color=colour_labels,
                         color_discrete_sequence=bar_colors,
                         text=colour_pct.values,
                         title="Colour palette preferences (% selecting)")
        fig_col.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_col.update_layout(height=380, showlegend=False, margin=dict(t=40,b=60))
        st.plotly_chart(fig_col, use_container_width=True)

    with r2c2:
        st.markdown('<div class="insight-box">📌 <strong>Neutrals dominate colour preference (~55%)</strong>, '
                    'which aligns with the Minimal/Clean Girl and Formal/Classic personas. '
                    'Vintage Washed colours (~48%) — faded denim, washed pastels, distressed finishes — '
                    'are the defining thrift aesthetic and your strongest colour story to tell visually on Instagram. '
                    'Bold/Neon (~30%) is Y2K signature — source more of these for your Aesthetic Chaser drops. '
                    'Prints & Patterns (~35%) signals strong upcycling/rework demand — '
                    'a natural feed into your upcycled originals product line.</div>',
                    unsafe_allow_html=True)

        acc_cols = [c for c in dff.columns if c.startswith("accessory_")]
        acc_sums = dff[acc_cols].fillna(0).sum().sort_values(ascending=False)
        acc_labels = [c.replace("accessory_","").replace("_"," ").title() for c in acc_sums.index]
        acc_pct = (acc_sums/len(dff)*100).round(1)
        fig_acc = px.bar(x=acc_labels, y=acc_pct.values,
                         color_discrete_sequence=[PURPLE],
                         text=acc_pct.values,
                         title="Accessory interest (% selecting)")
        fig_acc.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_acc.update_layout(height=320, margin=dict(t=40,b=40))
        st.plotly_chart(fig_acc, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Jewellery and bags are the top accessory interests</strong> — '
                    'both easy to source thrifted and high-margin. Bundle accessories into outfit drops '
                    'to increase average order value. Caps and sunglasses (~40%) support streetwear bundles.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Occasion Drivers & Bundle Preference</div>', unsafe_allow_html=True)
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        occ_cols = [c for c in dff.columns if c.startswith("occasion_")]
        occ_sums = dff[occ_cols].fillna(0).sum().sort_values(ascending=False)
        occ_labels = [c.replace("occasion_","").replace("_"," ").title() for c in occ_sums.index]
        occ_pct = (occ_sums/len(dff)*100).round(1)
        fig_occ2 = px.bar(x=occ_labels, y=occ_pct.values,
                          color=occ_pct.values, color_continuous_scale="Oranges",
                          text=occ_pct.values,
                          title="Purchase occasion drivers (% selecting)")
        fig_occ2.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_occ2.update_layout(height=360, showlegend=False,
                                coloraxis_showscale=False, margin=dict(t=40,b=60))
        st.plotly_chart(fig_occ2, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Everyday/casual wear leads at ~72%</strong> — '
                    'confirming daily-wear items (tees, jeans, co-ords) should dominate inventory. '
                    'College/work at ~65% confirms the 18–27 student/early-professional audience. '
                    'Festivals at ~52% is crucial for Indian context — plan themed festival drops '
                    '4–6 weeks before Diwali, Holi, and Navratri. Travel at ~47% suggests a travel '
                    'capsule wardrobe is a viable seasonal product concept.</div>',
                    unsafe_allow_html=True)

    with r3c2:
        bundle_order = ["Prefer complete looks","Sometimes if it appeals","Prefer to mix myself","No preference"]
        bun_counts = dff["bundle_preference"].value_counts().reindex(bundle_order).fillna(0).reset_index()
        bun_counts.columns = ["Preference","Count"]
        bun_counts["Pct"] = (bun_counts["Count"]/len(dff)*100).round(1)
        colors_bun = [BRAND_GREEN,"#5DCAA5","#BA7517","#888780"]
        fig_bun = px.bar(bun_counts, y="Preference", x="Count",
                         orientation="h", color="Preference",
                         color_discrete_sequence=colors_bun,
                         text="Pct",
                         title="Bundle vs individual piece preference")
        fig_bun.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_bun.update_layout(height=360, showlegend=False,
                               margin=dict(t=40,b=10,r=60))
        st.plotly_chart(fig_bun, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~30% prefer complete ready-made looks</strong> and '
                    '~38% would consider bundles situationally — together ~68% are bundle-receptive. '
                    'This strongly validates your curated outfit drop strategy (top + bottom + accessory). '
                    'The ~22% who prefer mixing themselves still benefit from your individual item listings — '
                    'offer both complete-look bundles and individual items to maximise coverage.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Upcycling Interest by Style & Persona</div>', unsafe_allow_html=True)
    upc_persona = dff.groupby(["persona","upcycle_interest"]).size().reset_index(name="Count")
    upc_order_list = ["Very interested","Interested if priced right","Curious but unsure","Not interested"]
    upc_piv = upc_persona.pivot(index="persona",columns="upcycle_interest",values="Count").fillna(0)
    upc_pct = upc_piv.div(upc_piv.sum(axis=1),axis=0)*100
    upc_colors = {k:v for k,v in zip(upc_order_list,[BRAND_GREEN,"#5DCAA5","#BA7517","#E24B4A"])}
    fig_upc = px.bar(upc_pct.reset_index().melt(id_vars="persona"),
                     x="value", y="persona", color="variable",
                     color_discrete_map=upc_colors, barmode="stack",
                     orientation="h",
                     title="Upcycling interest by persona",
                     labels={"value":"% of persona","variable":"Upcycle Interest"})
    fig_upc.update_layout(height=360, margin=dict(t=40,b=10))
    st.plotly_chart(fig_upc, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>Aesthetic Chasers and Conscious Spenders show the highest upcycling enthusiasm (~70%+ interested)</strong>. '
                'These are your target buyers for reworked jackets, patchwork denim, and hand-painted pieces. '
                'Bargain Hunters show moderate interest but are price-sensitive about it — offer upcycled pieces '
                'at modest premiums (₹200–₹400 above base thrift price). Skeptics have low interest but even '
                '~20% of them are curious — a well-photographed upcycled piece can convert fence-sitters.</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — THRIFT ATTITUDES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("## ♻️ Thrift Attitudes & Conversion Funnel")
    st.markdown("This section analyses the conversion funnel from awareness to purchase intent — including prior thrift experience, purchase barriers, trust signals, and key motivators. This is the diagnostic layer that explains WHY respondents are or aren't ready to buy.")

    st.markdown('<div class="section-header">Prior Thrift Experience & Size Confidence</div>', unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        exp_order = ["Yes regularly","Yes a few times","No but open","No and unlikely"]
        exp_counts = dff["prior_thrift_experience"].value_counts().reindex(exp_order).fillna(0).reset_index()
        exp_counts.columns = ["Experience","Count"]
        exp_counts["Pct"] = (exp_counts["Count"]/len(dff)*100).round(1)
        colors_exp = [BRAND_GREEN,"#5DCAA5","#BA7517","#E24B4A"]
        fig_exp = px.funnel(exp_counts, y="Experience", x="Count",
                            color_discrete_sequence=colors_exp,
                            title="Prior thrift shopping experience")
        fig_exp.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_exp, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~35% have bought thrift regularly or a few times</strong> — '
                    'your warm audience who just needs the right brand to trust. '
                    'The ~40% "No but open" cohort is your biggest growth opportunity — '
                    'they are not thrift buyers yet but they\'re receptive. Target them with '
                    'first-purchase offers, hygiene assurance messaging, and UGC reviews. '
                    'Only ~18% are firmly unlikely to buy thrift.</div>',
                    unsafe_allow_html=True)

    with r1c2:
        size_order = ["Very confident","Somewhat confident","Unsure - it concerns me","Not confident at all"]
        size_counts = dff["size_confidence"].value_counts().reindex(size_order).fillna(0).reset_index()
        size_counts.columns = ["Size Confidence","Count"]
        size_counts["Pct"] = (size_counts["Count"]/len(dff)*100).round(1)
        colors_size = [BRAND_GREEN,"#5DCAA5","#BA7517","#E24B4A"]
        fig_size = px.bar(size_counts, x="Size Confidence", y="Count", text="Pct",
                          color="Size Confidence", color_discrete_sequence=colors_size,
                          title="Size confidence for thrift shopping")
        fig_size.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_size.update_layout(height=360, showlegend=False,
                                margin=dict(t=40,b=80), xaxis_tickangle=-10)
        st.plotly_chart(fig_size, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~38% have concerns about finding the right size</strong> — '
                    'this is your single biggest conversion barrier after experience. Tackle it directly: '
                    'provide detailed measurements (not just S/M/L), offer size-filtered browsing, '
                    'and add a "fits like" comparison (e.g. "fits like a Zara M"). Consider a '
                    '"size guarantee" policy — if it doesn\'t fit, exchange for free.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Purchase Barriers & Concerns</div>', unsafe_allow_html=True)
    concern_counts = dff["top_concern"].value_counts().reset_index()
    concern_counts.columns = ["Concern","Count"]
    concern_counts["Pct"] = (concern_counts["Count"]/len(dff)*100).round(1)
    concern_colors_list = ["#E24B4A","#D85A30","#BA7517","#888780","#534AB7",BRAND_GREEN]
    fig_concern = px.bar(concern_counts.sort_values("Count",ascending=True),
                         y="Concern", x="Count", orientation="h",
                         color="Concern", color_discrete_sequence=concern_colors_list,
                         text="Pct",
                         title="Top purchase concerns / barriers for thrift shopping")
    fig_concern.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_concern.update_layout(height=380, showlegend=False,
                               margin=dict(t=40,b=10,r=60))
    st.plotly_chart(fig_concern, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>Hygiene/Cleanliness and Quality/Wear & Tear are the top barriers</strong>, '
                'together cited by ~50% of respondents with a concern. These are solvable with clear '
                'communication: show your washing/steaming process in Instagram Stories, add a "quality '
                'check" badge to each listing, and offer a "1-week wear test" return window. '
                'Social stigma at ~5% is low — thrift no longer carries significant stigma among '
                'India\'s urban 18–30 demographic, which is your target market.</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Digital Trust & Return Policy Sensitivity</div>', unsafe_allow_html=True)
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        trust_counts = dff["digital_trust_score"].value_counts().reset_index()
        trust_counts.columns = ["Trust Signal","Count"]
        trust_counts["Pct"] = (trust_counts["Count"]/len(dff)*100).round(1)
        fig_trust = px.pie(trust_counts, values="Count", names="Trust Signal",
                           color_discrete_sequence=[BRAND_GREEN,BLUE,AMBER,GRAY],
                           hole=0.45,
                           title="What builds digital trust for online thrift buying")
        fig_trust.update_traces(textinfo="label+percent", textfont_size=11)
        fig_trust.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_trust, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Reviews and tagged photos are the #1 trust builder (~35%)</strong> — '
                    'invest early in getting customers to post tagged content after purchase. '
                    'Create a "post and get 10% off next order" incentive. Clear size guides (~30%) '
                    'confirm the sizing anxiety finding above. COD/easy return at ~20% is a '
                    'dealbreaker for hesitant buyers — offer COD where operationally feasible.</div>',
                    unsafe_allow_html=True)

    with r3c2:
        ret_order = ["Would stop me","Makes me hesitate","Comfortable with it","Depends on price"]
        ret_counts = dff["return_policy_sensitivity"].value_counts().reindex(ret_order).fillna(0).reset_index()
        ret_counts.columns = ["Response","Count"]
        ret_counts["Pct"] = (ret_counts["Count"]/len(dff)*100).round(1)
        colors_ret = ["#E24B4A","#BA7517",BRAND_GREEN,"#888780"]
        fig_ret = px.bar(ret_counts, x="Response", y="Count", text="Pct",
                         color="Response", color_discrete_sequence=colors_ret,
                         title="Return policy sensitivity")
        fig_ret.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_ret.update_layout(height=360, showlegend=False,
                               margin=dict(t=40,b=80), xaxis_tickangle=-10)
        st.plotly_chart(fig_ret, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~40% would be stopped or hesitate without a return option</strong> — '
                    'meaning a hard no-returns policy kills 2 in 5 potential customers. '
                    'Offer an exchange-only policy (no cash refunds) — this protects your margins '
                    'while reducing the psychological barrier. For items above ₹1,500, '
                    'consider a 7-day exchange window as a premium trust signal.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Purchase Motivators & UGC Propensity</div>', unsafe_allow_html=True)
    r4c1, r4c2 = st.columns(2)

    with r4c1:
        mot_counts = dff["purchase_motivator"].value_counts().reset_index()
        mot_counts.columns = ["Motivator","Count"]
        mot_counts["Pct"] = (mot_counts["Count"]/len(dff)*100).round(1)
        fig_mot = px.treemap(mot_counts, path=["Motivator"], values="Count",
                             color="Count", color_continuous_scale="Greens",
                             title="What motivates purchase from a thrift brand")
        fig_mot.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_mot, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Great curation and unique pieces are the top motivators</strong> — '
                    'these are directly in your control. Low prices is important but ranks below curation, '
                    'which means buyers are willing to pay a fair price for well-curated pieces. '
                    'This validates premium pricing for your drops. Social proof (reviews) '
                    'is a top-5 motivator — prioritise this in your first 3 months.</div>',
                    unsafe_allow_html=True)

    with r4c2:
        ugc_order_list = ["Yes regularly","Occasionally","Engage but rarely post","No"]
        ugc_counts = dff["ugc_propensity"].value_counts().reindex(ugc_order_list).fillna(0).reset_index()
        ugc_counts.columns = ["UGC Behaviour","Count"]
        ugc_counts["Pct"] = (ugc_counts["Count"]/len(dff)*100).round(1)
        colors_ugc = [BRAND_GREEN,"#5DCAA5","#BA7517","#888780"]
        fig_ugc = px.pie(ugc_counts, values="Count", names="UGC Behaviour",
                         color_discrete_sequence=colors_ugc,
                         hole=0.45,
                         title="Social media content creation (UGC propensity)")
        fig_ugc.update_traces(textinfo="label+percent")
        fig_ugc.update_layout(height=360, margin=dict(t=40,b=10))
        st.plotly_chart(fig_ugc, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>~15% post fashion content regularly and ~28% do so occasionally</strong> — '
                    'meaning 43% of your buyers are potential UGC creators. This is extraordinarily high '
                    'for a fashion brand and is your biggest free marketing asset. '
                    'Build a structured creator programme early: identify these buyers, send them '
                    'surprise upgrades or early access, and incentivise tagging. '
                    'A 500-follower micro-influencer who genuinely loves your brand outperforms '
                    'a paid 100K-follower endorsement every time.</div>',
                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown("## 📊 Correlation & Relationship Analysis")
    st.markdown("This section examines statistical relationships between key variables — identifying which factors most strongly co-vary with purchase intent, spend, and sustainability. These findings directly inform which features matter most for predictive modelling.")

    # Numeric correlation heatmap
    st.markdown('<div class="section-header">Numeric Feature Correlation Heatmap</div>', unsafe_allow_html=True)
    num_features = [
        "sustainability_score","spend_numeric","outfit_spend_numeric","income_numeric",
        "purchase_intent_encoded","age_group_encoded","city_tier_encoded",
        "monthly_fashion_spend_encoded","max_outfit_spend_encoded","mystery_box_wtp_encoded",
        "discount_sensitivity_encoded","upcycle_interest_encoded","prior_thrift_experience_encoded",
        "size_confidence_encoded","digital_trust_score_encoded","return_policy_sensitivity_encoded",
        "subscription_intent_encoded","ugc_propensity_encoded","gifting_behaviour_encoded",
    ]
    available_num = [c for c in num_features if c in df.columns]
    corr_df = dff[available_num].dropna().corr().round(3)
    short_names = [c.replace("_encoded","").replace("_"," ").title()[:20] for c in available_num]

    fig_heatmap = px.imshow(
        corr_df,
        x=short_names, y=short_names,
        color_continuous_scale="RdYlGn",
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
        title="Pearson correlation matrix — key numeric variables"
    )
    fig_heatmap.update_traces(textfont_size=8)
    fig_heatmap.update_layout(height=600, margin=dict(t=50,b=80,l=150,r=20),
                               xaxis_tickangle=-40, xaxis_tickfont_size=9,
                               yaxis_tickfont_size=9)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>Key correlations to note:</strong><br>'
                '• <strong>Income ↔ Spend</strong>: Moderate positive (ρ ≈ 0.55) — income predicts spend but not perfectly, meaning lifestyle and identity also matter<br>'
                '• <strong>Prior thrift experience ↔ Purchase intent</strong>: Strong negative (encoded inversely — higher = less likely), confirming experience is the strongest predictor for the classifier<br>'
                '• <strong>Sustainability score ↔ Upcycle interest</strong>: Positive (~0.45) — your sustainability audience is your upcycling audience<br>'
                '• <strong>Discount sensitivity ↔ Income</strong>: Negative — lower income = higher discount motivation, confirming Bargain Hunter persona characteristics<br>'
                '• <strong>Size confidence ↔ Purchase intent</strong>: Meaningful — poor size confidence suppresses intent</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Top Correlates with Purchase Intent</div>', unsafe_allow_html=True)
    if "purchase_intent_encoded" in corr_df.columns:
        intent_corr = corr_df["purchase_intent_encoded"].drop("purchase_intent_encoded").sort_values()
        intent_corr_df = pd.DataFrame({"Feature": intent_corr.index, "Correlation": intent_corr.values})
        intent_corr_df["Feature"] = [f.replace("_encoded","").replace("_"," ").title() for f in intent_corr_df["Feature"]]
        intent_corr_df["Color"] = intent_corr_df["Correlation"].apply(lambda x: BRAND_GREEN if x > 0 else CORAL)
        fig_ic = px.bar(intent_corr_df, x="Correlation", y="Feature", orientation="h",
                        color="Correlation", color_continuous_scale="RdYlGn",
                        color_continuous_midpoint=0,
                        title="Correlation with Purchase Intent (encoded: 0=Interested, 1=Maybe, 2=Not Interested)")
        fig_ic.update_layout(height=500, margin=dict(t=50,b=20,l=200),
                              coloraxis_showscale=False,
                              yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_ic, use_container_width=True)
        st.markdown('<div class="insight-box">📌 <strong>Interpretation note:</strong> Purchase intent is encoded '
                    '0=Interested, 1=Maybe, 2=Not Interested — so negative correlations mean the '
                    'variable pushes toward "Interested" (desired). Prior thrift experience and '
                    'sustainability score show strong negative correlations — people with more '
                    'experience and stronger sustainability values are more likely to be "Interested". '
                    'Return policy sensitivity and size confidence show positive correlations — '
                    'when these concerns are high, respondents skew toward "Not Interested".</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Spend vs Sustainability × Purchase Intent (3-way)</div>', unsafe_allow_html=True)
    fig_3way = px.scatter(dff.dropna(subset=["spend_numeric","sustainability_score"]),
                          x="spend_numeric", y="sustainability_score",
                          color="purchase_intent",
                          color_discrete_map=INTENT_COLORS,
                          size="outfit_spend_numeric",
                          size_max=15,
                          opacity=0.7,
                          labels={"spend_numeric":"Monthly Fashion Spend (₹)",
                                  "sustainability_score":"Sustainability Score (1–4)",
                                  "outfit_spend_numeric":"Outfit WTP"},
                          title="Spend vs Sustainability — bubble size = outfit WTP, colour = purchase intent")
    fig_3way.update_layout(height=420, margin=dict(t=50,b=40))
    st.plotly_chart(fig_3way, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>The upper-right quadrant (high spend + high sustainability) is dominated by green dots (Interested)</strong> — '
                'this is your premium Conscious Spender persona and the most commercially valuable segment. '
                'Large bubbles in this quadrant indicate high outfit WTP, confirming premium pricing viability. '
                'The lower-left (low spend + low sustainability) is mostly amber/red — your lowest-priority segment. '
                'This visualisation identifies the clear "high-value buyer fingerprint": spend above ₹1,500/mo '
                'AND sustainability score ≥ 3. Target these 400+ respondents first for your beta launch.</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Clothing × Colour Co-occurrence (Association Preview)</div>', unsafe_allow_html=True)
    binary_cols_for_corr = [c for c in dff.columns if c.startswith(("clothing_","colour_","accessory_"))]
    binary_df = dff[binary_cols_for_corr].fillna(0)
    binary_corr = binary_df.corr().round(2)
    short_bin_names = [c.replace("clothing_","👕 ").replace("colour_","🎨 ").replace("accessory_","👜 ").replace("_"," ").title() for c in binary_cols_for_corr]
    fig_bin_hm = px.imshow(binary_corr, x=short_bin_names, y=short_bin_names,
                            color_continuous_scale="Greens", zmin=0, zmax=0.6,
                            aspect="auto", text_auto=".2f",
                            title="Co-selection correlation — clothing × colour × accessories")
    fig_bin_hm.update_traces(textfont_size=7)
    fig_bin_hm.update_layout(height=550, margin=dict(t=50,b=100,l=160,r=20),
                              xaxis_tickangle=-45, xaxis_tickfont_size=8,
                              yaxis_tickfont_size=8)
    st.plotly_chart(fig_bin_hm, use_container_width=True)
    st.markdown('<div class="insight-box">📌 <strong>This is your Association Rule Mining preview.</strong> '
                'High co-occurrence values (darker green cells) reveal natural product bundles — '
                'e.g. oversized tees correlate with bold/neon colours (Y2K bundle), '
                'jackets/blazers with neutrals (minimal bundle), dresses with earthy tones (boho bundle). '
                'In Phase 2, run Apriori on the binary transaction matrix to extract '
                'formal rules (support, confidence, lift) for building recommended bundles.</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 10 — CUSTOMER SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[9]:
    st.markdown("## 🎯 Customer Segment Profiling")
    st.markdown("This section deep-dives into the 6 synthetic personas — the pre-defined segment prototypes used to generate the dataset. These personas serve as the ground-truth basis for validating your future K-Means clustering results.")

    # Overview cards
    st.markdown('<div class="section-header">Segment Overview</div>', unsafe_allow_html=True)
    persona_meta = {
        "Aesthetic Chaser":  ("28%", "18–24", "Metro", "Y2K / Streetwear", "₹700–1,500", "High"),
        "Conscious Spender": ("22%", "23–30", "Metro/T2", "Minimal / Clean", "₹1,500–3,000", "Very High"),
        "Bargain Hunter":    ("20%", "18–28", "Tier 2/3", "Mixed", "₹300–800", "Moderate"),
        "Fence-Sitter":      ("15%", "22–35", "Mixed", "Mixed", "₹500–1,200", "Low-Moderate"),
        "Occasional Gifter": ("10%", "25–40", "Metro", "Classic/Mixed", "₹800–2,000", "Moderate"),
        "Skeptic":           ("5%",  "28–45", "Mixed", "Formal/Brand", "₹500–2,000", "Very Low"),
    }
    cols6 = st.columns(6)
    for col, (persona, (pct, age, city, style, spend, intent_strength)) in zip(cols6, persona_meta.items()):
        color = PERSONA_COLORS[persona]
        col.markdown(f"""<div style='background:{color}18;border:1.5px solid {color};border-radius:10px;padding:10px 8px;text-align:center'>
            <div style='font-size:12px;font-weight:600;color:{color}'>{persona}</div>
            <div style='font-size:18px;font-weight:700;color:{color};margin:4px 0'>{pct}</div>
            <div style='font-size:10px;color:#5F5E5A'>Age: {age}</div>
            <div style='font-size:10px;color:#5F5E5A'>{city}</div>
            <div style='font-size:10px;color:#5F5E5A'>{style}</div>
            <div style='font-size:10px;font-weight:500;color:{color}'>{spend}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    # Segment selector
    selected_persona = st.selectbox("Select a persona to deep-dive", list(persona_meta.keys()))
    persona_df = dff[dff["persona"] == selected_persona]
    pct_of_total = len(persona_df)/len(dff)*100

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Segment Size", f"{len(persona_df):,}")
    col_b.metric("% of Survey", f"{pct_of_total:.1f}%")
    col_c.metric("Median Spend", f"₹{int(persona_df['spend_numeric'].median()):,}/mo")
    col_d.metric("% Interested", f"{(persona_df['purchase_intent'].eq('Interested').sum()/len(persona_df)*100):.0f}%")

    p_c1, p_c2 = st.columns(2)

    with p_c1:
        # Intent pie
        int_counts = persona_df["purchase_intent"].value_counts().reset_index()
        int_counts.columns = ["Intent","Count"]
        fig_pint = px.pie(int_counts, values="Count", names="Intent",
                          color="Intent", color_discrete_map=INTENT_COLORS,
                          hole=0.5, title=f"{selected_persona} — Purchase intent")
        fig_pint.update_traces(textinfo="label+percent")
        fig_pint.update_layout(height=300, margin=dict(t=40,b=10))
        st.plotly_chart(fig_pint, use_container_width=True)

        # Style breakdown
        sty_counts = persona_df["style_primary"].value_counts().reset_index()
        sty_counts.columns = ["Style","Count"]
        fig_psty = px.bar(sty_counts, x="Style", y="Count",
                          color_discrete_sequence=[PERSONA_COLORS[selected_persona]],
                          title=f"Style preferences")
        fig_psty.update_layout(height=260, margin=dict(t=40,b=60), xaxis_tickangle=-15)
        st.plotly_chart(fig_psty, use_container_width=True)

    with p_c2:
        # Spider / radar chart for persona profile
        radar_features = ["sustainability_score","spend_numeric","outfit_spend_numeric",
                          "income_numeric","ugc_propensity_encoded","subscription_intent_encoded"]
        radar_labels = ["Sustainability","Monthly Spend","Outfit WTP","Income","UGC Activity","Sub Intent"]

        available_radar = [f for f in radar_features if f in persona_df.columns]
        available_labels = [radar_labels[i] for i,f in enumerate(radar_features) if f in persona_df.columns]

        # Normalise 0–1 across full dataset
        persona_means = []
        for feat in available_radar:
            mn = dff[feat].min()
            mx = dff[feat].max()
            val = persona_df[feat].mean()
            persona_means.append((val - mn) / (mx - mn + 1e-9))

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=persona_means + [persona_means[0]],
            theta=available_labels + [available_labels[0]],
            fill='toself',
            fillcolor=PERSONA_COLORS[selected_persona]+"40",
            line=dict(color=PERSONA_COLORS[selected_persona], width=2),
            name=selected_persona
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,1],
                                       tickfont_size=9)),
            showlegend=False, height=380,
            title=f"{selected_persona} — Normalised profile radar",
            margin=dict(t=50,b=10,l=40,r=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # All personas comparison
    st.markdown("---")
    st.markdown('<div class="section-header">All Personas — Comparative View</div>', unsafe_allow_html=True)

    comp_metric = st.selectbox("Compare by", ["spend_numeric","outfit_spend_numeric","sustainability_score","income_numeric"])
    comp_df = dff.groupby("persona")[comp_metric].mean().reset_index()
    comp_df.columns = ["Persona","Value"]
    comp_df["Color"] = comp_df["Persona"].map(PERSONA_COLORS)
    fig_comp = px.bar(comp_df, x="Persona", y="Value",
                      color="Persona", color_discrete_map=PERSONA_COLORS,
                      text=comp_df["Value"].round(0).astype(int),
                      title=f"Average {comp_metric.replace('_',' ').title()} by persona")
    fig_comp.update_traces(textposition="outside")
    fig_comp.update_layout(height=360, showlegend=False,
                            margin=dict(t=40,b=60,r=30))
    st.plotly_chart(fig_comp, use_container_width=True)

    # Multi-persona intent comparison
    st.markdown('<div class="section-header">Persona × Purchase Intent Matrix</div>', unsafe_allow_html=True)
    pi_cross = dff.groupby(["persona","purchase_intent"]).size().reset_index(name="Count")
    pi_piv = pi_cross.pivot(index="persona", columns="purchase_intent", values="Count").fillna(0)
    pi_pct = pi_piv.div(pi_piv.sum(axis=1),axis=0)*100

    fig_pi = px.bar(pi_pct.reset_index().melt(id_vars="persona"),
                    x="persona", y="value", color="variable",
                    color_discrete_map=INTENT_COLORS, barmode="stack",
                    title="Purchase intent breakdown by persona (%)",
                    labels={"value":"% of persona","variable":"Intent"})
    fig_pi.update_layout(height=380, margin=dict(t=40,b=80), xaxis_tickangle=-10)
    st.plotly_chart(fig_pi, use_container_width=True)

    st.markdown('<div class="insight-box">📌 <strong>Strategic prioritisation by persona:</strong><br>'
                '• <strong>Aesthetic Chaser (28%)</strong>: Your highest-intent, highest-Instagram-reach segment. Activate first with Y2K/streetwear drops and UGC incentives.<br>'
                '• <strong>Conscious Spender (22%)</strong>: Your highest LTV segment. Target with premium drops, sustainability storytelling, and styling services.<br>'
                '• <strong>Bargain Hunter (20%)</strong>: High volume, lower margin. Serve with mystery boxes, flash sales, and bundle deals.<br>'
                '• <strong>Fence-Sitter (15%)</strong>: Largest conversion opportunity. Target with first-purchase discounts, social proof, and easy returns.<br>'
                '• <strong>Occasional Gifter (10%)</strong>: Festival-season focused. Activate with gifting boxes and Diwali/birthday themed campaigns.<br>'
                '• <strong>Skeptic (5%)</strong>: Do not prioritise in Year 1. Convert passively through organic reach.</div>',
                unsafe_allow_html=True)
