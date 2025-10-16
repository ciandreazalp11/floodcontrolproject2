# pages/analysis.py
import streamlit as st
import pandas as pd
import io

def app():
    st.title("3 — Analysis")
    if 'processed' not in st.session_state:
        st.info("Process data in Data Cleaning first.")
        return

    res = st.session_state['processed']
    df = res['df']

    st.subheader("Summary per year")
    summary_df = pd.DataFrame({
        "year": res['floods_per_year'].index,
        "floods_per_year": res['floods_per_year'].values,
        "avg_water_per_year": res['avg_water_per_year'].values
    }).reset_index(drop=True)
    st.dataframe(summary_df)

    st.download_button("Download summary CSV", data=summary_df.to_csv(index=False).encode('utf-8'), file_name='summary_per_year.csv')

    st.subheader("Top affected areas")
    if res['most_affected'] is not None:
        ma = res['most_affected'].reset_index().rename(columns={'index':'area','is_flood':'count'})
        st.dataframe(ma)
        st.download_button("Download top-affected CSV", data=ma.to_csv(index=False).encode('utf-8'), file_name='top_affected.csv')
    else:
        st.write("No area information detected.")

    st.subheader("Damage summary (per year)")
    if not res['total_damage_per_year'].empty:
        st.dataframe(res['total_damage_per_year'])
        st.download_button("Download damage CSV", data=res['total_damage_per_year'].to_csv().encode('utf-8'), file_name='damage_per_year.csv')
    else:
        st.write("No damage columns detected.")
