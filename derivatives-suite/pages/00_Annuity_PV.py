import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Annuity Present Value", layout="wide")

st.title("💰 Present Value of Annuities")
st.markdown("Calculate PV for Ordinary Annuity, Annuity Due, and Growing Annuity")

# Sidebar inputs
with st.sidebar:
    st.markdown("## 📊 Annuity Parameters")
    payment = st.number_input("Payment per Period ($)", 100, 10000, 1000, 100)
    rate = st.slider("Discount Rate (%)", 0.0, 20.0, 5.0, 0.5) / 100
    periods = st.slider("Number of Periods", 1, 30, 10, 1)
    growth = st.slider("Growth Rate (%) - for Growing Annuity", 0.0, 10.0, 2.0, 0.5) / 100
    
    st.markdown("---")
    st.markdown("### 📚 Annuity Types Explained")
    st.info("""
    **Ordinary Annuity:** Payments at END of period
    - Car loans, mortgages, bonds
    
    **Annuity Due:** Payments at START of period  
    - Leases, rent, insurance premiums
    
    **Growing Annuity:** Payments grow at constant rate
    - Salary plans, dividends, pensions
    """)

# Annuity functions (from your Colab)
def pv_ordinary_annuity(payment, rate, periods):
    """Present Value of an Ordinary Annuity (payments at end of period)"""
    if rate == 0:
        return payment * periods
    return payment * (1 - (1 / (1 + rate) ** periods)) / rate

def pv_annuity_due(payment, rate, periods):
    """Present Value of an Annuity Due (payments at beginning of period)"""
    pv_ord = pv_ordinary_annuity(payment, rate, periods)
    return pv_ord * (1 + rate)

def pv_growing_annuity(payment, rate, growth, periods):
    """Present Value of a Growing Annuity"""
    if rate == growth:
        return payment * periods / (1 + rate)
    return payment * (1 - ((1 + growth) / (1 + rate)) ** periods) / (rate - growth)

# Calculate all three
pv_ordinary = pv_ordinary_annuity(payment, rate, periods)
pv_due = pv_annuity_due(payment, rate, periods)
pv_growing = pv_growing_annuity(payment, rate, growth, periods)

# Display results
st.subheader("📊 Present Value Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📆 Ordinary Annuity", f"${pv_ordinary:,.2f}")
    st.caption(f"Payments of ${payment:,.0f} at **end** of each period")

with col2:
    st.metric("🚀 Annuity Due", f"${pv_due:,.2f}")
    st.caption(f"Payments of ${payment:,.0f} at **beginning** of each period")
    st.metric("Premium vs Ordinary", f"${pv_due - pv_ordinary:,.2f}", 
              delta=f"{((pv_due - pv_ordinary)/pv_ordinary*100):.1f}%")

with col3:
    st.metric("📈 Growing Annuity", f"${pv_growing:,.2f}")
    st.caption(f"First payment ${payment:,.0f}, growing at {growth*100:.1f}% per period")

# Comparison visualization
st.subheader("📊 Annuity Type Comparison")

comparison_df = pd.DataFrame({
    'Annuity Type': ['Ordinary Annuity', 'Annuity Due', 'Growing Annuity'],
    'Present Value ($)': [pv_ordinary, pv_due, pv_growing],
    'Description': [
        f'${payment:,.0f} at end of each period',
        f'${payment:,.0f} at start of each period', 
        f'${payment:,.0f} growing {growth*100:.1f}%/period'
    ]
})

fig = go.Figure()
fig.add_trace(go.Bar(
    x=comparison_df['Annuity Type'],
    y=comparison_df['Present Value ($)'],
    text=comparison_df['Present Value ($)'].apply(lambda x: f'${x:,.0f}'),
    textposition='auto',
    marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
))
fig.update_layout(
    title='Present Value Comparison by Annuity Type',
    xaxis_title='Annuity Type',
    yaxis_title='Present Value ($)',
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# Sensitivity Analysis
st.subheader("📈 Sensitivity Analysis")

analysis_type = st.radio(
    "Select parameter to analyze:",
    ["Discount Rate", "Number of Periods", "Growth Rate"],
    horizontal=True
)

if analysis_type == "Discount Rate":
    rates = np.linspace(0.01, 0.15, 30)
    ordinary_vals = [pv_ordinary_annuity(payment, r, periods) for r in rates]
    due_vals = [pv_annuity_due(payment, r, periods) for r in rates]
    growing_vals = [pv_growing_annuity(payment, r, growth, periods) for r in rates]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=rates*100, y=ordinary_vals, name="Ordinary Annuity", mode="lines"))
    fig2.add_trace(go.Scatter(x=rates*100, y=due_vals, name="Annuity Due", mode="lines"))
    fig2.add_trace(go.Scatter(x=rates*100, y=growing_vals, name="Growing Annuity", mode="lines"))
    fig2.update_layout(
        title='Present Value vs Discount Rate',
        xaxis_title='Discount Rate (%)',
        yaxis_title='Present Value ($)'
    )
    st.plotly_chart(fig2, use_container_width=True)

