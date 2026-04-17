# 📊 Derivatives & Fixed Income Suite

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io/)

Interactive web application for bond pricing, ESO valuation, risk management, and derivatives pricing.

## 🚀 Live Demo

[![Streamlit App](https://derivatives-fixed-income-suite-z8lacpslxczvzvmnwmgr7p.streamlit.app/](https://derivatives-fixed-income-suite-z8lacpslxczvzvmnwmgr7p.streamlit.app/)

## ✨ Features

| Category | Tools |
|----------|-------|
| **Fixed Income** | Bond Pricing, Duration, YTM, Term Structure |
| **Mortgage** | Amortization, IO/PO Strips |
| **Risk** | VaR, CVaR, Portfolio Optimization |
| **Equity** | ESO Valuation with vesting/forfeiture |
| **Derivatives** | Black (1976) Model |
| **Macro** | Taylor Rule Analysis |

## 🛠 Tech Stack

- **Frontend:** Streamlit, Plotly
- **Backend:** Python 3.12+
- **Data:** Pandas, NumPy, yfinance
- **Stats:** SciPy, statsmodels

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/ayeayemyat-miso/Derivatives-Fixed-Income-Suite.git
cd Derivatives-Fixed-Income-Suite/derivatives-suite

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py