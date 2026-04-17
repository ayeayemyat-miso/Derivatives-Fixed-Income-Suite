import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Mortgage Amortization", layout="wide")

st.title("🏠 Mortgage Amortization Calculator")
st.markdown("Calculate payments, generate amortization schedule, and analyze IO/PO strips")

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
    index=0  # Monthly as default
)

freq_per_year = frequency_map[frequency_option]
st.caption(f"💡 {frequency_option} = {freq_per_year} payments per year")

# Advanced options
with st.expander("⚙️ Advanced Options"):
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        extra_payment = st.number_input("Extra Monthly Payment ($)", 0, 5000, 0, 50)
        st.caption("Applied to principal each payment")
    with col_a2:
        show_years = st.slider("Show amortization for first (years)", 1, 10, 5)

# Calculate payment based on frequency
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
        
        # Apply extra payment logic
        if extra_payment > 0:
            principal_paid = min(base_payment - interest + extra_payment, balance)
        
        balance -= principal_paid
        
        # Calculate year and period within year
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

# Calculate
schedule, base_payment, total_payment, total_interest, total_principal = amortization_schedule(
    principal, annual_rate, years, freq_per_year, extra_payment
)

# Calculate IO/PO strip values (present value of interest and principal streams)
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
        st.caption(f"💡 Saved {years_saved:.1f} years with extra payments")

# Payment breakdown visualization
st.subheader("💰 Payment Breakdown Over Time")

# Create payment breakdown chart (first X years)
show_periods = min(show_years * freq_per_year, len(schedule))
schedule_subset = schedule.head(show_periods)

# Group by year for better visualization
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

# Sample balance at regular intervals
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

# Format schedule for display
display_cols = ['Payment #', 'Year', 'Period', 'Payment', 'Interest', 'Principal', 'Balance']
display_schedule = schedule[display_cols].head(12).copy()

# Format currency columns
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

# Show how IO/PO values change with interest rates
rate_range = np.linspace(annual_rate * 0.5, annual_rate * 1.5, 30)
io_values = []
po_values = []

for r in rate_range:
    temp_schedule, _, _, _, _ = amortization_schedule(principal, r, years, freq_per_year, extra_payment)
    temp_io, temp_po = calculate_io_po_strips(temp_schedule, r, freq_per_year)
    io_values.append(temp_io)
    po_values.append(temp_po)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=rate_range*100, y=io_values, name='IO Strip', mode='lines', line=dict(color='orange')))
fig3.add_trace(go.Scatter(x=rate_range*100, y=po_values, name='PO Strip', mode='lines', line=dict(color='green')))
fig3.add_vline(x=annual_rate*100, line_dash="dash", line_color="gray", 
               annotation_text="Current Rate")
fig3.update_layout(title='IO/PO Strip Values vs Interest Rate',
                   xaxis_title='Interest Rate (%)',
                   yaxis_title='Strip Value ($)')
st.plotly_chart(fig3, use_container_width=True)

# Comparison: Different payment frequencies
if st.checkbox("Compare different payment frequencies"):
    st.subheader("📊 Payment Frequency Comparison")
    
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
    """)

# Educational content
with st.expander("📚 Understanding Mortgage Amortization"):
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
    
    ### IO/PO Strips Explained:
    
    - **IO Strip (Interest Only):** Value of all future interest payments = ${io_value:,.2f}
    - **PO Strip (Principal Only):** Value of all future principal payments = ${po_value:,.2f}
    
    **Trading Strategy:**
    - Buy IO when expecting **stable/rising rates** (prepayments slow)
    - Buy PO when expecting **falling rates** (prepayments accelerate)
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

st.caption(f"📊 {len(schedule)} total payments | {frequency_option} | {'With' if extra_payment > 0 else 'Without'} extra payments")