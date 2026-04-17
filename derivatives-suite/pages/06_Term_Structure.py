import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="IO/PO Strips Analysis", layout="wide")

st.title("📊 IO/PO Strips Analysis")
st.markdown("Analyze Interest-Only and Principal-Only strips from mortgage pools")

# Payment frequency mapping
frequency_map = {
    "Monthly (12x/year)": 12,
    "Bi-Weekly (26x/year)": 26,
    "Weekly (52x/year)": 52,
    "Quarterly (4x/year)": 4,
    "Semi-Annual (2x/year)": 2,
    "Annual (1x/year)": 1
}

# Inputs
st.subheader("📋 Loan Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    principal = st.number_input("Loan Amount ($)", 50000, 1000000, 300000, 25000)
    
with col2:
    annual_rate = st.number_input("Annual Interest Rate (%)", 1.0, 15.0, 5.0, 0.125) / 100
    
with col3:
    years = st.number_input("Loan Term (years)", 1, 40, 30, 1)

# Payment frequency selection
st.subheader("📅 Payment Schedule")
frequency_option = st.selectbox(
    "Payment Frequency",
    list(frequency_map.keys()),
    index=0
)

freq_per_year = frequency_map[frequency_option]
st.caption(f"💡 {frequency_option} = {freq_per_year} payments per year")

# Advanced options
with st.expander("⚙️ Advanced Options"):
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        extra_payment = st.number_input("Extra Payment Amount ($)", 0, 5000, 0, 50)
        st.caption("Applied to principal each payment")
    with col_a2:
        show_years = st.slider("Show amortization for first (years)", 1, 10, 5)

def calculate_payment(principal, annual_rate, years, freq_per_year, extra_payment=0):
    """Calculate periodic payment with optional extra payment"""
    periods = years * freq_per_year
    periodic_rate = annual_rate / freq_per_year
    
    if periodic_rate == 0:
        base_payment = principal / periods
    else:
        base_payment = principal * (periodic_rate * (1 + periodic_rate) ** periods) / ((1 + periodic_rate) ** periods - 1)
    
    total_payment = base_payment + extra_payment
    return base_payment, total_payment, periods, periodic_rate

def amortization_schedule(principal, annual_rate, years, freq_per_year, extra_payment=0):
    """Generate full amortization schedule with frequency options"""
    base_payment, total_payment, periods, periodic_rate = calculate_payment(
        principal, annual_rate, years, freq_per_year, extra_payment
    )
    
    schedule = []
    balance = principal
    payment_num = 1
    total_interest_paid = 0
    total_principal_paid = 0
    
    while balance > 0 and payment_num <= periods:
        interest = balance * periodic_rate
        principal_paid = min(total_payment - interest, balance)
        
        if extra_payment > 0:
            principal_paid = min(base_payment - interest + extra_payment, balance)
        
        balance -= principal_paid
        
        year = (payment_num - 1) // freq_per_year + 1
        period_in_year = (payment_num - 1) % freq_per_year + 1
        
        schedule.append({
            'Payment #': payment_num,
            'Year': year,
            'Period': period_in_year,
            'Payment': total_payment,
            'Interest': interest,
            'Principal': principal_paid,
            'Balance': max(0, balance),
            'Cumulative Interest': total_interest_paid + interest,
            'Cumulative Principal': total_principal_paid + principal_paid
        })
        
        total_interest_paid += interest
        total_principal_paid += principal_paid
        payment_num += 1
        
        if balance <= 0:
            break
    
    return pd.DataFrame(schedule), base_payment, total_payment, total_interest_paid, total_principal_paid

def calculate_io_po_strips(schedule, annual_rate, freq_per_year):
    """Calculate present value of IO and PO strips"""
    periodic_rate = annual_rate / freq_per_year
    io_value = 0
    po_value = 0
    
    for _, row in schedule.iterrows():
        discount_factor = 1 / (1 + periodic_rate) ** row['Payment #']
        io_value += row['Interest'] * discount_factor
        po_value += row['Principal'] * discount_factor
    
    return io_value, po_value

# Calculate
schedule, base_payment, total_payment, total_interest, total_principal = amortization_schedule(
    principal, annual_rate, years, freq_per_year, extra_payment
)

io_value, po_value = calculate_io_po_strips(schedule, annual_rate, freq_per_year)

# Display summary
st.subheader("📊 Loan Summary")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    st.metric("Periodic Payment", f"${total_payment:,.2f}")
    st.caption(f"({frequency_option})")

with col_s2:
    total_payments = total_payment * len(schedule)
    st.metric("Total Payments", f"${total_payments:,.2f}")

with col_s3:
    st.metric("Total Interest", f"${total_interest:,.2f}")

with col_s4:
    actual_term_years = len(schedule) / freq_per_year
    st.metric("Actual Term", f"{actual_term_years:.1f} years")
    if extra_payment > 0:
        original_term_years = years
        years_saved = original_term_years - actual_term_years
        st.caption(f"💡 Saved {years_saved:.1f} years")

# Payment breakdown visualization
st.subheader("💰 Payment Breakdown Over Time")

show_periods = min(show_years * freq_per_year, len(schedule))
schedule_subset = schedule.head(show_periods)
schedule_subset['Year_Group'] = schedule_subset['Year']
yearly_summary = schedule_subset.groupby('Year_Group').agg({
    'Interest': 'sum',
    'Principal': 'sum',
    'Payment': 'first'
}).reset_index()

fig = go.Figure()
fig.add_trace(go.Bar(x=yearly_summary['Year_Group'], y=yearly_summary['Interest'], 
                     name='Interest', marker_color='#ff7f0e'))
fig.add_trace(go.Bar(x=yearly_summary['Year_Group'], y=yearly_summary['Principal'], 
                     name='Principal', marker_color='#2ca02c'))
fig.update_layout(title=f'Payment Breakdown (First {show_years} years)',
                  xaxis_title='Year',
                  yaxis_title='Amount ($)',
                  barmode='stack')
st.plotly_chart(fig, use_container_width=True)

# Loan balance over time
st.subheader("📉 Loan Balance Over Time")

balance_over_time = schedule[['Payment #', 'Year', 'Balance']].copy()
balance_over_time = balance_over_time[balance_over_time['Payment #'] % max(1, freq_per_year // 12) == 0]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=balance_over_time['Year'], y=balance_over_time['Balance'], 
                          mode='lines', name='Remaining Balance', 
                          line=dict(color='blue', width=2)))
fig2.add_hline(y=principal/2, line_dash="dash", line_color="green", 
               annotation_text="Half Paid")
fig2.update_layout(title='Loan Balance Amortization',
                   xaxis_title='Year',
                   yaxis_title='Balance ($)')
st.plotly_chart(fig2, use_container_width=True)

# Amortization schedule (first X periods)
st.subheader(f"📅 Amortization Schedule (First {min(12, len(schedule))} {frequency_option.lower()})")

display_cols = ['Payment #', 'Year', 'Period', 'Payment', 'Interest', 'Principal', 'Balance']
display_schedule = schedule[display_cols].head(12).copy()

for col in ['Payment', 'Interest', 'Principal', 'Balance']:
    display_schedule[col] = display_schedule[col].apply(lambda x: f"${x:,.2f}")

st.dataframe(display_schedule, use_container_width=True)

if len(schedule) > 12:
    st.caption(f"Showing first 12 of {len(schedule)} total payments")

# IO/PO Strips Analysis
st.subheader("📊 IO/PO Strip Analysis")

col_io1, col_io2 = st.columns(2)

with col_io1:
    st.metric("Interest-Only (IO) Strip Value", f"${io_value:,.2f}")
    st.caption("Present value of all future interest payments")

with col_io2:
    st.metric("Principal-Only (PO) Strip Value", f"${po_value:,.2f}")
    st.caption("Present value of all future principal payments")

# IO/PO sensitivity
st.subheader("📈 IO/PO Interest Rate Sensitivity")

rate_range = np.linspace(annual_rate * 0.5, annual_rate * 1.5, 30)
io_values = []
po_values = []

for r in rate_range:
    temp_schedule, _, _, _, _ = amortization_schedule(principal, r, years, freq_per_year, extra_payment)
    temp_io, temp_po = calculate_io_po_strips(temp_schedule, r, freq_per_year)
    io_values.append(temp_io)
    po_values.append(temp_po)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=rate_range*100, y=io_values, name='IO Strip', mode='lines', line=dict(color='orange', width=2)))
