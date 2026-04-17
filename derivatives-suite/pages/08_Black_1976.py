import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Black (1976) Model", layout="wide")

st.title("🎯 Black (1976) Model for Bond Futures Options")
st.markdown("Price European options on bond futures using the Black model.")

# ========== EXPLANATION SECTION ==========
with st.expander("📖 How This Calculator Works", expanded=False):
    st.markdown("""
    ### The Formula
    
    **Step 1: Calculate Futures Price**
    
    F = (B - I) × e^(r × T)
    
    Where:
    - **B** = Current bond price
    - **I** = Present value of coupon payments
    - **r** = Risk-free interest rate
    - **T** = Time to expiry in years
    
    **Step 2: Price Option using Black (1976)**
    
    Call = e^(-rT) × [F × N(d1) - K × N(d2)]
    
    Put = e^(-rT) × [K × N(-d2) - F × N(-d1)]
    
    Where:
    - **K** = Strike price
    - **σ** = Volatility
    - **N()** = Cumulative normal distribution
    """)

# ========== INPUT METHOD SELECTION ==========
method = st.radio(
    "Select input method:",
    ["Method 1: Input Bond Price (B) and Coupons (I)",
     "Method 2: Input Futures Price (F) Directly"],
    index=0,
    help="Method 1 calculates futures price from bond data. Method 2 uses futures price directly."
)

st.subheader("Option Parameters")

col1, col2 = st.columns(2)

with col1:
    K = st.number_input("Strike Price (K)", 50.0, 200.0, 100.0, 1.0, help="Option strike price")
    r = st.number_input("Risk-Free Rate (r)", 0.0, 0.15, 0.05, 0.005, format="%.3f", help="Annual risk-free interest rate")
    T = st.number_input("Time to Expiry (T)", 0.1, 5.0, 1.0, 0.1, format="%.1f", help="Time to expiry in years")
    
with col2:
    sigma = st.number_input("Volatility (σ)", 0.05, 0.50, 0.20, 0.01, format="%.2f", help="Annualized volatility")
    option_type = st.selectbox("Option Type", ["Call", "Put"], index=0, help="Call = right to buy, Put = right to sell")

# ========== CALCULATE FUTURES PRICE ==========
B = None
I = None
F = None

if method == "Method 1: Input Bond Price (B) and Coupons (I)":
    st.subheader("Bond Inputs")
    
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        B = st.number_input("Bond Price (B)", 80.0, 150.0, 125.0, 1.0, help="Current market price of the bond")
    with col_b2:
        I = st.number_input("Coupon PV (I)", 0.0, 50.0, 10.0, 1.0, help="Present value of coupon payments")
    
    spot_price = B - I
    F = spot_price * np.exp(r * T)
    
    # Show calculated futures price
    st.info(f"**Calculated Futures Price:** ${F:.3f} = (${B} - ${I}) × e^({r:.2f} × {T})")

else:
    st.subheader("Futures Input")
    F = st.number_input("Futures Price (F)", 80.0, 200.0, 120.90, 1.0, help="Current futures price")

# ========== BLACK (1976) FUNCTIONS ==========
def black_1976_call(F, K, T, r, sigma):
    """Black (1976) Call Option Price"""
    if T <= 0:
        return max(0, F - K)
    d1 = (np.log(F / K) + (0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return np.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))

def black_1976_put(F, K, T, r, sigma):
    """Black (1976) Put Option Price"""
    if T <= 0:
        return max(0, K - F)
    d1 = (np.log(F / K) + (0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return np.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))

# Calculate option prices
call_price = black_1976_call(F, K, T, r, sigma)
put_price = black_1976_put(F, K, T, r, sigma)

# ========== DISPLAY RESULTS ==========
st.subheader("📊 Option Prices")

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    if option_type == "Call":
        st.metric("Call Option Price", f"${call_price:.3f}")
        st.caption(f"Right to buy futures at ${K}")
    else:
        st.metric("Put Option Price", f"${put_price:.3f}")
        st.caption(f"Right to sell futures at ${K}")

with col_r2:
    st.metric("Futures Price (F)", f"${F:.3f}")
    st.caption("Underlying asset price")

