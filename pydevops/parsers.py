from datetime import timedelta
import re

def parse_timedelta(time_str):
    # Define time unit mappings
    time_units = {
        'seconds': ['s', 'sec', 'second', 'seconds'],
        'minutes': ['m', 'min', 'minute', 'minutes'],
        'hours': ['h', 'hr', 'hour', 'hours'],
        'days': ['d', 'day', 'days'],
        'weeks': ['w', 'wk', 'week', 'weeks'],
        'months': ['mo', 'month', 'months'],  # Approximate months to 30 days
    }

    # Invert time_units mapping for reverse lookup
    unit_mapping = {alias: unit for unit, aliases in time_units.items() for alias in aliases}

    # Regular expression to extract value and unit
    regex = r'(\d+)\s*([a-zA-Z]+)'

    total_timedelta = timedelta()

    # Find all matches in the string
    for match in re.findall(regex, time_str):
        value, unit = match
        value = int(value)

        # Normalize unit to the standard name
        normalized_unit = unit_mapping.get(unit.lower())
        if not normalized_unit:
            raise ValueError(f"Unrecognized time unit: {unit}")

        # Add to total_timedelta based on unit
        if normalized_unit == 'seconds':
            total_timedelta += timedelta(seconds=value)
        elif normalized_unit == 'minutes':
            total_timedelta += timedelta(minutes=value)
        elif normalized_unit == 'hours':
            total_timedelta += timedelta(hours=value)
        elif normalized_unit == 'days':
            total_timedelta += timedelta(days=value)
        elif normalized_unit == 'weeks':
            total_timedelta += timedelta(weeks=value)
        elif normalized_unit == 'months':  # Approximate 1 month = 30 days
            total_timedelta += timedelta(days=value * 30)

    return total_timedelta

if __name__ == "__main__":
    # Examples
    examples = [
        "1h",
        "1h 2m",
        "1 hour",
        "3 days",
        "5 minutes 25 seconds",
        "2 weeks",
        "1 month",
        "2 months 3 days 4 hours 5 minutes"
    ]

    for example in examples:
        print(f"'{example}' -> {parse_to_timedelta(example)}")
