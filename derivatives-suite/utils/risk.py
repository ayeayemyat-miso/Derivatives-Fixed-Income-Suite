import numpy as np
import pandas as pd
from scipy import stats

def calculate_returns(prices):
    """Calculate daily returns from price series"""
    return prices.pct_change().dropna()

def covariance_matrix(returns):
    """Calculate variance-covariance matrix"""
    return returns.cov() * 252  # Annualized

def portfolio_var(returns, weights, confidence_level=0.99, horizon=10):
    """Calculate portfolio VaR"""
    # Portfolio returns
    portfolio_returns = returns.dot(weights)
    
    # Mean and std of portfolio returns
    mu = portfolio_returns.mean() * horizon
    sigma = portfolio_returns.std() * np.sqrt(horizon)
    
    # VaR assuming normal distribution
    z_score = stats.norm.ppf(confidence_level)
    var = mu - z_score * sigma
    
    # If we want absolute VaR (not relative to mean)
    var_absolute = -z_score * sigma
    
    return var, var_absolute

def portfolio_cvar(returns, weights, confidence_level=0.99, horizon=10):
    """Calculate Conditional VaR (Expected Shortfall)"""
    portfolio_returns = returns.dot(weights)
    
    # Historical simulation approach
    horizon_returns = portfolio_returns * horizon
    var_threshold = np.percentile(horizon_returns, (1 - confidence_level) * 100)
    
    cvar = horizon_returns[horizon_returns <= var_threshold].mean()
    
    return cvar

def calculate_var_covar_matrix(returns):
    """Calculate VaR using variance-covariance method"""
    cov_matrix = returns.cov() * 252
    return cov_matrix