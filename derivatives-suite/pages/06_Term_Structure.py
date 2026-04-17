import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import minimize_scalar
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Term Structure", layout="wide")

st.title("🔮 Term Structure of Interest Rates (Yield Curve)")
st.markdown("""
Learn how interest rates vary with time to maturity - a fundamental concept in fixed income.
""")

# ========== EXPLANATION SECTION ==========
with st.expander("📖 What is Term Structure? Click to learn", expanded=True):
    st.markdown("""
    ### Simple Explanation
    
    **Term Structure** = How interest rates change with different time horizons.
    
    ### Real-World Example:
    
    | Investment | Time Horizon | Interest Rate |
    |------------|--------------|---------------|
    | 3-month Treasury bill | 3 months | 4.5% |
    | 2-year Treasury note | 2 years | 4.8% |
    | 10-year Treasury bond | 10 years | 5.2% |
    | 30-year Treasury bond | 30 years | 5.5% |
    
    When you plot these points, you get the **Yield Curve**.
    
    ### Three Typical Shapes:
    
    | Shape | What it means | Economic Signal |
    |-------|---------------|-----------------|
    | 📈 **Normal (Upward Sloping)** | Long-term rates > Short-term rates | Economic growth expected |
    | 📉 **Inverted (Downward Sloping)** | Short-term rates > Long-term rates | Recession may be coming |
    | ➡️ **Flat** | Rates are similar across maturities | Economic uncertainty |
    
    ### Why This Matters:
    - **Banks** borrow short, lend long → profit from normal curve
    - **Investors** use curve to decide bond maturities
    - **Central Banks** monitor curve for policy signals
    """)

# ========== METHOD SELECTION ==========
st.subheader("📊 Choose Your Method")

method = st.radio(
    "Select how you want to estimate the term structure:",
    ["📈 Method 1: Use Real Treasury Data (Yahoo Finance)", 
     "📝 Method 2: Enter Your Own Bond Data",
     "📐 Method 3: Nelson-Siegel Model (Smooth Curve)"],
    index=0
)

