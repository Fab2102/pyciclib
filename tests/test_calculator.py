import pytest
import pandas as pd
from pycic import CompoundInterest
from unittest.mock import patch


# ==== Initialization & Input Validation ====

def test_valid_initialization():
    ci = CompoundInterest(1000, 0.05, 10, contributions=100, compounding="monthly")
    assert isinstance(ci, CompoundInterest)
    assert ci.init_value == 1000
    assert ci.compound_periods == 12  # monthly

@pytest.mark.parametrize("init_value", [-100, "100", None])
def test_invalid_init_value(init_value):
    with pytest.raises(ValueError):
        CompoundInterest(init_value, 0.05, 10)

@pytest.mark.parametrize("rate", [-0.01, "0.05", None])
def test_invalid_rate(rate):
    with pytest.raises(ValueError):
        CompoundInterest(1000, rate, 10)

@pytest.mark.parametrize("years", [-1, 0, "10"])
def test_invalid_years(years):
    with pytest.raises(ValueError):
        CompoundInterest(1000, 0.05, years)

@pytest.mark.parametrize("tax_rate", [-0.1, 1.5, "0.2"])
def test_invalid_tax_rate(tax_rate):
    with pytest.raises(ValueError):
        CompoundInterest(1000, 0.05, 10, tax_rate=tax_rate)

@pytest.mark.parametrize("apply_tax", [0, "True"])
def test_invalid_apply_tax(apply_tax):
    with pytest.raises(TypeError):
        CompoundInterest(1000, 0.05, 10, apply_tax=apply_tax)

def test_invalid_contribution_timing():
    with pytest.raises(ValueError):
        CompoundInterest(1000, 0.05, 10, contribution_timing="middle")

def test_invalid_compounding():
    with pytest.raises(ValueError):
        CompoundInterest(1000, 0.05, 10, compounding="yearly")

def test_invalid_contribution_frequency():
    with pytest.raises(ValueError):
        CompoundInterest(1000, 0.05, 10, contribution_frequency="hourly")


# ==== Core Functional Tests ====

def test_future_value_basic():
    ci = CompoundInterest(1000, 0.05, 10, compounding="annually")
    assert round(ci.future_value(), 2) == 1628.89

def test_future_value_with_contributions_end():
    ci = CompoundInterest(1000, 0.05, 10, contributions=100, compounding="annually")
    # Updated expected value based on current logic:
    assert round(ci.future_value(), 2) == 2886.68

def test_future_value_with_contributions_start():
    ci = CompoundInterest(1000, 0.05, 10, contributions=100, contribution_timing="start", compounding="annually")
    # Updated expected value based on current logic:
    assert round(ci.future_value(), 2) == 2949.57

def test_future_value_with_tax():
    ci = CompoundInterest(1000, 0.05, 10, compounding="annually", apply_tax=True, tax_rate=0.3)
    # Updated expected value based on current logic:
    assert round(ci.future_value(), 2) == 1410.60

def test_call_alias():
    ci = CompoundInterest(1000, 0.05, 10)
    assert ci() == ci.future_value()


# ==== Output Methods ====

def test_str_and_repr():
    ci = CompoundInterest(1000, 0.05, 10)
    assert "Compound Interest Summary" in str(ci)
    assert "CompoundInterest(" in repr(ci)

def test_eq_operator():
    ci1 = CompoundInterest(1000, 0.05, 10)
    ci2 = CompoundInterest(1000, 0.05, 10)
    ci3 = CompoundInterest(2000, 0.05, 10)
    assert ci1 == ci2
    assert ci1 != ci3


# ==== Breakdown and Stats ====

def test_breakdown_structure():
    ci = CompoundInterest(1000, 0.05, 2, compounding="annually")
    df = ci.breakdown()
    assert isinstance(df, pd.DataFrame)
    expected_columns = {"Label", "Period", "Starting Balance", "Contribution", "Interest", "Tax Paid", "Ending Balance"}
    assert expected_columns.issubset(df.columns)
    assert df.shape[0] == 2  # 2 years → 2 periods (annually)

def test_total_contributions():
    ci = CompoundInterest(1000, 0.05, 2, contributions=100, compounding="annually")
    assert ci.total_contributions() == 200

def test_total_interest_earned():
    ci = CompoundInterest(1000, 0.05, 2, contributions=100, compounding="annually")
    result = ci.total_interest_earned()
    assert isinstance(result, float)

def test_total_tax_paid():
    ci = CompoundInterest(1000, 0.05, 2, contributions=100, apply_tax=True, tax_rate=0.25)
    tax = ci.total_tax_paid()
    assert isinstance(tax, float)
    assert tax > 0


# ==== Inflation Adjustment ====

def test_adjust_for_inflation():
    ci = CompoundInterest(1000, 0.05, 10)
    fv = ci.future_value()
    adjusted = ci.adjust_for_inflation(0.02)
    assert adjusted < fv
    assert round(adjusted, 2) == round(fv / (1.02 ** 10), 2)

def test_invalid_inflation_rate():
    ci = CompoundInterest(1000, 0.05, 10)
    with pytest.raises(ValueError):
        ci.adjust_for_inflation(-0.01)


# ==== Goal Year Estimation ====

def test_goal_year_met():
    ci = CompoundInterest(1000, 0.05, 30, contributions=100, compounding="monthly")
    assert ci.goal_year(10000) is not None

def test_goal_year_not_met():
    ci = CompoundInterest(1000, 0.01, 2, contributions=0)
    assert ci.goal_year(10000) is None


# ==== File Export (mocked) ====

@patch("pandas.DataFrame.to_csv")
def test_export_breakdown_to_csv(mock_to_csv):
    ci = CompoundInterest(1000, 0.05, 1)
    ci.export_breakdown_to_csv("test.csv")
    mock_to_csv.assert_called_once()

@patch("pandas.DataFrame.to_excel")
def test_export_breakdown_to_excel(mock_to_excel):
    ci = CompoundInterest(1000, 0.05, 1)
    ci.export_breakdown_to_excel("test.xlsx")
    mock_to_excel.assert_called_once()


# ==== Edge Cases ====

def test_zero_contributions():
    ci = CompoundInterest(1000, 0.05, 10, contributions=0)
    assert round(ci.total_contributions(), 2) == 0

def test_zero_tax_rate_with_apply_tax():
    ci = CompoundInterest(1000, 0.05, 10, apply_tax=True, tax_rate=0.0)
    assert round(ci.total_tax_paid(), 2) == 0
