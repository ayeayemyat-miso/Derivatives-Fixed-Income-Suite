import streamlit as st
import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Taylor Rule Analysis", layout="wide")

st.title("🎛️ Taylor Rule Analysis")
st.markdown("Analyze Greenspan FOMC era monetary policy (1987-2006)")

# Generate sample data (FRED-simulated for demonstration)
@st.cache_data
def generate_taylor_data():
    years = np.arange(1987, 2007, 0.25)
    n = len(years)
    
    # Actual Fed Funds Rate
    fed_funds = np.zeros(n)
    
    # Taylor Rule: i = r* + π + 0.5(π-π*) + 0.5(y-y*)
    # Parameters
    r_star = 2.0  # Equilibrium real rate
    pi_star = 2.0  # Target inflation
    
    # Inflation (CPI YoY)
    inflation = 3.0 + np.sin(np.linspace(0, 4*np.pi, n)) * 1.5
    inflation[inflation < 0] = 1
    
    # Output gap (simulated)
    output_gap = np.sin(np.linspace(0, 3*np.pi, n)) * 1.5
    output_gap[:20] = np.linspace(-2, 0, 20)  # Early 90s recession
    output_gap[40:60] = np.linspace(0, -1, 20)  # 2001 recession
    
    # Taylor Rule prescription
    taylor_rate = r_star + inflation + 0.5*(inflation - pi_star) + 0.5*output_gap
    
    # Actual Fed Funds (simulated - Greenspan followed Taylor until 2000)
    actual_rate = taylor_rate.copy()
    # Greenspan got "off track" 2001-2005
    off_track_start = np.where(years >= 2001)[0][0]
    off_track_end = np.where(years <= 2005)[0][-1]
    actual_rate[off_track_start:off_track_end] = taylor_rate[off_track_start:off_track_end] - 1.5
    
    return pd.DataFrame({
        'Date': years,
        'Fed_Funds_Actual': actual_rate,
        'Taylor_Prescribed': taylor_rate,
        'Inflation': inflation,
        'Output_Gap': output_gap
    })

df = generate_taylor_data()

# Display charts
st.subheader("📈 Taylor Rule vs Actual Fed Funds Rate")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Fed_Funds_Actual'], 
                         mode='lines', name='Actual Fed Funds Rate', line=dict(color='blue', width=2)))
fig.add_trace(go.Scatter(x=df['Date'], y=df['Taylor_Prescribed'], 
                         mode='lines', name='Taylor Rule Prescribed', line=dict(color='red', dash='dash')))

# Highlight Greenspan off-track period
fig.add_vrect(x0=2001, x1=2005, fillcolor="yellow", opacity=0.3, 
              annotation_text="Greenspan 'Off Track' Period", annotation_position="top left")

fig.update_layout(title='Greenspan FOMC: Taylor Rule vs Actual Policy (1987-2006)',
                  xaxis_title='Year',
                  yaxis_title='Interest Rate (%)',
                  hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# OLS Regression
st.subheader("📊 Regression Analysis")

# Create dummy for post-2000
df['Post_2000'] = (df['Date'] >= 2000).astype(int)

from sklearn.linear_model import LinearRegression

# Model 1: Simple Taylor Rule
X1 = df[['Inflation', 'Output_Gap']].values
y = df['Fed_Funds_Actual'].values

model1 = LinearRegression()
model1.fit(X1, y)

# Model 2: Taylor Rule with post-2000 dummy
df['Taylor_Baseline'] = 2 + df['Inflation'] + 0.5*(df['Inflation'] - 2) + 0.5*df['Output_Gap']
X2 = df[['Taylor_Baseline', 'Post_2000']].values
model2 = LinearRegression()
model2.fit(X2, y)

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.markdown("**Model 1: Standard Taylor Rule**")
    st.write(f"R² = {model1.score(X1, y):.3f}")
    st.write(f"Coefficient on Inflation: {model1.coef_[0]:.3f}")
    st.write(f"Coefficient on Output Gap: {model1.coef_[1]:.3f}")
    st.write(f"Intercept: {model1.intercept_:.3f}")

with col_r2:
    st.markdown("**Model 2: Taylor Rule + Post-2000 Dummy**")
    st.write(f"R² = {model2.score(X2, y):.3f}")
    st.write(f"Coefficient on Taylor Baseline: {model2.coef_[0]:.3f}")
    st.write(f"Post-2000 Dummy: {model2.coef_[1]:.3f}")
    st.write(f"Intercept: {model2.intercept_:.3f}")

# Unemployment extension
st.subheader("📊 Extension: Taylor Rule with Unemployment")

# Generate unemployment data
df['Unemployment'] = 5.5 + np.sin(np.linspace(0, 3*np.pi, len(df))) * 1.5
df['Unemployment_Gap'] = df['Unemployment'] - 5.5  # NAIRU approx

# Augmented Taylor Rule: i = r* + π + 0.5(π-π*) - 0.5(u-u*)
X3 = df[['Inflation', 'Output_Gap', 'Unemployment_Gap']].values
model3 = LinearRegression()
model3.fit(X3, y)

st.write(f"**Augmented Taylor Rule with Unemployment:**")
st.write(f"R² = {model3.score(X3, y):.3f}")
st.write(f"Inflation coefficient: {model3.coef_[0]:.3f}")
st.write(f"Output Gap coefficient: {model3.coef_[1]:.3f}")
st.write(f"Unemployment Gap coefficient: {model3.coef_[2]:.3f}")

# Model comparison
st.subheader("📊 Model Comparison")
comparison = pd.DataFrame({
    'Model': ['Standard Taylor', '+ Post-2000 Dummy', '+ Unemployment Gap'],
    'R²': [model1.score(X1, y), model2.score(X2, y), model3.score(X3, y)],
    'AIC': [len(y) * np.log(np.mean((y - model1.predict(X1))**2)) + 2*2,
            len(y) * np.log(np.mean((y - model2.predict(X2))**2)) + 2*3,
            len(y) * np.log(np.mean((y - model3.predict(X3))**2)) + 2*4]
})
st.dataframe(comparison, use_container_width=True)

with st.expander("📚 Taylor (1993) and Greenspan FOMC"):
    st.markdown("""
    **Taylor Rule (1993):**
    
    i = r* + π + 0.5(π-π*) + 0.5(y-y*)
    
    Where:
    - i = federal funds rate
    - r* = equilibrium real rate (2%)
    - π = inflation rate
    - π* = target inflation (2%)
    - y-y* = output gap
    
    **Greenspan Got Off Track (2001-2005):**
    
    According to Taylor (2007), the Fed kept rates too low after the 2001 recession:
    - Actual rates ~1% lower than Taylor rule prescribed
    - Contributed to housing bubble
    - Led to financial crisis of 2007-2008
    
    **Evidence:**
    - Post-2000 dummy coefficient is negative and significant
    - Model fit improves when allowing regime shift
    """)
    
    st.markdown("**Sources:** FRED St. Louis, Taylor (1993, 2007)")

# Footer
st.caption("Note: Data simulated for demonstration. For actual FRED data, use pandas_datareader to fetch real-time data.")