with col_r3:
    if option_type == "Call":
        intrinsic = max(0, F - K)
        time_value = call_price - intrinsic
    else:
        intrinsic = max(0, K - F)
        time_value = put_price - intrinsic
    st.metric("Intrinsic Value", f"${intrinsic:.3f}")
    st.metric("Time Value", f"${time_value:.3f}", delta="Option premium" if time_value > 0 else None)

# ========== COMPLETE RESULTS TABLE ==========
st.subheader("📋 Complete Results")

results_df = pd.DataFrame({
    'Option Type': ['Call', 'Put'],
    'Price': [f"${call_price:.3f}", f"${put_price:.3f}"],
    'Intrinsic Value': [f"${max(0, F-K):.3f}", f"${max(0, K-F):.3f}"],
    'Time Value': [f"${call_price - max(0, F-K):.3f}", f"${put_price - max(0, K-F):.3f}"],
    'Moneyness': [
        'In the Money' if F > K else 'Out of Money' if F < K else 'At the Money',
        'In the Money' if K > F else 'Out of Money' if K < F else 'At the Money'
    ]
})
st.dataframe(results_df, use_container_width=True, hide_index=True)

# ========== SENSITIVITY ANALYSIS ==========
st.subheader("📈 Sensitivity Analysis")

analysis_type = st.radio(
    "Select parameter to analyze:",
    ["Futures Price (F)", "Volatility (σ)", "Time to Expiry (T)"],
    horizontal=True
)

