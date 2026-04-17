import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bond import price_bond, duration_macaulay, duration_modified

st.set_page_config(page_title="Duration Analysis", layout="wide")

st.title("⏱️ Bond Duration Analysis")
st.markdown("Analyze interest rate sensitivity using Macaulay and Modified Duration")

# Inputs
col1, col2 = st.columns(2)

with col1:
    face_value = st.number_input("Face Value ($)", 100, 100000, 1000, 100)
    coupon_rate = st.number_input("Coupon Rate (%)", 0.0, 15.0, 5.0, 0.1) / 100
    years = st.number_input("Years to Maturity", 1.0, 30.0, 10.0, 0.5)

with col2:
    # FIXED: number_input instead of slider
    ytm = st.number_input("Yield to Maturity (%)", 0.0, 20.0, 6.0, 0.1) / 100
    freq = st.selectbox("Coupon Frequency", [1, 2, 4, 12], index=1)

# Calculate duration
mac_dur = duration_macaulay(face_value, coupon_rate, years, ytm, freq)
mod_dur = duration_modified(mac_dur, ytm, freq)
price = price_bond(face_value, coupon_rate, years, ytm, freq)

# Display
col_d1, col_d2, col_d3 = st.columns(3)
col_d1.metric("Macaulay Duration", f"{mac_dur:.2f} years")
col_d2.metric("Modified Duration", f"{mod_dur:.2f} years")
col_d3.metric("Current Price", f"${price:,.2f}")

# Interest rate risk simulation
st.subheader("⚠️ Interest Rate Risk Simulation")
rate_shock = st.number_input("Interest Rate Shock (basis points)", -500, 500, 25, 5) / 10000

# Price change using duration approximation
approx_price_change = -mod_dur * rate_shock * 100
approx_new_price = price * (1 + approx_price_change / 100)

# Actual price change
new_ytm = ytm + rate_shock
actual_new_price = price_bond(face_value, coupon_rate, years, new_ytm, freq)
actual_price_change = ((actual_new_price - price) / price) * 100

col_a1, col_a2 = st.columns(2)
col_a1.metric("Duration-Approximated Price", f"${approx_new_price:,.2f}", delta=f"{approx_price_change:.2f}%")
col_a2.metric("Actual New Price", f"${actual_new_price:,.2f}", delta=f"{actual_price_change:.2f}%")

# Duration across maturities
st.subheader("📊 Duration vs Maturity")
maturities = np.linspace(1, 30, 30)
durations = [duration_macaulay(face_value, coupon_rate, m, ytm, freq) for m in maturities]

fig = go.Figure()
fig.add_trace(go.Scatter(x=maturities, y=durations, mode='lines+markers', name='Macaulay Duration'))
fig.update_layout(title='Duration vs Time to Maturity', xaxis_title='Years to Maturity', yaxis_title='Duration (years)')
st.plotly_chart(fig, use_container_width=True)

# Duration vs Coupon
st.subheader("📊 Duration vs Coupon Rate")
coupons = np.linspace(0, 0.12, 30)
durations_coupon = [duration_macaulay(face_value, c, years, ytm, freq) for c in coupons]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=coupons*100, y=durations_coupon, mode='lines', name='Macaulay Duration'))
fig2.update_layout(title='Duration vs Coupon Rate', xaxis_title='Coupon Rate (%)', yaxis_title='Duration (years)')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("📚 Hopewell & Kaufman (1973) - Duration Properties"):
    st.markdown("""
    **Key Findings from Hopewell & Kaufman:**
    
    1. Duration increases with maturity but at a decreasing rate
    2. Duration decreases as coupon rate increases
    3. Duration decreases as yield to maturity increases
    4. For zero-coupon bonds, duration = time to maturity
    
    **Convexity:** Duration is a linear approximation. Actual price changes have convexity (curvature).
    """)