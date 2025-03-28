import os

FREQ_MAP = {
    "annually": 1,
    "semiannually": 2,
    "quarterly": 4,
    "monthly": 12,
    "biweekly": 26,
    "weekly": 52,
    "daily": 365,
}


LABEL_MAP = {
    "annually": "Year",
    "semiannually": "Semester",
    "quarterly": "Quarter",
    "monthly": "Month",
    "biweekly": "Biweek",
    "weekly": "Week",
    "daily": "Day",
}

def validate_filename(filename: str, extension: str) -> None:
    """
    Validates that the given filename is a plain filename (not a path)
    and ends with the expected file extension.

    Parameters:
        filename (str): The filename to validate.
        extension (str): The expected file extension (e.g., '.csv', '.xlsx').

    Raises:
        TypeError: If the filename is not a string.
        ValueError: If the filename does not end with the specified extension
                    or includes any directory path.
    """
    
    if not isinstance(filename, str):
        raise TypeError("Filename must be a string.")
    if not filename.lower().endswith(extension):
        raise ValueError(f"Filename must end with '{extension}'")
    if os.path.dirname(filename):
        raise ValueError("Filename must not include a directory path.")