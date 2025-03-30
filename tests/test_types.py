import pytest
from pycic.calculator import CompoundInterest


@pytest.mark.parametrize(
    "params, expected_error",
    [
        # None values
        ({"init_value": None}, TypeError),
        ({"interest_rate": None}, TypeError),
        ({"years": None}, TypeError),
        ({"contribution": None}, TypeError),
        ({"comp_freq": None}, TypeError),
        # Note: contribution_freq defaults to comp_freq when None is given.
        ({"contribution_freq": None}, None),
        ({"contribution_timing": None}, TypeError),
        ({"tax_rate": None}, TypeError),
        # Wrong types
        ({"init_value": "10000"}, TypeError),
        ({"interest_rate": "0.05"}, TypeError),
        ({"years": "5"}, TypeError),
        ({"contribution": "100"}, TypeError),
        ({"comp_freq": 123}, TypeError),
        ({"contribution_freq": 123}, TypeError),
        ({"contribution_timing": 123}, TypeError),
        ({"tax_rate": "0.25"}, TypeError),
        # Invalid numeric values
        ({"init_value": -10000}, ValueError),
        ({"interest_rate": -0.05}, ValueError),
        ({"years": -5}, ValueError),
        ({"years": 0}, ValueError),
        ({"contribution": -100}, ValueError),
        ({"tax_rate": -0.25}, ValueError),
        ({"tax_rate": 1.1}, ValueError),
        # tests for interest_rate > 1 and years > 500
        ({"interest_rate": 1.1}, ValueError),
        ({"years": 501}, ValueError),
        # Invalid string values
        ({"comp_freq": "invalid"}, ValueError),
        ({"contribution_freq": "invalid"}, ValueError),
        ({"contribution_timing": "invalid"}, ValueError),
        # Valid edge cases
        ({"init_value": 0}, None),
        ({"interest_rate": 0}, None),
        ({"contribution": 0}, None),
        ({"tax_rate": 0}, None),
    ],
)
def test_edge_cases(params, expected_error):
    """
    Test various edge cases and verify that the correct error
    (or no error) is raised.
    """
    defaults = {
        "init_value": 10000,
        "interest_rate": 0.05,
        "years": 5,
        "contribution": 100,
        "comp_freq": "annually",
        "contribution_freq": "annually",
        "contribution_timing": "end",
        "tax_rate": 0.25,
    }
    kwargs = {**defaults, **params}

    if expected_error is None:
        ci = CompoundInterest(**kwargs)
        assert isinstance(ci, CompoundInterest)
    else:
        with pytest.raises(expected_error):
            CompoundInterest(**kwargs)


def test_optional_parameters_defaults():
    """
    Test that omitting the optional parameters uses the default values correctly.
    """

    ci = CompoundInterest(
        init_value=5000,
        interest_rate=0.04,
        years=10,
        comp_freq="quarterly",
    )

    assert ci.contribution == 0.0, "Default contribution should be 0.0"
    assert (
        ci.contribution_freq == "quarterly"
    ), "Default contribution_freq should match comp_freq"
    assert (
        ci.contribution_timing == "end"
    ), "Default contribution_timing should be 'end'"
    assert ci.tax_rate == 0.0, "Default tax_rate should be 0.0"


invalid_inflation_inputs = [
    "0.03",
    "high",
    True,
    [0.03],
    {"rate": 0.03},
    None,
    complex(0.03),
]


@pytest.mark.parametrize("invalid_inflation", invalid_inflation_inputs)
def test_future_value_invalid_inflation_raises(invalid_inflation):
    ci = CompoundInterest(
        init_value=10000,
        interest_rate=0.05,
        years=5,
        contribution=100,
        comp_freq="annually",
        contribution_freq="annually",
        contribution_timing="end",
        tax_rate=0.25,
    )
    with pytest.raises(ValueError, match="Inflation must be a numeric type"):
        ci.future_value(inflation=invalid_inflation)
