import streamlit as st
import sys
import os
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bond import price_bond, duration_macaulay, duration_modified

st.set_page_config(page_title="Bond Pricing", layout="wide")

st.title("🏷️ Bond Pricing Calculator")

# Inputs
col1, col2 = st.columns(2)

with col1:
    face_value = st.number_input("Face Value ($)", 100, 100000, 1000, 100)
    coupon_rate = st.slider("Coupon Rate (%)", 0.0, 15.0, 5.0, 0.25) / 100
    years = st.slider("Years to Maturity", 1, 30, 10, 1)

with col2:
    ytm = st.slider("Yield to Maturity (%)", 0.0, 15.0, 6.0, 0.25) / 100
    freq = st.selectbox("Coupon Frequency", [1, 2, 4, 12], index=1)

# Calculate
price = price_bond(face_value, coupon_rate, years, ytm, freq)
mac_dur = duration_macaulay(face_value, coupon_rate, years, ytm, freq)
mod_dur = duration_modified(mac_dur, ytm, freq)

# Display
col_r1, col_r2, col_r3 = st.columns(3)
col_r1.metric("💰 Bond Price", f"${price:,.2f}")
col_r2.metric("⏱️ Macaulay Duration", f"{mac_dur:.2f} years")
col_r3.metric("⚡ Modified Duration", f"{mod_dur:.2f} years")

# Sensitivity
st.subheader("📊 Price Sensitivity to Yield")
yields = np.linspace(0.01, 0.15, 50)
prices = [price_bond(face_value, coupon_rate, years, y, freq) for y in yields]
df = pd.DataFrame({"Yield (%)": yields * 100, "Price": prices})
st.line_chart(df.set_index("Yield (%)"))