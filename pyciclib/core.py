import pandas as pd

from datetime import datetime
from typing import Union, Literal, Optional
from pandas.tseries.offsets import DateOffset


class CompoundInterest:
    """
    Calculate compound interest with support for periodic contributions.

    This class handles the computation of compound interest over a specified number
    of years, with options for different compounding frequencies and contribution timings.
    It validates inputs, converts the effective interest rate to a daily rate, and sets up
    frequency mappings for both compounding and contributions.
    """

    # mappings
    RATE_PERIOD_MAP = {
        "p.a.": "annually",
        "p.s.": "semiannually",
        "p.q.": "quarterly",
        "p.m.": "monthly",
        "p.biw.": "biweekly",
        "p.w.": "weekly",
        "p.d.": "daily",
        "annually": {"per_year": 1},
        "semiannually": {"per_year": 2},
        "quarterly": {"per_year": 4},
        "monthly": {"per_year": 12},
        "biweekly": {"per_year": 26},
        "weekly": {"per_year": 52},
        "daily": {"per_year": 365},
    }

    FREQ_OPTIONS = {
        "annually",
        "semiannually",
        "quarterly",
        "monthly",
        "biweekly",
        "weekly",
        "daily",
    }

    RATE_BASIS_OPTIONS = {"p.a.", "p.s.", "p.q.", "p.m.", "p.biw.", "p.w.", "p.d."}
    TIMING_OPTIONS = {"start", "end"}

    COMPOUND_FREQ_MAP = {
        "annually": "A-DEC",
        "semiannually": "6M",
        "quarterly": "QE",
        "monthly": "M",
        "biweekly": "2W-SUN",
        "weekly": "W-SUN",
        "daily": "D",
    }

    CONTRIB_FREQ_MAP = {
        "annually": {"start": "AS", "end": "A-DEC"},
        "semiannually": {"start": "6MS", "end": "6M"},
        "quarterly": {
            "start": "QS",
            "end": "QE",
        },
        "monthly": {"start": "MS", "end": "M"},
        "biweekly": {
            "start": "2W-MON",
            "end": "2W-SUN",
        },
        "weekly": {"start": "W-MON", "end": "W-SUN"},
        "daily": {"start": "D", "end": "D"},
    }

    def __init__(
        self,
        init_value: float,
        interest_rate: float,
        rate_basis: Literal["p.a.", "p.s.", "p.q.", "p.m.", "p.biw.", "p.w.", "p.d."],
        years: float,
        start_date: Optional[Union[str, datetime]] = datetime.today(),
        comp_freq: Optional[
            Literal[
                "annually",
                "semiannually",
                "quarterly",
                "monthly",
                "biweekly",
                "weekly",
                "daily",
            ]
        ] = None,
        contribution: float = 0.0,
        contribution_freq: Optional[
            Literal[
                "annually",
                "semiannually",
                "quarterly",
                "monthly",
                "biweekly",
                "weekly",
                "daily",
            ]
        ] = None,
        contribution_timing: Literal["start", "end"] = None,
        tax_rate: float = 0.0,
    ) -> None:
        """
        Initialize a CompoundInterest instance.

        Args:
            init_value (float, required): Initial investment amount.
            interest_rate (float, required): Effective interest rate.
            rate_basis (str, required): Rate basis; allowed values: "p.a.", "p.s.", "p.q.", "p.m.", "p.biw.", "p.w.", "p.d.".
            years (float, required): Investment duration in years.
            start_date (Union[str, datetime], optional): Start date (ISO/European date string or datetime object). Defaults to today's date.
            comp_freq (str, optional): Compounding frequency; if None, determined from rate_basis.
            contribution (float, optional): Regular contribution amount. Defaults to 0.0.
            contribution_freq (str, optional): Frequency for contributions; required if contributions are made.
            contribution_timing (str, optional): Timing of contributions ("start" or "end"). Defaults to "end".
            tax_rate (float, optional): Tax rate as a decimal (between 0 and 1). Defaults to 0.0.
        """

        # validation and input checking for all passed parameters
        if not isinstance(init_value, (int, float)):
            raise TypeError("init_value must be a number (int or float).")
        if init_value < 0:
            raise ValueError("init_value must be non-negative.")
        self.init_value = float(init_value)

        if not isinstance(interest_rate, (int, float)):
            raise TypeError("interest_rate must be a number (int or float).")
        if not (0 <= interest_rate <= 1):
            raise ValueError("interest_rate must be between 0 and 1 (inclusive).")
        self.effective_interest_rate = float(interest_rate)

        if not isinstance(rate_basis, str):
            raise TypeError("rate_basis must be a string.")
        if rate_basis not in self.RATE_BASIS_OPTIONS:
            raise ValueError(f"rate_basis must be one of {self.RATE_BASIS_OPTIONS}.")
        self.rate_basis = rate_basis

        self.daily_rate = self._to_daily_rate()

        if not isinstance(years, (int, float)):
            raise TypeError("years must be a number (int or float).")
        if years <= 0:
            raise ValueError("years must be greater than zero.")
        if years > 200:
            raise ValueError("years must not exceed 200.")
        self.years = float(years)

        if start_date is None:
            self.start_date = datetime.today()
        elif isinstance(start_date, str):
            try:
                # parse as ISO date format
                self.start_date = datetime.fromisoformat(start_date)
            except ValueError:
                try:
                    # parse as European date format
                    self.start_date = datetime.strptime(start_date, "%d.%m.%Y")
                except ValueError as e:
                    raise ValueError(
                        "start_date string is not in a valid ISO or European date format."
                    ) from e
        elif isinstance(start_date, datetime):
            self.start_date = start_date
        else:
            raise TypeError(
                "start_date must be None, or a string or datetime instance."
            )

        if comp_freq is None:
            default_freq = self.RATE_PERIOD_MAP.get(rate_basis)
            if isinstance(default_freq, str):
                comp_freq = default_freq
            else:
                raise ValueError(
                    "Cannot determine compounding frequency from rate_basis."
                )
        else:
            if not isinstance(comp_freq, str):
                raise TypeError("comp_freq must be a string.")
            if comp_freq not in self.FREQ_OPTIONS:
                raise ValueError(f"comp_freq must be one of {self.FREQ_OPTIONS}.")
        self.comp_freq = comp_freq

        if not isinstance(contribution, (int, float)):
            raise TypeError("contribution must be a number (int or float).")
        if contribution < 0:
            raise ValueError("contribution must be non-negative.")
        self.contribution = float(contribution)

        if contribution_freq is not None:
            if self.contribution <= 0:
                raise ValueError(
                    "A contribution frequency is provided, but the contribution is not greater than zero."
                )
            if not isinstance(contribution_freq, str):
                raise TypeError("contribution_freq must be a string.")
            if contribution_freq not in self.FREQ_OPTIONS:
                raise ValueError(
                    f"contribution_freq must be one of {self.FREQ_OPTIONS}."
                )
        else:
            if self.contribution > 0:
                raise ValueError(
                    "A contribution frequency must be provided when contribution is greater than zero."
                )
        self.contribution_freq = contribution_freq

        if self.contribution <= 0 and contribution_timing is not None:
            raise ValueError(
                "Contribution timing should not be provided when there is no contribution or contribution frequency."
            )

        if self.contribution > 0:
            # If no timing is provided and a contribution frequency exists, default to "end"
            if contribution_timing is None:
                contribution_timing = "end"
            else:
                if not isinstance(contribution_timing, str):
                    raise TypeError("contribution_timing must be a string.")
                if contribution_timing not in self.TIMING_OPTIONS:
                    raise ValueError(
                        f"contribution_timing must be one of {self.TIMING_OPTIONS}."
                    )

        self.contribution_timing = contribution_timing

        if not isinstance(tax_rate, (int, float)):
            raise TypeError("tax_rate must be a number (int or float).")
        if not (0 <= tax_rate <= 1):
            raise ValueError("tax_rate must be between 0 and 1 (inclusive).")
        self.tax_rate = float(tax_rate)

    def _to_daily_rate(self) -> float:
        """
        Convert the effective interest rate to an equivalent daily rate.
        """
        try:
            period_key = self.RATE_PERIOD_MAP[self.rate_basis]
            n = self.RATE_PERIOD_MAP[period_key]["per_year"]
        except KeyError as e:
            raise ValueError(f"Unsupported rate_basis: {self.rate_basis}") from e

        return (1 + self.effective_interest_rate) ** (n / 365) - 1

    def _generate_compounding_dates(
        self, start_ts: pd.Timestamp, end_ts: pd.Timestamp, freq: str
    ) -> set:
        """
        Generate compounding dates from start_ts based on the given frequency.
        Compounding is applied one day before the next period starts.
        """
        offset_map = {
            "annually": DateOffset(years=1),
            "semiannually": DateOffset(months=6),
            "quarterly": DateOffset(months=3),
            "monthly": DateOffset(months=1),
            "biweekly": DateOffset(weeks=2),
            "weekly": DateOffset(weeks=1),
            "daily": DateOffset(days=1),
        }
        offset = offset_map[freq]
        dates = set()
        n = 0
        while True:
            current = start_ts + (n + 1) * offset - pd.Timedelta(days=1)
            if current > end_ts:
                break
            dates.add(current.normalize())
            n += 1
        return dates

    def _generate_contribution_dates(
        self, start_ts: pd.Timestamp, end_ts: pd.Timestamp, freq: str, timing: str
    ) -> set:
        """
        Generate contribution dates starting from start_ts.
        If timing is 'start', the contribution occurs on start_ts;
        if 'end', it occurs one day before the next period starts.
        """
        offset_map = {
            "annually": DateOffset(years=1),
            "semiannually": DateOffset(months=6),
            "quarterly": DateOffset(months=3),
            "monthly": DateOffset(months=1),
            "biweekly": DateOffset(weeks=2),
            "weekly": DateOffset(weeks=1),
            "daily": DateOffset(days=1),
        }
        offset = offset_map[freq]
        dates = set()
        n = 0
        while True:
            if timing == "start":
                current = start_ts + n * offset
            else:
                current = start_ts + (n + 1) * offset - pd.Timedelta(days=1)
            if current > end_ts:
                break
            dates.add(current.normalize())
            n += 1
        return dates

    def timeline(self) -> pd.DataFrame:
        """
        Generate a detailed timeline DataFrame for the investment based on dynamically computed dates.
        """
        # mapping for weekday labels
        weekday_map = {
            0: "Mon",
            1: "Tue",
            2: "Wed",
            3: "Thu",
            4: "Fri",
            5: "Sat",
            6: "Sun",
        }

        # normalize the start date and calculate the end date
        start_ts = pd.Timestamp(self.start_date).normalize()
        end_ts = start_ts + DateOffset(years=self.years)

        # compute compounding dates dynamically
        comp_dates = self._generate_compounding_dates(start_ts, end_ts, self.comp_freq)

        # compute contribution dates if specified
        if self.contribution_freq is not None and self.contribution > 0:
            contr_dates = self._generate_contribution_dates(
                start_ts, end_ts, self.contribution_freq, self.contribution_timing
            )
        else:
            contr_dates = set()

        # combine all relevant dates
        all_dates = {start_ts, end_ts} | comp_dates | contr_dates
        sorted_dates = sorted(d for d in all_dates if start_ts <= d <= end_ts)

        results = []
        current_balance = self.init_value
        last_comp_date = start_ts

        # iterate through all dates (starting with the start date)
        for i, current_date in enumerate(sorted_dates):
            if i == 0:
                contribution = (
                    self.contribution
                    if (
                        current_date in contr_dates
                        and self.contribution_timing == "start"
                    )
                    else 0.0
                )
                current_balance += contribution
                record = {
                    "date": current_date.strftime("%d.%m.%Y"),
                    "weekday": weekday_map[current_date.weekday()],
                    "start_balance": self.init_value,
                    "contribution": contribution,
                    "gross_interest": 0.0,
                    "tax": 0.0,
                    "net_interest": 0.0,
                    "end_balance": current_balance,
                }
            else:
                # record the opening balance before any contributions.
                period_start_balance = current_balance
                contribution = 0.0

                # if a 'start' contribution occurs on this day, add to the balance.
                if current_date in contr_dates and self.contribution_timing == "start":
                    # if contribution frequency is daily, display the contribution effect already in the start balance so its easier to follow around for the user
                    if self.contribution_freq == "daily":
                        display_start_balance = period_start_balance + self.contribution
                    else:
                        display_start_balance = period_start_balance
                    contribution += self.contribution
                    current_balance += self.contribution
                else:
                    display_start_balance = period_start_balance

                # compounding: if current_date is a compounding date.
                if current_date in comp_dates:
                    comp_interval_days = (current_date - last_comp_date).days
                    if comp_interval_days > 0:
                        factor = (1 + self.daily_rate) ** comp_interval_days
                        gross_interest = current_balance * (factor - 1)
                        tax_amount = gross_interest * self.tax_rate
                        net_interest = gross_interest - tax_amount
                        current_balance += net_interest
                    else:
                        gross_interest = tax_amount = net_interest = 0.0
                    last_comp_date = current_date
                else:
                    gross_interest = tax_amount = net_interest = 0.0

                # if there's an 'end' contribution, add it here.
                if current_date in contr_dates and self.contribution_timing == "end":
                    contribution += self.contribution
                    current_balance += self.contribution

                record = {
                    "date": current_date.strftime("%d.%m.%Y"),
                    "weekday": weekday_map[current_date.weekday()],
                    "start_balance": display_start_balance,
                    "contribution": contribution,
                    "gross_interest": gross_interest,
                    "tax": tax_amount,
                    "net_interest": net_interest,
                    "end_balance": current_balance,
                }
            results.append(record)

        timeline_df = pd.DataFrame(results)

        return timeline_df

    def future_value(self) -> float:
        """
        Returns the final value of the investment as a float.
        """
        fv = float(self.timeline().iloc[-1]["end_balance"])
        return fv

    def total_contributions(self) -> float:
        """
        Returns the total contributions over the investment period.
        """
        timeline_df = self.timeline()
        return float(timeline_df["contribution"].sum())

    def total_gross_interest(self) -> float:
        """
        Returns the total gross interest earned over the investment period.
        """
        timeline_df = self.timeline()
        return float(timeline_df["gross_interest"].sum())

    def total_tax_paid(self) -> float:
        """
        Returns the total tax paid on interest over the investment period.
        """
        timeline_df = self.timeline()
        return float(timeline_df["tax"].sum())

    def total_net_interest(self) -> float:
        """
        Returns the total net interest earned (after tax) over the investment period.
        """
        timeline_df = self.timeline()
        return float(timeline_df["net_interest"].sum())

    def summary(self):
        """
        Returns a summary dictionary with two sections:
        - "input": the initialization parameters provided.
        - "end": the summarized results from the timeline.
        """
        input_params = {
            "Initial Value": self.init_value,
            "Interest Rate": self.effective_interest_rate,
            "Rate Basis": self.rate_basis,
            "Equivalent Daily Interest Rate": self.daily_rate,
            "Years": self.years,
            "Start Date": (
                self.start_date.strftime("%d.%m.%Y")
                if isinstance(self.start_date, datetime)
                else self.start_date
            ),
            "Compounding Frequency": self.comp_freq,
            "Contribution": self.contribution,
            "Contribution Frequency": self.contribution_freq,
            "Contribution Timing": self.contribution_timing,
            "Tax Rate": self.tax_rate,
        }
        output_params = {
            "Total Contributions": self.total_contributions(),
            "Total Gross Interest": self.total_gross_interest(),
            "Total Tax Paid": self.total_tax_paid(),
            "Total Net Interest": self.total_net_interest(),
            "Final Value": self.future_value(),
        }
        return {"input": input_params, "output": output_params}

    def __call__(self):
        """
        Allows the instance to be callable.
        When called, it returns the timeline DataFrame.
        """
        return self.timeline()

    def __eq__(self, other):
        """
        Compares two CompoundInterest instances for equality by checking all relevant attributes.
        """
        if not isinstance(other, CompoundInterest):
            return NotImplemented
        return (
            self.init_value == other.init_value
            and self.effective_interest_rate == other.effective_interest_rate
            and self.rate_basis == other.rate_basis
            and self.years == other.years
            and self.start_date == other.start_date
            and self.comp_freq == other.comp_freq
            and self.contribution == other.contribution
            and self.contribution_freq == other.contribution_freq
            and self.contribution_timing == other.contribution_timing
            and self.tax_rate == other.tax_rate
        )

    def __str__(self):
        """
        Returns a user-friendly string representation of this CompoundInterest instance.
        """
        return (
            f"CompoundInterest(init_value={self.init_value}, "
            f"interest_rate={self.effective_interest_rate}, "
            f"years={self.years}, "
            f"start_date={self.start_date.strftime("%d.%m.%Y")}, "
            f"comp_freq='{self.comp_freq}', "
            f"contribution={self.contribution}, "
            f"contribution_freq={self.contribution_freq}, "
            f"contribution_timing='{self.contribution_timing}', "
            f"tax_rate={self.tax_rate})"
        )

    def __repr__(self):
        """
        Returns an unambiguous string representation of the CompoundInterest instance.
        """
        return (
            f"CompoundInterest(init_value={self.init_value!r}, "
            f"interest_rate={self.effective_interest_rate!r}, "
            f"rate_basis={self.rate_basis!r}, "
            f"years={self.years!r}, "
            f"start_date={self.start_date!r}, "
            f"comp_freq={self.comp_freq!r}, "
            f"contribution={self.contribution!r}, "
            f"contribution_freq={self.contribution_freq!r}, "
            f"contribution_timing={self.contribution_timing!r}, "
            f"tax_rate={self.tax_rate!r})"
        )
