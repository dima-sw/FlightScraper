from datetime import datetime, timedelta
from enum import Enum

class Weekday(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

"""
    Generate a list of dates within a specified range.

    Parameters:
    - dayIn: Integer representing the starting day of the week (0 for Monday, 1 for Tuesday, ..., 6 for Sunday).
    - dayEnd: Integer representing the ending day of the week (0 for Monday, 1 for Tuesday, ..., 6 for Sunday).
    - weeks: Number of weeks for each iteration.
    - monthsRange: Number of months to generate dates for.
    - weeksStep: Step size between each week (default is 1).

    Returns:
    - List of dictionaries, each containing a start date and an end date in the format {"startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD"}.

    Example:
    dataGen(4, 6, 2, 6)  # Generates dates from Friday to Sunday for 6 months, with a step size of 1 week.
"""
def dataGen(dayIn, dayEnd, weeks, monthsRange, fromMonth, weeksStep=1):
    dates=[]
    # Get today's date
    today = datetime.now().date()

    today = today + timedelta(days=30*(fromMonth-today.month))
    end_date = today + timedelta(days=30*monthsRange)
    current_date = today   
    endStep= dayEnd-dayIn

    if endStep<0:
        endStep+=7

    while current_date <= end_date:
        start_date = current_date - timedelta(days=current_date.weekday() - dayIn)

        end_datet = start_date + timedelta(days=endStep*weeks)
        dates.append({"startDate": start_date.strftime("%Y-%m-%d"), "endDate": end_datet.strftime("%Y-%m-%d")})
        
        current_date = current_date + timedelta(days=7*weeksStep)
        

    return dates



print(dataGen(0,4,1,1,5))