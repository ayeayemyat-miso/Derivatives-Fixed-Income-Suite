import numpy as np

def price_bond(face, coupon_rate, years, ytm, freq=2):
    """Calculate bond price with periodic coupons"""
    n_periods = int(years * freq)
    coupon_pmt = face * coupon_rate / freq
    ytm_period = ytm / freq
    
    # Present value of coupons
    if ytm_period == 0:
        pv_coupons = coupon_pmt * n_periods
    else:
        pv_coupons = coupon_pmt * (1 - (1 + ytm_period) ** -n_periods) / ytm_period
    
    # Present value of face value
    pv_face = face * (1 + ytm_period) ** -n_periods
    
    return pv_coupons + pv_face

def duration_macaulay(face, coupon_rate, years, ytm, freq=2):
    """Calculate Macaulay duration"""
    n_periods = int(years * freq)
    coupon_pmt = face * coupon_rate / freq
    ytm_period = ytm / freq
    
    # Weighted present values
    weighted_pv = 0
    total_pv = 0
    
    for t in range(1, n_periods + 1):
        pv_cf = coupon_pmt / (1 + ytm_period) ** t
        weighted_pv += t * pv_cf
        total_pv += pv_cf
    
    # Add face value at maturity
    pv_face = face / (1 + ytm_period) ** n_periods
    weighted_pv += n_periods * pv_face
    total_pv += pv_face
    
    mac_dur_periods = weighted_pv / total_pv
    return mac_dur_periods / freq

def duration_modified(mac_dur, ytm, freq=2):
    """Calculate modified duration"""
    return mac_dur / (1 + ytm/freq)

def ytm_bisection(face, coupon_rate, years, price, freq=2, tol=1e-6, max_iter=100):
    """Find YTM using bisection method"""
    low, high = 0.0001, 0.50
    
    for _ in range(max_iter):
        mid = (low + high) / 2
        p = price_bond(face, coupon_rate, years, mid, freq)
        
        if abs(p - price) < tol:
            return mid
        elif p > price:
            low = mid
        else:
            high = mid
    
    return (low + high) / 2