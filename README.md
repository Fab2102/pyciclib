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
print(calc.breakdown())
print(calc.future_value(inflation=0.02))
print(calc.total_contributions())
print(calc.total_gross_interest_earned())
print(calc.total_net_interest_earned())
print(calc.total_tax_paid())

# you can also use pandas csv function to create a csv
calc.breakdown().to_csv()
```

###

<h2 align="left">Class Parameters</h2>

###

<h3 align="left">Required Parameters</h2>
<h3 align="left">Optional Parameters</h2>

<p align="left"><Text></p>

###

<h2 align="left">Available Methods</h2>

###

<p align="left"><Text></p>

###

<h2 align="left">Table from breakdown() method</h2>

###

<p align="left"><Text></p>

###

<h2 align="left">License</h2>

###

<p align="left"><Text></p>

###

```

```
