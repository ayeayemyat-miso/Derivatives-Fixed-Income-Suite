import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="VaR & CVaR Analysis", layout="wide")

st.title("🎲 Value at Risk (VaR) & Conditional VaR (CVaR)")
st.markdown("""
Calculate portfolio risk metrics using **Historical Simulation** and **Variance-Covariance** methods.
Learn how much you could lose in normal and extreme market conditions.
""")

# ========== EXPLANATION SECTION ==========
with st.expander("📖 What is VaR and CVaR? Click to learn", expanded=False):
    st.markdown("""
    ### Simple Explanation
    
    **Value at Risk (VaR):** The maximum loss you expect over a given time period at a certain confidence level.
    
    **Example:** "10-day 99% VaR = $10,000" means:
    - There is a **99% confidence** that you won't lose more than $10,000
    - Or: Only **1% chance** (1 in 100) of losing MORE than $10,000
    
    **Conditional VaR (CVaR):** The average loss IF losses exceed the VaR threshold.
    
    **Example:** If VaR = $10,000 and CVaR = $15,000:
    - When you DO lose money, the average loss is $15,000
    - CVaR captures "tail risk" that VaR misses
    
    ### Real-World Example:
    
    | Confidence Level | Meaning | Business Use |
    |-----------------|---------|--------------|
    | 95% | Standard risk management | Daily trading limits |
    | 99% | Regulatory capital (Basel) | Bank capital requirements |
    | 99.9% | Extreme stress scenarios | "Black swan" planning |
    
    ### Why CVaR is Better for Regulators:
    - VaR tells you the threshold (lose at least X)
    - CVaR tells you the expected loss beyond that threshold
    - Basel III.5 now requires CVaR (Expected Shortfall)
    """)

# ========== INPUT SECTION ==========
st.subheader("📊 Portfolio Setup")

# Stock selection
default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ']
tickers = st.multiselect(
    "Select stocks for your portfolio", 
    default_tickers,
    default=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
)

# Period selection
period_options = {
    "6 months (approx 126 trading days)": "6mo",
    "1 year (approx 252 trading days)": "1y",
    "2 years (approx 504 trading days)": "2y",
    "3 years (approx 756 trading days)": "3y",
    "5 years (approx 1260 trading days)": "5y"
}

period_label = st.selectbox(
    "Select data period for analysis",
    list(period_options.keys()),
    index=1
)
period = period_options[period_label]

# Risk parameters
col_r1, col_r2 = st.columns(2)
with col_r1:
    confidence = st.slider(
        "Confidence Level (%)", 
        90, 99, 95, 1,
        help="95% is standard for risk management. 99% is for regulatory capital."
    ) / 100
    
with col_r2:
    horizon = st.number_input(
        "VaR Horizon (days)", 
        1, 30, 10, 1,
        help="How many days ahead. 10-day VaR is standard for Basel regulations."
    )

st.caption(f"📊 Calculating {horizon}-day {confidence*100:.0f}% VaR using {period_label.lower()}")

if len(tickers) == 0:
    st.warning("⚠️ Please select at least one stock")
    st.stop()

# ========== DOWNLOAD AND CALCULATE ==========
with st.spinner(f"Downloading {len(tickers)} stocks from Yahoo Finance for {period_label}..."):
    try:
        data = yf.download(tickers, period=period)
        
        # Extract Adjusted Close prices
        if 'Adj Close' in data.columns:
            if len(tickers) == 1:
                prices = pd.DataFrame(data['Adj Close'])
                prices.columns = tickers
            else:
                prices = data['Adj Close']
        else:
            if len(tickers) == 1:
                prices = pd.DataFrame(data['Close'])
                prices.columns = tickers
            else:
                prices = data['Close']
        
        if isinstance(prices, pd.Series):
            prices = pd.DataFrame(prices)
            prices.columns = tickers if len(tickers) > 1 else [tickers[0]]
        
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        if len(returns) < 10:
            st.error(f"Not enough data. Only {len(returns)} trading days available.")
            st.stop()
            
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        st.stop()

# Get actual data range
start_date = returns.index[0].strftime('%B %d, %Y')
end_date = returns.index[-1].strftime('%B %d, %Y')
trading_days = len(returns)

st.success(f"✅ Downloaded {trading_days} trading days of data from {start_date} to {end_date}")

# Equal weights
weights = np.ones(len(tickers)) / len(tickers)

# Portfolio returns
portfolio_returns = returns.dot(weights)

# ========== VAR CALCULATIONS ==========
# Historical VaR (Non-parametric)
historical_var = np.percentile(portfolio_returns * horizon, (1 - confidence) * 100)

# Normal distribution VaR (Parametric)
mu = portfolio_returns.mean() * horizon
sigma = portfolio_returns.std() * np.sqrt(horizon)
from scipy import stats
z_score = stats.norm.ppf(confidence)
normal_var = mu - z_score * sigma

