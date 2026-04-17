import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eso_model import black_scholes, eso_adjusted_value

st.set_page_config(page_title="ESO Valuation", layout="wide")

st.title("🌟 Employee Stock Option (ESO) Valuation Tool")
st.markdown("""
Values ESOs with vesting, early exercise, and forfeiture adjustments.
**ESOs are typically worth 40-60% less than standard options due to restrictions.**
""")

# ========== SIDEBAR INPUTS ==========
with st.sidebar:
    st.markdown("## 📊 Market Inputs")
    S = st.number_input("Current Stock Price ($)", 10.0, 500.0, 100.0, 5.0)
    K = st.number_input("Strike Price ($)", 10.0, 500.0, 100.0, 5.0)
    T = st.slider("Time to Maturity (years)", 1.0, 10.0, 5.0, 0.5)
    r = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 4.0, 0.25) / 100
    sigma = st.slider("Volatility (%)", 10, 80, 35, 5) / 100
    q = st.slider("Dividend Yield (%)", 0.0, 8.0, 2.0, 0.25) / 100
    
    st.markdown("## 🏢 ESO-Specific Inputs")
    vesting = st.slider("Vesting Period (years)", 0.0, 4.0, 2.0, 0.5)
    expected_life = st.slider("Expected Life (years)", 1.0, 10.0, 4.0, 0.5)
    exercise_multiple = st.slider("Early Exercise Multiple", 1.0, 3.0, 1.5, 0.1)
    forfeiture = st.slider("Annual Forfeiture Rate (%)", 0.0, 20.0, 5.0, 1.0) / 100
    
    st.markdown("---")
    st.caption("💡 ESOs cannot be sold or traded like regular options")

# ========== CALCULATIONS ==========
bs_value = black_scholes(S, K, T, r, sigma, q, "call")
eso_value = eso_adjusted_value(S, K, T, r, sigma, q, vesting, expected_life, exercise_multiple, forfeiture)
diff = eso_value - bs_value
pct_diff = (diff / bs_value) * 100

# ========== RESULTS DISPLAY ==========
st.subheader("📊 Valuation Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Black-Scholes Value", f"${bs_value:.2f}")
    st.caption("If ESO were a traded option")

with col2:
    st.metric("🎯 Adjusted ESO Value", f"${eso_value:.2f}")
    st.caption("Realistic value with restrictions")

with col3:
    st.metric("Difference", f"${diff:.2f}", delta=f"{pct_diff:.1f}%")
    st.caption("ESOs are worth less due to restrictions")

# ========== WHAT YOUR RESULTS MEAN (EXPANDER - OPEN BY DEFAULT) ==========
st.subheader("📖 What Your Results Mean")

with st.expander("💡 Click to understand your ESO value", expanded=True):
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.markdown(f"""
        ### Your ESO Value: ${eso_value:.2f}
        
        **What this means for you:**
        
        - Each option is worth **${eso_value:.2f}** to you
        - If you have 10,000 options → **${eso_value * 10000:,.0f}** total value
        - Stock needs to reach **${K + eso_value:.2f}** for you to break even
        
        **Why it's not ${bs_value:.2f}:**
        
        | Factor | Impact |
        |--------|--------|
        | {vesting:.0f}-year vesting | Cannot exercise early |
        | Exercise at year {expected_life:.0f} (not {T:.0f}) | Less time for growth |
        | {forfeiture*100:.0f}% forfeiture risk | May lose if you leave |
        | Cannot sell (liquidity) | Must exercise to get value |
        """)
    
    with col_exp2:
        # Calculate profit scenarios
        break_even = K + eso_value
        st.markdown(f"""
        ### When You Make Money
        
        | Stock Price | Your Profit per Option |
        |-------------|----------------------|
        | ${K:.0f} | -${eso_value:.2f} (loss) |
        | ${break_even:.0f} | $0 (break-even) |
        | ${K + 50:.0f} | ${50 - eso_value:.2f} |
        | ${K + 100:.0f} | ${100 - eso_value:.2f} |
        
        ### Key Insight
        
        Your ESO is worth **{abs(pct_diff):.0f}% less** than a traded option.
        This is normal - most ESOs are worth 40-60% of Black-Scholes.
        """)

# ========== EXECUTIVE INCENTIVE INSIGHTS ==========
st.subheader("🎯 Executive Incentive Insights")

