import numpy as np
from scipy.stats import norm

def black_1976_call(F, K, T, r, sigma):
    """
    Black (1976) model for pricing options on futures
    
    Parameters:
    F: Futures price
    K: Strike price
    T: Time to maturity (years)
    r: Risk-free rate
    sigma: Volatility of futures price
    """
    if T <= 0:
        return max(0, F - K)
    
    d1 = (np.log(F / K) + (0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    call_price = np.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))
    
    return call_price

def black_1976_put(F, K, T, r, sigma):
    """Black (1976) put option price"""
    if T <= 0:
        return max(0, K - F)
    
    d1 = (np.log(F / K) + (0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    put_price = np.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
    
    return put_price

def futures_price_implied_volatility(call_price, F, K, T, r, tol=1e-6):
    """Find implied volatility using bisection"""
    low, high = 0.001, 2.0
    
    for _ in range(100):
        mid = (low + high) / 2
        price = black_1976_call(F, K, T, r, mid)
        
        if abs(price - call_price) < tol:
            return mid
        elif price > call_price:
            high = mid
        else:
            low = mid
    
    return (low + high) / 2