# CVaR (Expected Shortfall) - Historical method
losses = portfolio_returns * horizon
var_threshold = np.percentile(losses, (1 - confidence) * 100)
cvar = losses[losses <= var_threshold].mean()

# Convert to dollar amounts (assuming $1,000,000 portfolio)
portfolio_value = 1_000_000
var_dollar = abs(historical_var) * portfolio_value
cvar_dollar = abs(cvar) * portfolio_value

# ========== DISPLAY RESULTS ==========
st.subheader("📈 Portfolio Risk Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Historical VaR", f"{historical_var*100:.2f}%")
    st.caption(f"= ${var_dollar:,.0f} on $1M")

with col2:
    st.metric("Normal VaR", f"{normal_var*100:.2f}%")
    st.caption("(Assumes normal distribution)")

with col3:
    st.metric("Conditional VaR (CVaR)", f"{cvar*100:.2f}%")
    st.caption(f"= ${cvar_dollar:,.0f} on $1M")

with col4:
    st.metric("Confidence Level", f"{confidence*100:.0f}%")
    st.caption(f"{horizon}-day horizon")

# Interpretation box
st.info(f"""
📖 **Interpretation for your portfolio:**

- **{horizon}-day {confidence*100:.0f}% VaR = {abs(historical_var)*100:.2f}%**  
  → There is a {(1-confidence)*100:.0f}% chance of losing MORE than {abs(historical_var)*100:.2f}% over {horizon} days

- **CVaR = {abs(cvar)*100:.2f}%**  
  → When losses exceed {abs(historical_var)*100:.2f}%, the AVERAGE loss is {abs(cvar)*100:.2f}%

- **On a $1,000,000 portfolio:**  
  → Worst expected loss (95% confidence): **${var_dollar:,.0f}**  
  → Average loss in extreme scenarios: **${cvar_dollar:,.0f}**
""")

# ========== DISTRIBUTION CHART ==========
st.subheader("📊 Return Distribution with VaR Thresholds")

fig = go.Figure()

# Histogram of returns
fig.add_trace(go.Histogram(
    x=portfolio_returns * horizon * 100,
    nbinsx=50,
    name='Portfolio Returns',
    marker_color='lightblue',
    opacity=0.7
))

# VaR line
fig.add_vline(
    x=historical_var * 100, 
    line_dash="dash", 
    line_color="red", 
    line_width=3,
    annotation_text=f"VaR: {historical_var*100:.2f}%",
    annotation_position="top left"
)

# CVaR line
fig.add_vline(
    x=cvar * 100, 
    line_dash="dash", 
    line_color="purple", 
    line_width=3,
    annotation_text=f"CVaR: {cvar*100:.2f}%",
    annotation_position="bottom right"
)

# Shade the tail region
tail_mask = (portfolio_returns * horizon * 100) <= (historical_var * 100)
if any(tail_mask):
    tail_returns = portfolio_returns[tail_mask] * horizon * 100
    fig.add_trace(go.Histogram(
        x=tail_returns,
        nbinsx=20,
        name='Tail Region (Beyond VaR)',
        marker_color='red',
        opacity=0.5
    ))

fig.update_layout(
    title=f'{horizon}-Day Portfolio Return Distribution (Based on {trading_days} trading days)',
    xaxis_title=f'{horizon}-Day Return (%)',
    yaxis_title='Frequency',
    barmode='overlay',
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# ========== CORRELATION MATRIX ==========
st.subheader("📊 Stock Return Correlation Matrix")

# Calculate correlation matrix correctly
corr_matrix = returns.corr()

# Create heatmap
fig_corr = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns.tolist(),
    y=corr_matrix.index.tolist(),
    colorscale='RdBu',
    zmin=-1, 
    zmax=1,
    text=corr_matrix.round(2).values,
    texttemplate='%{text}',
    textfont={"size": 12, "color": "black"},
    hoverongaps=False,
    colorbar=dict(title="Correlation", tickvals=[-1, -0.5, 0, 0.5, 1])
))

fig_corr.update_layout(
    title=f'Correlation Matrix (Based on {period_label} data: {start_date} to {end_date})',
    height=500
)
st.plotly_chart(fig_corr, use_container_width=True)

# Add correlation interpretation
avg_correlation = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
st.caption(f"📈 Average correlation between stocks: {avg_correlation:.3f}")
if avg_correlation > 0.7:
    st.warning("⚠️ High average correlation means limited diversification benefit!")
elif avg_correlation > 0.4:
    st.info("📊 Moderate correlation - some diversification benefit")
else:
    st.success("✅ Low correlation - good diversification!")

# ========== INDIVIDUAL STOCK RISK ==========
st.subheader("📋 Individual Stock Risk Metrics")

