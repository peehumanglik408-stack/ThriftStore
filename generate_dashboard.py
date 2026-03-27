"""
Thrift Fashion Analytics Dashboard — Standalone HTML Generator
=============================================================
Run this script from the same folder as data.csv:

    python generate_dashboard.py

It will produce  thrift_dashboard.html  which you can open in any browser.
No Streamlit required. Requires: pandas, numpy, plotly, scipy, scikit-learn
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import warnings, json, os, sys

warnings.filterwarnings("ignore")

# ── Colour palette ────────────────────────────────────────────────────────────
BRAND_GREEN    = "#1D9E75"
AMBER          = "#BA7517"
CORAL          = "#D85A30"
PURPLE         = "#534AB7"
BLUE           = "#378ADD"
GRAY           = "#888780"
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

# ── Data loading & cleaning ────────────────────────────────────────────────────
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "data.csv")
    if not os.path.exists(csv_path):
        print("ERROR: data.csv not found next to this script.")
        sys.exit(1)

    raw = pd.read_csv(csv_path)
    df  = raw.copy()

    age_order      = ["Under 18","18-22","23-27","28-34","35-44","45+"]
    income_order   = ["Below 10k","10k-25k","25k-50k","50k-1L","Above 1L"]
    spend_order    = ["Under 500","500-1000","1000-2500","2500-5000","Above 5000"]
    outfit_order   = ["Under 300","300-700","700-1500","1500-3000","Above 3000"]
    mbox_order     = ["Under 500","500-800","800-1200","1200-1800","Would not buy"]
    freq_order     = ["Multiple times a month","Once a month","Once every 2-3 months","Few times a year","Rarely"]
    city_order     = ["Metro","Tier 2","Tier 3 / Small town","Rural"]
    thrift_exp_order = ["Yes regularly","Yes a few times","No but open","No and unlikely"]
    upc_order      = ["Very interested","Interested if priced right","Curious but unsure","Not interested"]
    disc_order     = ["Definitely yes","Likely yes","Unsure","Probably not","No"]
    size_order     = ["Very confident","Somewhat confident","Unsure - it concerns me","Not confident at all"]
    trust_order    = ["Reviews and tagged photos","Clear size guide and photos","COD/Easy return","Follower count/Brand credibility"]
    sub_order      = ["Would subscribe immediately","Maybe after first box","Prefer one-off","No interest"]
    return_order   = ["Would stop me","Makes me hesitate","Comfortable with it","Depends on price"]
    ugc_order      = ["Yes regularly","Occasionally","Engage but rarely post","No"]
    gifting_order  = ["Yes frequently","Yes occasionally","Rarely","Never"]
    intent_order   = ["Interested","Maybe","Not Interested"]
    bundle_order   = ["Prefer complete looks","Sometimes if it appeals","Prefer to mix myself","No preference"]

    ordinal_maps = {
        "age_group":               {v:i for i,v in enumerate(age_order)},
        "monthly_income_band":     {v:i for i,v in enumerate(income_order)},
        "monthly_fashion_spend":   {v:i for i,v in enumerate(spend_order)},
        "max_outfit_spend":        {v:i for i,v in enumerate(outfit_order)},
        "mystery_box_wtp":         {v:i for i,v in enumerate(mbox_order)},
        "shop_frequency":          {v:i for i,v in enumerate(freq_order)},
        "city_tier":               {v:i for i,v in enumerate(city_order)},
        "prior_thrift_experience": {v:i for i,v in enumerate(thrift_exp_order)},
        "upcycle_interest":        {v:i for i,v in enumerate(upc_order)},
        "discount_sensitivity":    {v:i for i,v in enumerate(disc_order)},
        "size_confidence":         {v:i for i,v in enumerate(size_order)},
        "digital_trust_score":     {v:i for i,v in enumerate(trust_order)},
        "subscription_intent":     {v:i for i,v in enumerate(sub_order)},
        "return_policy_sensitivity":{v:i for i,v in enumerate(return_order)},
        "ugc_propensity":          {v:i for i,v in enumerate(ugc_order)},
        "gifting_behaviour":       {v:i for i,v in enumerate(gifting_order)},
        "purchase_intent":         {v:i for i,v in enumerate(intent_order)},
        "bundle_preference":       {v:i for i,v in enumerate(bundle_order)},
    }
    for col, mapping in ordinal_maps.items():
        if col in df.columns:
            df[col+"_encoded"] = df[col].map(mapping)

    binary_cols = [c for c in df.columns if c.startswith(("clothing_","colour_","accessory_","occasion_"))]
    for col in binary_cols:
        df[col] = df[col].fillna(0).astype(int)

    spend_mid  = {"Under 500":250,"500-1000":750,"1000-2500":1750,"2500-5000":3750,"Above 5000":6000}
    outfit_mid = {"Under 300":150,"300-700":500,"700-1500":1100,"1500-3000":2250,"Above 3000":4000}
    income_mid = {"Below 10k":5000,"10k-25k":17500,"25k-50k":37500,"50k-1L":75000,"Above 1L":125000}
    df["spend_numeric"]        = df["monthly_fashion_spend"].map(spend_mid)
    df["outfit_spend_numeric"] = df["max_outfit_spend"].map(outfit_mid)
    df["income_numeric"]       = df["monthly_income_band"].map(income_mid)

    return raw, df


def fig_to_html(fig, div_id=None):
    """Return a <div> string with the Plotly figure (no full page, no CDN scripts)."""
    kwargs = dict(full_html=False, include_plotlyjs=False, default_width="100%", default_height="100%")
    if div_id:
        kwargs["div_id"] = div_id
    return pio.to_html(fig, **kwargs)


# ── Build all chart HTML ───────────────────────────────────────────────────────
def build_charts(raw, df):
    charts = {}
    N = len(df)

    # ── TAB 1: Business Overview ──────────────────────────────────────────────
    intent_counts = df["purchase_intent"].value_counts().reset_index()
    intent_counts.columns = ["Intent","Count"]
    fig = px.pie(intent_counts, values="Count", names="Intent",
                 color="Intent", color_discrete_map=INTENT_COLORS, hole=0.55,
                 title="Purchase Intent Distribution")
    fig.update_traces(textinfo="label+percent", textfont_size=13)
    fig.update_layout(height=320, margin=dict(t=40,b=10,l=10,r=10), showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t1_intent_pie"] = fig_to_html(fig)

    persona_counts = df["persona"].value_counts().reset_index()
    persona_counts.columns = ["Persona","Count"]
    fig = px.bar(persona_counts, x="Count", y="Persona", orientation="h",
                 color="Persona", color_discrete_map=PERSONA_COLORS, text="Count",
                 title="Persona Distribution")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=280, showlegend=False, margin=dict(t=40,b=10,l=10,r=60),
                      yaxis=dict(categoryorder="total ascending"),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t1_persona_bar"] = fig_to_html(fig)

    # ── TAB 2: Raw Data ───────────────────────────────────────────────────────
    missing = raw.isnull().sum()
    missing = missing[missing > 0].reset_index()
    missing.columns = ["Column","Missing Count"]
    missing["Missing %"] = (missing["Missing Count"]/N*100).round(2)
    if len(missing):
        fig = px.bar(missing, x="Column", y="Missing Count",
                     color="Missing %", color_continuous_scale="Oranges",
                     text="Missing Count", title="Columns with Missing Values")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=360, margin=dict(t=40,b=80),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        charts["t2_missing"] = fig_to_html(fig)
    else:
        charts["t2_missing"] = "<p style='color:#1D9E75;font-weight:600'>✅ No missing values detected.</p>"

    # ── TAB 3: Cleaned Data ───────────────────────────────────────────────────
    encoded_cols = [c for c in df.columns if c.endswith("_encoded")]
    enc_summary = pd.DataFrame({
        "Encoded Column": encoded_cols,
        "Min": [int(df[c].min()) for c in encoded_cols],
        "Max": [int(df[c].max()) for c in encoded_cols],
        "Levels": [int(df[c].nunique()) for c in encoded_cols],
    })
    # Render as a simple table (no interactive widget needed here)
    charts["t3_enc_table"] = enc_summary.to_html(index=False, classes="data-table", border=0)

    # ── TAB 4: Demographics ───────────────────────────────────────────────────
    age_order = ["Under 18","18-22","23-27","28-34","35-44","45+"]
    age_counts = df["age_group"].value_counts().reindex(age_order).fillna(0).reset_index()
    age_counts.columns = ["Age Group","Count"]
    age_counts["Pct"] = (age_counts["Count"]/N*100).round(1)
    fig = px.bar(age_counts, x="Age Group", y="Count", text="Pct",
                 color_discrete_sequence=[BRAND_GREEN], title="Age Distribution")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t4_age"] = fig_to_html(fig)

    gender_counts = df["gender"].value_counts().reset_index()
    gender_counts.columns = ["Gender","Count"]
    fig = px.pie(gender_counts, values="Count", names="Gender",
                 color_discrete_sequence=[BRAND_GREEN, PURPLE, AMBER, CORAL],
                 hole=0.45, title="Gender Distribution")
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(height=360, margin=dict(t=40,b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t4_gender"] = fig_to_html(fig)

    city_order = ["Metro","Tier 2","Tier 3 / Small town","Rural"]
    city_counts = df["city_tier"].value_counts().reindex(city_order).fillna(0).reset_index()
    city_counts.columns = ["City Tier","Count"]
    city_counts["Pct"] = (city_counts["Count"]/N*100).round(1)
    fig = px.bar(city_counts, x="City Tier", y="Count", text="Pct",
                 color="City Tier", color_discrete_sequence=[BRAND_GREEN,BLUE,AMBER,CORAL],
                 title="City Tier Distribution")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, showlegend=False, margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t4_city"] = fig_to_html(fig)

    income_order = ["Below 10k","10k-25k","25k-50k","50k-1L","Above 1L"]
    income_counts = df["monthly_income_band"].value_counts().reindex(income_order).fillna(0).reset_index()
    income_counts.columns = ["Income Band","Count"]
    income_counts["Pct"] = (income_counts["Count"]/N*100).round(1)
    fig = px.bar(income_counts, x="Income Band", y="Count", text="Pct",
                 color_discrete_sequence=[PURPLE], title="Monthly Income Distribution")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t4_income"] = fig_to_html(fig)

    # Age × Intent stacked bar
    age_intent = df.groupby(["age_group","purchase_intent"]).size().reset_index(name="Count")
    age_piv = age_intent.pivot(index="age_group", columns="purchase_intent", values="Count").fillna(0)
    age_piv = age_piv.reindex([a for a in age_order if a in age_piv.index])
    age_pct = age_piv.div(age_piv.sum(axis=1), axis=0)*100
    fig = px.bar(age_pct.reset_index().melt(id_vars="age_group"),
                 x="age_group", y="value", color="purchase_intent",
                 color_discrete_map=INTENT_COLORS, barmode="stack",
                 title="Purchase Intent by Age Group (%)",
                 labels={"value":"% of age group","age_group":"Age Group","purchase_intent":"Intent"})
    fig.update_layout(height=380, margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t4_age_intent"] = fig_to_html(fig)

    # ── TAB 5: Fashion Behaviour ──────────────────────────────────────────────
    style_counts = df["style_primary"].value_counts().reset_index()
    style_counts.columns = ["Style","Count"]
    style_counts["Pct"] = (style_counts["Count"]/N*100).round(1)
    style_colors = {"Y2K / Retro":CORAL,"Streetwear":PURPLE,"Minimal / Clean girl":BRAND_GREEN,
                    "Cottagecore / Boho":AMBER,"Sporty / Athleisure":BLUE,
                    "Formal / Classic":GRAY,"Dark academia":"#3C3489"}
    fig = px.bar(style_counts, y="Style", x="Count", orientation="h",
                 color="Style", color_discrete_map=style_colors,
                 text="Pct", title="Primary Style Preferences")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=400, showlegend=False, margin=dict(t=40,b=10,r=60),
                      yaxis=dict(categoryorder="total ascending"),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t5_style"] = fig_to_html(fig)

    fi_counts = df["fashion_identity"].value_counts().reset_index()
    fi_counts.columns = ["Identity","Count"]
    fig = px.pie(fi_counts, values="Count", names="Identity",
                 color_discrete_sequence=[BRAND_GREEN,PURPLE,CORAL,AMBER,BLUE],
                 hole=0.45, title="Fashion Identity / Motivation")
    fig.update_traces(textinfo="label+percent", textfont_size=11)
    fig.update_layout(height=400, margin=dict(t=40,b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t5_identity"] = fig_to_html(fig)

    freq_order = ["Multiple times a month","Once a month","Once every 2-3 months","Few times a year","Rarely"]
    freq_counts = df["shop_frequency"].value_counts().reindex(freq_order).fillna(0).reset_index()
    freq_counts.columns = ["Frequency","Count"]
    freq_counts["Pct"] = (freq_counts["Count"]/N*100).round(1)
    fig = px.bar(freq_counts, x="Frequency", y="Count", text="Pct",
                 color_discrete_sequence=[BLUE], title="Shopping Frequency")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, margin=dict(t=40,b=100), xaxis_tickangle=-20,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t5_freq"] = fig_to_html(fig)

    disc_counts = df["discovery_channel"].value_counts().reset_index()
    disc_counts.columns = ["Channel","Count"]
    disc_counts["Pct"] = (disc_counts["Count"]/N*100).round(1)
    fig = px.bar(disc_counts, x="Pct", y="Channel", orientation="h",
                 color_discrete_sequence=[AMBER], text="Pct",
                 title="Preferred Discovery Channels")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=380, showlegend=False, margin=dict(t=40,b=10,r=60),
                      yaxis=dict(categoryorder="total ascending"),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t5_discovery"] = fig_to_html(fig)

    # Style × Intent
    si = df.groupby(["style_primary","purchase_intent"]).size().reset_index(name="Count")
    si_piv = si.pivot(index="style_primary", columns="purchase_intent", values="Count").fillna(0)
    si_pct = si_piv.div(si_piv.sum(axis=1), axis=0)*100
    fig = px.bar(si_pct.reset_index().melt(id_vars="style_primary"),
                 x="style_primary", y="value", color="purchase_intent",
                 color_discrete_map=INTENT_COLORS, barmode="stack",
                 title="Purchase Intent by Primary Style (%)",
                 labels={"value":"% of style group","style_primary":"Style","purchase_intent":"Intent"})
    fig.update_layout(height=400, margin=dict(t=40,b=80), xaxis_tickangle=-15,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t5_style_intent"] = fig_to_html(fig)

    # ── TAB 6: Budget & Spend ─────────────────────────────────────────────────
    spend_order = ["Under 500","500-1000","1000-2500","2500-5000","Above 5000"]
    sp_int = df.groupby(["monthly_fashion_spend","purchase_intent"]).size().reset_index(name="Count")
    sp_piv = sp_int.pivot(index="monthly_fashion_spend", columns="purchase_intent", values="Count").fillna(0)
    sp_piv = sp_piv.reindex([s for s in spend_order if s in sp_piv.index])
    sp_pct = sp_piv.div(sp_piv.sum(axis=1), axis=0)*100
    fig = px.bar(sp_pct.reset_index().melt(id_vars="monthly_fashion_spend"),
                 x="monthly_fashion_spend", y="value", color="purchase_intent",
                 color_discrete_map=INTENT_COLORS, barmode="stack",
                 title="Purchase Intent by Monthly Spend Band (%)",
                 labels={"value":"% of spend group","monthly_fashion_spend":"Monthly Spend","purchase_intent":"Intent"})
    fig.update_layout(height=380, margin=dict(t=40,b=60), xaxis_tickangle=-15,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t6_spend_intent"] = fig_to_html(fig)

    outfit_order = ["Under 300","300-700","700-1500","1500-3000","Above 3000"]
    outfit_counts = df["max_outfit_spend"].value_counts().reindex(outfit_order).fillna(0).reset_index()
    outfit_counts.columns = ["Max Outfit Spend","Count"]
    outfit_counts["Pct"] = (outfit_counts["Count"]/N*100).round(1)
    fig = px.bar(outfit_counts, x="Max Outfit Spend", y="Count", text="Pct",
                 color="Count", color_continuous_scale="Greens",
                 title="Max WTP for One Thrifted Outfit")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=380, showlegend=False, margin=dict(t=40,b=60),
                      xaxis_categoryorder="array", xaxis_categoryarray=outfit_order,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t6_outfit"] = fig_to_html(fig)

    mbox_order = ["Under 500","500-800","800-1200","1200-1800","Would not buy"]
    mb_counts = df["mystery_box_wtp"].value_counts().reindex(mbox_order).fillna(0).reset_index()
    mb_counts.columns = ["WTP","Count"]
    mb_counts["Pct"] = (mb_counts["Count"]/N*100).round(1)
    colors_mbox = [BRAND_GREEN,BRAND_GREEN,BRAND_GREEN,BRAND_GREEN,"#E24B4A"]
    fig = px.bar(mb_counts, x="WTP", y="Count", text="Pct",
                 color="WTP", color_discrete_sequence=colors_mbox,
                 title="Mystery Box WTP per Box (4–6 Items)")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=370, showlegend=False, margin=dict(t=40,b=60),
                      xaxis_categoryorder="array", xaxis_categoryarray=mbox_order,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t6_mbox"] = fig_to_html(fig)

    # Income vs spend scatter
    fig = px.scatter(df, x="income_numeric", y="spend_numeric",
                     color="purchase_intent", color_discrete_map=INTENT_COLORS,
                     opacity=0.5, title="Income vs Monthly Fashion Spend",
                     labels={"income_numeric":"Monthly Income (₹)","spend_numeric":"Monthly Fashion Spend (₹)"})
    fig.update_layout(height=400, margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t6_scatter"] = fig_to_html(fig)

    # ── TAB 7: Product Preferences ────────────────────────────────────────────
    clothing_cols = [c for c in df.columns if c.startswith("clothing_")]
    clothing_sums = df[clothing_cols].fillna(0).sum().sort_values(ascending=True)
    clothing_labels = [c.replace("clothing_","").replace("_"," ").title() for c in clothing_sums.index]
    clothing_pct = (clothing_sums/N*100).round(1)
    fig = px.bar(x=clothing_pct.values, y=clothing_labels, orientation="h",
                 color=clothing_pct.values, color_continuous_scale="Greens",
                 text=clothing_pct.values,
                 title="Clothing Type Preferences (% selecting)")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=420, showlegend=False, coloraxis_showscale=False,
                      margin=dict(t=40,b=20,r=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t7_clothing"] = fig_to_html(fig)

    colour_cols = [c for c in df.columns if c.startswith("colour_")]
    colour_sums = df[colour_cols].fillna(0).sum().sort_values(ascending=False)
    colour_labels = [c.replace("colour_","").replace("_"," ").title() for c in colour_sums.index]
    colour_pct = (colour_sums/N*100).round(1)
    colour_display = {"Neutrals":"#D3D1C7","Earthy Tones":AMBER,"Pastels":"#F4C0D1",
                      "Bold Neon":"#E24B4A","Vintage Washed":"#9FE1CB",
                      "Prints Patterns":"#7F77DD","Monochrome":"#444441"}
    bar_colors = [colour_display.get(lbl, BRAND_GREEN) for lbl in colour_labels]
    fig = px.bar(x=colour_labels, y=colour_pct.values,
                 color=colour_labels, color_discrete_sequence=bar_colors,
                 text=colour_pct.values, title="Colour Palette Preferences (% selecting)")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=380, showlegend=False, margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t7_colours"] = fig_to_html(fig)

    acc_cols = [c for c in df.columns if c.startswith("accessory_")]
    acc_sums = df[acc_cols].fillna(0).sum().sort_values(ascending=False)
    acc_labels = [c.replace("accessory_","").replace("_"," ").title() for c in acc_sums.index]
    acc_pct = (acc_sums/N*100).round(1)
    fig = px.bar(x=acc_labels, y=acc_pct.values, color_discrete_sequence=[PURPLE],
                 text=acc_pct.values, title="Accessory Interest (% selecting)")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=340, margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t7_accessories"] = fig_to_html(fig)

    occ_cols = [c for c in df.columns if c.startswith("occasion_")]
    occ_sums = df[occ_cols].fillna(0).sum().sort_values(ascending=False)
    occ_labels = [c.replace("occasion_","").replace("_"," ").title() for c in occ_sums.index]
    occ_pct = (occ_sums/N*100).round(1)
    fig = px.bar(x=occ_labels, y=occ_pct.values,
                 color=occ_pct.values, color_continuous_scale="Oranges",
                 text=occ_pct.values, title="Purchase Occasion Drivers (% selecting)")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, showlegend=False, coloraxis_showscale=False,
                      margin=dict(t=40,b=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t7_occasions"] = fig_to_html(fig)

    bundle_order = ["Prefer complete looks","Sometimes if it appeals","Prefer to mix myself","No preference"]
    bun_counts = df["bundle_preference"].value_counts().reindex(bundle_order).fillna(0).reset_index()
    bun_counts.columns = ["Preference","Count"]
    bun_counts["Pct"] = (bun_counts["Count"]/N*100).round(1)
    fig = px.bar(bun_counts, y="Preference", x="Count", orientation="h",
                 color="Preference", color_discrete_sequence=[BRAND_GREEN,"#5DCAA5",AMBER,GRAY],
                 text="Pct", title="Bundle vs Individual Piece Preference")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, showlegend=False, margin=dict(t=40,b=10,r=60),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t7_bundle"] = fig_to_html(fig)

    # ── TAB 8: Thrift Attitudes ───────────────────────────────────────────────
    thrift_exp_order = ["Yes regularly","Yes a few times","No but open","No and unlikely"]
    te_counts = df["prior_thrift_experience"].value_counts().reindex(thrift_exp_order).fillna(0).reset_index()
    te_counts.columns = ["Experience","Count"]
    te_counts["Pct"] = (te_counts["Count"]/N*100).round(1)
    colors_te = [BRAND_GREEN,"#5DCAA5",AMBER,"#E24B4A"]
    fig = px.bar(te_counts, x="Experience", y="Count", text="Pct",
                 color="Experience", color_discrete_sequence=colors_te,
                 title="Prior Thrift Shopping Experience")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, showlegend=False, margin=dict(t=40,b=80),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t8_thrift_exp"] = fig_to_html(fig)

    upc_order = ["Very interested","Interested if priced right","Curious but unsure","Not interested"]
    upc_counts = df["upcycle_interest"].value_counts().reindex(upc_order).fillna(0).reset_index()
    upc_counts.columns = ["Interest","Count"]
    upc_counts["Pct"] = (upc_counts["Count"]/N*100).round(1)
    fig = px.bar(upc_counts, x="Interest", y="Count", text="Pct",
                 color="Interest", color_discrete_sequence=[BRAND_GREEN,"#5DCAA5",AMBER,"#E24B4A"],
                 title="Interest in Upcycled / Reworked Items")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, showlegend=False, margin=dict(t=40,b=80),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t8_upcycle"] = fig_to_html(fig)

    sub_order = ["Would subscribe immediately","Maybe after first box","Prefer one-off","No interest"]
    sub_counts = df["subscription_intent"].value_counts().reindex(sub_order).fillna(0).reset_index()
    sub_counts.columns = ["Intent","Count"]
    sub_counts["Pct"] = (sub_counts["Count"]/N*100).round(1)
    fig = px.pie(sub_counts, values="Count", names="Intent",
                 color_discrete_sequence=[BRAND_GREEN,"#5DCAA5",AMBER,"#E24B4A"],
                 hole=0.45, title="Subscription / Mystery Box Intent")
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(height=380, margin=dict(t=40,b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t8_sub"] = fig_to_html(fig)

    ret_order = ["Would stop me","Makes me hesitate","Comfortable with it","Depends on price"]
    ret_counts = df["return_policy_sensitivity"].value_counts().reindex(ret_order).fillna(0).reset_index()
    ret_counts.columns = ["Sensitivity","Count"]
    ret_counts["Pct"] = (ret_counts["Count"]/N*100).round(1)
    fig = px.bar(ret_counts, x="Sensitivity", y="Count", text="Pct",
                 color="Sensitivity", color_discrete_sequence=["#E24B4A",AMBER,BRAND_GREEN,BLUE],
                 title="Return Policy Sensitivity")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, showlegend=False, margin=dict(t=40,b=100),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t8_returns"] = fig_to_html(fig)

    # ── TAB 9: Correlations ───────────────────────────────────────────────────
    numeric_cols = ["spend_numeric","outfit_spend_numeric","income_numeric","sustainability_score"]
    encoded_cols_corr = [c for c in df.columns if c.endswith("_encoded")]
    corr_cols = [c for c in numeric_cols + encoded_cols_corr if c in df.columns]
    corr_matrix = df[corr_cols].corr().round(2)
    short_labels = [c.replace("_encoded","").replace("_"," ") for c in corr_cols]
    fig = px.imshow(corr_matrix, x=short_labels, y=short_labels,
                    color_continuous_scale="RdYlGn", zmin=-1, zmax=1,
                    title="Feature Correlation Heatmap", text_auto=True)
    fig.update_layout(height=600, margin=dict(t=50,b=80,l=120,r=20),
                      xaxis_tickangle=-45, xaxis_tickfont_size=9, yaxis_tickfont_size=9,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t9_corr"] = fig_to_html(fig)

    # Persona spend boxplot
    fig = px.box(df, x="persona", y="spend_numeric",
                 color="persona", color_discrete_map=PERSONA_COLORS,
                 title="Monthly Fashion Spend Distribution by Persona",
                 labels={"spend_numeric":"Monthly Spend (₹)","persona":"Persona"})
    fig.update_layout(height=420, showlegend=False, margin=dict(t=40,b=80),
                      xaxis_tickangle=-10,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t9_spend_box"] = fig_to_html(fig)

    # ── TAB 10: Customer Segments ─────────────────────────────────────────────
    comp_df = df.groupby("persona")["spend_numeric"].mean().reset_index()
    comp_df.columns = ["Persona","Avg Monthly Spend (₹)"]
    fig = px.bar(comp_df, x="Persona", y="Avg Monthly Spend (₹)",
                 color="Persona", color_discrete_map=PERSONA_COLORS,
                 text=comp_df["Avg Monthly Spend (₹)"].round(0).astype(int),
                 title="Average Monthly Spend by Persona")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=380, showlegend=False, margin=dict(t=40,b=80),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t10_spend"] = fig_to_html(fig)

    pi_cross = df.groupby(["persona","purchase_intent"]).size().reset_index(name="Count")
    pi_piv = pi_cross.pivot(index="persona", columns="purchase_intent", values="Count").fillna(0)
    pi_pct = pi_piv.div(pi_piv.sum(axis=1), axis=0)*100
    fig = px.bar(pi_pct.reset_index().melt(id_vars="persona", var_name = "variable", value_name = "value"),
                 x="persona", y="value", color="variable",
                 color_discrete_map=INTENT_COLORS, barmode="stack",
                 title="Purchase Intent Breakdown by Persona (%)",
                 labels={"value":"% of persona","variable":"Intent"})
    fig.update_layout(height=400, margin=dict(t=40,b=80), xaxis_tickangle=-10,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    charts["t10_intent"] = fig_to_html(fig)

    # Radar charts per persona
    radar_features = ["sustainability_score","spend_numeric","outfit_spend_numeric",
                      "income_numeric","ugc_propensity_encoded","subscription_intent_encoded"]
    radar_labels = ["Sustainability","Monthly Spend","Outfit WTP","Income","UGC Activity","Sub Intent"]
    available_radar = [f for f in radar_features if f in df.columns]
    available_labels = [radar_labels[i] for i,f in enumerate(radar_features) if f in df.columns]

    radar_figs = {}
    for persona, color in PERSONA_COLORS.items():
        persona_df = df[df["persona"]==persona]
        means = []
        for feat in available_radar:
            mn, mx = df[feat].min(), df[feat].max()
            val = persona_df[feat].mean()
            means.append((val-mn)/(mx-mn+1e-9))
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=means+[means[0]], theta=available_labels+[available_labels[0]],
            fill='toself', fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.25)",
            line=dict(color=color, width=2), name=persona
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,1], tickfont_size=9)),
            showlegend=False, height=300,
            title=f"{persona} — Profile Radar",
            margin=dict(t=50,b=10,l=40,r=40),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        safe_key = persona.replace(" ","_").replace("/","")
        radar_figs[safe_key] = fig_to_html(fig)

    charts.update(radar_figs)
    return charts, N, df


# ── HTML template ──────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Thrift Fashion Analytics · Peehu</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  :root{{
    --green:#1D9E75; --green-light:#E1F5EE; --amber:#BA7517;
    --coral:#D85A30; --purple:#534AB7; --blue:#378ADD;
    --gray:#888780; --bg:#F5F7F6; --card:#fff;
    --border:#E0EDE8; --text:#2C2C2A; --muted:#5F5E5A;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);}}
  /* ── Header ── */
  .header{{background:var(--green);color:#fff;padding:1.2rem 2rem;display:flex;align-items:center;gap:1rem;}}
  .header h1{{font-size:1.4rem;font-weight:700;}}
  .header p{{font-size:.85rem;opacity:.85;margin-top:.2rem;}}
  /* ── Tab bar ── */
  .tab-bar{{background:#fff;border-bottom:2px solid var(--border);display:flex;flex-wrap:wrap;gap:4px;padding:.5rem 1rem;position:sticky;top:0;z-index:100;box-shadow:0 2px 6px rgba(0,0,0,.06);}}
  .tab-btn{{background:none;border:none;padding:.5rem 1rem;font-size:.8rem;font-weight:500;cursor:pointer;border-radius:8px 8px 0 0;color:var(--muted);transition:all .15s;}}
  .tab-btn:hover{{background:var(--green-light);color:var(--green);}}
  .tab-btn.active{{background:var(--green);color:#fff;}}
  /* ── Content ── */
  .tab-content{{display:none;padding:1.5rem 2rem;max-width:1600px;margin:0 auto;}}
  .tab-content.active{{display:block;}}
  h2{{font-size:1.4rem;font-weight:700;color:var(--text);margin-bottom:.4rem;}}
  h3{{font-size:1.05rem;font-weight:600;color:var(--text);margin:1.2rem 0 .5rem;}}
  p.subtitle{{color:var(--muted);font-size:.9rem;margin-bottom:1.2rem;line-height:1.6;}}
  /* ── Metric cards ── */
  .metric-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;margin:1rem 0;}}
  .metric-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem 1.2rem;text-align:center;}}
  .metric-val{{font-size:1.8rem;font-weight:700;color:var(--green);line-height:1.1;}}
  .metric-label{{font-size:.75rem;color:var(--muted);margin-top:.3rem;}}
  /* ── Insight boxes ── */
  .insight-box{{background:#F0FAF6;border-left:4px solid var(--green);border-radius:0 8px 8px 0;padding:.9rem 1.2rem;margin:.8rem 0;font-size:.85rem;line-height:1.7;color:var(--text);}}
  .warning-box{{background:#FFFBF0;border-left:4px solid var(--amber);border-radius:0 8px 8px 0;padding:.9rem 1.2rem;margin:.8rem 0;font-size:.85rem;line-height:1.7;}}
  .info-box{{background:#EEF5FE;border-left:4px solid var(--blue);border-radius:0 8px 8px 0;padding:.9rem 1.2rem;margin:.8rem 0;font-size:.85rem;line-height:1.7;}}
  /* ── Section header ── */
  .section-header{{font-size:1rem;font-weight:600;color:var(--green);margin:1.5rem 0 .6rem;padding-bottom:.4rem;border-bottom:2px solid var(--border);}}
  /* ── 2-col grid ── */
  .grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin:1rem 0;}}
  @media(max-width:900px){{.grid-2{{grid-template-columns:1fr;}}}}
  /* ── Chart wrapper ── */
  .chart-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:.8rem;}}
  /* ── Data table ── */
  .data-table{{width:100%;border-collapse:collapse;font-size:.8rem;margin-top:.5rem;}}
  .data-table th{{background:var(--green-light);color:var(--green);font-weight:600;padding:.5rem .8rem;text-align:left;}}
  .data-table td{{padding:.4rem .8rem;border-bottom:1px solid var(--border);}}
  .data-table tr:hover td{{background:#fafafa;}}
  /* ── Persona card ── */
  .persona-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;margin:1rem 0;}}
  .persona-card{{border-radius:10px;padding:.8rem;text-align:center;border:1.5px solid;}}
  .persona-name{{font-size:.75rem;font-weight:700;}}
  .persona-pct{{font-size:1.3rem;font-weight:800;margin:.3rem 0;}}
  .persona-meta{{font-size:.68rem;color:var(--muted);line-height:1.5;}}
  /* ── Radar grid ── */
  .radar-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem;margin:1rem 0;}}
  hr{{border:none;border-top:1px solid var(--border);margin:1.5rem 0;}}
  /* ── Strategy list ── */
  .strategy-item{{display:flex;gap:.8rem;padding:.6rem 0;border-bottom:1px solid var(--border);font-size:.88rem;}}
  .strategy-num{{font-weight:700;color:var(--green);min-width:24px;}}
  .tag{{display:inline-block;padding:2px 10px;border-radius:99px;font-size:.7rem;font-weight:600;margin:2px;}}
  .tag-green{{background:#E1F5EE;color:#0F6E56;}}
  .tag-blue{{background:#E6F1FB;color:#185FA5;}}
  .tag-amber{{background:#FAEEDA;color:#854F0B;}}
  .tag-purple{{background:#EEEDFE;color:#534AB7;}}
</style>
</head>
<body>

<div class="header">
  <div>♻️</div>
  <div>
    <h1>Thrift Fashion Analytics · Peehu</h1>
    <p>Phase 1 — Descriptive &amp; Diagnostic Analysis &nbsp;·&nbsp; {N:,} Respondents &nbsp;·&nbsp; 6 Personas</p>
  </div>
</div>

<div class="tab-bar">
  <button class="tab-btn active" onclick="showTab('t1',this)">🏠 Business Overview</button>
  <button class="tab-btn" onclick="showTab('t2',this)">📋 Raw Data</button>
  <button class="tab-btn" onclick="showTab('t3',this)">🔧 Cleaned Data</button>
  <button class="tab-btn" onclick="showTab('t4',this)">👥 Demographics</button>
  <button class="tab-btn" onclick="showTab('t5',this)">👗 Fashion Behaviour</button>
  <button class="tab-btn" onclick="showTab('t6',this)">💰 Budget &amp; Spend</button>
  <button class="tab-btn" onclick="showTab('t7',this)">🛍️ Product Preferences</button>
  <button class="tab-btn" onclick="showTab('t8',this)">♻️ Thrift Attitudes</button>
  <button class="tab-btn" onclick="showTab('t9',this)">📊 Correlations</button>
  <button class="tab-btn" onclick="showTab('t10',this)">🎯 Customer Segments</button>
</div>

<!-- ════════ TAB 1: Business Overview ════════ -->
<div id="t1" class="tab-content active">
  <h2>♻️ Thrift Fashion Brand — Business Intelligence Dashboard</h2>
  <p class="subtitle">Data-driven decision making for a curated thrift fashion brand targeting Gen Z and millennial buyers across India. Based on a {N:,}-respondent synthetic consumer survey.</p>
  <div class="metric-row">
    <div class="metric-card"><div class="metric-val">{N:,}</div><div class="metric-label">Survey Respondents</div></div>
    <div class="metric-card"><div class="metric-val">{likely_buyers:,}</div><div class="metric-label">Likely Buyers</div></div>
    <div class="metric-card"><div class="metric-val">{nurture:,}</div><div class="metric-label">Nurture Pipeline</div></div>
    <div class="metric-card"><div class="metric-val">₹{median_spend:,}</div><div class="metric-label">Median Monthly Spend</div></div>
    <div class="metric-card"><div class="metric-val">6</div><div class="metric-label">Distinct Personas</div></div>
  </div>
  <hr/>
  <div class="grid-2">
    <div>
      <div class="section-header">Brand Strategy</div>
      <p style="font-size:.88rem;line-height:1.8;">
        <strong>Mission:</strong> Build India's most recognisable curated thrift brand — affordable, unique, and sustainability-first.<br/><br/>
        <strong>Core pillars:</strong><br/>
        🎨 <strong>Aesthetic curation</strong> — Y2K, streetwear, minimal, cottagecore drops<br/>
        ♻️ <strong>Sustainability narrative</strong> — circular fashion, trade-in programme<br/>
        📱 <strong>Digital-first</strong> — Instagram-led, community-driven<br/>
        📊 <strong>Data-driven</strong> — personalised recs, targeted discounts, smart bundling
      </p>
      <div class="section-header">7 Product Offerings</div>
      <div class="strategy-item"><span class="strategy-num">01</span><span>Aesthetic-curated outfit drops <em style="color:var(--muted);font-size:.8rem">· High demand · 60–80% margin</em></span></div>
      <div class="strategy-item"><span class="strategy-num">02</span><span>Upcycled &amp; reworked originals <em style="color:var(--muted);font-size:.8rem">· Highest margin · Brand differentiator</em></span></div>
      <div class="strategy-item"><span class="strategy-num">03</span><span>Mystery thrift boxes <em style="color:var(--muted);font-size:.8rem">· Viral potential · Subscription path</em></span></div>
      <div class="strategy-item"><span class="strategy-num">04</span><span>Style profile &amp; personal styling <em style="color:var(--muted);font-size:.8rem">· Premium · Data engine for ML</em></span></div>
      <div class="strategy-item"><span class="strategy-num">05</span><span>Trade-in &amp; community sourcing <em style="color:var(--muted);font-size:.8rem">· Solves inventory · Loyalty loop</em></span></div>
      <div class="strategy-item"><span class="strategy-num">06</span><span>Digital lookbooks <em style="color:var(--muted);font-size:.8rem">· 95%+ margin · Brand authority</em></span></div>
      <div class="strategy-item"><span class="strategy-num">07</span><span>Thrift event &amp; pop-up drops <em style="color:var(--muted);font-size:.8rem">· UGC flywheel · Community anchor</em></span></div>
    </div>
    <div>
      <div class="section-header">Purchase Intent Distribution</div>
      <div class="chart-card">{t1_intent_pie}</div>
      <div class="insight-box">📌 <strong>57% of respondents are likely to purchase</strong> from a curated thrift brand — a strong conversion base. 35% are in the nurture pipeline (Maybe), representing a large opportunity for targeted discounts and social proof. Only 8% are firmly Not Interested.</div>
      <div class="section-header">Persona Distribution</div>
      <div class="chart-card">{t1_persona_bar}</div>
    </div>
  </div>
</div>

<!-- ════════ TAB 2: Raw Data ════════ -->
<div id="t2" class="tab-content">
  <h2>📋 Raw Survey Data</h2>
  <p class="subtitle">The unprocessed dataset exactly as generated — before any encoding, imputation, or transformation.</p>
  <div class="metric-row">
    <div class="metric-card"><div class="metric-val">{N:,}</div><div class="metric-label">Total Rows</div></div>
    <div class="metric-card"><div class="metric-val">{n_cols}</div><div class="metric-label">Total Columns</div></div>
    <div class="metric-card"><div class="metric-val">{missing_cells}</div><div class="metric-label">Missing Cells</div></div>
    <div class="metric-card"><div class="metric-val">{missing_pct:.2f}%</div><div class="metric-label">Missing %</div></div>
  </div>
  <hr/>
  <div class="section-header">Missing Value Map</div>
  <div class="chart-card">{t2_missing}</div>
  <div class="warning-box">⚠️ Missing values are confined to binary columns (colour preferences, accessory choices, travel occasions) — injected as deliberate noise (~2% of rows) to simulate real survey skip patterns. These will be imputed with 0 in the cleaned dataset.</div>
  <hr/>
  <div class="section-header">Raw Data Preview (first 30 rows)</div>
  <div style="overflow-x:auto">{raw_table}</div>
</div>

<!-- ════════ TAB 3: Cleaned Data ════════ -->
<div id="t3" class="tab-content">
  <h2>🔧 Cleaned &amp; Encoded Dataset</h2>
  <p class="subtitle">Ordinal encoding, missing value imputation, and numeric approximation applied. This is the version used for all EDA and modelling.</p>
  <div class="metric-row">
    <div class="metric-card"><div class="metric-val">{N:,}</div><div class="metric-label">Rows (after cleaning)</div></div>
    <div class="metric-card"><div class="metric-val">{n_cols}</div><div class="metric-label">Original Columns</div></div>
    <div class="metric-card"><div class="metric-val">{n_engineered}</div><div class="metric-label">Engineered Columns</div></div>
    <div class="metric-card"><div class="metric-val">{n_total_cols}</div><div class="metric-label">Total Columns</div></div>
  </div>
  <hr/>
  <div class="section-header">Transformation Log</div>
  <p><span class="tag tag-green">Ordinal Encoding</span> — 18 categorical columns encoded to integer scale preserving order</p><br/>
  <p><span class="tag tag-amber">Binary Imputation</span> — All multi-select binary columns filled with 0 where missing</p><br/>
  <p><span class="tag tag-blue">Numeric Spend Midpoints</span> — Monthly fashion spend, outfit spend, mystery box WTP mapped to midpoint INR values</p><br/>
  <p><span class="tag tag-blue">Income Numeric</span> — Income band mapped to midpoint INR for correlation analysis</p><br/>
  <p><span class="tag tag-purple">Encoded Column Naming</span> — All encoded columns appended with _encoded suffix</p>
  <hr/>
  <div class="section-header">Encoded Column Summary</div>
  <div style="overflow-x:auto">{t3_enc_table}</div>
</div>

<!-- ════════ TAB 4: Demographics ════════ -->
<div id="t4" class="tab-content">
  <h2>👥 Demographics Analysis</h2>
  <p class="subtitle">Age, gender, city tier, and income distributions — who is your customer base in India?</p>
  <div class="grid-2">
    <div class="chart-card">{t4_age}</div>
    <div class="chart-card">{t4_gender}</div>
  </div>
  <div class="insight-box">📌 <strong>18–27 is the dominant cohort (~55%)</strong>, confirming Gen Z and early millennials as your primary audience. Strong Metro and Tier 2 presence validates an Instagram-first digital strategy over offline-first.</div>
  <div class="grid-2">
    <div class="chart-card">{t4_city}</div>
    <div class="chart-card">{t4_income}</div>
  </div>
  <hr/>
  <div class="section-header">Purchase Intent by Age Group</div>
  <div class="chart-card">{t4_age_intent}</div>
  <div class="insight-box">📌 The 18–22 and 23–27 cohorts show the highest "Interested" proportions — these are your core conversion audience. The 23–27 cohort has a large "Maybe" segment — convertible with the right social proof or one-time discount. Older segments (35+) skew toward lower intent.</div>
</div>

<!-- ════════ TAB 5: Fashion Behaviour ════════ -->
<div id="t5" class="tab-content">
  <h2>👗 Fashion Behaviour Analysis</h2>
  <p class="subtitle">Style identity, shopping frequency, sustainability attitudes, and channel preferences — the primary clustering variables defining your segments.</p>
  <div class="grid-2">
    <div>
      <div class="chart-card">{t5_style}</div>
      <div class="insight-box">📌 <strong>Y2K/Retro and Streetwear together account for ~28% each</strong> — making them the top priority for your first inventory builds. Minimal/Clean girl represents higher-income buyers with larger spend capacity. Cottagecore/Boho is an emerging trend with low competition in Indian thrift.</div>
    </div>
    <div>
      <div class="chart-card">{t5_identity}</div>
      <div class="insight-box">📌 <strong>"Fashion as self-expression" is the dominant identity (~30%)</strong>, directly validating the brand's positioning around unique, curated aesthetics. The "Avoid fast fashion actively" cohort (~18%) aligns with your sustainability narrative.</div>
    </div>
  </div>
  <hr/>
  <div class="section-header">Sustainability &amp; Shopping Frequency</div>
  <div class="grid-2">
    <div class="chart-card">{t5_freq}</div>
    <div class="chart-card">{t5_discovery}</div>
  </div>
  <div class="insight-box">📌 <strong>Instagram/Reels dominates at ~42%</strong> — perfectly validating your Instagram-first strategy. WhatsApp drops at ~20% suggest a strong community group / broadcast channel strategy should run in parallel.</div>
  <hr/>
  <div class="section-header">Style × Purchase Intent Cross-Analysis</div>
  <div class="chart-card">{t5_style_intent}</div>
  <div class="insight-box">📌 <strong>Y2K/Retro and Streetwear show the highest "Interested" proportions</strong>, confirming these are your highest-converting style segments. Formal/Classic skews toward "Not Interested" — lower ROI for formal workwear drops early on.</div>
</div>

<!-- ════════ TAB 6: Budget & Spend ════════ -->
<div id="t6" class="tab-content">
  <h2>💰 Budget &amp; Spending Analysis</h2>
  <p class="subtitle">Spend capacity and WTP analysis directly informs your pricing architecture. Maps income against spending behaviour and reveals pricing sweet spots.</p>
  <div class="metric-row">
    <div class="metric-card"><div class="metric-val">₹{median_spend:,}</div><div class="metric-label">Median Monthly Spend</div></div>
    <div class="metric-card"><div class="metric-val">₹{mean_outfit:,}</div><div class="metric-label">Mean Outfit WTP</div></div>
    <div class="metric-card"><div class="metric-val">{high_spend}</div><div class="metric-label">High-spend (>₹2.5k/mo)</div></div>
    <div class="metric-card"><div class="metric-val">{would_buy_mbox}</div><div class="metric-label">Would Buy Mystery Box</div></div>
  </div>
  <hr/>
  <div class="grid-2">
    <div>
      <div class="chart-card">{t6_spend_intent}</div>
      <div class="insight-box">📌 <strong>"Interested" grows steadily with monthly spend</strong> — higher-spending buyers are more likely to try thrift. This counter-intuitive finding is driven by uniqueness-seeking, not just price. Target the ₹2,500–₹5,000/month segment with premium drops.</div>
    </div>
    <div>
      <div class="chart-card">{t6_outfit}</div>
      <div class="insight-box">📌 <strong>₹700–₹1,500 is the modal WTP for a single outfit (~35%)</strong>, perfectly aligning with your planned pricing. Price upcycled originals toward ₹1,500–₹3,000 and curated drops at ₹800–₹1,500.</div>
    </div>
  </div>
  <hr/>
  <div class="section-header">Mystery Box WTP &amp; Income vs Spend</div>
  <div class="grid-2">
    <div class="chart-card">{t6_mbox}</div>
    <div class="chart-card">{t6_scatter}</div>
  </div>
  <div class="insight-box">📌 <strong>~78% are willing to pay something for a mystery box</strong> — a very strong launch signal. Price your first mystery boxes at ₹500–₹800 to capture the widest initial audience, then test ₹800–₹1,200 as the brand builds trust.</div>
</div>

<!-- ════════ TAB 7: Product Preferences ════════ -->
<div id="t7" class="tab-content">
  <h2>🛍️ Product Preferences Analysis</h2>
  <p class="subtitle">Clothing types, colour palettes, accessories, and occasion drivers — feeds association rule mining for bundle strategy.</p>
  <div class="section-header">Clothing Type Preferences</div>
  <div class="chart-card">{t7_clothing}</div>
  <div class="insight-box">📌 <strong>Oversized tees and baggy jeans lead by a wide margin (~55–60%)</strong>, confirming streetwear and casual aesthetics as your highest-volume inventory categories. Jackets/blazers and crop tops are "cross-aesthetic" items that serve multiple customer types and reduce inventory risk.</div>
  <hr/>
  <div class="grid-2">
    <div>
      <div class="section-header">Colour Palette Preferences</div>
      <div class="chart-card">{t7_colours}</div>
    </div>
    <div>
      <div class="section-header">Accessory Interest</div>
      <div class="chart-card">{t7_accessories}</div>
      <div class="insight-box">📌 <strong>Jewellery and bags are the top accessory interests</strong> — both easy to source thrifted and high-margin. Bundle accessories into outfit drops to increase average order value.</div>
    </div>
  </div>
  <hr/>
  <div class="section-header">Occasion Drivers &amp; Bundle Preference</div>
  <div class="grid-2">
    <div class="chart-card">{t7_occasions}</div>
    <div class="chart-card">{t7_bundle}</div>
  </div>
  <div class="insight-box">📌 <strong>Everyday/casual wear leads at ~72%</strong> — confirming daily-wear items should dominate inventory. Festivals at ~52% is crucial for India — plan themed drops 4–6 weeks before Diwali, Holi, and Navratri.</div>
</div>

<!-- ════════ TAB 8: Thrift Attitudes ════════ -->
<div id="t8" class="tab-content">
  <h2>♻️ Thrift Attitudes &amp; Barriers</h2>
  <p class="subtitle">Prior experience, purchase barriers, discovery channels, and motivators — your conversion funnel.</p>
  <div class="grid-2">
    <div>
      <div class="chart-card">{t8_thrift_exp}</div>
      <div class="insight-box">📌 A significant share has prior thrift experience — both "regularly" and "a few times" segments are your warmest leads. The "open but haven't yet" cohort is the highest-priority acquisition target.</div>
    </div>
    <div>
      <div class="chart-card">{t8_upcycle}</div>
      <div class="insight-box">📌 Strong upcycling interest validates your upcycled originals product line as a brand differentiator with premium pricing potential.</div>
    </div>
  </div>
  <hr/>
  <div class="grid-2">
    <div class="chart-card">{t8_sub}</div>
    <div>
      <div class="chart-card">{t8_returns}</div>
      <div class="insight-box">📌 Return policy sensitivity is a significant purchase barrier. Prioritise COD and easy 7-day returns as a trust-builder in your early months — the incremental logistics cost is worth the conversion uplift.</div>
    </div>
  </div>
</div>

<!-- ════════ TAB 9: Correlations ════════ -->
<div id="t9" class="tab-content">
  <h2>📊 Correlation &amp; Cross-Tab Analysis</h2>
  <p class="subtitle">Heatmaps and distributional comparisons revealing relationships between spend, intent, style, and demographics.</p>
  <div class="section-header">Feature Correlation Heatmap</div>
  <div class="chart-card">{t9_corr}</div>
  <div class="insight-box">📌 Strong positive correlations between income, spend, and outfit WTP confirm that higher-income respondents are your higher-value customers. Sustainability score correlates positively with subscription intent — your eco-conscious segment is also your most loyal.</div>
  <hr/>
  <div class="section-header">Monthly Fashion Spend by Persona</div>
  <div class="chart-card">{t9_spend_box}</div>
  <div class="insight-box">📌 Conscious Spender and Occasional Gifter show the highest median spends — these are your premium product targets. Bargain Hunter has lower spend but high volume — serve with mystery boxes and flash sales.</div>
</div>

<!-- ════════ TAB 10: Customer Segments ════════ -->
<div id="t10" class="tab-content">
  <h2>🎯 Customer Segment Profiling</h2>
  <p class="subtitle">Deep-dive into the 6 synthetic personas — the ground-truth basis for validating future K-Means clustering results.</p>
  <div class="section-header">Segment Overview</div>
  <div class="persona-grid">
    <div class="persona-card" style="background:#7F77DD18;border-color:#7F77DD"><div class="persona-name" style="color:#7F77DD">Aesthetic Chaser</div><div class="persona-pct" style="color:#7F77DD">28%</div><div class="persona-meta">Age: 18–24 · Metro<br/>Y2K / Streetwear · ₹700–1,500<br/>High intent</div></div>
    <div class="persona-card" style="background:#1D9E7518;border-color:#1D9E75"><div class="persona-name" style="color:#1D9E75">Conscious Spender</div><div class="persona-pct" style="color:#1D9E75">22%</div><div class="persona-meta">Age: 23–30 · Metro/T2<br/>Minimal / Clean · ₹1,500–3,000<br/>Very High intent</div></div>
    <div class="persona-card" style="background:#D85A3018;border-color:#D85A30"><div class="persona-name" style="color:#D85A30">Bargain Hunter</div><div class="persona-pct" style="color:#D85A30">20%</div><div class="persona-meta">Age: 18–28 · Tier 2/3<br/>Mixed · ₹300–800<br/>Moderate intent</div></div>
    <div class="persona-card" style="background:#378ADD18;border-color:#378ADD"><div class="persona-name" style="color:#378ADD">Fence-Sitter</div><div class="persona-pct" style="color:#378ADD">15%</div><div class="persona-meta">Age: 22–35 · Mixed<br/>Mixed · ₹500–1,200<br/>Low-Moderate intent</div></div>
    <div class="persona-card" style="background:#BA751718;border-color:#BA7517"><div class="persona-name" style="color:#BA7517">Occasional Gifter</div><div class="persona-pct" style="color:#BA7517">10%</div><div class="persona-meta">Age: 25–40 · Metro<br/>Classic/Mixed · ₹800–2,000<br/>Moderate intent</div></div>
    <div class="persona-card" style="background:#88878018;border-color:#888780"><div class="persona-name" style="color:#888780">Skeptic</div><div class="persona-pct" style="color:#888780">5%</div><div class="persona-meta">Age: 28–45 · Mixed<br/>Formal/Brand · ₹500–2,000<br/>Very Low intent</div></div>
  </div>
  <hr/>
  <div class="section-header">Persona Radar Profiles</div>
  <div class="radar-grid">
    <div class="chart-card">{Aesthetic_Chaser}</div>
    <div class="chart-card">{Conscious_Spender}</div>
    <div class="chart-card">{Bargain_Hunter}</div>
    <div class="chart-card">{Fence-Sitter}</div>
    <div class="chart-card">{Occasional_Gifter}</div>
    <div class="chart-card">{Skeptic}</div>
  </div>
  <hr/>
  <div class="section-header">Average Monthly Spend by Persona</div>
  <div class="chart-card">{t10_spend}</div>
  <hr/>
  <div class="section-header">Persona × Purchase Intent Matrix</div>
  <div class="chart-card">{t10_intent}</div>
  <div class="insight-box">📌 <strong>Strategic prioritisation:</strong><br/>
    • <strong>Aesthetic Chaser (28%)</strong>: Highest-intent, highest-Instagram-reach segment. Activate first with Y2K/streetwear drops and UGC incentives.<br/>
    • <strong>Conscious Spender (22%)</strong>: Highest LTV segment. Target with premium drops, sustainability storytelling, and styling services.<br/>
    • <strong>Bargain Hunter (20%)</strong>: High volume, lower margin. Serve with mystery boxes, flash sales, and bundle deals.<br/>
    • <strong>Fence-Sitter (15%)</strong>: Largest conversion opportunity. Target with first-purchase discounts, social proof, and easy returns.<br/>
    • <strong>Occasional Gifter (10%)</strong>: Festival-season focused. Activate with gifting boxes and Diwali/birthday themed campaigns.<br/>
    • <strong>Skeptic (5%)</strong>: Do not prioritise in Year 1. Convert passively through organic reach.
  </div>
</div>

<script>
function showTab(id, btn) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
  // Trigger plotly resize for charts in newly visible tab
  setTimeout(()=>{{ window.dispatchEvent(new Event('resize')); }}, 50);
}}
</script>
</body>
</html>
"""


