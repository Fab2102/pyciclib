import pandas as pd
from typing import Optional, List, Dict
from .utils import FREQ_MAP, LABEL_MAP, validate_filename



class CompoundInterest:
    """
    A flexible and high-precision compound interest calculator.

    This class models the growth of an investment over time with customizable
    compounding frequency, contribution schedule, tax treatment, and inflation adjustment.
    It also supports exporting detailed breakdowns to CSV or Excel.

    Parameters:
        init_value (float): 
            Initial investment amount. (Required)
        
        rate (float): 
            Annual interest rate as a decimal (e.g., 0.05 for 5%). (Required)
        
        years (float): 
            Investment duration in years. (Required)
        
        compounding (str): 
            Compounding frequency. Must be one of: 
            'annually', 'semiannually', 'quarterly', 'monthly',
            'biweekly', 'weekly', or 'daily'. (Required)

        contributions (float, optional): 
            Amount contributed at each interval. Defaults to 0.0.

        contribution_frequency (str, optional): 
            Frequency of contributions. Defaults to the compounding frequency.

        contribution_timing (str, optional): 
            Whether contributions are made at the 'start' or 'end' of each period. Defaults to 'end'.

        apply_tax (bool, optional): 
            Whether to apply tax on interest. Defaults to False.

        tax_rate (float, optional): 
            Flat tax rate to apply on interest (if enabled). Defaults to 0.0.

    Example:
        >>> from pycic import CompoundInterest
        >>> ci = CompoundInterest(
        ...     init_value=1000,
        ...     rate=0.05,
        ...     years=10,
        ...     contributions=100,
        ...     compounding="monthly",
        ...     apply_tax=True,
        ...     tax_rate=0.25
        ... )
        >>> ci.future_value()
        20045.12

        >>> ci.export_breakdown_to_csv("output.csv")
    """

    def __init__(
        self,
        init_value: float,
        rate: float,
        years: float,
        contributions: float = 0.0,
        compounding: str = "annually",
        contribution_frequency: Optional[str] = None,
        contribution_timing: str = "end",  # "start" or "end"
        apply_tax: bool = False,
        tax_rate: float = 0.0,
    ) -> None:
        
        """
        Initialize a CompoundInterest calculator.

        Required Parameters:
            init_value (float): Initial investment amount.
            rate (float): Annual interest rate (e.g., 0.05 for 5%).
            years (float): Investment duration in years.
            compounding (str): Frequency of interest compounding (e.g., 'monthly', 'annually').

        Optional Parameters:
            contributions (float): Amount contributed at each interval. Defaults to 0.0.
            contribution_frequency (str): Frequency of contributions. Defaults to same as compounding.
            contribution_timing (str): 'start' or 'end' of period. Defaults to 'end'.
            apply_tax (bool): Whether to apply tax on interest. Defaults to False.
            tax_rate (float): Tax rate applied to interest (if enabled). Defaults to 0.0.
        """

        # Type and value checks
        if not isinstance(init_value, (int, float)) or init_value < 0:
            raise ValueError("init_value must be a non-negative number.")
        if not isinstance(rate, (int, float)) or rate < 0:
            raise ValueError("rate must be a non-negative number.")
        if not isinstance(years, (int, float)) or years <= 0:
            raise ValueError("years must be a positive number.")
        if not isinstance(contributions, (int, float)) or contributions < 0:
            raise ValueError("contributions must be a non-negative number.")
        if not isinstance(tax_rate, (int, float)) or not 0 <= tax_rate <= 1:
            raise ValueError("tax_rate must be between 0 and 1.")
        if not isinstance(apply_tax, bool):
            raise TypeError("apply_tax must be a boolean.")
        if not isinstance(compounding, str):
            raise TypeError("compounding must be a string.")
        if not isinstance(contribution_frequency, (str, type(None))):
            raise TypeError("contribution_frequency must be a string or None.")
        if not isinstance(contribution_timing, str):
            raise TypeError("contribution_timing must be a string.")

        # Normalize string inputs
        compounding = compounding.strip().lower()
        contribution_frequency = (contribution_frequency or compounding).strip().lower()
        contribution_timing = contribution_timing.strip().lower()

        if contribution_timing not in {"start", "end"}:
            raise ValueError("contribution_timing must be either 'start' or 'end'.")
        if compounding not in FREQ_MAP:
            raise ValueError(f"Invalid compounding frequency: '{compounding}'")
        if contribution_frequency not in FREQ_MAP:
            raise ValueError(f"Invalid contribution frequency: '{contribution_frequency}'")

        self.init_value = init_value
        self.rate = rate
        self.years = years
        self.contributions = contributions
        self.compounding = compounding
        self.contribution_frequency = contribution_frequency
        self.contribution_timing = contribution_timing
        self.apply_tax = apply_tax
        self.tax_rate = tax_rate

        self.compound_periods = FREQ_MAP[compounding]
        self.contrib_periods = FREQ_MAP[contribution_frequency]


    def __repr__(self) -> str:
        """
        Returns a precise string representation of the object for debugging and development.
        """

        return (
            f"CompoundInterest("
            f"init_value={self.init_value}, "
            f"rate={self.rate}, "
            f"years={self.years}, "
            f"contributions={self.contributions}, "
            f"compounding='{self.compounding}', "
            f"contribution_frequency='{self.contribution_frequency}', "
            f"contribution_timing='{self.contribution_timing}', "
            f"apply_tax={self.apply_tax}, "
            f"tax_rate={self.tax_rate})"
        )
    

    def __str__(self) -> str:
        """
        Returns a user-friendly summary of the compound interest scenario.
        """

        tax_info = f"{self.tax_rate * 100:.1f}%" if self.apply_tax else "No tax"
        return (
            f"📊 Compound Interest Summary\n"
            f"------------------------------\n"
            f"Initial Value:         ${self.init_value:,.2f}\n"
            f"Annual Rate:           {self.rate * 100:.2f}%\n"
            f"Years:                 {self.years}\n"
            f"Contribution:          ${self.contributions:,.2f} ({self.contribution_frequency}, {self.contribution_timing})\n"
            f"Compounding:           {self.compounding.capitalize()}\n"
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



    def future_value(self) -> float:
        """
        Calculates the future value of the investment.

        Returns:
            float: Final balance after the specified number of years.
        """

        total_periods = int(self.years * self.compound_periods)
        period_rate = self.rate / self.compound_periods
        balance = self.init_value

        for period in range(1, total_periods + 1):
            # Add contributions before interest
            if self.contribution_timing == "start":
                if (period * self.contrib_periods) % self.compound_periods == 0:
                    balance += self.contributions

            # Apply interest
            interest = balance * period_rate
            if self.apply_tax:
                interest *= (1 - self.tax_rate)
            balance += interest

            # Add contributions after interest
            if self.contribution_timing == "end":
                if (period * self.contrib_periods) % self.compound_periods == 0:
                    balance += self.contributions

        return balance
    

    def breakdown(self) -> pd.DataFrame:
        """
        Returns a detailed breakdown of each period as a Pandas DataFrame.

        Columns:
            Label, Period, Starting Balance, Contribution, Interest, Tax Paid, Ending Balance
        """

        total_periods = int(self.years * self.compound_periods)
        period_rate = self.rate / self.compound_periods
        balance = self.init_value

        label_base = LABEL_MAP.get(self.compounding, "Period")

        data: List[Dict[str, float]] = []

        for period in range(1, total_periods + 1):
            starting_balance = balance
            contribution = 0.0
            tax_paid = 0.0

            # Contribution before interest
            if self.contribution_timing == "start":
                if (period * self.contrib_periods) % self.compound_periods == 0:
                    balance += self.contributions
                    contribution = self.contributions

            # Interest calculation
            gross_interest = balance * period_rate
            net_interest = gross_interest
            if self.apply_tax:
                tax_paid = gross_interest * self.tax_rate
                net_interest = gross_interest - tax_paid

            balance += net_interest

            # Contribution after interest
            if self.contribution_timing == "end":
                if (period * self.contrib_periods) % self.compound_periods == 0:
                    balance += self.contributions
                    contribution = self.contributions

            data.append({
                "Label": label_base,
                "Period": period,
                "Starting Balance": round(starting_balance, 2),
                "Contribution": round(contribution, 2),
                "Interest": round(net_interest, 2),
                "Tax Paid": round(tax_paid, 2),
                "Ending Balance": round(balance, 2),
            })

        return pd.DataFrame(data)
    

    def total_contributions(self) -> float:
        """
        Returns the total amount contributed over the investment period.
        """

        total = self.contributions * self.years * self.contrib_periods
        return round(total, 2)


    def total_interest_earned(self) -> float:
        """
        Returns the total net interest earned over the investment period.
        """

        final_value = self.future_value()
        total_contrib = self.total_contributions()
        net_interest = final_value - self.init_value - total_contrib
        return round(net_interest, 2)
    

    def total_tax_paid(self) -> float:
        """
        Returns the total tax paid on interest over the investment period.
        """

        if not self.apply_tax:
            return 0.0
        df = self.breakdown()
        return round(df["Tax Paid"].sum(), 2)


    def goal_year(self, target_amount: float) -> Optional[float]:
        """
        Estimates how many years are needed to reach a target amount.

        Returns None if the goal cannot be reached.
        """

        total_periods = int(self.years * self.compound_periods)
        period_rate = self.rate / self.compound_periods
        balance = self.init_value

        for period in range(1, total_periods + 1):
            if self.contribution_timing == "start":
                if (period * self.contrib_periods) % self.compound_periods == 0:
                    balance += self.contributions

            interest = balance * period_rate
            if self.apply_tax:
                interest *= (1 - self.tax_rate)
            balance += interest

            if self.contribution_timing == "end":
                if (period * self.contrib_periods) % self.compound_periods == 0:
                    balance += self.contributions

            if balance >= target_amount:
                return round(period / self.compound_periods, 2)

        return None
    

    def adjust_for_inflation(self, inflation_rate: float) -> float:
        """
        Returns the future value adjusted for a given annual inflation rate.

        Parameters:
            inflation_rate (float): Annual inflation rate (e.g., 0.02 for 2%)

        Returns:
            float: Future value in today's money.
        """
        
        if not isinstance(inflation_rate, (int, float)) or not (0 <= inflation_rate <= 1):
            raise ValueError("Inflation rate must be a float between 0 and 1.")

        nominal_fv = self.future_value()
        real_fv = nominal_fv / ((1 + inflation_rate) ** self.years)
        return round(real_fv, 2)
    

    def export_breakdown_to_csv(self, filename: str = "py-cic_breakdown.csv") -> None:
        """
        Export the period-by-period breakdown to a CSV file.

        Parameters:
            filename (str): Name of the CSV file to save (e.g., 'output.csv').
                            Must end with '.csv' and not contain any directory path.

        Raises:
            TypeError: If the filename is not a string.
            ValueError: If the filename is not a '.csv' file or contains directories.
        """

        validate_filename(filename, ".csv")
        df = self.breakdown()
        df.to_csv(filename, index=False)


    def export_breakdown_to_excel(self, filename: str = "py-cic_breakdown.xlsx") -> None:
        """
        Export the period-by-period breakdown to an Excel (.xlsx) file.

        Parameters:
            filename (str): Name of the Excel file to save (e.g., 'output.xlsx').
                            Must end with '.xlsx' and not contain any directory path.

        Raises:
            TypeError: If the filename is not a string.
            ValueError: If the filename is not a '.xlsx' file or contains directories.
        """

        validate_filename(filename, ".xlsx")
        df = self.breakdown()
        df.to_excel(filename, index=False)