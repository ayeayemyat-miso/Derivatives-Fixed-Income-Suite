import numpy as np
import pandas as pd

def monthly_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment"""
    monthly_rate = annual_rate / 12
    n_months = years * 12
    
    if monthly_rate == 0:
        return principal / n_months
    else:
        payment = principal * (monthly_rate * (1 + monthly_rate) ** n_months) / ((1 + monthly_rate) ** n_months - 1)
        return payment

def amortization_schedule(principal, annual_rate, years):
    """Generate full amortization schedule"""
    monthly_rate = annual_rate / 12
    n_months = years * 12
    payment = monthly_payment(principal, annual_rate, years)
    
    schedule = []
    balance = principal
    
    for month in range(1, n_months + 1):
        interest = balance * monthly_rate
        principal_paid = payment - interest
        balance -= principal_paid
        
        schedule.append({
            'Month': month,
            'Payment': payment,
            'Interest': interest,
            'Principal': principal_paid,
            'Balance': max(0, balance)
        })
        
        if balance <= 0:
            break
    
    return pd.DataFrame(schedule)

def io_po_strips(principal, annual_rate, years):
    """Calculate Interest Only (IO) and Principal Only (PO) strip values"""
    schedule = amortization_schedule(principal, annual_rate, years)
    
    total_interest = schedule['Interest'].sum()
    total_principal = schedule['Principal'].sum()
    
    # Present value of strips (using risk-free rate approximation)
    discount_rate = annual_rate
    io_value = sum(schedule['Interest'] / (1 + discount_rate/12) ** schedule['Month'])
    po_value = sum(schedule['Principal'] / (1 + discount_rate/12) ** schedule['Month'])
    
    return {
        'io_value': io_value,
        'po_value': po_value,
        'total_interest': total_interest,
        'total_principal': total_principal,
        'schedule': schedule
    }