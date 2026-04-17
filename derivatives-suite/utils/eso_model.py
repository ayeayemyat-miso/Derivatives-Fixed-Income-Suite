import numpy as np
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, q=0, option_type="call"):
    """Standard Black-Scholes formula"""
    if T <= 0:
        return max(0, S - K) if option_type == "call" else max(0, K - S)
    
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        value = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        value = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    
    return value

def eso_adjusted_value(S, K, T, r, sigma, q, vesting, expected_life, early_exercise_multiple, forfeiture_rate):
    """Adjusted ESO valuation with behavioral factors"""
    # Effective life after vesting
    effective_life = max(0.5, expected_life - vesting)
    
    # Early exercise adjustment
    early_exercise_factor = 1 / early_exercise_multiple
    adjusted_life = effective_life * early_exercise_factor
    
    # Forfeiture adjustment
    survival_prob = np.exp(-forfeiture_rate * vesting)
    
    # Base Black-Scholes
    base_value = black_scholes(S, K, adjusted_life, r, sigma, q, "call")
    
    # Apply adjustments
    adjusted_value = base_value * survival_prob
    
    # Liquidity discount (10% typical)
    liquidity_discount = 0.10
    final_value = adjusted_value * (1 - liquidity_discount)
    
    return max(final_value, 0)