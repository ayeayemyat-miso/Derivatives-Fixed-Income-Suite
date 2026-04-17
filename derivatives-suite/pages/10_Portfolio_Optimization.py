import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Portfolio Optimization", layout="wide")

st.title("⚖️ Modern Portfolio Theory")
st.markdown("Optimize portfolio weights using Markowitz efficient frontier")

# Stock selection
st.subheader("📊 Portfolio Selection")
tickers = st.multiselect(
    "Select stocks", 
    ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ', 'WMT', 'KO'],
    default=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
)

period = st.selectbox("Data Period", ["1y", "2y", "3y", "6mo"], index=0)

if len(tickers) >= 2:
    # Download data - FIXED: Handle MultiIndex correctly
    with st.spinner("Downloading data..."):
        data = yf.download(tickers, period=period)
        
        # Extract Adjusted Close prices
        if 'Adj Close' in data.columns:
            # Single ticker case or when data is not MultiIndex
            if len(tickers) == 1:
                prices = pd.DataFrame(data['Adj Close'])
                prices.columns = tickers
            else:
                prices = data['Adj Close']
        else:
            # Fallback to Close if Adj Close not available
            if len(tickers) == 1:
                prices = pd.DataFrame(data['Close'])
                prices.columns = tickers
            else:
                prices = data['Close']
        
        # Ensure we have all tickers
        if isinstance(prices, pd.Series):
            prices = pd.DataFrame(prices)
            prices.columns = tickers if len(tickers) > 1 else [tickers[0]]
    
    # Calculate returns
    returns = prices.pct_change().dropna()
    
    # Check if we have enough data
    if len(returns) < 10:
        st.error("Not enough data available for selected period. Try a longer period.")
        st.stop()
    
    # Calculate annualized statistics
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    # Generate random portfolios
    n_portfolios = st.slider("Number of random portfolios", 500, 5000, 1000, 500)
    
    results = np.zeros((3, n_portfolios))
    weights_record = []
    
    for i in range(n_portfolios):
        weights = np.random.random(len(tickers))
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std
        results[2,i] = portfolio_return / portfolio_std if portfolio_std > 0 else 0
    
    # Find optimal portfolios
    max_sharpe_idx = np.argmax(results[2])
    min_vol_idx = np.argmin(results[1])
    
    # Display
    st.subheader("📈 Efficient Frontier")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results[1,:]*100, y=results[0,:]*100, 
                             mode='markers', 
                             marker=dict(color=results[2,:], colorscale='Viridis', showscale=True,
                                        colorbar=dict(title="Sharpe Ratio")),
                             text=[f'Sharpe: {s:.2f}' for s in results[2,:]],
                             name='Random Portfolios',
                             hovertemplate='Return: %{y:.2f}%<br>Risk: %{x:.2f}%<br>Sharpe: %{text}<extra></extra>'))
    
    fig.add_trace(go.Scatter(x=[results[1,max_sharpe_idx]*100], y=[results[0,max_sharpe_idx]*100],
                             mode='markers', marker=dict(size=15, color='red', symbol='star'), 
                             name='Max Sharpe Ratio'))
    
    fig.add_trace(go.Scatter(x=[results[1,min_vol_idx]*100], y=[results[0,min_vol_idx]*100],
                             mode='markers', marker=dict(size=15, color='green', symbol='circle'),
                             name='Min Variance'))
    
    fig.update_layout(title='Efficient Frontier',
                      xaxis_title='Annualized Volatility (%)',
                      yaxis_title='Annualized Return (%)',
                      hovermode='closest')
    st.plotly_chart(fig, use_container_width=True)
    
    # Optimal portfolio weights
    st.subheader("🎯 Optimal Portfolio Weights")
    
    col_w1, col_w2 = st.columns(2)
    
    with col_w1:
        st.markdown("**📈 Maximum Sharpe Ratio Portfolio**")
        optimal_weights = weights_record[max_sharpe_idx]
        weight_df = pd.DataFrame({'Stock': tickers, 'Weight %': optimal_weights * 100})
        weight_df = weight_df.sort_values('Weight %', ascending=False)
        st.dataframe(weight_df, use_container_width=True)
        
        st.metric("Expected Annual Return", f"{results[0,max_sharpe_idx]*100:.2f}%")
        st.metric("Expected Annual Volatility", f"{results[1,max_sharpe_idx]*100:.2f}%")
        st.metric("Sharpe Ratio", f"{results[2,max_sharpe_idx]:.3f}")
    
    with col_w2:
        st.markdown("**🛡️ Minimum Variance Portfolio**")
        min_var_weights = weights_record[min_vol_idx]
        weight_df2 = pd.DataFrame({'Stock': tickers, 'Weight %': min_var_weights * 100})
        weight_df2 = weight_df2.sort_values('Weight %', ascending=False)
        st.dataframe(weight_df2, use_container_width=True)
        
        st.metric("Expected Annual Return", f"{results[0,min_vol_idx]*100:.2f}%")
        st.metric("Expected Annual Volatility", f"{results[1,min_vol_idx]*100:.2f}%")
        st.metric("Sharpe Ratio", f"{results[2,min_vol_idx]:.3f}")
    
    # Equal weights comparison
    st.subheader("📊 Strategy Comparison")
    equal_weights = np.ones(len(tickers)) / len(tickers)
    eq_return = np.sum(mean_returns * equal_weights)
    eq_std = np.sqrt(np.dot(equal_weights.T, np.dot(cov_matrix, equal_weights)))
    eq_sharpe = eq_return / eq_std if eq_std > 0 else 0
    
    comparison = pd.DataFrame({
        'Strategy': ['Max Sharpe', 'Min Variance', 'Equal Weight'],
        'Return (%)': [results[0,max_sharpe_idx]*100, results[0,min_vol_idx]*100, eq_return*100],
        'Risk (%)': [results[1,max_sharpe_idx]*100, results[1,min_vol_idx]*100, eq_std*100],
        'Sharpe Ratio': [results[2,max_sharpe_idx], results[2,min_vol_idx], eq_sharpe]
    })
    st.dataframe(comparison, use_container_width=True)
    
    # Pie chart of optimal portfolio
    st.subheader("🥧 Optimal Portfolio Allocation")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown("**Max Sharpe Portfolio**")
        fig_pie1 = go.Figure(data=[go.Pie(labels=weight_df['Stock'], values=weight_df['Weight %'], 
                                          hole=0.3, textinfo='percent', textposition='auto')])
        fig_pie1.update_layout(height=400)
        st.plotly_chart(fig_pie1, use_container_width=True)
    
    with col_p2:
        st.markdown("**Min Variance Portfolio**")
        fig_pie2 = go.Figure(data=[go.Pie(labels=weight_df2['Stock'], values=weight_df2['Weight %'],
                                          hole=0.3, textinfo='percent', textposition='auto')])
        fig_pie2.update_layout(height=400)
        st.plotly_chart(fig_pie2, use_container_width=True)
    
    # Correlation matrix heatmap
    st.subheader("📊 Correlation Matrix")
    corr_matrix = returns.corr()
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        text=corr_matrix.round(2).values,
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    fig_heat.update_layout(title='Stock Return Correlations', height=500)
    st.plotly_chart(fig_heat, use_container_width=True)
    
    with st.expander("📚 Markowitz Modern Portfolio Theory"):
        st.markdown("""
        **Key Concepts:**
        
        1. **Diversification Benefit:** Portfolio risk < weighted average of individual risks
           - Correlation < 1 reduces portfolio variance
        
        2. **Efficient Frontier:** Set of optimal portfolios offering highest return for given risk
           - Portfolios below frontier are suboptimal
        
        3. **Sharpe Ratio:** (Return - Risk-free rate) / Volatility
           - Measures risk-adjusted return
           - Higher Sharpe = better risk/reward tradeoff
        
        **Your Portfolio Analysis:**
        
        - The **Max Sharpe portfolio** balances risk and return
        - The **Min Variance portfolio** minimizes risk regardless of return
        - Diversification benefit: Individual stock volatilities are typically 25-40%, 
          but portfolio risk is lower
        
        **Limitations:**
        - Assumes normal returns (not true in practice)
        - Sensitive to input parameters (estimation error)
        - Historical returns may not predict future
        - Correlations change during market stress
        """)
    
    # Download info
    st.caption(f"📊 Data from Yahoo Finance | Period: {period} | {len(returns)} trading days")

else:
    st.warning("⚠️ Please select at least 2 stocks for portfolio optimization")