fig3.add_trace(go.Scatter(x=rate_range*100, y=po_values, name='PO Strip', mode='lines', line=dict(color='green', width=2)))
fig3.add_vline(x=annual_rate*100, line_dash="dash", line_color="gray", 
               annotation_text="Current Rate")
fig3.update_layout(title='IO/PO Strip Values vs Interest Rate',
                   xaxis_title='Interest Rate (%)',
                   yaxis_title='Strip Value ($)')
st.plotly_chart(fig3, use_container_width=True)

# ========== COMPREHENSIVE INTERPRETATION SECTION ==========
st.subheader("📖 How to Interpret This Graph")

with st.expander("🎓 Click to understand what IO/PO strips mean (Finance explanation)", expanded=False):
    
    st.markdown("""
    ### 🔷 What are IO and PO Strips?
    
    When you split a mortgage into two separate securities:
    
    - **🟠 IO Strip (Interest-Only):** Represents ONLY the interest payments
    - **🟢 PO Strip (Principal-Only):** Represents ONLY the principal repayments
    
    ---
    
    ### 📈 What the Graph Shows
    
    The graph above shows how the **value of IO and PO strips changes** when interest rates change.
    
    ---
    
    ### 🟠 IO Strip Behavior (Orange Line)
    
    **IO value INCREASES when interest rates RISE**
    **IO value DECREASES when interest rates FALL**
    
    **Why?**
    - When rates rise → borrowers are less likely to refinance
    - The loan lasts longer → you collect interest payments for longer
    - Therefore IO becomes MORE valuable
    
    ✅ **IO = Positively related to interest rates**
    
    ---
    
    ### 🟢 PO Strip Behavior (Green Line)
    
    **PO value DECREASES when interest rates RISE**
    **PO value INCREASES when interest rates FALL**
    
    **Why?**
    - When rates fall → borrowers refinance early
    - You get your principal back FASTER
    - Therefore PO becomes MORE valuable when rates drop
    
    ✅ **PO = Negatively related to interest rates**
    
    ---
    
    ### 🔄 They Behave Like Opposites
    
    | Interest Rates | IO Value | PO Value |
    |---------------|----------|----------|
    | Go Up ⬆ | Goes Up ⬆ | Goes Down ⬇ |
    | Go Down ⬇ | Goes Down ⬇ | Goes Up ⬆ |
    
    ---
    
    ### 💡 Why This Matters for Investors
    
    - **Buy IO strips** when you expect interest rates to **rise or stay stable**
    - **Buy PO strips** when you expect interest rates to **fall**
    - **Hedge:** Combine both to create duration-neutral positions
    
    ---
    
    ### 📚 Key Financial Concept: Prepayment Risk
    
    This graph illustrates **prepayment risk**:
    - Homeowners refinance when rates drop
    - This hurts IO investors (interest stops early)
    - This helps PO investors (get money back faster)
    
    **IO investors want rates to stay high or rise**
    **PO investors want rates to drop**
    """)

