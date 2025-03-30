# 📈 PyCIC – Python Compound Interest Calculator

**PyCIC** is a flexible compound interest calculator designed for serious financial modeling, simulations, and personal finance tools.  
It supports variable compounding frequencies, periodic contributions, tax treatment, inflation adjustment, and rich DataFrame outputs.

---

## 🚀 Features

- Customizable compounding frequency (`daily`, `monthly`, `quarterly`, etc.)
- Periodic contributions at start or end of intervals
- Optional tax rate on interest earned
- Inflation-adjusted future value calculation
- Pandas DataFrame breakdown of every period
- Summary statistics including gross/net interest and total tax paid

---

## 📦 Installation

```bash
pip install pycic
```

Or clone and install locally:

```bash
git clone https://github.com/Fab2102/pycic.git
cd pycic
pip install -e .[dev]
```

---

## 🧺 Example Usage

```python
from pycic import CompoundInterest

calc = CompoundInterest(
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
print(calc.breakdown())
print(calc.future_value(inflation=0.02))
print(calc.total_contributions())
print(calc.total_gross_interest_earned())
print(calc.total_net_interest_earned())
print(calc.total_tax_paid())

# create a csv file from the detailed breakdown
calc.breakdown().to_csv()
```

---

## 📈 Sample Output (Terminal)

```
===================================================
                   PyCIC Summary
===================================================
Initial Investment    :    10,000.00
Total Contributions   :    500.00
Gross Interest Earned :    2,746.58
Net Interest Earned   :    2,059.93
Tax Paid              :    686.65
Future Value          :    12,559.93
===================================================
```

---

## 📊 Sample Data Breakdown (Annual, 5 Years)

| label | period | starting_balance | contribution_at_end | gross_interest | net_interest | tax_paid | ending_balance |
| ----- | ------ | ---------------- | ------------------- | -------------- | ------------ | -------- | -------------- |
| Year  | 1      | 10000.00         | 100                 | 500.00         | 375.00       | 125.00   | 10475.00       |
| Year  | 2      | 10475.00         | 100                 | 523.75         | 392.81       | 130.94   | 10967.81       |
| Year  | 3      | 10967.81         | 100                 | 548.39         | 411.29       | 137.10   | 11479.11       |
| Year  | 4      | 11479.11         | 100                 | 573.96         | 430.47       | 143.49   | 12009.57       |
| Year  | 5      | 12009.57         | 100                 | 600.48         | 450.36       | 150.12   | 12559.93       |

_This table reflects annual compounding and contributions with a 25% tax rate over 5 years._

---

## 🔹 Class Interface

### `CompoundInterest(...)`

Initialize with:

- `init_value`: Initial investment (float)
- `interest_rate`: Annual rate, as a decimal (e.g., 0.05 for 5%)
- `years`: Duration in years (float)
- `comp_freq`: Compounding frequency (`"monthly"`, `"weekly"`, etc.)
- `contribution`: Amount added each interval (optional)
- `contribution_freq`: Frequency of contributions (optional)
- `contribution_timing`: `"start"` or `"end"` (default: `"end"`)
- `tax_rate`: Optional tax on interest (default: 0.0)

---

## 📈 Available Methods

| Method                          | Description                                      |
| ------------------------------- | ------------------------------------------------ |
| `future_value()`                | Calculates final value (with optional inflation) |
| `breakdown()`                   | Returns full period-wise DataFrame               |
| `summary()`                     | Prints a readable summary                        |
| `total_contributions()`         | Total amount contributed                         |
| `total_gross_interest_earned()` | Interest before taxes                            |
| `total_net_interest_earned()`   | Interest after taxes                             |
| `total_tax_paid()`              | Total tax paid on interest                       |

---

## 📁 Project Structure

```
pycic/
├── __init__.py
├── core.py          # Contains CompoundInterest
├── utils.py         # Frequency maps, label mapping
tests/
pyproject.toml
README.md
LICENSE
```

---

## 📃 License

MIT License © 2024 Fabian Bauer

---

## 🌐 Links

- [📦 PyPI (coming soon)](https://pypi.org/project/pycic)
- [📁 GitHub Repo](https://github.com/Fab2102/pycic)