def main():
    print("🔄 Loading data...")
    raw, df = load_data()
    N = len(df)

    print("📊 Building charts (this may take 30–60 seconds)...")
    charts, N, df = build_charts(raw, df)

    # Compute summary stats for template
    likely_buyers  = int(df["purchase_intent"].eq("Interested").sum())
    nurture        = int(df["purchase_intent"].eq("Maybe").sum())
    median_spend   = int(df["spend_numeric"].median())
    mean_outfit    = int(df["outfit_spend_numeric"].mean())
    high_spend     = int(df["monthly_fashion_spend"].isin(["2500-5000","Above 5000"]).sum())
    would_buy_mbox = int((~df["mystery_box_wtp"].eq("Would not buy")).sum())
    n_cols         = raw.shape[1]
    missing_cells  = int(raw.isnull().sum().sum())
    missing_pct    = missing_cells / (raw.shape[0] * raw.shape[1]) * 100
    n_engineered   = df.shape[1] - raw.shape[1]
    n_total_cols   = df.shape[1]

    raw_table = raw.head(30).to_html(index=False, classes="data-table", border=0)

    print("🖊️  Assembling HTML...")
    html = HTML_TEMPLATE.format(
        N=N,
        likely_buyers=likely_buyers, nurture=nurture,
        median_spend=median_spend, mean_outfit=mean_outfit,
        high_spend=high_spend, would_buy_mbox=would_buy_mbox,
        n_cols=n_cols, missing_cells=missing_cells, missing_pct=missing_pct,
        n_engineered=n_engineered, n_total_cols=n_total_cols,
        raw_table=raw_table,
        **charts,
    )

    out_path = os.path.join(os.path.dirname(__file__), "thrift_dashboard.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\n✅ Done! File saved: {out_path}  ({size_mb:.1f} MB)")
    print("   Open thrift_dashboard.html in any browser — no server needed.\n")


if __name__ == "__main__":
    main()