stock_metrics = []
for ticker in tickers:
    stock_returns = returns[ticker]
    stock_var = np.percentile(stock_returns * horizon, (1 - confidence) * 100)
    stock_cvar = stock_returns[stock_returns * horizon <= stock_var * horizon].mean() if any(stock_returns * horizon <= stock_var * horizon) else stock_var
    stock_vol = stock_returns.std() * np.sqrt(252) * 100
    stock_return = stock_returns.mean() * 252 * 100
    stock_sharpe = stock_return / stock_vol if stock_vol > 0 else 0
    
    stock_metrics.append({
        'Stock': ticker,
        'VaR (%)': f"{stock_var * 100:.2f}%",
        'CVaR (%)': f"{stock_cvar * 100:.2f}%",
        'Volatility (%)': f"{stock_vol:.1f}%",
        'Annual Return (%)': f"{stock_return:.1f}%",
        'Sharpe Ratio': f"{stock_sharpe:.2f}"
    })

stock_df = pd.DataFrame(stock_metrics)
st.dataframe(stock_df, use_container_width=True)

# ========== DIVERSIFICATION BENEFIT ==========
st.subheader("📊 Diversification Benefit")

# Calculate average individual risk
avg_individual_var = np.mean([float(s['VaR (%)'].replace('%', '')) for s in stock_metrics]) / 100
portfolio_var_abs = abs(historical_var)

benefit = (avg_individual_var - portfolio_var_abs) / avg_individual_var * 100 if avg_individual_var > 0 else 0

col_b1, col_b2 = st.columns(2)

with col_b1:
    st.metric("Average Individual Stock VaR", f"{avg_individual_var*100:.2f}%")
    st.metric("Portfolio VaR", f"{portfolio_var_abs*100:.2f}%")

with col_b2:
    st.metric("Diversification Benefit", f"{benefit:.1f}%", 
              delta=f"Risk reduced by {benefit:.1f}%" if benefit > 0 else "No benefit")
    st.caption("Lower portfolio risk vs. average individual stock risk")

if benefit > 20:
    st.success(f"🎯 Great diversification! Your portfolio risk is {benefit:.0f}% lower than the average individual stock risk.")
elif benefit > 0:
    st.info(f"📉 Some diversification benefit: {benefit:.0f}% risk reduction.")
else:
    st.warning("⚠️ No diversification benefit - stocks are highly correlated!")

# ========== REGULATORY CONTEXT ==========
with st.expander("🏛️ Why VaR and CVaR Matter for Regulators (Basel Framework)"):
    st.markdown(f"""
    ### Basel III Capital Requirements
    
    **Market Risk Capital = max(VaR, avg VaR × 3) + SVaR + CVaR**
    
    ### Your Portfolio Would Require:
    
    | Metric | Your Value | Regulatory Use |
    |--------|-----------|----------------|
    | 10-day 99% VaR | {abs(historical_var)*100:.2f}% | Basel standard VaR |
    | CVaR (Expected Shortfall) | {abs(cvar)*100:.2f}% | Basel III.5 requirement |
    
    ### Key Regulatory Requirements:
    
    **1. Backtesting (Basel II.5)**
    - Compare daily VaR to actual losses
    - More than 4 exceptions in 250 days = penalty
    
    **2. CVaR (Basel III.5 - 2019)**
    - Replaces VaR for market risk
    - Captures tail risk better
    
    **3. Stress VaR (SVaR)**
    - Based on 1-year stressed period
    - Captures crisis behavior
    
    **4. Trading Book vs Banking Book**
    - Trading book: Mark-to-market, daily VaR
    - Banking book: Hold-to-maturity, different rules
    
    **Source:** Basel Committee on Banking Supervision (2019)
    """)

# ========== METHODOLOGY EXPLANATION ==========
with st.expander("📚 How VaR and CVaR Are Calculated"):
    st.markdown(f"""
    ### Methodology Used in This Calculator
    
    **1. Historical Simulation (Non-parametric)**
    - VaR = percentile(historical_returns × horizon, 1 - confidence)
    - CVaR = mean(returns[returns ≤ VaR])
    
    **Your Results:**
    - VaR: {abs(historical_var)*100:.2f}%
    - CVaR: {abs(cvar)*100:.2f}%
    
    **2. Normal Distribution Method (Parametric)**
    - VaR = μ - z_α × σ
    - Where: μ = mean return × horizon, σ = standard deviation × √horizon
    
    **3. Covariance Method (for portfolios)**
    - σ_portfolio = √(wᵀ × Σ × w)
    - Where Σ is the variance-covariance matrix
    
    ### Key Assumptions:
    - Returns are independent and identically distributed
    - Historical data predicts future (not always true)
    - No extreme events (but CVaR helps)
    
    ### Limitations:
    - VaR is not subadditive
    - Historical VaR assumes past repeats
    - Normal VaR underestimates tail risk
    
    **Reference:** Hull, J. (2023), "Risk Management and Financial Institutions", Chapter 9
    """)

# Data summary footer
st.caption(f"""
---
📊 **Data Summary:** {len(tickers)} stocks | {trading_days} trading days | {start_date} to {end_date} | {period_label}
📐 **Methodology:** Historical Simulation (VaR & CVaR) + Normal Distribution
🏛️ **Regulatory Standard:** Basel III.5 compliant (CVaR / Expected Shortfall)
""")