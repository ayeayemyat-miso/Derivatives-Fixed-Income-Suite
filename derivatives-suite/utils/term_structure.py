import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

def bootstrap_yield_curve(bond_data):
    """
    Bootstrap zero-coupon yield curve from coupon bonds
    
    bond_data: DataFrame with columns ['maturity', 'coupon', 'price']
    """
    zero_rates = []
    
    for i, bond in bond_data.iterrows():
        maturity = bond['maturity']
        coupon = bond['coupon']
        price = bond['price']
        
        # Solve for zero rate
        def objective(rate):
            pv = 0
            for t in np.arange(0.5, maturity + 0.5, 0.5):
                if t < maturity:
                    pv += coupon * 0.5 * np.exp(-rate * t)
                else:
                    pv += (100 + coupon * 0.5) * np.exp(-rate * t)
            return abs(pv - price)
        
        result = minimize_scalar(objective, bounds=(0, 1), method='bounded')
        zero_rates.append({'maturity': maturity, 'zero_rate': result.x})
    
    return pd.DataFrame(zero_rates)

def forward_rates(zero_curve):
    """Calculate forward rates from zero curve"""
    forwards = []
    for i in range(len(zero_curve) - 1):
        t1 = zero_curve.iloc[i]['maturity']
        t2 = zero_curve.iloc[i + 1]['maturity']
        r1 = zero_curve.iloc[i]['zero_rate']
        r2 = zero_curve.iloc[i + 1]['zero_rate']
        
        forward = (r2 * t2 - r1 * t1) / (t2 - t1)
        forwards.append({'period': f'{t1}-{t2}', 'forward_rate': forward})
    
    return pd.DataFrame(forwards)