# Dynamic insights based on parameters
insights = []
recommendations = []

if sigma > 0.4:
    insights.append("⚠️ **High volatility** increases ESO value → encourages risk-taking behavior")
    recommendations.append("Consider balancing with RSUs to reduce risk-seeking incentives")
else:
    insights.append("✅ **Low volatility** provides stable ESO value → aligns with steady management")

if vesting > 2:
    insights.append("⏳ **Long vesting period** promotes employee retention and long-term focus")
    recommendations.append("Long vesting works well for senior executives")
else:
    insights.append("🚀 **Short vesting** provides immediate incentives but less retention power")

if exercise_multiple < 1.5:
    insights.append("💵 **Low exercise multiple** → employees exercise early → reduces potential upside")
    recommendations.append("Educate employees on benefits of holding longer")
else:
    insights.append("📈 **High exercise multiple** → employees hold longer → aligns with shareholders")

if forfeiture > 0.1:
    insights.append("👥 **High forfeiture rate** → reduces perceived ESO value → consider retention strategies")
    recommendations.append("Improve retention programs to increase ESO perceived value")
else:
    insights.append("✅ **Low forfeiture rate** → employees value ESOs more")

col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    st.markdown("**📌 Key Insights:**")
    for insight in insights:
        st.markdown(f"- {insight}")

with col_insight2:
    st.markdown("**💡 Recommendations:**")
    for rec in recommendations[:3]:  # Show top 3
        st.markdown(f"- {rec}")
    if not recommendations:
        st.markdown("- Your ESO structure is well-balanced")

# ========== SENSITIVITY ANALYSIS ==========
st.subheader("📊 Sensitivity Analysis")

sensitivity_type = st.radio(
    "Select parameter to analyze:",
    ["Volatility", "Stock Price", "Vesting Period", "Forfeiture Rate"],
    horizontal=True
)

