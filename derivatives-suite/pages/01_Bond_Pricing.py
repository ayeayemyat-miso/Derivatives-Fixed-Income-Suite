import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bond import price_bond, duration_macaulay, duration_modified

st.set_page_config(page_title="Bond Pricing", layout="wide")

st.title("🏷️ Bond Pricing Calculator")
st.markdown("Calculate bond price, Macaulay duration, and modified duration")

# Inputs
col1, col2 = st.columns(2)

with col1:
    face_value = st.number_input("Face Value ($)", 100, 100000, 1000, 100)
    coupon_rate = st.number_input("Coupon Rate (%)", 0.0, 15.0, 5.0, 0.1) / 100
    years = st.number_input("Years to Maturity", 1.0, 30.0, 10.0, 0.5)

with col2:
    ytm = st.number_input("Yield to Maturity (%)", 0.0, 20.0, 6.0, 0.1) / 100
    freq = st.selectbox("Coupon Frequency per Year", [1, 2, 4, 12], index=1)

# Calculate
price = price_bond(face_value, coupon_rate, years, ytm, freq)
mac_dur = duration_macaulay(face_value, coupon_rate, years, ytm, freq)
mod_dur = duration_modified(mac_dur, ytm, freq)

# Results
col_r1, col_r2, col_r3 = st.columns(3)
col_r1.metric("💰 Bond Price", f"${price:,.2f}")
col_r2.metric("⏱️ Macaulay Duration", f"{mac_dur:.2f} years")
col_r3.metric("⚡ Modified Duration", f"{mod_dur:.2f} years")

# Sensitivity Analysis
st.subheader("📊 Sensitivity Analysis")
sensitivity_type = st.radio("Show sensitivity to:", ["Yield to Maturity", "Maturity", "Coupon Rate"], horizontal=True)

if sensitivity_type == "Yield to Maturity":
    col_y1, col_y2 = st.columns(2)
    with col_y1:
        ytm_min = st.number_input("Min Yield (%)", 0.0, 10.0, 1.0, 0.5) / 100
    with col_y2:
        ytm_max = st.number_input("Max Yield (%)", 1.0, 20.0, 15.0, 0.5) / 100
    
    yields = np.linspace(ytm_min, ytm_max, 50)
    prices = [price_bond(face_value, coupon_rate, years, y, freq) for y in yields]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yields*100, y=prices, mode='lines', name='Bond Price'))
    fig.update_layout(title='Price-Yield Relationship', xaxis_title='Yield (%)', yaxis_title='Price ($)')
    st.plotly_chart(fig, use_container_width=True)
    
elif sensitivity_type == "Maturity":
    maturities = np.linspace(1, 30, 30)
    prices = [price_bond(face_value, coupon_rate, m, ytm, freq) for m in maturities]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=maturities, y=prices, mode='lines+markers', name='Bond Price'))
    fig.update_layout(title='Price vs Maturity', xaxis_title='Years to Maturity', yaxis_title='Price ($)')
    st.plotly_chart(fig, use_container_width=True)
    
else:
    coupons = np.linspace(0, 0.12, 50)
    prices = [price_bond(face_value, c, years, ytm, freq) for c in coupons]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=coupons*100, y=prices, mode='lines', name='Bond Price'))
    fig.update_layout(title='Price vs Coupon Rate', xaxis_title='Coupon Rate (%)', yaxis_title='Price ($)')
    st.plotly_chart(fig, use_container_width=True)

# ========== COMPREHENSIVE INTERPRETATION SECTION ==========
st.subheader("📖 How to Interpret Bond Price and Duration")

