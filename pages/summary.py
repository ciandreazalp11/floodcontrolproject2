# pages/summary.py
import streamlit as st
import pandas as pd

def app():
    st.title("5 — Summary & Download")
    if 'processed' not in st.session_state:
        st.info("No processed data available. Run Data Cleaning first.")
        return

    res = st.session_state['processed']
    df = res['df']

    st.subheader("Processed dataset (sample)")
    st.dataframe(df.head(200))

    summary_df = pd.DataFrame({
        "year": res['floods_per_year'].index,
        "floods_per_year": res['floods_per_year'].values,
        "avg_water_per_year": res['avg_water_per_year'].values
    }).reset_index(drop=True)

    st.subheader("Summary per year")
    st.dataframe(summary_df)

    st.download_button("Download processed dataset", data=df.to_csv(index=False).encode('utf-8'), file_name='processed_flood_data.csv', mime='text/csv')
    st.download_button("Download yearly summary", data=summary_df.to_csv(index=False).encode('utf-8'), file_name='summary_per_year.csv', mime='text/csv')