if sensitivity_type == "Volatility":
    vol_range = np.linspace(0.1, 0.8, 50)
    bs_vals = [black_scholes(S, K, T, r, v, q, "call") for v in vol_range]
    eso_vals = [eso_adjusted_value(S, K, T, r, v, q, vesting, expected_life, exercise_multiple, forfeiture) for v in vol_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=vol_range*100, y=bs_vals, name="Black-Scholes", mode="lines", line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=vol_range*100, y=eso_vals, name="ESO Adjusted", mode="lines", line=dict(color='green', width=2)))
    fig.update_layout(
        title='ESO Value vs Volatility',
        xaxis_title='Volatility (%)',
        yaxis_title='Option Value ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📈 Higher volatility increases option value but also increases risk for employees")

elif sensitivity_type == "Stock Price":
    price_range = np.linspace(S * 0.5, S * 1.5, 50)
    bs_vals = [black_scholes(p, K, T, r, sigma, q, "call") for p in price_range]
    eso_vals = [eso_adjusted_value(p, K, T, r, sigma, q, vesting, expected_life, exercise_multiple, forfeiture) for p in price_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price_range, y=bs_vals, name="Black-Scholes", mode="lines", line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=price_range, y=eso_vals, name="ESO Adjusted", mode="lines", line=dict(color='green', width=2)))
    fig.add_vline(x=S, line_dash="dash", line_color="gray", annotation_text=f"Current: ${S}")
    fig.add_vline(x=K, line_dash="dot", line_color="red", annotation_text=f"Strike: ${K}")
    fig.update_layout(
        title='ESO Value vs Stock Price',
        xaxis_title='Stock Price ($)',
        yaxis_title='Option Value ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📈 ESO value increases as stock price rises above strike price")

elif sensitivity_type == "Vesting Period":
    vest_range = np.linspace(0, 5, 30)
    eso_vals = [eso_adjusted_value(S, K, T, r, sigma, q, v, expected_life, exercise_multiple, forfeiture) for v in vest_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=vest_range, y=eso_vals, name="ESO Value", mode="lines+markers", line=dict(color='green', width=2)))
    fig.add_vline(x=vesting, line_dash="dash", line_color="gray", annotation_text=f"Current: {vesting} years")
    fig.update_layout(
        title='ESO Value vs Vesting Period',
        xaxis_title='Vesting Period (years)',
        yaxis_title='ESO Value ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📈 Shorter vesting periods increase ESO value by allowing earlier access")

else:  # Forfeiture Rate
    forfeit_range = np.linspace(0, 0.20, 30)
    eso_vals = [eso_adjusted_value(S, K, T, r, sigma, q, vesting, expected_life, exercise_multiple, f) for f in forfeit_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forfeit_range*100, y=eso_vals, name="ESO Value", mode="lines+markers", line=dict(color='green', width=2)))
    fig.add_vline(x=forfeiture*100, line_dash="dash", line_color="gray", annotation_text=f"Current: {forfeiture*100:.0f}%")
    fig.update_layout(
        title='ESO Value vs Forfeiture Rate',
        xaxis_title='Forfeiture Rate (%)',
        yaxis_title='ESO Value ($)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📈 Higher forfeiture rates reduce ESO value as employees may leave before vesting")

# ========== HOW PARAMETERS AFFECT VALUE ==========
st.subheader("🎛️ How Changing Parameters Affects Your ESO Value")

with st.expander("📊 Parameter Impact Guide", expanded=False):
    st.markdown("""
    ### What Happens If You Change These Parameters?
    
    | Parameter | Change | Effect on ESO Value | Best For |
    |-----------|--------|---------------------|----------|
    | **Volatility** | 35% → 50% | Increases +30-40% | Tech/growth stocks |
    | **Vesting Period** | 2 yrs → 1 yr | Increases +15-20% | Employee retention |
    | **Forfeiture Rate** | 5% → 2% | Increases +8-12% | Stable companies |
    | **Expected Life** | 4 yrs → 5 yrs | Increases +10-15% | Optimistic employees |
    | **Early Exercise Multiple** | 1.5x → 2.0x | Increases +5-10% | Patient employees |
    | **Stock Price** | $100 → $120 | Increases +40-50% | Company performance |
    
    ### Practical Takeaways:
    
    **To get higher ESO value:**
    1. Negotiate shorter vesting (1 year instead of 2)
    2. Work at higher volatility companies (tech/biotech)
    3. Plan to hold longer (don't exercise early)
    4. Stay with the company (avoid forfeiture)
    
    **If you're risk-averse:**
    1. Choose lower volatility stocks (utilities/consumer)
    2. Shorter expected life (take profits earlier)
    3. Lower early exercise multiple (exit sooner)
    """)

# ========== WHAT-IF SCENARIOS ==========
with st.expander("🔧 Try 'What If' Scenarios", expanded=False):
    st.markdown("### See How Different Scenarios Affect Your Value")
    
    scenario = st.selectbox(
        "Select a scenario:",
        ["Current Settings", "High Growth Tech Company", "Stable Mature Company", "Short Vesting (1 year)", "Long Holding Period"]
    )
    
    if scenario == "High Growth Tech Company":
        high_vol = 0.50
        high_bs = black_scholes(S, K, T, r, high_vol, q, "call")
        high_eso = eso_adjusted_value(S, K, T, r, high_vol, q, vesting, expected_life, exercise_multiple, forfeiture)
        
        st.info(f"""
        **Scenario: High Growth Tech Company**
        
        | Parameter | Current | New |
        |-----------|---------|-----|
        | Volatility | {sigma*100:.0f}% | 50% |
        | Black-Scholes | ${bs_value:.2f} | ${high_bs:.2f} |
        | Adjusted ESO | ${eso_value:.2f} | ${high_eso:.2f} |
        
        **Change:** +{((high_eso/eso_value)-1)*100:.0f}% increase
        
        **Insight:** Higher volatility increases option value significantly, but also means more stock price uncertainty.
        """)
        
    elif scenario == "Stable Mature Company":
        low_vol = 0.20
        low_bs = black_scholes(S, K, T, r, low_vol, q, "call")
        low_eso = eso_adjusted_value(S, K, T, r, low_vol, q, vesting, expected_life, exercise_multiple, forfeiture)
        
        st.info(f"""
        **Scenario: Stable Mature Company**
        
        | Parameter | Current | New |
        |-----------|---------|-----|
        | Volatility | {sigma*100:.0f}% | 20% |
        | Black-Scholes | ${bs_value:.2f} | ${low_bs:.2f} |
        | Adjusted ESO | ${eso_value:.2f} | ${low_eso:.2f} |
        
        **Change:** {((low_eso/eso_value)-1)*100:.0f}% decrease
        
        **Insight:** Lower volatility means more predictable value but less upside potential.
        """)
        
    elif scenario == "Short Vesting (1 year)":
        short_vest = 1.0
        short_eso = eso_adjusted_value(S, K, T, r, sigma, q, short_vest, expected_life, exercise_multiple, forfeiture)
        
        st.info(f"""
        **Scenario: 1-Year Vesting (instead of {vesting:.0f} years)**
        
        | Parameter | Current | New |
        |-----------|---------|-----|
        | Vesting Period | {vesting:.0f} years | 1 year |
        | Adjusted ESO | ${eso_value:.2f} | ${short_eso:.2f} |
        
        **Change:** +{((short_eso/eso_value)-1)*100:.0f}% increase
        
        **Insight:** Shorter vesting significantly improves perceived value and retention appeal.
        """)
        
    elif scenario == "Long Holding Period":
        long_life = T
        long_eso = eso_adjusted_value(S, K, T, r, sigma, q, vesting, long_life, exercise_multiple, forfeiture)
        
        st.info(f"""
        **Scenario: Hold Until Expiry (exercise at year {T:.0f})**
        
        | Parameter | Current | New |
        |-----------|---------|-----|
        | Expected Life | {expected_life:.0f} years | {T:.0f} years |
        | Adjusted ESO | ${eso_value:.2f} | ${long_eso:.2f} |
        
        **Change:** +{((long_eso/eso_value)-1)*100:.0f}% increase
        
        **Insight:** Patient employees who hold longer get more value from their ESOs.
        """)
        
    else:
        st.info(f"""
        **Current Settings:**
        
        - Stock Price: ${S}
        - Strike Price: ${K}
        - Volatility: {sigma*100:.0f}%
        - Vesting: {vesting:.0f} years
        - Forfeiture Rate: {forfeiture*100:.0f}%
        - ESO Value: ${eso_value:.2f}
        
        Use the sidebar to adjust parameters and see real-time changes in the graphs above.
        """)

# ========== MODEL COMPARISON ==========
st.subheader("📊 Model Comparison")

comparison_df = pd.DataFrame({
    "Model": ["Black-Scholes", "Adjusted ESO Model"],
    "Value": [f"${bs_value:.2f}", f"${eso_value:.2f}"],
    "Assumptions": [
        "Tradable, no vesting, optimal exercise, no forfeiture, liquid",
        "Non-tradable, vesting period, early exercise, forfeiture risk, illiquid"
    ]
})
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# ========== INTERPRETATION GUIDE ==========
with st.expander("📚 How ESO Valuation Works (Technical Explanation)", expanded=False):
    st.markdown(f"""
    ### Why ESOs Are Valued Differently
    
    **Step 1: Black-Scholes Baseline**
    
    The Black-Scholes model assumes:
    - Options can be sold anytime (liquid)
    - No vesting restrictions
    - Optimal exercise at expiry
    - No forfeiture risk
    
    **Step 2: ESO Adjustments**
    
    | Adjustment | Your Input | Impact |
    |------------|------------|--------|
    | Vesting Period | {vesting:.0f} years | Cannot exercise until vested |
    | Expected Life | {expected_life:.0f} years (vs {T:.0f}) | Less time for growth |
    | Early Exercise Multiple | {exercise_multiple:.1f}x | Exercise when stock hits ${S * exercise_multiple:.0f} |
    | Forfeiture Rate | {forfeiture*100:.0f}% | {((1 - np.exp(-forfeiture * vesting))*100):.0f}% chance of losing options |
    | Liquidity Discount | 10% | Cannot sell, must exercise |
    
    **The Math:**

### Key Academic References

- **Hull, J.** (2023) - Options, Futures and Other Derivatives
- **FASB ASC 718** - Stock Compensation Accounting Standard
- **Carpenter, J.** (1998) - "The Exercise and Valuation of Executive Stock Options"

### Limitations of This Model

- Assumes constant volatility (not true in reality)
- Simplified early exercise behavior
- No suboptimal exercise patterns
- Does not model blackout periods
""")

# ========== FOOTER ==========
st.markdown("---")
st.caption("""
**Important Note:** ESOs are worth significantly less than standard options due to vesting, 
non-tradability, forfeiture risk, and early exercise behavior. Use the adjusted value for 
financial planning, not the Black-Scholes value.

**Part of Derivatives & Fixed Income Suite **
""")