# ========== METHOD 1: REAL DATA ==========
if method == "📈 Method 1: Use Real Treasury Data (Yahoo Finance)":
    st.markdown("### Downloading Real US Treasury Yields")
    st.info("📡 Fetching current US Treasury yield curve data...")
    
    # Treasury ETF tickers as proxies
    treasury_data = {
        '1-3 months': 'BIL',
        '1-3 years': 'SHY',
        '3-7 years': 'IEI',
        '7-10 years': 'IEF',
        '10-20 years': 'TLH',
        '20+ years': 'TLT'
    }
    
    maturities = {
        'BIL': 0.25,
        'SHY': 2.0,
        'IEI': 5.0,
        'IEF': 8.5,
        'TLH': 15.0,
        'TLT': 25.0
    }
    
    try:
        with st.spinner("Fetching real-time treasury data..."):
            yields_data = {}
            for name, ticker in treasury_data.items():
                try:
                    etf = yf.Ticker(ticker)
                    info = etf.info
                    sec_yield = info.get('thirtyDayAverageYield', None)
                    if sec_yield:
                        yields_data[name] = sec_yield * 100
                    else:
                        dividend_yield = info.get('dividendYield', 0.04)
                        yields_data[name] = dividend_yield * 100
                except:
                    fallback = {
                        '1-3 months': 5.25,
                        '1-3 years': 4.75,
                        '3-7 years': 4.50,
                        '7-10 years': 4.40,
                        '10-20 years': 4.45,
                        '20+ years': 4.50
                    }
                    yields_data[name] = fallback.get(name, 4.5)
            
            plot_data = pd.DataFrame({
                'Maturity (Years)': [maturities[t] for t in treasury_data.values()],
                'Yield (%)': [yields_data[name] for name in treasury_data.keys()],
                'Treasury': list(treasury_data.keys())
            })
            plot_data = plot_data.sort_values('Maturity (Years)')
            
            st.success("✅ Data retrieved successfully!")
            
    except Exception as e:
        st.warning(f"Could not fetch live data. Using sample data.")
        plot_data = pd.DataFrame({
            'Maturity (Years)': [0.25, 1, 2, 3, 5, 7, 10, 20, 30],
            'Yield (%)': [5.25, 5.00, 4.75, 4.65, 4.55, 4.50, 4.45, 4.50, 4.55],
            'Treasury': ['3mo', '1yr', '2yr', '3yr', '5yr', '7yr', '10yr', '20yr', '30yr']
        })
    
    # Display yield curve
    st.subheader("📈 Current US Treasury Yield Curve")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_data['Maturity (Years)'], 
        y=plot_data['Yield (%)'],
        mode='lines+markers',
        name='Yield Curve',
        line=dict(color='blue', width=3),
        marker=dict(size=10, color='red')
    ))
    
    fig.update_layout(
        title='US Treasury Yield Curve',
        xaxis_title='Time to Maturity (Years)',
        yaxis_title='Yield (%)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Curve shape interpretation
    short_term = plot_data[plot_data['Maturity (Years)'] <= 2]['Yield (%)'].mean()
    long_term = plot_data[plot_data['Maturity (Years)'] >= 10]['Yield (%)'].mean()
    
    if long_term > short_term:
        curve_shape = "📈 Normal (Upward Sloping)"
        interpretation = "Markets expect economic growth and higher future inflation."
    elif long_term < short_term:
        curve_shape = "📉 Inverted (Downward Sloping)"
        interpretation = "⚠️ Potential recession signal. Markets expect rate cuts."
    else:
        curve_shape = "➡️ Flat"
        interpretation = "Economic uncertainty. Markets unsure about future direction."
    
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.metric("Short-term Rate (≤2yr)", f"{short_term:.2f}%")
    with col_i2:
        st.metric("Long-term Rate (≥10yr)", f"{long_term:.2f}%")
    
    st.info(f"**Curve Shape:** {curve_shape}\n\n**Interpretation:** {interpretation}")

# ========== METHOD 2: USER INPUT ==========
elif method == "📝 Method 2: Enter Your Own Bond Data":
    st.markdown("### Enter Bond Data to Bootstrap the Yield Curve")
    st.caption("💡 Enter the price and coupon for bonds of different maturities")
    
    default_bonds = pd.DataFrame({
        'Maturity (years)': [0.5, 1, 2, 3, 5, 7, 10],
        'Coupon Rate (%)': [0.0, 0.0, 4.0, 4.0, 3.5, 4.0, 4.5],
        'Bond Price ($)': [98.5, 96.0, 101.5, 102.0, 100.5, 103.0, 105.0]
    })
    
    edited_bonds = st.data_editor(
        default_bonds,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Maturity (years)": st.column_config.NumberColumn("Maturity (years)", min_value=0.1, max_value=50.0),
            "Coupon Rate (%)": st.column_config.NumberColumn("Coupon Rate (%)", min_value=0.0, max_value=20.0),
            "Bond Price ($)": st.column_config.NumberColumn("Bond Price ($)", min_value=50.0, max_value=150.0)
        }
    )
    
    if len(edited_bonds) < 2:
        st.warning("⚠️ Please enter at least 2 bonds to estimate the curve")
        st.stop()
    
    # Bootstrap function
    def bootstrap_curve(bond_df):
        zero_rates = []
        
        for i, row in bond_df.iterrows():
            maturity = row['Maturity (years)']
            coupon = row['Coupon Rate (%)'] / 100
            price = row['Bond Price ($)']
            
            def objective(rate):
                pv = 0
                n_periods = int(maturity * 2)
                for t in range(1, n_periods + 1):
                    if t < n_periods:
                        pv += (coupon * 100 / 2) * np.exp(-rate * (t/2))
                    else:
                        pv += (coupon * 100 / 2 + 100) * np.exp(-rate * (t/2))
                return abs(pv - price)
            
            result = minimize_scalar(objective, bounds=(0, 0.20), method='bounded')
            zero_rates.append({
                'Maturity': maturity,
                'Zero Rate (%)': result.x * 100
            })
        
        return pd.DataFrame(zero_rates)
    
    # Calculate curve
    zero_curve = bootstrap_curve(edited_bonds)
    
    # Display results
    st.subheader("📈 Bootstrapped Zero-Coupon Yield Curve")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=zero_curve['Maturity'], 
        y=zero_curve['Zero Rate (%)'],
        mode='lines+markers',
        name='Zero Rates',
        line=dict(color='blue', width=3),
        marker=dict(size=10)
    ))
    fig.update_layout(
        title='Zero-Coupon Yield Curve (Bootstrapped)',
        xaxis_title='Maturity (Years)',
        yaxis_title='Zero Rate (%)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(zero_curve, use_container_width=True)

# ========== METHOD 3: NELSON-SIEGEL ==========
else:
    st.markdown("### Nelson-Siegel Model - Smooth Yield Curve")
    st.caption("The Nelson-Siegel model fits a smooth mathematical curve to yield curve data")
    
    col_n1, col_n2 = st.columns(2)
    
    with col_n1:
        st.markdown("**Model Parameters (adjust to see effect):**")
        beta0 = st.slider("β₀ (Long-term level)", 2.0, 8.0, 4.5, 0.1)
        beta1 = st.slider("β₁ (Short-term slope)", -4.0, 0.0, -1.5, 0.1)
        beta2 = st.slider("β₂ (Curvature)", -2.0, 4.0, 1.0, 0.1)
        tau = st.slider("τ (Decay factor)", 0.5, 5.0, 2.0, 0.1)
    
    with col_n2:
        st.markdown("**Curve Shape Interpretation:**")
        short_rate = beta0 + beta1
        long_rate = beta0
        st.info(f"""
        - **Long-term rate:** {beta0:.2f}%
        - **Short-term rate:** {short_rate:.2f}%
        - **Curve shape:** {'Normal' if short_rate < long_rate else 'Inverted' if short_rate > long_rate else 'Flat'}
        """)
    
    def nelson_siegel(beta0, beta1, beta2, tau, maturity):
        lambd = maturity / tau
        factor1 = (1 - np.exp(-lambd)) / lambd if lambd > 0 else 1
        factor2 = ((1 - np.exp(-lambd)) / lambd) - np.exp(-lambd) if lambd > 0 else 0
        return beta0 + beta1 * factor1 + beta2 * factor2
    
    maturities = np.linspace(0.1, 30, 100)
    yields = [nelson_siegel(beta0, beta1, beta2, tau, m) for m in maturities]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=maturities, 
        y=yields,
        mode='lines',
        name='Nelson-Siegel Curve',
        line=dict(color='blue', width=3)
    ))
    fig.update_layout(
        title='Nelson-Siegel Yield Curve',
        xaxis_title='Maturity (Years)',
        yaxis_title='Yield (%)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sample yields
    st.subheader("📊 Sample Yields")
    sample_maturities = [0.25, 1, 2, 3, 5, 7, 10, 20, 30]
    sample_yields = [nelson_siegel(beta0, beta1, beta2, tau, m) for m in sample_maturities]
    
    sample_df = pd.DataFrame({
        'Maturity': ['3mo', '1yr', '2yr', '3yr', '5yr', '7yr', '10yr', '20yr', '30yr'],
        'Yield (%)': [f"{y:.2f}%" for y in sample_yields]
    })
    st.dataframe(sample_df, use_container_width=True)

# ========== INTERPRETATION SECTION ==========
with st.expander("📖 Understanding the Yield Curve", expanded=False):
    st.markdown("""
    ### How to Read and Interpret the Yield Curve
    
    **Three Classic Shapes and What They Mean:**
    
    | Shape | Economic Signal | What to Do |
    |-------|-----------------|------------|
    | **Normal (Upward)** | Economic growth expected | Buy longer-term bonds for higher yield |
    | **Inverted (Downward)** | Recession may be coming | Move to short-term, safe investments |
    | **Flat** | Economic uncertainty | Stay flexible, medium-term bonds |
    
    ### Historical Examples:
    - **Before 2008 Crisis:** Curve inverted in 2006 → Recession followed in 2008
    - **2022-2023:** Curve inverted → Many predicted recession
    
    ### Why This Matters for Regulators:
    - Banks use yield curve for interest rate risk management
    - Central banks monitor curve for policy signals
    - Inverted curve often precedes economic downturns
    """)

st.caption("📊 The term structure is fundamental to bond pricing, risk management, and monetary policy")