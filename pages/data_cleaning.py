# pages/data_cleaning.py
import streamlit as st
import pandas as pd
from utils.data_utils import load_csv, process_df
import os

def app():
    st.title("1 — Data Cleaning & Upload")

    uploaded_file = st.file_uploader("Upload CSV (or leave blank to use sample data/create demo)", type=["csv","xlsx","txt"])
    if uploaded_file is None:
        st.info("No file uploaded. You can optionally generate a sample dataset below.")
    else:
        st.success(f"Loaded: {getattr(uploaded_file, 'name', 'uploaded file')}")

    # Sample generator
    if st.button("Generate sample dataset (and save to ./data/sample_data.csv)"):
        os.makedirs("data", exist_ok=True)
        dates = pd.date_range("2020-01-01", periods=360, freq="D")
        sample = pd.DataFrame({
            "Date": dates,
            "WaterLevel_m": (pd.Series(range(len(dates))).apply(lambda x: 1.5 + 0.6 * (pd.np.sin(x/30)) ) + pd.Series(pd.np.random.normal(0,0.15,len(dates)))).round(3),
            "Barangay": pd.np.random.choice(['Brgy A','Brgy B','Brgy C'], len(dates)),
            "Estimated_damage": (pd.np.random.rand(len(dates))*1000).round(2)
        })
        sample.to_csv("data/sample_data.csv", index=False)
        st.success("Sample persisted to data/sample_data.csv. Now use Upload and choose that file or leave blank to auto-load.")

    # Load preview
    df_preview = None
    if uploaded_file is not None:
        try:
            if str(uploaded_file).endswith('.xlsx') or getattr(uploaded_file,'name','').endswith('.xlsx'):
                df_preview = pd.read_excel(uploaded_file)
            else:
                df_preview = load_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error loading file: {e}")
            df_preview = None
    else:
        try:
            df_preview = pd.read_csv("data/sample_data.csv")
            st.info("Loaded data/sample_data.csv as default sample.")
        except Exception:
            df_preview = None

    if df_preview is not None:
        st.subheader("Preview")
        st.dataframe(df_preview.head(10))
        st.write("Columns detected:", df_preview.columns.tolist())

    st.subheader("Optional overrides & preprocessing")
    date_col = st.text_input("Date column name (leave blank to auto-detect)", "")
    water_col = st.text_input("Water column name (leave blank to auto-detect)", "")
    area_col = st.text_input("Area column name (leave blank to auto-detect)", "")
    damage_cols_raw = st.text_input("Damage column names (comma-separated, optional)", "")
    damage_cols = [s.strip() for s in damage_cols_raw.split(",") if s.strip()]

    interp_method = st.selectbox("Interpolation method", ['linear','time','pad','nearest'], index=0)
    zscore_outlier_thresh = st.number_input("Outlier z-score threshold", value=3.0, step=0.5)
    flood_zscore_thresh = st.number_input("Flood z-score threshold (lower)", value=1.5, step=0.1)
    flood_threshold_multiplier = st.slider("Flood threshold = mean + multiplier * std", 0.0, 3.0, 1.0, 0.1)

    if st.button("Process dataset"):
        if df_preview is None:
            st.error("No data available to process. Upload or generate sample first.")
            return
        try:
            res = process_df(
                df_preview,
                date_col=date_col or None,
                water_col=water_col or None,
                area_col=area_col or None,
                damage_cols_candidates=damage_cols or None,
                interp_method=interp_method,
                zscore_outlier_thresh=zscore_outlier_thresh,
                flood_zscore_thresh=flood_zscore_thresh,
                flood_threshold_multiplier=flood_threshold_multiplier
            )
            st.session_state['processed'] = res
            st.success("Processing complete. You can now go to Visualization or Analysis pages.")
        except Exception as e:
            st.error(f"Processing error: {e}")
