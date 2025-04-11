import math
import pandas as pd
from typing import Optional, Literal
from .utils import FREQ_MAP, LABEL_MAP


class CompoundInterest:
    def __init__(
        self,
        init_value: float,
        interest_rate: float,
        years: float,
        comp_freq: Literal[
            "annually",
            "semiannually",
            "quarterly",
            "monthly",
            "biweekly",
            "weekly",
            "daily",
        ],
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
        """
        Initialize a CompoundInterest calculator.

        Required Parameters:
            init_value (float): Initial investment amount.
            interest_rate (float): Interest rate per annum (p.a.), entered as a decimal (e.g.: 0.05 for 5% p.a.).
            years (float): Investment duration in years.
            comp_freq (str): Frequency of interest compounding.
                Recommended options: 'annually', 'semiannually', 'quarterly',
                'monthly', 'biweekly', 'weekly', 'daily'.

        Optional Parameters:
            contribution (float): Amount contributed at each interval. Defaults to 0.0.
            contribution_freq (str): Frequency of contributions. Defaults to same as compounding.
                Recommended options are the same as for comp_freq.
            contribution_timing (str): When the contribution is made.
                Recommended options: "start" or "end". Defaults to "end".
            tax_rate (float): Tax rate applied to interest. Defaults to 0.0.
        """

        # Type and value checks
        if not isinstance(init_value, (int, float)):
            raise TypeError("init_value must be a number")
        if init_value < 0:
            raise ValueError("init_value must be non-negative")

        if not isinstance(interest_rate, (int, float)):
            raise TypeError("interest_rate must be a number")
        if interest_rate < 0 or interest_rate > 1:
            raise ValueError("interest_rate must be between 0 and 1")

        if not isinstance(years, (int, float)):
            raise TypeError("years must be a number")
        if years <= 0:
            raise ValueError("years must be positive")
        if years > 200:
            raise ValueError("years must be 200 or less")

        if not isinstance(contribution, (int, float)):
            raise TypeError("contribution must be a number")
        if contribution < 0:
            raise ValueError("contribution must be non-negative")

        if not isinstance(tax_rate, (int, float)):
            raise TypeError("tax_rate must be a number")
        if not 0 <= tax_rate <= 1:
            raise ValueError("tax_rate must be between 0 and 1")

        # String parameter validation
        if comp_freq is None:
            raise TypeError("comp_freq cannot be None")
        if not isinstance(comp_freq, str):
            raise TypeError("comp_freq must be a string")
        comp_freq = comp_freq.strip().lower()
        if comp_freq not in FREQ_MAP:
            raise ValueError(f"Invalid compounding frequency: '{comp_freq}'")

        if contribution_freq is not None and not isinstance(contribution_freq, str):
            raise TypeError("contribution_freq must be a string or None")
        contribution_freq = (contribution_freq or comp_freq).strip().lower()
        if contribution_freq not in FREQ_MAP:
            raise ValueError(f"Invalid contribution frequency: '{contribution_freq}'")

        if contribution_timing is None:
            raise TypeError("contribution_timing cannot be None")
        if not isinstance(contribution_timing, str):
            raise TypeError("contribution_timing must be a string")
        contribution_timing = contribution_timing.strip().lower()
        if contribution_timing not in {"start", "end"}:
            raise ValueError("contribution_timing must be either 'start' or 'end'")

        # Normalize string inputs
        comp_freq = comp_freq.strip().lower()
        contribution_freq = (contribution_freq or comp_freq).strip().lower()
        contribution_timing = contribution_timing.strip().lower()

        self.init_value = init_value
        self.interest_rate = interest_rate
        self.years = years
        self.contribution = contribution
        self.comp_freq = comp_freq
        self.contribution_freq = contribution_freq
        self.contribution_timing = contribution_timing
        self.tax_rate = tax_rate

        self.compound_periods = FREQ_MAP[comp_freq]
        self.contrib_periods = FREQ_MAP[contribution_freq]

    def __repr__(self) -> str:
        """
        Returns a precise string representation of the object for debugging and development.
        """
        return (
            f"CompoundInterest("
            f"init_value={self.init_value}, "
            f"interest_rate={self.interest_rate}, "
            f"years={self.years}, "
            f"comp_freq='{self.comp_freq}', "
            f"contribution={self.contribution}, "
            f"contribution_freq='{self.contribution_freq}', "
            f"contribution_timing='{self.contribution_timing}', "
            f"tax_rate={self.tax_rate})"
        )

    def __str__(self) -> str:
        """
        Returns a user-friendly summary of the compound interest scenario.
        """
        tax_info = f"{self.tax_rate * 100:.1f}%" if self.tax_rate > 0 else "No tax"
        return (
            f"📊 Compound Interest Summary\n"
            f"------------------------------\n"
            f"Initial Value:         ${self.init_value:,.2f}\n"
            f"Annual Rate:           {self.interest_rate * 100:.2f}%\n"
            f"Years:                 {self.years}\n"
            f"Contribution:          ${self.contribution:,.2f} ({self.contribution_freq}, {self.contribution_timing})\n"
            f"Compounding:           {self.comp_freq.capitalize()}\n"
            f"Tax on Interest:       {tax_info}\n"
            f"Future Value:          ${self.future_value():,.2f}"
        )

    def __call__(self) -> float:
        """
        Allows the instance to be called like a function to return the future value.
        """
        return self.future_value()

    def __eq__(self, other: object) -> bool:
        """
        Compares two instances of CompoundInterest for equality.
        """
        if not isinstance(other, CompoundInterest):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def future_value(self, inflation: float = 0.0) -> float:
        """
        Calculates the future value of the investment.

        Parameters:
        inflation (float): Annual inflation rate as a decimal (e.g., 0.02 for 2% inflation). Default is 0.0.
        """

        if not isinstance(inflation, (float, int)) or isinstance(inflation, bool):
            raise ValueError("Inflation must be a numeric type (float or int).")
        if not (0 <= inflation <= 1):
            raise ValueError("Inflation must be a value between 0 and 1.")

        compound_periods = FREQ_MAP.get(self.comp_freq, 1)
        contrib_periods = FREQ_MAP.get(self.contribution_freq, 1)
        freq = max(compound_periods, contrib_periods)
        total_periods = int(self.years * freq)
        period_rate = (1 + self.interest_rate) ** (1 / compound_periods) - 1

        balance = self.init_value
        compound_interval = freq // compound_periods
        n_contrib = int(self.years * contrib_periods)

        if self.contribution_timing == "start":
            deposit_days = {
                int(math.floor(i * total_periods / n_contrib)) + 1
                for i in range(n_contrib)
            }
        else:
            deposit_days = {
                int(math.floor((i + 1) * total_periods / n_contrib))
                for i in range(n_contrib)
            }

        contrib_count = 0

        for period in range(1, total_periods + 1):
            if self.contribution_timing == "start" and period in deposit_days:
                if contrib_count < n_contrib:
                    balance += self.contribution
                    contrib_count += 1

            if period % compound_interval == 0:
                interest = balance * period_rate
                if self.tax_rate > 0:
                    interest *= 1 - self.tax_rate
                balance += interest

            if self.contribution_timing == "end" and period in deposit_days:
                if contrib_count < n_contrib:
                    balance += self.contribution
                    contrib_count += 1

        # Adjust for inflation if provided
        if inflation > 0:
            balance = balance / ((1 + inflation) ** self.years)

        return round(balance, 2)

    def breakdown(self) -> pd.DataFrame:
        """
        Returns a detailed breakdown of each period as a Pandas DataFrame.

        Columns:
            Label, Period, Starting Balance, Contribution at <start/end>, Gross Interest, Net Interest, Tax Paid, Ending Balance
        """
        compound_periods = FREQ_MAP.get(self.comp_freq, 1)
        contrib_periods = FREQ_MAP.get(self.contribution_freq, 1)
        freq = max(compound_periods, contrib_periods)
        total_periods = int(self.years * freq)
        period_rate = (1 + self.interest_rate) ** (1 / compound_periods) - 1

        if contrib_periods >= compound_periods:
            label_base = LABEL_MAP.get(self.contribution_freq, "Period")
        else:
            label_base = LABEL_MAP.get(self.comp_freq, "Period")

        data = []
        balance = self.init_value
        compound_interval = freq // compound_periods
        n_contrib = int(self.years * contrib_periods)

        if self.contribution_timing == "start":
            deposit_days = {
                int(math.floor(i * total_periods / n_contrib)) + 1
                for i in range(n_contrib)
            }
        else:
            deposit_days = {
                int(math.floor((i + 1) * total_periods / n_contrib))
                for i in range(n_contrib)
            }

        contrib_count = 0

        for period in range(1, total_periods + 1):
            starting_balance = balance
            contribution_val = 0.0
            gross_interest = 0.0
            net_interest = 0.0
            tax_paid = 0.0

            if self.contribution_timing == "start" and period in deposit_days:
                if contrib_count < n_contrib:
                    balance += self.contribution
                    contribution_val = self.contribution
                    contrib_count += 1
                    starting_balance = balance

            if period % compound_interval == 0:
                gross_interest = balance * period_rate
                net_interest = gross_interest
                if self.tax_rate > 0:
                    tax_paid = gross_interest * self.tax_rate
                    net_interest = gross_interest - tax_paid

            balance += net_interest

            if self.contribution_timing == "end" and period in deposit_days:
                if contrib_count < n_contrib:
                    balance += self.contribution
                    contribution_val = self.contribution
                    contrib_count += 1

            data.append(
                {
                    "label": label_base,
                    "period": period,
                    "starting_balance": round(starting_balance, 2),
                    f"contribution_at_{self.contribution_timing}": round(
                        contribution_val, 2
                    ),
                    "gross_interest": round(gross_interest, 2),
                    "net_interest": round(net_interest, 2),
                    "tax_paid": round(tax_paid, 2),
                    "ending_balance": round(balance, 2),
                }
            )

        return pd.DataFrame(data)

    def total_contributions(self) -> float:
        """
        Returns the total amount contributed over the investment period.
        """
        total = self.contribution * self.years * self.contrib_periods
        return round(total, 2)

    def total_gross_interest_earned(self) -> float:
        """
        Returns the total gross interest earned over the investment period.
        """
        df = self.breakdown()
        return round(df["gross_interest"].sum(), 2)

    def total_net_interest_earned(self) -> float:
        """
        Returns the total net interest earned over the investment period.
        """
        df = self.breakdown()
        return round(df["net_interest"].sum(), 2)

    def total_tax_paid(self) -> float:
        """
        Returns the total tax paid on interest over the investment period.
        """
        if self.tax_rate == 0:
            return 0.0
        df = self.breakdown()
        return round(df["tax_paid"].sum(), 2)

    def summary(self) -> None:
        """
        Prints a summary of the compound interest scenario.
        """

        initial = self.init_value
        total_contrib = self.total_contributions()
        gross_int = self.total_gross_interest_earned()
        net_int = self.total_net_interest_earned()
        tax = self.total_tax_paid()
        end_val = self.future_value()

        items = [
            ("Initial Investment", initial),
            ("Total Contributions", total_contrib),
            ("Gross Interest Earned", gross_int),
            ("Net Interest Earned", net_int),
            ("Tax Paid", tax),
            ("Future Value", end_val),
        ]

        max_label_length = max(len(label) for label, _ in items)
        header = "PyCIC Summary"
        border = "=" * (max_label_length + 30)

        print(border)
        print(header.center(max_label_length + 30))
        print(border)

        for label, value in items:
            print(f"{label:<{max_label_length}} :    {value:,.2f}")

        print(border)

    @staticmethod
    def to_pa_rate(
        nominal_rate: float,
        rate_period: Literal["p.a.", "p.s.", "p.q.", "p.m.", "p.biw.", "p.w.", "p.d."],
    ) -> float:
        """
        Converts a nominal interest rate expressed per period (e.g., per month "p.m.")
        into an effective annual interest rate (EAR), assuming compounding.

        This function is useful when preparing an optimal input rate for the
        CompoundInterest class in the pycic package — particularly when the
        interest rate is not originally given per annum.

        For example:
            - If a user has 0.4% per month (p.m.), this converts it to ~4.9% p.a. EAR.
            - This EAR can then be passed into pycic.CompoundInterest for realistic modeling.

        Parameters:
            nominal_rate (float): The nominal interest rate per given period
                                (e.g., 0.004 for 0.4% per month)
            rate_period (str): The basis of the nominal rate. One of:
                - 'p.a.'   → per annum
                - 'p.s.'   → per semiannual
                - 'p.q.'   → per quarter
                - 'p.m.'   → per month
                - 'p.biw.' → per biweek (every two weeks)
                - 'p.w.'   → per week
                - 'p.d.'   → per day

        Returns:
            float: Effective annual rate (EAR), as a decimal (e.g., 0.049 = 4.9%)
        """

        PERIOD_MAP = {
            "p.a.": 1,
            "p.s.": 2,
            "p.q.": 4,
            "p.m.": 12,
            "p.biw.": 26,
            "p.w.": 52,
            "p.d.": 365,
        }

        if rate_period not in PERIOD_MAP:
            raise ValueError(
                f"Invalid rate_period '{rate_period}'. Must be one of: {list(PERIOD_MAP.keys())}"
            )

        periods_per_year = PERIOD_MAP[rate_period]
        return (1 + nominal_rate) ** periods_per_year - 1
