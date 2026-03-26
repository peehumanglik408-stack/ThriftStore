# Thrift Fashion Analytics Dashboard

**A data-driven analytics dashboard for Peehu's curated thrift fashion business — built with Streamlit.**

---

## Overview

This dashboard provides full descriptive and diagnostic analytics of a 2,000-respondent synthetic consumer survey conducted across India, designed to support the launch and growth strategy of a curated thrift fashion brand. It covers business context, raw & cleaned data exploration, and deep exploratory data analysis (EDA) with actionable insights mapped to the core business strategy.

---

## Dashboard Tabs

| Tab | Contents |
|-----|----------|
| **Business Overview** | Strategy, product mix, target segments, growth objectives |
| **Raw Data** | Unfiltered dataset preview, shape, dtypes, missing values |
| **Cleaned Data** | Encoded & imputed dataset, transformation log |
| **EDA — Demographics** | Age, gender, city tier, occupation, income distributions |
| **EDA — Fashion Behaviour** | Style identity, shopping habits, sustainability, frequency |
| **EDA — Budget & Spend** | Spend distributions, WTP analysis, income vs spend correlations |
| **EDA — Product Preferences** | Clothing types, colour palettes, accessories, upcycling interest |
| **EDA — Thrift Attitudes** | Prior experience, concerns, discovery channels, motivators |
| **EDA — Correlations** | Heatmaps, cross-tabs, key variable relationships |
| **Customer Segments** | Persona distribution, segment profiling, spider charts |

---

## Project Structure

```
thrift_dashboard/
├── app.py                  # Main Streamlit application
├── data.csv                # Synthetic survey dataset (2000 rows × 56 cols)
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .streamlit/
    └── config.toml         # Streamlit theme configuration
```

---

## Local Setup

```bash
# 1. Clone your repository
git clone https://github.com/YOUR_USERNAME/thrift-dashboard.git
cd thrift-dashboard

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run app.py
```

---

## Deploy on Streamlit Community Cloud

1. Push this entire folder to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as the main file
4. Click **Deploy** — Streamlit handles the rest

> Make sure `data.csv` is committed to the repository alongside `app.py`.

---

## Dataset

- **Rows:** 2,000 synthetic survey respondents (India-wide)
- **Columns:** 56 features covering demographics, fashion preferences, spending behaviour, product interests, and thrift attitudes
- **Target variable:** `purchase_intent` — Interested / Maybe / Not Interested
- **Noise injected:** ~7% (contradictory responses, missing values, extreme spenders)

---

## Business Context

The dashboard is built to serve a curated thrift fashion startup targeting Gen Z and millennial buyers in India, with 7 product/service offerings:
1. Aesthetic-curated outfit drops
2. Upcycled & reworked originals
3. Mystery thrift boxes
4. Style profile & personal thrift styling
5. Thrift trade-in & community sourcing
6. Aesthetic digital lookbooks
7. Thrift event & pop-up drops

**Core objective:** Use data-driven decision making to identify the right customer segments, personalise recommendations, and drive 20%+ annual growth.

---

## Built With

- [Streamlit](https://streamlit.io) — Dashboard framework
- [Plotly](https://plotly.com/python/) — Interactive visualisations
- [Pandas](https://pandas.pydata.org) — Data manipulation
- [Scikit-learn](https://scikit-learn.org) — Data preprocessing utilities

---

*Dashboard created as part of the Thrift Fashion Business Analytics Project — Phase 1: Descriptive & Diagnostic Analysis.*