with st.expander("🎓 Click to understand what these numbers mean", expanded=False):
    st.markdown("""
    ### What Do These Numbers Mean?
    
    **💰 Bond Price:**
    - **Price > Face Value** → Bond trades at **premium** (coupon rate > market yield)
    - **Price < Face Value** → Bond trades at **discount** (coupon rate < market yield)
    - **Price = Face Value** → Bond trades at **par**
    
    **⏱️ Macaulay Duration:**
    - Weighted average time to receive all cash flows (in years)
    - Example: 5.2 years means you get your money back in 5.2 years on average
    
    **⚡ Modified Duration:**
    - Measures **interest rate sensitivity**
    - Formula: **%ΔPrice ≈ -Modified Duration × ΔYield**
    - Example: Duration = 5 → 1% yield increase = 5% price decrease
    
    ---
    
    ### How to Use This Calculator
    
    **Try changing these inputs to see effects:**
    
    | Change | Effect on Price | Effect on Duration |
    |--------|----------------|-------------------|
    | Higher Yield | Price DECREASES | Duration DECREASES |
    | Higher Coupon | Price INCREASES | Duration DECREASES |
    | Longer Maturity | Price changes (depends on yield) | Duration INCREASES |
    
    **Example Analysis:**
    - If you expect rates to RISE → buy SHORT duration bonds
    - If you expect rates to FALL → buy LONG duration bonds
    """)

with st.expander("🏛️ Why Duration Matters for Financial Regulators", expanded=False):
    st.markdown("""
    ### SVB Bank Case (March 2023) - A Cautionary Tale
    
    **What happened:**
    - Silicon Valley Bank (SVB) bought long-term US Treasury bonds (duration ~10 years)
    - Funded these bonds with short-term customer deposits (duration ~0 years)
    - When Fed raised interest rates rapidly → bond prices crashed
    
    **The Math:**
    - Modified Duration = 10 years
    - Interest rate increase = 5%
    - Approximate loss = -10 × 5% = **-50%** on bond portfolio
    
    **Result:**
    - SVB lost billions on their bond portfolio
    - Depositors panicked and withdrew money (bank run)
    - Bank failed and was taken over by regulators
    
    **Regulatory Lesson:**
    - Banks must match **Asset Duration = Liability Duration**
    - Regulators now require **duration gap analysis** for all banks
    - Stress testing includes **interest rate shock scenarios**
    
    **Basel III Requirements:**
    - Interest Rate Risk in the Banking Book (IRRBB)
    - Mandatory duration gap reporting
    - Capital add-ons for duration mismatches
    """)

with st.expander("📚 Hopewell & Kaufman (1973) - Duration Properties", expanded=False):
    st.markdown("""
    **Key Findings from Hopewell & Kaufman (1973) - "Bond Price Volatility and Term to Maturity"**
    
    | Property | Relationship |
    |----------|--------------|
    | Duration vs Maturity | Increases but at decreasing rate |
    | Duration vs Coupon | DECREASES as coupon increases |
    | Duration vs Yield | DECREASES as yield increases |
    | Zero-coupon bonds | Duration = Time to maturity |
    
    **Why This Matters:**
    - Duration is NOT simply time to maturity
    - Higher coupon bonds are LESS sensitive to rate changes
    - Low yield environment creates HIGH duration risk
    
    **Practical Implication:**
    - In 2020-2021 (near-zero yields), bond durations were artificially high
    - When rates rose in 2022-2023, losses were amplified
    - Many investors underestimated this Hopewell-Kaufman insight
    """)

# Duration explanation (keeping original but enhanced)
with st.expander("📚 Understanding Duration (Quick Reference)", expanded=False):
    st.markdown("""
    **Duration measures interest rate risk:**
    
    - **Macaulay Duration**: Weighted average time to receive cash flows
    - **Modified Duration**: Approximate % change in price for 1% change in yield
    
    **Formula:** %ΔPrice ≈ -Modified Duration × ΔYield
    
    **Example:** If Modified Duration = 5, a 1% increase in yield → 5% price decrease
    
    **SVB Bank Case (2023):** Asset-liability duration mismatch led to bank failure.
    """)

st.caption("📊 Bond pricing uses present value of future cash flows | Duration is key for risk management")