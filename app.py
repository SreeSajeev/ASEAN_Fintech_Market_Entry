import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    mci_data = pd.read_pickle('mci_data_clean (2).pkl')
    mci_scores = pd.read_pickle('mci_index_scores_clean (2).pkl')
    findex = pd.read_csv('findex_cleaned (1).csv')
    rankings = pd.read_excel('Rankings.xlsx')
    return mci_data, mci_scores, findex, rankings

mci_data, mci_scores, findex, rankings = load_data()

st.title("ASEAN Fintech Market Entry Dashboard")


# Radar chart
st.subheader("Market Readiness Comparison")
countries = st.multiselect(
    "Select Countries",
    mci_scores['Country'].unique(),
    default=["Singapore", "Malaysia", "Indonesia"]
)

readiness_cols = [
    'Mobile Social Media Penetration',
    'Mobile ownership',
    'E-Government Score'
]

if countries:
    radar_data = mci_scores[mci_scores['Country'].isin(countries)]

    # Ensure selected columns exist
    missing_cols = [col for col in readiness_cols if col not in radar_data.columns]
    if missing_cols:
        st.warning(f"Missing columns: {missing_cols}")
    else:
        # Melt data to long format
        melted = radar_data.melt(
            id_vars='Country',
            value_vars=readiness_cols,
            var_name='Metric',
            value_name='Score'
        )

        # Plot radar chart
        fig = px.line_polar(
            melted,
            r='Score',
            theta='Metric',
            color='Country',
            line_close=True
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("📌 Financial Inclusion Indicators (Heatmap)")

findex_filtered = findex[findex['Country'].isin(countries)]

if not findex_filtered.empty:
    heatmap_data = findex_filtered.set_index('Country').select_dtypes(include='number')
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Indicator", y="Country", color="Score"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No financial inclusion data available for the selected countries.")

st.subheader(" Ease of Doing Business Comparison")

eodb_cols = [
    'Starting a business', 'Getting electricity', 'Registering property',
    'Getting credit', 'Paying taxes', 'Trading across borders',
    'Enforcing contracts', 'Resolving insolvency'
]

rankings_filtered = rankings[rankings['Economy'].isin(countries)]

if not rankings_filtered.empty:
    rankings_melted = rankings_filtered.melt(
        id_vars='Economy',
        value_vars=eodb_cols,
        var_name='Indicator',
        value_name='Score'
    )

    fig = px.bar(
        rankings_melted,
        x='Score',
        y='Economy',
        color='Indicator',
        barmode='group',
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No EoDB data available for the selected countries.")




def compute_readiness(df):
    metrics = ['mobile ownership', 'account_penetration', 'network coverage', 'literacy']
    df = df.copy()

    for metric in metrics:
        if metric in df.columns:
            min_val = df[metric].min()
            max_val = df[metric].max()
            if pd.api.types.is_numeric_dtype(df[metric]):
                if min_val != max_val:
                    df[metric] = (df[metric] - min_val) / (max_val - min_val)
                else:
                    df[metric] = 1
            else:
                st.warning(f"Skipping non-numeric metric: {metric}")
        else:
            st.warning(f"Missing metric: {metric}")

    weights = {
        'mobile ownership': 0.25,
        'account_penetration': 0.25,
        'network coverage': 0.25,
        'literacy': 0.25
    }

    df['readiness_score'] = df.apply(
        lambda row: sum(row[m] * weights[m] for m in weights if m in row),
        axis=1
    )

    def assess_risk(score):
        if score >= 0.75:
            return "Low Risk"
        elif score >= 0.60:
            return "Medium Risk"
        elif score >= 0.45:
            return "High Risk"
        else:
            return "Very High Risk"

    df['risk_level'] = df['readiness_score'].apply(assess_risk)

    return df[['country'] + metrics + ['readiness_score', 'risk_level']].round(3)