with st.expander("🏛️ Relevance to Financial Regulation", expanded=False):
    st.markdown("""
    ### Why Regulators Care About IO/PO Strips
    
    **1. Prepayment Modeling Risk**
    - Banks must model prepayment behavior for capital requirements
    - Incorrect prepayment assumptions → undercapitalization
    - Regulators require **PSA (Public Securities Association)** prepayment models
    
    **2. Interest Rate Risk**
    - IO strips have **negative convexity** (price drops more than it rises)
    - Traditional duration models FAIL for IO strips
    - Regulators require specialized risk models for MBS
    
    **3. 2008 Financial Crisis Lesson**
    - Complex MBS with IO/PO tranches hid true risk
    - Investors didn't understand prepayment sensitivity
    - Led to massive unexpected losses during the crisis
    
    **4. Basel III Requirements**
    - Banks must hold additional capital for negative convexity instruments
    - Stress testing must include prepayment scenarios
    - Liquidity coverage ratios (LCR) account for MBS behavior
    
    **5. Regulatory Arbitrage Warning**
    - Banks used IO/PO strips to reduce regulatory capital
    - Hidden risk led to stricter rules post-2008
    - Now: Full risk disclosure required
    
    **Source:** Coval, Jurek & Stafford (2009) - "The Economics of Structured Finance"
    """)

