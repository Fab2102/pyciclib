<h1 align="left">PyCIC – Python Compound Interest Calculator</h1>

###

<p align="left">
PyCIC is a flexible compound interest calculator designed for serious financial modeling, simulations, and personal finance tools.<br>
It supports variable compounding frequencies, periodic contributions, tax treatment, inflation adjustment, and rich DataFrame outputs.
</p>

###

<h2 align="left">Installation</h2>

###

<p align="left">
<code>pip install pycic</code>
</p>

###

<h2 align="left">Example Usage</h2>

###

<p align="left">
<pre>
from pycic import CompoundInterest

# Create a compound interest calculator instance
ci = CompoundInterest(
    init_value=10000,
    interest_rate=0.07,
    years=20,
    comp_freq="monthly",
    contribution=200,
    contribution_freq="monthly",
    contribution_timing="end",
    tax_rate=0.15
)

# Calculate future value with inflation adjustment
print("Future Value:", ci.future_value(inflation=0.02))

# Display a detailed breakdown (returns a Pandas DataFrame)
print(ci.breakdown().head())

# Print a summary of the investment scenario
ci.summary()
</pre>
</p>

###

<h2 align="left">Class Parameters</h2>

###

<p align="left">
<strong>init_value</strong>: Initial investment amount (float).<br>
<strong>interest_rate</strong>: Annual interest rate as a decimal (e.g., 0.07 for 7%).<br>
<strong>years</strong>: Investment duration in years (float).<br>
<strong>comp_freq</strong>: Compounding frequency (e.g., "annually", "monthly", etc.).<br>
<strong>contribution</strong>: Amount contributed at each interval (default: 0.0).<br>
<strong>contribution_freq</strong>: Frequency of contributions (default: same as compounding).<br>
<strong>contribution_timing</strong>: When contributions are made ("start" or "end", default: "end").<br>
<strong>tax_rate</strong>: Tax rate applied to interest as a decimal (default: 0.0).
</p>

###

<h2 align="left">Available Methods</h2>

###

<p align="left">
<strong>future_value(inflation=0.0)</strong>: Calculates the future value of the investment, optionally adjusting for inflation.<br>
<strong>breakdown()</strong>: Returns a detailed period-by-period breakdown as a Pandas DataFrame.<br>
<strong>total_contributions()</strong>: Computes the total amount contributed over the investment period.<br>
<strong>total_gross_interest_earned()</strong>: Returns the total gross interest earned.<br>
<strong>total_net_interest_earned()</strong>: Returns the total net interest earned.<br>
<strong>total_tax_paid()</strong>: Returns the total tax paid on interest.<br>
<strong>summary()</strong>: Prints a summary of the compound interest scenario.
</p>

###

<h2 align="left">Table from breakdown() method</h2>

###

<p align="left">
The <code>breakdown()</code> method outputs a Pandas DataFrame with the following columns:
<ul>
  <li><strong>label</strong>: Period label (derived from frequency settings).</li>
  <li><strong>period</strong>: The sequential period number.</li>
  <li><strong>starting_balance</strong>: Balance at the beginning of the period.</li>
  <li><strong>contribution_at_start/end</strong>: Contribution added at the period (depending on timing).</li>
  <li><strong>gross_interest</strong>: Interest calculated before tax.</li>
  <li><strong>net_interest</strong>: Interest after tax deductions.</li>
  <li><strong>tax_paid</strong>: Tax amount deducted from the gross interest.</li>
  <li><strong>ending_balance</strong>: Balance at the end of the period.</li>
</ul>
</p>

###

<h2 align="left">License</h2>

###

<p align="left">
MIT License © 2025 [Your Name]
</p>
