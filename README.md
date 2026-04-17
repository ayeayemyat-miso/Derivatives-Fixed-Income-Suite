# 📊 Derivatives & Fixed Income Suite

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

An interactive web application for pricing and analyzing fixed income securities, derivatives, and executive stock options. Built for the **Masters of Finance (TU318)** program.

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Calculations & Models](#calculations--models)
- [Academic References](#academic-references)
- [Screenshots](#screenshots)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This suite provides professional-grade financial analytics tools for:

- **Fixed Income Analytics**: Bond pricing, duration, YTM, and term structure
- **Mortgage Analytics**: Amortization schedules, IO/PO strips analysis
- **Risk Management**: VaR, CVaR, portfolio optimization, diversification metrics
- **Equity Derivatives**: ESO valuation with behavioral adjustments
- **Derivatives Pricing**: Black (1976) model for bond futures options
- **Macro Analysis**: Taylor Rule regression with FRED data

## ✨ Features

### Fixed Income
| Tool | Description |
|------|-------------|
| **Bond Pricing** | Calculate price, Macaulay duration, modified duration |
| **Duration Analysis** | Interest rate sensitivity and convexity |
| **YTM Calculator** | Bisection method for yield to maturity |
| **Term Structure** | Bootstrapping & Nelson-Siegel yield curves |

### Mortgage Analytics
| Tool | Description |
|------|-------------|
| **Amortization Schedule** | Monthly/bi-weekly/weekly payments |
| **IO/PO Strips** | Interest-Only & Principal-Only strip valuation |
| **Prepayment Analysis** | Interest rate sensitivity and prepayment risk |

### Risk Management
| Tool | Description |
|------|-------------|
| **VaR & CVaR** | Historical simulation & normal distribution methods |
| **Portfolio Optimization** | Markowitz efficient frontier |
| **Correlation Matrix** | Stock return correlations with heatmap |
| **Diversification Metrics** | Risk reduction calculations |

### Equity Derivatives
| Tool | Description |
|------|-------------|
| **ESO Valuation** | Vesting, forfeiture, early exercise adjustments |
| **Executive Insights** | Compensation strategy recommendations |
| **Scenario Analysis** | Compare different company types |

### Derivatives Pricing
| Tool | Description |
|------|-------------|
| **Black (1976)** | Options on bond futures |
| **Option Greeks** | Delta, Vega calculations |

### Macro Analysis
| Tool | Description |
|------|-------------|
| **Taylor Rule** | Monetary policy regression analysis |
| **Greenspan Era** | Historical policy evaluation |

## 🛠 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Frontend** | Streamlit, Plotly, HTML/CSS |
| **Backend** | Python 3.12+ |
| **Data Processing** | Pandas, NumPy, SciPy |
| **Financial Data** | yfinance, pandas-datareader |
| **Statistical Analysis** | statsmodels, scikit-learn |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Deployment** | Streamlit Cloud, GitHub |

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Git (optional)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/derivatives-fixed-income-suite.git
cd derivatives-fixed-income-suite

### Navigate to the app directory

cd derivatives-suite
### Install dependencies
pip install -r requirements.txt
### Run the application
streamlit run app.py