elif analysis_type == "Number of Periods":
    period_range = range(1, 31)
    ordinary_vals = [pv_ordinary_annuity(payment, rate, n) for n in period_range]
    due_vals = [pv_annuity_due(payment, rate, n) for n in period_range]
    growing_vals = [pv_growing_annuity(payment, rate, growth, n) for n in period_range]
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=list(period_range), y=ordinary_vals, name="Ordinary Annuity", mode="lines+markers"))
    fig3.add_trace(go.Scatter(x=list(period_range), y=due_vals, name="Annuity Due", mode="lines+markers"))
    fig3.add_trace(go.Scatter(x=list(period_range), y=growing_vals, name="Growing Annuity", mode="lines+markers"))
    fig3.update_layout(
        title='Present Value vs Number of Periods',
        xaxis_title='Number of Periods',
        yaxis_title='Present Value ($)'
    )
    st.plotly_chart(fig3, use_container_width=True)

else:  # Growth Rate
    if growth > 0:
        growth_rates = np.linspace(0, rate * 0.9, 20)  # Keep below discount rate
        growing_vals = [pv_growing_annuity(payment, rate, g, periods) for g in growth_rates]
        
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=growth_rates*100, y=growing_vals, name="Growing Annuity", mode="lines+markers"))
        fig4.add_hline(y=pv_ordinary, line_dash="dash", line_color="red", 
                      annotation_text="Ordinary Annuity (0% growth)")
        fig4.update_layout(
            title='Present Value of Growing Annuity vs Growth Rate',
            xaxis_title='Growth Rate (%)',
            yaxis_title='Present Value ($)'
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Increase the growth rate to see sensitivity analysis")

# Cash flow visualization
st.subheader("💵 Cash Flow Timeline Comparison")

# Show first 10 periods of cash flows
n_show = min(10, periods)
periods_list = list(range(1, n_show + 1))

# Calculate cash flows for each type
ordinary_cf = [payment] * n_show
due_cf = [payment] * n_show
growing_cf = [payment * (1 + growth) ** (i-1) for i in range(1, n_show + 1)]

fig5 = go.Figure()
fig5.add_trace(go.Bar(x=periods_list, y=ordinary_cf, name="Ordinary Annuity", marker_color='blue'))
fig5.add_trace(go.Bar(x=periods_list, y=due_cf, name="Annuity Due", marker_color='orange'))
fig5.add_trace(go.Bar(x=periods_list, y=growing_cf, name="Growing Annuity", marker_color='green'))
fig5.update_layout(
    title=f'Cash Flow Comparison (First {n_show} Periods)',
    xaxis_title='Period',
    yaxis_title='Cash Flow ($)',
    barmode='group'
)
st.plotly_chart(fig5, use_container_width=True)

# Mathematical explanation
with st.expander("📚 Mathematical Formulas & Explanation"):
    st.markdown(f"""
    ### 1. Ordinary Annuity (Payments at END of period)
    
    **Formula:** 
    $$PV = P \\times \\frac{{1 - (1 + r)^{{-n}}}}{{r}}$$
    
    **Your calculation:** ${payment:,.0f} × (1 - (1 + {rate*100:.1f}%)⁻{periods}) / {rate*100:.1f}% = **${pv_ordinary:,.2f}**
    
    **Real-World Use:** Car loans, mortgages, corporate bonds
    
    ---
    
    ### 2. Annuity Due (Payments at START of period)
    
    **Formula:**
    $$PV = P \\times \\frac{{1 - (1 + r)^{{-n}}}}{{r}} \\times (1 + r)$$
    
    **Your calculation:** ${pv_ordinary:,.2f} × (1 + {rate*100:.1f}%) = **${pv_due:,.2f}**
    
    **Real-World Use:** Lease agreements, rental payments, insurance premiums
    
    ---
    
    ### 3. Growing Annuity (Payments grow at rate g)
    
    **Formula:**
    $$PV = P \\times \\frac{{1 - \\left(\\frac{{1 + g}}{{1 + r}}\\right)^n}}{{r - g}}$$
    
    **Your calculation:** ${payment:,.0f} × (1 - ((1+{growth*100:.1f}%)/(1+{rate*100:.1f}%))^{periods}) / ({rate*100:.1f}% - {growth*100:.1f}%) = **${pv_growing:,.2f}**
    
    **Real-World Use:** Salary plans, dividend-paying stocks, pension plans with inflation adjustments
    
    ---
    
    ### Key Insights:
    
    - **Annuity Due** is always more valuable than Ordinary Annuity (by factor of 1 + r)
    - **Growing Annuity** value increases with higher growth rates
    - When r = g, the formula simplifies to: $PV = P \\times n / (1 + r)$
    """)

# Link to original assignment
st.caption("🔗 Part of Question 5 | User-defined function for Present Value Annuity | Original Colab notebook available")

# Interactive quiz/insight
st.subheader("💡 Financial Insight")

if pv_due > pv_ordinary:
    st.success(f"💡 **Annuity Due is worth ${pv_due - pv_ordinary:,.2f} more than Ordinary Annuity** because payments are received earlier, allowing more time for compounding.")
else:
    st.info("Annuity Due = Ordinary Annuity × (1 + r)")

if growth > 0 and pv_growing > pv_ordinary:
    st.success(f"💡 **Growing Annuity adds ${pv_growing - pv_ordinary:,.2f} in value** due to {growth*100:.1f}% annual payment growth.")