with st.expander("📊 Trading Strategies & Real-World Application", expanded=False):
    st.markdown("""
    ### How Professional Investors Trade IO/PO Strips
    
    **🟠 IO Strip Trading Strategy:**
    - **Buy IO when:** Expecting rising rates or stable prepayments
    - **Sell IO when:** Expecting falling rates or refinancing wave
    - **Typical buyers:** Insurance companies, pension funds (liability matching)
    - **Risk:** IO can lose 50%+ value in falling rate environments
    
    **🟢 PO Strip Trading Strategy:**
    - **Buy PO when:** Expecting falling rates (refinancing play)
    - **Sell PO when:** Expecting rising rates
    - **Typical buyers:** Hedge funds, opportunistic investors
    - **Risk:** PO underperforms when rates rise or prepayments slow
    
    **🏦 Hedging Application:**
    
    | Risk Exposure | Hedge Strategy |
    |---------------|----------------|
    | Bank holds mortgages | Buy PO strips (gains when rates fall) |
    | Servicer wants stable income | Buy IO strips (steady interest income) |
    | Falling rate expectation | Long PO / Short IO |
    | Rising rate expectation | Long IO / Short PO |
    
    **⚠️ Key Risk Warning:**
    - IO strips can lose value rapidly in falling rate environments
    - PO strips require accurate prepayment modeling
    - Both require sophisticated risk management
    - NOT suitable for retail investors
    """)

# Comparison: Different payment frequencies
st.subheader("📊 Payment Frequency Comparison")

if st.checkbox("Compare different payment frequencies"):
    freq_comparison = []
    for freq_name, freq_num in frequency_map.items():
        _, base_pmt, total_pmt, interest_total, _ = amortization_schedule(
            principal, annual_rate, years, freq_num, 0
        )
        periods = years * freq_num
        freq_comparison.append({
            'Frequency': freq_name,
            'Payment Amount': f"${base_pmt:.2f}",
            'Total Interest': f"${interest_total:,.2f}",
            'Total Payments': f"${base_pmt * periods:,.2f}",
            '# of Payments': periods
        })
    
    st.dataframe(pd.DataFrame(freq_comparison), use_container_width=True)
    
    st.info("""
    **Key Insight:** More frequent payments (weekly/bi-weekly) reduce total interest paid because:
    - Interest accrues on a smaller balance more frequently
    - You make more payments per year, reducing principal faster
    - Bi-weekly = 26 half-payments = 13 full payments per year (1 extra payment annually)
    """)

# Educational content - FIXED VERSION (escaped curly braces)
with st.expander("📚 Understanding Mortgage Amortization (Technical)", expanded=False):
    st.markdown(f"""
    ### How Amortization Works
    
    **Payment Formula:**
    $$P = \\frac{{r \\times PV}}{{1 - (1 + r)^{{-n}}}}$$
    
    Where:
    - P = periodic payment
    - PV = Loan amount (${principal:,.0f})
    - r = periodic interest rate ({annual_rate*100:.2f}% / {freq_per_year} = {(annual_rate/freq_per_year)*100:.4f}%)
    - n = total number of payments ({years} years × {freq_per_year} = {years * freq_per_year})
    
    ### Your Loan Summary:
    - **Payment:** ${total_payment:,.2f} {frequency_option.lower()}
    - **Total Interest:** ${total_interest:,.2f}
    - **Interest as % of Loan:** {(total_interest/principal)*100:.1f}%
    - **Total Cost:** ${principal + total_interest:,.2f}
    
    ### IO/PO Strips Mathematical Formula:
    
    **IO Strip Value:**
    $$IO = \\sum_{{t=1}}^{{n}} \\frac{{I_t}}{{(1+r)^t}}$$
    
    **PO Strip Value:**
    $$PO = \\sum_{{t=1}}^{{n}} \\frac{{P_t}}{{(1+r)^t}}$$
    
    Where:
    - I_t = Interest payment at time t
    - P_t = Principal payment at time t
    - r = Discount rate
    - n = Total number of payments
    
    **Note:** IO Value + PO Value = Present Value of all mortgage payments
    """)

# Download option
st.subheader("📥 Export Data")

if st.button("Generate Full Amortization Schedule (CSV)"):
    csv = schedule.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"mortgage_amortization_{principal}_{years}years.csv",
        mime="text/csv"
    )

st.caption(f"📊 {len(schedule)} total payments | {frequency_option} | {'With' if extra_payment > 0 else 'Without'} extra payments | IO/PO strips show prepayment risk")