import math
import pandas as pd
from datetime import datetime
from typing import Union, Literal, Optional
from pandas.tseries.offsets import DateOffset


class CompoundInterest:
    # Rate period mapping for converting rate basis to frequency & daily conversion.
    # These mappings are used to determine the number of periods per year, etc.
    RATE_PERIOD_MAP = {
        "p.a.": "annually",
        "p.s.": "semiannually",
        "p.q.": "quarterly",
        "p.m.": "monthly",
        "p.biw.": "biweekly",
        "p.w.": "weekly",
        "p.d.": "daily",
        # The detailed properties for each frequency below:
        "annually": {"per_year": 1},
        "semiannually": {"per_year": 2},
        "quarterly": {"per_year": 4},
        "monthly": {"per_year": 12},
        "biweekly": {"per_year": 26},
        "weekly": {"per_year": 52},
        "daily": {"per_year": 365},
    }
    # Frequency options for compounding and contributions.
    FREQ_OPTIONS = {
        "annually",
        "semiannually",
        "quarterly",
        "monthly",
        "biweekly",
        "weekly",
        "daily",
    }
    # Rate basis allowed options.
    RATE_BASIS_OPTIONS = {"p.a.", "p.s.", "p.q.", "p.m.", "p.biw.", "p.w.", "p.d."}
    # Contribution timing allowed options.
    TIMING_OPTIONS = {"start", "end"}

    # Local mapping to force compounding on period-end dates.
    COMPOUND_FREQ_MAP = {
        "annually": "A-DEC",  # December end-of-year
        "semiannually": "6M",  # Every 6 months, use period-end dates
        "quarterly": "QE",  # Quarter end
        "monthly": "M",  # Month end
        "biweekly": "2W-SUN",  # Every 2 weeks on Sunday
        "weekly": "W-SUN",  # Week end: Sunday
        "daily": "D",  # Daily compounding
    }
    # Mapping for contributions. When contributions are at the start, use period-beginning offsets.
    CONTRIB_FREQ_MAP = {
        "annually": {"start": "AS", "end": "A-DEC"},  # Annually: Jan 1 versus Dec 31
        "semiannually": {"start": "6MS", "end": "6M"},  # Semiannual start vs. end
        "quarterly": {
            "start": "QS",
            "end": "QE",
        },  # Quarterly: Quarter start vs. quarter end
        "monthly": {"start": "MS", "end": "M"},  # Monthly: 1st vs. month end
        "biweekly": {
            "start": "2W-MON",
            "end": "2W-SUN",
        },  # Biweekly: Monday vs. Sunday (assuming 2-week period)
        "weekly": {"start": "W-MON", "end": "W-SUN"},  # Weekly: Monday vs. Sunday
        "daily": {"start": "D", "end": "D"},  # Daily contributions are the same
    }

    def __init__(
        self,
        init_value: float,
        interest_rate: float,
        rate_basis: Literal["p.a.", "p.s.", "p.q.", "p.m.", "p.biw.", "p.w.", "p.d."],
        years: float,
        start_date: Union[str, datetime] = datetime.today(),
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
        contribution_timing: Literal["start", "end"] = "end",
        tax_rate: float = 0.0,
    ) -> None:
        # Check for initial investment value.
        if not isinstance(init_value, (int, float)):
            raise TypeError("init_value must be a number (int or float).")
        if init_value < 0:
            raise ValueError("init_value must be non-negative.")
        self.init_value = float(init_value)

        # Check and set the interest rate.
        if not isinstance(interest_rate, (int, float)):
            raise TypeError("interest_rate must be a number (int or float).")
        if interest_rate < 0:
            raise ValueError("interest_rate must be non-negative.")
        self.nominal_interest_rate = float(interest_rate)

        # Validate rate basis.
        if not isinstance(rate_basis, str):
            raise TypeError("rate_basis must be a string.")
        if rate_basis not in self.RATE_BASIS_OPTIONS:
            raise ValueError(f"rate_basis must be one of {self.RATE_BASIS_OPTIONS}.")
        self.rate_basis = rate_basis

        # Set daily rate from nominal rate.
        self.daily_rate = self._to_daily_rate()

        # Check years.
        if not isinstance(years, (int, float)):
            raise TypeError("years must be a number (int or float).")
        if years <= 0:
            raise ValueError("years must be greater than zero.")
        if years > 200:
            raise ValueError("years must not exceed 200.")
        self.years = float(years)

        # Check and parse start_date.
        if isinstance(start_date, str):
            try:
                self.start_date = datetime.fromisoformat(start_date)
            except ValueError as e:
                raise ValueError(
                    "start_date string is not in a valid ISO format."
                ) from e
        elif isinstance(start_date, datetime):
            self.start_date = start_date
        else:
            raise TypeError(
                "start_date must be either a string or a datetime instance."
            )

        # Set compounding frequency.
        if comp_freq is None:
            default_freq = self.RATE_PERIOD_MAP.get(rate_basis)
            if isinstance(default_freq, str):
                comp_freq = default_freq  # e.g. "annually", "monthly", etc.
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

        # Validate contribution.
        if not isinstance(contribution, (int, float)):
            raise TypeError("contribution must be a number (int or float).")
        self.contribution = float(contribution)

        # Validate contribution frequency if provided.
        if contribution_freq is not None:
            if not isinstance(contribution_freq, str):
                raise TypeError("contribution_freq must be a string.")
            if contribution_freq not in self.FREQ_OPTIONS:
                raise ValueError(
                    f"contribution_freq must be one of {self.FREQ_OPTIONS} if provided."
                )
        self.contribution_freq = contribution_freq

        # Validate contribution timing.
        if not isinstance(contribution_timing, str):
            raise TypeError("contribution_timing must be a string.")
        if contribution_timing not in self.TIMING_OPTIONS:
            raise ValueError(
                f"contribution_timing must be one of {self.TIMING_OPTIONS}."
            )
        self.contribution_timing = contribution_timing

        # Validate tax rate.
        if not isinstance(tax_rate, (int, float)):
            raise TypeError("tax_rate must be a number (int or float).")
        if not (0 <= tax_rate <= 1):
            raise ValueError("tax_rate must be between 0 and 1 (inclusive).")
        self.tax_rate = float(tax_rate)

    def _to_daily_rate(self) -> float:
        """
        Converts the nominal interest rate into an equivalent daily rate.
        The conversion uses the per-year frequency defined in RATE_PERIOD_MAP.
        """
        try:
            period_key = self.RATE_PERIOD_MAP[self.rate_basis]
            n = self.RATE_PERIOD_MAP[period_key]["per_year"]
        except KeyError as e:
            raise ValueError(f"Unsupported rate_basis: {self.rate_basis}") from e

        return (1 + self.nominal_interest_rate) ** (n / 365) - 1

    def timeline(self) -> pd.DataFrame:
        """
        Generates a detailed timeline of the investment
        """
        # Mapping for weekday abbreviations. Python's weekday() returns Monday as 0.
        weekday_map = {
            0: "Mon",
            1: "Tue",
            2: "Wed",
            3: "Thu",
            4: "Fri",
            5: "Sat",
            6: "Sun",
        }

        # Normalize start date and compute end date.
        start_ts = pd.Timestamp(self.start_date).normalize()
        end_ts = start_ts + DateOffset(years=self.years)

        # ------------------------------------------------------------------------------
        # Generate compounding dates using the COMPOUND_FREQ_MAP.
        # ------------------------------------------------------------------------------
        comp_freq_str = self.COMPOUND_FREQ_MAP[self.comp_freq]
        comp_dates = set(
            pd.date_range(start=start_ts, end=end_ts, freq=comp_freq_str).normalize()
        )

        # ------------------------------------------------------------------------------
        # Generate contribution dates (if applicable) based on CONTRIB_FREQ_MAP.
        # ------------------------------------------------------------------------------
        contr_dates = set()
        if self.contribution_freq is not None and self.contribution > 0:
            contr_freq_str = self.CONTRIB_FREQ_MAP[self.contribution_freq][
                self.contribution_timing
            ]
            contr_dates = set(
                pd.date_range(
                    start=start_ts, end=end_ts, freq=contr_freq_str
                ).normalize()
            )

        # ------------------------------------------------------------------------------
        # Combine all relevant dates ensuring that start and end dates are included.
        # ------------------------------------------------------------------------------
        all_dates = {start_ts, end_ts} | comp_dates | contr_dates
        sorted_dates = sorted(d for d in all_dates if start_ts <= d <= end_ts)

        # ------------------------------------------------------------------------------
        # Initialize state and timeline container.
        # ------------------------------------------------------------------------------
        results = []
        current_balance = self.init_value
        last_comp_date = start_ts  # Most recent date when interest was compounded
        prev_date = start_ts  # Previous event date

        # Process initial date.
        initial_contribution = 0.0
        if start_ts in contr_dates and self.contribution_timing == "start":
            initial_contribution = self.contribution
            current_balance += self.contribution

        results.append(
            {
                "date": start_ts.strftime("%d.%m.%Y"),
                "weekday": weekday_map[start_ts.weekday()],
                "start_balance": self.init_value,
                "contribution": initial_contribution,
                "gross_interest": 0.0,
                "tax": 0.0,
                "net_interest": 0.0,
                "end_balance": current_balance,
            }
        )

        # ------------------------------------------------------------------------------
        # Process each subsequent event date.
        # ------------------------------------------------------------------------------
        for current_date in sorted_dates:
            if current_date == start_ts:
                continue

            # Calculate elapsed days for internal state update (not shown in the output).
            _ = (current_date - prev_date).days  # n_days computed internally

            period_start_balance = current_balance
            contribution_today = 0.0
            gross_interest = 0.0
            tax_amount = 0.0
            net_interest = 0.0

            # 1. Apply start-of-period contribution if applicable.
            if current_date in contr_dates and self.contribution_timing == "start":
                contribution_today += self.contribution
                current_balance += self.contribution

            # 2. Apply interest if today is a compounding day.
            if current_date in comp_dates:
                comp_interval_days = (current_date - last_comp_date).days
                if comp_interval_days > 0:
                    base_balance = current_balance
                    compound_factor = (1 + self.daily_rate) ** comp_interval_days
                    gross_interest = base_balance * (compound_factor - 1)
                    tax_amount = gross_interest * self.tax_rate
                    net_interest = gross_interest - tax_amount
                    current_balance += net_interest
                last_comp_date = current_date

            # 3. Apply end-of-period contribution if applicable.
            if current_date in contr_dates and self.contribution_timing == "end":
                contribution_today += self.contribution
                current_balance += self.contribution

            # 4. Record the day's results.
            results.append(
                {
                    "date": current_date.strftime("%d.%m.%Y"),
                    "weekday": weekday_map[current_date.weekday()],
                    "start_balance": period_start_balance,
                    "contribution": contribution_today,
                    "gross_interest": gross_interest,
                    "tax": tax_amount,
                    "net_interest": net_interest,
                    "end_balance": current_balance,
                }
            )

            prev_date = current_date

        timeline_df = pd.DataFrame(results)
        # Optionally round numerical columns for neat display.
        cols_to_round = [
            "start_balance",
            "contribution",
            "gross_interest",
            "tax",
            "net_interest",
            "end_balance",
        ]
        timeline_df[cols_to_round] = timeline_df[cols_to_round].round(2)

        return timeline_df

    def total_contributions(self) -> float:
        """
        Returns the total contributions over the investment period.
        """
        timeline_df = self.timeline()
        return timeline_df["contribution"].sum()

    def total_gross_interest(self) -> float:
        """
        Returns the total gross interest earned over the investment period.
        """
        timeline_df = self.timeline()
        return timeline_df["gross_interest"].sum()

    def total_tax_paid(self) -> float:
        """
        Returns the total tax paid on interest over the investment period.
        """
        timeline_df = self.timeline()
        return timeline_df["tax"].sum()

    def total_net_interest(self) -> float:
        """
        Returns the total net interest earned (after tax) over the investment period.
        """
        timeline_df = self.timeline()
        return timeline_df["net_interest"].sum()


# Example usage:
if __name__ == "__main__":
    # Create an instance with some sample parameters.
    ci = CompoundInterest(
        init_value=10000,
        interest_rate=0.05,
        rate_basis="p.a.",
        years=2,
        start_date="2020-02-20",
        comp_freq="annually",
        contribution=100,
        contribution_freq="quarterly",
        contribution_timing="start",
        tax_rate=0.15,
    )

    timeline_df = ci.timeline()
    print(timeline_df.head(60))


# contribution dates are fixed like compounding frequency dates, but should be dynamically depending on the start date
