<h1 align="left">PyCIC – Python Compound Interest Calculator</h1>

###

PyCIC is a small Python package offering a versatile compound interest calculator for realistic investment analysis and personal finance applications. It supports variable interest rates and compounding frequencies, periodic contributions with flexible frequencies, 2 different contribution timings and tax adjustments. Additionally, the `timeline()` method returns a detailed pandas DataFrame that lets you visualize your growth scenarios and export the results to CSV or Excel files.

##### Calculation Overview

For compounding purposes, the nominal `interest_rate` is converted to an equivalent daily rate (p.d.) for enhanced calculation accuracy. The system dynamically computes dates starting from the specified `start_date`; if no date is provided, today’s date is used by default. Interest is applied at the end of each period according to the selected frequency. Contributions are executed either at the beginning of the period if `contribution_timing` is set to `"start"`, or at the end if it is set to `"end"`. For both `comp_freq` and `contribution_freq`, you can choose from the following options: `"annually"`, `"semiannually"`, `"quarterly"`, `"monthly"`, `"biweekly"`, `"weekly"`, and `"daily"`. If no `comp_freq` is provided, it is automatically determined based on the given `rate_basis`.

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
    init_value=10_000,
    interest_rate=0.05,
    rate_basis="p.a.",
    years=2,
    start_date="21.02.2025",
    comp_freq="annually",
    contribution=100,
    contribution_freq="monthly",
    contribution_timing="start",
    tax_rate=0.25,
)

# overview of all methods
print(calc.timeline())
print(calc.final_value())
print(calc.summary())
print(calc.total_contributions())
print(calc.total_gross_interest())
print(calc.total_tax_paid())
print(calc.total_net_interest())

# you can also write the detailed investment table to csv or excel with pandas
calc.timeline().to_csv("investment_details.csv", index=False)
calc.timeline().to_excel("investment_details.xlsx", index=False, engine="openpyxl")
```

###

<h2 align="left">Class Parameters</h2>

###

<h3 align="left">Required Parameters:</h2>

###

- `init_value`: Initial investment

- `interest_rate`: Nominal interest rate as decimal (e.g. 0.05 for 5%)

- `rate_basis`: Interest rate basis (`"p.a."`, `"p.m."`, ...)

- `years`: Duration in years

<br>

<h3 align="left">Optional Parameters:</h2>

- `start_date`: Starting date of the investment (`datetime()`, `"YYYY-MM-DD"` or `"DD.MM.YYYY"`)

- `comp_freq`: Compounding frequency (`"annually"`, `"semiannually"`, ...)

- `contribution`: Amount added each interval

- `contribution_freq`: Frequency of contributions (`"annually"`, `"semiannually"`, ...)

- `contribution_timing`: Payment at start/end of period. (`"start"`, `"end"`)

- `tax_rate`: Tax rate applied to interest immediately after compounding.

<br>

<h2 align="left">Available Methods</h2>

- `timeline()`: Returns a detailed pandas dataframe of the investment (see table below)

- `future_value()`: Returns the future value of the investment

- `summary()`: Returns a dictonary of the inputs/outputs of the investment

- `total_contributions()`: Returns the total amount of contributions

- `total_gross_interest()`: Returns the total amount of gross interest earned

- `total_tax_paid()`: Returns the total amount of tax paid

- `total_net_interest()`: Returns the total amount of net interest earned

<br>

## Sample table output

| date       | weekday | start_balance | contribution | gross_interest | tax    | net_interest | end_balance |
| ---------- | ------- | ------------- | ------------ | -------------- | ------ | ------------ | ----------- |
| 21.02.2025 | Fri     | 10000.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10100.00    |
| 21.03.2025 | Fri     | 10100.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10200.00    |
| 21.04.2025 | Mon     | 10200.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10300.00    |
| 21.05.2025 | Wed     | 10300.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10400.00    |
| 21.06.2025 | Sat     | 10400.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10500.00    |
| 21.07.2025 | Mon     | 10500.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10600.00    |
| 21.08.2025 | Thu     | 10600.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10700.00    |
| 21.09.2025 | Sun     | 10700.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10800.00    |
| 21.10.2025 | Tue     | 10800.00      | 100.0        | 0.00           | 0.00   | 0.00         | 10900.00    |
| 21.11.2025 | Fri     | 10900.00      | 100.0        | 0.00           | 0.00   | 0.00         | 11000.00    |
| 21.12.2025 | Sun     | 11000.00      | 100.0        | 0.00           | 0.00   | 0.00         | 11100.00    |
| 21.01.2026 | Wed     | 11100.00      | 100.0        | 0.00           | 0.00   | 0.00         | 11200.00    |
| 20.02.2026 | Fri     | 11200.00      | 0.0          | 558.43         | 139.61 | 418.82       | 11618.82    |
| 21.02.2026 | Sat     | 11618.82      | 100.0        | 0.00           | 0.00   | 0.00         | 11718.82    |
| 21.03.2026 | Sat     | 11718.82      | 100.0        | 0.00           | 0.00   | 0.00         | 11818.82    |
| 21.04.2026 | Tue     | 11818.82      | 100.0        | 0.00           | 0.00   | 0.00         | 11918.82    |
