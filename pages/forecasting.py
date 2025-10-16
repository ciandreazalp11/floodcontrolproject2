# pages/forecasting.py
import streamlit as st
import pandas as pd
from utils.forecast_utils import fit_sarima, evaluate_forecast
import plotly.graph_objects as go

def app():
    st.title("4 — Forecasting (SARIMA)")
    if 'processed' not in st.session_state:
        st.info("Process data first (Data Cleaning).")
        return

    res = st.session_state['processed']
    df = res['df']
    wc = res['water_col']

    series = df[wc].resample('M').mean().fillna(method='ffill').fillna(0)
    if len(series.dropna()) < 12:
        st.warning("Not enough monthly data for SARIMA (need >= 12 aggregated months).")
        return

    train_ratio = st.slider("Train split ratio", min_value=0.5, max_value=0.95, value=0.8, step=0.01)
    split = int(len(series) * train_ratio)
    train = series.iloc[:split]
    test = series.iloc[split:]

    st.write(f"Train months: {len(train)}  Test months: {len(test)}")

    manual_order = st.text_input("Manual (p,d,q) e.g. 1,1,1", "")
    manual_seasonal = st.text_input("Manual seasonal (P,D,Q,s) e.g. 1,1,1,12", "")
    run_button = st.button("Run SARIMA")

    if run_button:
        chosen_res = None
        if manual_order and manual_seasonal:
            try:
                order = tuple(int(x.strip()) for x in manual_order.split(","))
                seasonal = tuple(int(x.strip()) for x in manual_seasonal.split(","))
                chosen_res = fit_sarima(train, order=order, seasonal_order=seasonal)
            except Exception as e:
                st.error(f"Manual SARIMA fit failed: {e}")
                return
        else:
            try:
                chosen_res = fit_sarima(train, order=(1,0,1), seasonal_order=(1,0,1,12))
            except Exception as e:
                st.error(f"Default SARIMA fit failed: {e}")
                return

        eval_res = evaluate_forecast(chosen_res, test)
        st.success(f"SARIMA done. AIC: {eval_res['aic']:.2f}, MAE: {eval_res['mae']:.4f}, MSE: {eval_res['mse']:.4f}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=train.index, y=train, name='Train'))
        fig.add_trace(go.Scatter(x=test.index, y=test, name='Test'))
        fig.add_trace(go.Scatter(x=eval_res['forecast'].index, y=eval_res['forecast'].values, name='Forecast'))
        fig.update_layout(title="SARIMA: Actual vs Forecast", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)

        # future
        periods = st.number_input("Forecast future months", min_value=1, max_value=60, value=6, step=1)
        if st.button("Generate future forecast"):
            future = chosen_res.get_forecast(steps=int(periods))
            fut_mean = future.predicted_mean
            future_index = pd.date_range(start=series.index[-1] + pd.offsets.MonthBegin(1), periods=periods, freq='M')
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=series.index, y=series, name='Historical'))
            fig2.add_trace(go.Scatter(x=future_index, y=fut_mean.values, name='Forecast'))
            fig2.update_layout(title=f"Forecast next {periods} months", xaxis_title="Date")
            st.plotly_chart(fig2, use_container_width=True)