if analysis_type == "Futures Price (F)":
    F_min = max(1, F * 0.7)
    F_max = F * 1.3
    F_range = np.linspace(F_min, F_max, 50)
    call_prices = [black_1976_call(f, K, T, r, sigma) for f in F_range]
    put_prices = [black_1976_put(f, K, T, r, sigma) for f in F_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=F_range, y=call_prices, name="Call", mode="lines", line=dict(color='green', width=2)))
    fig.add_trace(go.Scatter(x=F_range, y=put_prices, name="Put", mode="lines", line=dict(color='red', width=2)))
    fig.add_vline(x=F, line_dash="dash", line_color="gray", annotation_text=f"Current F = ${F:.2f}")
    fig.add_hline(y=0, line_dash="dot", line_color="black", opacity=0.3)
    fig.update_layout(
        title='Option Price vs Futures Price',
        xaxis_title='Futures Price ($)',
        yaxis_title='Option Price ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📈 As futures price increases, calls gain value, puts lose value.")

elif analysis_type == "Volatility (σ)":
    sigma_range = np.linspace(0.05, 0.50, 50)
    call_prices = [black_1976_call(F, K, T, r, s) for s in sigma_range]
    put_prices = [black_1976_put(F, K, T, r, s) for s in sigma_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sigma_range*100, y=call_prices, name="Call", mode="lines", line=dict(color='green', width=2)))
    fig.add_trace(go.Scatter(x=sigma_range*100, y=put_prices, name="Put", mode="lines", line=dict(color='red', width=2)))
    fig.add_vline(x=sigma*100, line_dash="dash", line_color="gray", annotation_text=f"Current σ = {sigma*100:.0f}%")
    fig.update_layout(
        title='Option Price vs Volatility',
        xaxis_title='Volatility (%)',
        yaxis_title='Option Price ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📈 Higher volatility increases both call and put option prices (positive vega).")

else:
    T_range = np.linspace(0.1, 3.0, 50)
    call_prices = [black_1976_call(F, K, T, r, sigma) for t in T_range]
    put_prices = [black_1976_put(F, K, T, r, sigma) for t in T_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=T_range, y=call_prices, name="Call", mode="lines", line=dict(color='green', width=2)))
    fig.add_trace(go.Scatter(x=T_range, y=put_prices, name="Put", mode="lines", line=dict(color='red', width=2)))
    fig.add_vline(x=T, line_dash="dash", line_color="gray", annotation_text=f"Current T = {T} year")
    fig.update_layout(
        title='Option Price vs Time to Expiry',
        xaxis_title='Time to Expiry (years)',
        yaxis_title='Option Price ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📈 Options lose value as time passes (time decay / theta).")

# ========== OPTION GREEKS ==========
with st.expander("📚 Option Greeks (Risk Measures)", expanded=False):
    
    def calculate_d1(F, K, T, r, sigma):
        if T <= 0:
            return 0
        return (np.log(F / K) + (0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    def calculate_vega(F, K, T, r, sigma):
        if T <= 0:
            return 0
        d1 = calculate_d1(F, K, T, r, sigma)
        return F * norm.pdf(d1) * np.sqrt(T) * np.exp(-r * T)
    
    d1 = calculate_d1(F, K, T, r, sigma)
    delta_call = norm.cdf(d1)
    delta_put = norm.cdf(d1) - 1
    vega = calculate_vega(F, K, T, r, sigma)
    
    st.markdown("### Greeks for Current Position")
    
    greeks_df = pd.DataFrame({
        'Greek': ['Delta (Δ)', 'Vega (ν)'],
        'Call Option': [f"{delta_call:.4f}", f"${vega:.4f}"],
        'Put Option': [f"{delta_put:.4f}", f"${vega:.4f}"],
        'Interpretation': [
            f"Change per $1 change in futures price",
            f"Change per 1% change in volatility"
        ]
    })
    st.dataframe(greeks_df, use_container_width=True, hide_index=True)
    
    st.markdown(f"""
    **Current Values:**
    - **Call Delta = {delta_call:.2f}** → For every $1 increase in futures, the call gains ${delta_call:.2f}
    - **Put Delta = {delta_put:.2f}** → For every $1 increase in futures, the put loses ${abs(delta_put):.2f}
    - **Vega = ${vega:.2f}** → For every 1% increase in volatility, the option gains ${vega:.2f}
    """)

# ========== HEDGING EXPLANATION ==========
with st.expander("🏛️ Hedging with Bond Futures Options", expanded=False):
    st.markdown(f"""
    ### Using Put Options to Hedge Bond Portfolios
    
    **The Strategy:** Buy put options on bond futures to protect against rising interest rates.
    
    **How it works:**
    - When interest rates rise → bond prices fall → futures price falls
    - Put options gain value when futures price falls
    - Gains offset bond portfolio losses
    
    **Current Put Option:**
    - Price: ${put_price:.3f}
    - Delta: {delta_put:.2f}
    - Strike: ${K}
    
    **Example Hedge:**
    - Portfolio value: $10,000,000
    - Duration: 5 years
    - Expected rate increase: 1%
    - Expected loss: $500,000
    - Puts needed: Approximately 1,650 contracts
    
    **Reference:** Black, F. (1976). "The Pricing of Commodity Contracts"
    """)

# ========== INTERPRETATION ==========
with st.expander("💡 How to Interpret Results", expanded=False):
    st.markdown(f"""
    ### Current Option Status
    
    **Call Option (if selected):**
    - Futures Price (F): ${F:.2f}
    - Strike Price (K): ${K}
    - Moneyness: {'In the money' if F > K else 'Out of money' if F < K else 'At the money'}
    - Intrinsic Value: ${max(0, F-K):.3f}
    - Time Value: ${call_price - max(0, F-K):.3f}
    
    **Put Option (if selected):**
    - Futures Price (F): ${F:.2f}
    - Strike Price (K): ${K}
    - Moneyness: {'In the money' if K > F else 'Out of money' if K < F else 'At the money'}
    - Intrinsic Value: ${max(0, K-F):.3f}
    - Time Value: ${put_price - max(0, K-F):.3f}
    
    ### Key Concepts
    
    | Term | Meaning |
    |------|---------|
    | **In the Money** | Option has intrinsic value (exercise would be profitable) |
    | **Out of Money** | Option has no intrinsic value (only time value) |
    | **Time Value** | Premium for potential future movement |
    | **Intrinsic Value** | Immediate profit if exercised now |
    """)

# ========== FOOTER ==========
st.markdown("---")
st.caption("""
**Reference:** Black, F. (1976). "The Pricing of Commodity Contracts," Journal of Financial Economics

**Part of Derivatives & Fixed Income Suite | Masters of Finance TU318**
""")