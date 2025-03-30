import math
import pytest
from pycic.calculator import CompoundInterest


test_cases = [
    # general test cases
    (10000, 0.05, 5, 100, "annually", "annually", "start", 0.25, 12_580.14),
    (10000, 0.05, 5, 100, "annually", "annually", "end", 0.25, 12_559.93),
    (10000, 0.05, 5, 0, "annually", "annually", "end", 0.25, 12_021.00),
    (10000, 0.05, 5, 100, "annually", "annually", "end", 0.0, 13_315.38),
    (10000, 0.05, 5, 100, "annually", "annually", "end", 0.10, 13_008.89),
    # Compounding vs. Contribution Frequency Combinations
    (10000, 0.05, 1, 100, "annually", "annually", "end", 0.25, 10_475.00),
    (10000, 0.05, 1, 100, "annually", "semiannually", "end", 0.25, 10_578.75),
    (10000, 0.05, 1, 100, "annually", "quarterly", "end", 0.25, 10_786.25),
    (10000, 0.05, 1, 100, "annually", "monthly", "end", 0.25, 11_616.25),
    (10000, 0.05, 1, 100, "annually", "biweekly", "end", 0.25, 13_068.75),
    (10000, 0.05, 1, 100, "annually", "weekly", "end", 0.25, 15_766.25),
    (10000, 0.05, 1, 100, "annually", "daily", "end", 0.25, 48_240.00),
    (10000, 0.05, 1, 100, "semiannually", "annually", "end", 0.25, 10_478.52),
    (10000, 0.05, 1, 100, "semiannually", "semiannually", "end", 0.25, 10_580.39),
    (10000, 0.05, 1, 100, "semiannually", "quarterly", "end", 0.25, 10_786.05),
    (10000, 0.05, 1, 100, "semiannually", "monthly", "end", 0.25, 11_608.69),
    (10000, 0.05, 1, 100, "semiannually", "biweekly", "end", 0.25, 13_048.31),
    (10000, 0.05, 1, 100, "semiannually", "weekly", "end", 0.25, 15_721.89),
    (10000, 0.05, 1, 100, "semiannually", "daily", "end", 0.25, 47_904.88),
    (10000, 0.05, 1, 100, "quarterly", "annually", "end", 0.25, 10_480.31),
    (10000, 0.05, 1, 100, "quarterly", "semiannually", "end", 0.25, 10_582.19),
    (10000, 0.05, 1, 100, "quarterly", "quarterly", "end", 0.25, 10_785.97),
    (10000, 0.05, 1, 100, "quarterly", "monthly", "end", 0.25, 11_604.89),
    (10000, 0.05, 1, 100, "quarterly", "biweekly", "end", 0.25, 13_033.28),
    (10000, 0.05, 1, 100, "quarterly", "weekly", "end", 0.25, 15_699.53),
    (10000, 0.05, 1, 100, "quarterly", "daily", "end", 0.25, 47_737.66),
    (10000, 0.05, 1, 100, "monthly", "annually", "end", 0.25, 10_481.51),
    (10000, 0.05, 1, 100, "monthly", "semiannually", "end", 0.25, 10_583.40),
    (10000, 0.05, 1, 100, "monthly", "quarterly", "end", 0.25, 10_787.19),
    (10000, 0.05, 1, 100, "monthly", "monthly", "end", 0.25, 11_602.35),
    (10000, 0.05, 1, 100, "monthly", "biweekly", "end", 0.25, 13_067.41),
    (10000, 0.05, 1, 100, "monthly", "weekly", "end", 0.25, 15_725.00),
    (10000, 0.05, 1, 100, "monthly", "daily", "end", 0.25, 47_617.39),
    (10000, 0.05, 1, 100, "biweekly", "annually", "end", 0.25, 10_481.84),
    (10000, 0.05, 1, 100, "biweekly", "semiannually", "end", 0.25, 10_583.73),
    (10000, 0.05, 1, 100, "biweekly", "quarterly", "end", 0.25, 10_787.67),
    (10000, 0.05, 1, 100, "biweekly", "monthly", "end", 0.25, 11_603.43),
    (10000, 0.05, 1, 100, "biweekly", "biweekly", "end", 0.25, 13_029.26),
    (10000, 0.05, 1, 100, "biweekly", "weekly", "end", 0.25, 15_680.50),
    (10000, 0.05, 1, 100, "biweekly", "daily", "end", 0.25, 47_595.36),
    (10000, 0.05, 1, 100, "weekly", "annually", "end", 0.25, 10_481.98),
    (10000, 0.05, 1, 100, "weekly", "semiannually", "end", 0.25, 10_583.87),
    (10000, 0.05, 1, 100, "weekly", "quarterly", "end", 0.25, 10_787.66),
    (10000, 0.05, 1, 100, "weekly", "monthly", "end", 0.25, 11_603.14),
    (10000, 0.05, 1, 100, "weekly", "biweekly", "end", 0.25, 13_029.42),
    (10000, 0.05, 1, 100, "weekly", "weekly", "end", 0.25, 15_678.76),
    (10000, 0.05, 1, 100, "weekly", "daily", "end", 0.25, 47_582.39),
    (10000, 0.05, 1, 100, "daily", "annually", "end", 0.25, 10_482.10),
    (10000, 0.05, 1, 100, "daily", "semiannually", "end", 0.25, 10_584.00),
    (10000, 0.05, 1, 100, "daily", "quarterly", "end", 0.25, 10_787.79),
    (10000, 0.05, 1, 100, "daily", "monthly", "end", 0.25, 11_603.03),
    (10000, 0.05, 1, 100, "daily", "biweekly", "end", 0.25, 13_029.68),
    (10000, 0.05, 1, 100, "daily", "weekly", "end", 0.25, 15_679.18),
    (10000, 0.05, 1, 100, "daily", "daily", "end", 0.25, 47_573.16),
]


