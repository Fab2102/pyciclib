<h1 align="left">PyCIC – Python Compound Interest Calculator</h1>

###

<p align="left">PyCIC is a flexible compound interest calculator designed for serious financial modeling, simulations, and personal finance tools.<br>It supports variable compounding frequencies, periodic contributions, tax treatment, inflation adjustment, and rich DataFrame outputs.</p>

###

<h2 align="left">Installation</h2>

###

```bash
pip install pycic
```

###

<h2 align="left">Example Usage</h2>

###

```python
import pycic as pc

# creating an instance
calc = pc.CompoundInterest(
init_value=10000,
interest_rate=0.05,
years=5,
comp_freq="annually",
contribution=100,
contribution_freq="annually",
contribution_timing="end",
tax_rate=0.25,
)

# function overview
calc.summary()
print(calc.future_value(inflation=0.02))
print(calc.breakdown())
print(calc.total_contributions())
print(calc.total_gross_interest_earned())
print(calc.total_net_interest_earned())
print(calc.total_tax_paid())

# breakdown() outputs a pandas DataFrame, so you can also call pandas methods on it
calc.breakdown().to_csv("investment_details.csv")
calc.breakdown().to_excel("investment_details.xlsx", engine="openpyxl")
```

###

<h2 align="left">Class Parameters</h2>

###

<h3 align="left">Required Parameters:</h2>

###

- `init_value`: Initial investment

- `interest_rate`: interest rate in p.a., as a decimal (e.g., 0.05 for 5%)

- `years`: Duration in years

- `comp_freq`: Compounding frequency (`"annually"`, `"semiannually"`, etc.)

<br>

<h3 align="left">Optional Parameters:</h2>

- `contribution`: Amount added each interval

- `contribution_freq`: Frequency of contributions (`"annually"`, `"semiannually"`, etc.)

- `contribution_timing`: Payment at start/end of period. (`"start"`, `"end"`)

- `tax_rate`: Tax rate applied to interest immediately after compounding.

<br>

<h2 align="left">Available Methods</h2>

- `future_value(inflation=0.02)`: Calculates the final future value (with optional inflation)

- `breakdown()`: Returns a pandas dataframe with all periods listed (see table below)

- `summary()`: Prints a readable summary of the investment

- `total_contributions()`: Total amount contributed

- `total_gross_interest_earned()`: Total interest before taxes

- `total_net_interest_earned()`: Total interest after taxes

- `total_tax_paid()`: Total tax paid on interest

<br>

<h2 align="left" style="border-bottom: none;">Sample table output</h2>

| label | period | starting_balance | contribution_at_end | gross_interest | net_interest | tax_paid | ending_balance |
| ----- | ------ | ---------------- | ------------------- | -------------- | ------------ | -------- | -------------- |
| Year  | 1      | 10000.00         | 100                 | 500.00         | 375.00       | 125.00   | 10475.00       |
| Year  | 2      | 10475.00         | 100                 | 523.75         | 392.81       | 130.94   | 10967.81       |
| Year  | 3      | 10967.81         | 100                 | 548.39         | 411.29       | 137.10   | 11479.11       |
| Year  | 4      | 11479.11         | 100                 | 573.96         | 430.47       | 143.49   | 12009.57       |
| Year  | 5      | 12009.57         | 100                 | 600.48         | 450.36       | 150.12   | 12559.93       |
