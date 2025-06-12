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

st.title(" ASEAN Fintech Market Entry Dashboard")

tabs = st.tabs([
    "Market Readiness", 
    "Financial Inclusion", 
    "Ease of Doing Business", 
    "Digital vs Inclusion", 
    "Country Snapshot", 
    "Top Performers"
])

# --- Tab 1: Market Readiness Radar ---
with tabs[0]:
    st.subheader(" Market Readiness Comparison")
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

        missing_cols = [col for col in readiness_cols if col not in radar_data.columns]
        if missing_cols:
            st.warning(f"Missing columns: {missing_cols}")
        else:
            melted = radar_data.melt(
                id_vars='Country',
                value_vars=readiness_cols,
                var_name='Metric',
                value_name='Score'
            )
            fig = px.line_polar(
                melted,
                r='Score',
                theta='Metric',
                color='Country',
                line_close=True
            )
            st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Financial Inclusion Heatmap ---
with tabs[1]:
    st.subheader("📌 Financial Inclusion Indicators (Heatmap)")
    if countries:
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

# --- Tab 3: Ease of Doing Business ---
with tabs[2]:
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

# --- Tab 4: Scatter Plot Digital Access vs Inclusion ---
with tabs[3]:
    st.subheader(" Digital Access vs Financial Inclusion")

    if 'Mobile Social Media Penetration' in mci_scores.columns and 'Country' in findex.columns:
        merged = pd.merge(
            mci_scores[['Country', 'Mobile Social Media Penetration']],
            findex[['Country', 'Account_Penetration']],
            on='Country',
            how='inner'
        )

        fig = px.scatter(
            merged,
            x='Mobile Social Media Penetration',
            y='Account_Penetration',
            color='Country',
            size='Account_Penetration',
            hover_name='Country',
            title='Mobile Social Media Penetration vs Account Penetration'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Required columns not found for scatter plot.")

# --- Tab 5: Country Snapshot ---
with tabs[4]:
    st.subheader(" Country Snapshot")

    selected_country = st.selectbox("Choose a Country for Detailed View", mci_scores['Country'].unique())

    if selected_country:
        mci_row = mci_scores[mci_scores['Country'] == selected_country]
        findex_row = findex[findex['Country'] == selected_country]

        st.markdown(f"### 📊 {selected_country} Metrics")

        if not mci_row.empty:
            st.write("**MCI Scores:**")
            st.dataframe(mci_row.drop(columns=['Country']).T.rename(columns={mci_row.index[0]: 'Value'}))

        if not findex_row.empty:
            st.write("**Financial Inclusion Indicators:**")
            st.dataframe(findex_row.drop(columns=['Country']).T.rename(columns={findex_row.index[0]: 'Value'}))

# --- Tab 6: Top Performers by Metric ---
with tabs[5]:
    st.subheader("🏆 Top ASEAN Countries by Individual Metrics")

    # Combined list from both datasets
    mci_cols = ['Mobile ownership', 'Network coverage', 'Literacy']
    findex_cols = ['Account_Penetration']

    available_metrics = mci_cols + findex_cols
    metric = st.selectbox("Select a Metric", available_metrics)

    source_df = None

    if metric in findex.columns:
        source_df = findex[['Country', metric]].dropna()
    elif metric in mci_scores.columns:
        source_df = mci_scores[['Country', metric]].dropna()
    else:
        st.warning(f"{metric} not found in datasets.")

    if source_df is not None and not source_df.empty:
        top_df = source_df.sort_values(by=metric, ascending=False).head(5)
        fig = px.bar(
            top_df,
            x='Country',
            y=metric,
            color='Country',
            title=f"Top 5 Countries by {metric}",
            text=metric
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for the selected metric: {metric}")
