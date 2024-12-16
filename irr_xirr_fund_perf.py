import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import newton

# Cash flows for Fund A
cashflows_a = [-100, 150, 0, 0, 0, 10]
cashflows_b = [-100, 50, 0, 0, 0, 10]
cashflows_c = [-30, 60, 20, -10, 0, 20]


# Dates for cash flows (used for XIRR)
dates = [datetime(2019, 6, 15),
         datetime(2020, 8, 1),
         datetime(2021, 2, 14),
         datetime(2022, 12, 11),
         datetime(2023, 1, 4),
         datetime(2024, 12, 21)]


# Time periods for cash flows (years for IRR)
time_periods = np.arange(1, len(cashflows_a) + 1)


# Range of discount rates (r) to test for NPV
discount_rates = np.linspace(-0.5, 1.0, 400)

# Function to calculate NPV for a given discount rate
def calculate_npv(r, cashflows):
    npv = 0
    for i, cf in enumerate(cashflows):
        npv += cf / (1 + r)**(i + 1)
    return npv

# Function to calculate the *derivative* of NPV with respect to 'r' for a given discount rate
def calculate_npv_derivative(r, cashflows):
    dpv = 0
    for i, cf in enumerate(cashflows):
         dpv += - cf * (i+1) / (1 + r)**(i + 2)
    return dpv


# Function to calculate XNPV for a given discount rate
def calculate_xnpv(r, cashflows, dates):
    xnpv = 0
    d0 = dates[0]
    for i, cf in enumerate(cashflows):
        d = dates[i]
        days_diff = (d-d0).days
        xnpv += cf / (1+r)**(days_diff/365)
    return xnpv

# Function to calculate the derivative of XNPV with respect to "r"
def calculate_xnpv_derivative(r, cashflows, dates):
    dxnpv = 0
    d0 = dates[0]
    for i, cf in enumerate(cashflows):
      d = dates[i]
      days_diff = (d-d0).days
      dxnpv += - cf * (days_diff/365) / (1+r)**((days_diff/365) + 1)
    return dxnpv


# Calculate IRR using scipy (Newton's method)
def find_irr(cashflows):
    low_rate = -0.99  # Ensure to have a negative NPV
    high_rate = 10.0  # Ensure to have a positive NPV
    irr = None

    try:
      irr = newton(calculate_npv, x0=0.1, fprime = calculate_npv_derivative , args=(cashflows,), full_output=True) # Newton's method for IRR
      if isinstance(irr, tuple):
        irr = irr[0]
    except Exception as e:
         irr = np.nan
         print(f"IRR Error:\n {e}")
    return irr

# Calculate XIRR using the Newton method
def find_xirr(cashflows, dates):
    low_rate = -0.99  # Ensure to have a negative NPV
    high_rate = 10.0    # Ensure to have a positive NPV
    xirr = None
    try:
        xirr = newton(calculate_xnpv, x0=0.1, fprime = calculate_xnpv_derivative, args = (cashflows,dates), full_output = True) # Newton's method for XIRR
        if isinstance(xirr,tuple):
           xirr = xirr[0]
    except Exception as e:
          xirr = np.nan
          print(f"XIRR Error:\n {e}")
    return xirr


# Calculate IRR and XIRR for each fund
irr_a_npf = npf.irr(cashflows_a)
irr_b_npf = npf.irr(cashflows_b)
irr_c_npf = npf.irr(cashflows_c)

irr_a = find_irr(cashflows_a)
irr_b = find_irr(cashflows_b)
irr_c = find_irr(cashflows_c)

xirr_a = find_xirr(cashflows_a, dates)
xirr_b = find_xirr(cashflows_b, dates)
xirr_c = find_xirr(cashflows_c, dates)


# Calculate NPV for each discount rate
npvs_a = [calculate_npv(r, cashflows_a) for r in discount_rates]
npvs_b = [calculate_npv(r, cashflows_b) for r in discount_rates]
npvs_c = [calculate_npv(r, cashflows_c) for r in discount_rates]

# Enable interactive mode for Matplotlib
plt.ion()

# Create the Plot
plt.figure(figsize=(12, 8))
plt.plot(discount_rates, npvs_a, label=f'NPV a (IRR={irr_a_npf:.2f} / {irr_a:.2f}, XIRR={xirr_a:.2f})', color='blue')
plt.plot(discount_rates, npvs_b, label=f'NPV b (IRR={irr_b_npf:.2f} / {irr_b:.2f}, XIRR={xirr_b:.2f})', color='red')
plt.plot(discount_rates, npvs_c, label=f'NPV c (IRR={irr_c_npf:.2f} / {irr_c:.2f}, XIRR={xirr_c:.2f})', color='green')
plt.xlabel('Discount Rate (r)')
plt.ylabel('Net Present Value (NPV)')
plt.title('NPV vs. Discount Rate and IRR/XIRR for Funds A, B and C')
plt.grid(True)
plt.axhline(y=0, color='black', linestyle='--', label='NPV = 0')
plt.legend()

plt.show()


# Print results for comparison
print("--- IRR and XIRR ---")
print(f"Fund A: IRR (numpy): {irr_a_npf:.4f}, IRR (scipy): {irr_a:.4f}, XIRR: {xirr_a:.4f}")
print(f"Fund B: IRR (numpy): {irr_b_npf:.4f}, IRR (scipy): {irr_b:.4f}, XIRR: {xirr_b:.4f}")
print(f"Fund C: IRR (numpy): {irr_c_npf:.4f}, IRR (scipy): {irr_c:.4f}, XIRR: {xirr_c:.4f}")
input("Press Enter to close the plot and end the execution")