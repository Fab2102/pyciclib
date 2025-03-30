from pycic import CompoundInterest


c1 = CompoundInterest(
    init_value=10_000,
    interest_rate=0.05,
    years=10,
    contribution=100,
    comp_freq="annually",
    contribution_freq="annually",
    contribution_timing="start",
    tax_rate=0.25,
)


c1.breakdown().to_excel("1234.xlsx", engine="openpyxl")