@pytest.mark.parametrize(
    "init_value, interest_rate, years, contribution, comp_freq, contribution_freq, contribution_timing, tax_rate, expected",
    test_cases,
)
def test_compound_interest_calculation(
    init_value,
    interest_rate,
    years,
    contribution,
    comp_freq,
    contribution_freq,
    contribution_timing,
    tax_rate,
    expected,
):
    ci = CompoundInterest(
        init_value=init_value,
        interest_rate=interest_rate,
        years=years,
        contribution=contribution,
        comp_freq=comp_freq,
        contribution_freq=contribution_freq,
        contribution_timing=contribution_timing,
        tax_rate=tax_rate,
    )
    result = ci.future_value()
    assert math.isclose(
        result, expected, abs_tol=0.01
    ), f"Expected {expected}, got {result}"


@pytest.mark.parametrize(
    "init_value, interest_rate, years, contribution, comp_freq, contribution_freq, contribution_timing, tax_rate, expected",
    test_cases,
)
def test_compound_interest_breakdown(
    init_value,
    interest_rate,
    years,
    contribution,
    comp_freq,
    contribution_freq,
    contribution_timing,
    tax_rate,
    expected,
):
    ci = CompoundInterest(
        init_value=init_value,
        interest_rate=interest_rate,
        years=years,
        contribution=contribution,
        comp_freq=comp_freq,
        contribution_freq=contribution_freq,
        contribution_timing=contribution_timing,
        tax_rate=tax_rate,
    )
    df = ci.breakdown()
    last_balance = df.iloc[-1]["ending_balance"]
    assert math.isclose(
        last_balance, expected, abs_tol=0.01
    ), f"Expected {expected}, got {last_balance}"


inflation_test_cases = [
    (10000, 0.05, 5, 100, "annually", "annually", "end", 0.25, 0.02, 11_375.92),
    (10000, 0.05, 5, 100, "annually", "annually", "start", 0.25, 0.10, 7_811.28),
]


@pytest.mark.parametrize(
    "init_value, interest_rate, years, contribution, comp_freq, contribution_freq, contribution_timing, tax_rate, inflation, expected",
    inflation_test_cases,
)
def test_compound_interest_future_value_with_inflation(
    init_value,
    interest_rate,
    years,
    contribution,
    comp_freq,
    contribution_freq,
    contribution_timing,
    tax_rate,
    inflation,
    expected,
):
    ci = CompoundInterest(
        init_value=init_value,
        interest_rate=interest_rate,
        years=years,
        contribution=contribution,
        comp_freq=comp_freq,
        contribution_freq=contribution_freq,
        contribution_timing=contribution_timing,
        tax_rate=tax_rate,
    )
    result = ci.future_value(inflation=inflation)
    assert math.isclose(
        result, expected, abs_tol=0.01
    ), f"Expected {expected}, got {result}"
