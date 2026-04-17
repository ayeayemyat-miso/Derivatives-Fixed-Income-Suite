import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bond import price_bond, ytm_bisection

st.set_page_config(page_title="YTM Calculator", layout="wide")

st.title("🎯 Yield to Maturity Calculator")
st.markdown("Calculate YTM using the Bisection numerical method")

# Inputs
col1, col2 = st.columns(2)

with col1:
    face_value = st.number_input("Face Value ($)", 100, 100000, 1000, 100)
    coupon_rate = st.number_input("Coupon Rate (%)", 0.0, 15.0, 5.0, 0.1) / 100
    years = st.number_input("Years to Maturity", 1.0, 30.0, 10.0, 0.5)

with col2:
    market_price = st.number_input("Current Market Price ($)", 100.0, 2000.0, 950.0, 5.0)
    freq = st.selectbox("Coupon Frequency", [1, 2, 4, 12], index=1)

# Calculate YTM
ytm = ytm_bisection(face_value, coupon_rate, years, market_price, freq)

# Verification price
calc_price = price_bond(face_value, coupon_rate, years, ytm, freq)

# Display
col_r1, col_r2 = st.columns(2)
col_r1.metric("Yield to Maturity", f"{ytm*100:.4f}%")
col_r2.metric("Calculated Price (verification)", f"${calc_price:,.2f}")

# Difference
st.metric("Price Difference", f"${abs(market_price - calc_price):.4f}", 
          delta="Should be near zero" if abs(market_price - calc_price) < 0.01 else "Check inputs")

# Show bisection steps
st.subheader("📈 Bisection Method Convergence")

# Demonstrate bisection steps
low, high = 0.0001, 0.50
convergence_data = []

for i in range(15):
    mid = (low + high) / 2
    p = price_bond(face_value, coupon_rate, years, mid, freq)
    convergence_data.append({'iteration': i+1, 'ytm': mid*100, 'price': p})
    
    if p > market_price:
        low = mid
    else:
        high = mid

df_convergence = pd.DataFrame(convergence_data)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_convergence['iteration'], y=df_convergence['ytm'], 
                         mode='lines+markers', name='YTM Estimate'))
fig.add_hline(y=ytm*100, line_dash="dash", line_color="red", annotation_text=f"Final YTM: {ytm*100:.4f}%")
fig.update_layout(title='Bisection Method Convergence', 
                  xaxis_title='Iteration', 
                  yaxis_title='YTM (%)')
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df_convergence, use_container_width=True)

with st.expander("📚 How Bisection Works"):
    st.markdown("""
    **Bisection Method Steps:**
    
    1. Start with low = 0.01% and high = 50%
    2. Calculate price at midpoint: mid = (low + high) / 2
    3. If price(mid) > market price → YTM too low → set low = mid
    4. If price(mid) < market price → YTM too high → set high = mid
    5. Repeat until convergence
    
    **Why Bisection?**
    - Guaranteed to converge (unlike Newton-Raphson)
    - No derivatives needed
    - Robust for non-convex problems
    """)