from pydantic import BaseModel, NonNegativeInt


class ViolationCost(BaseModel):
    """Cost of constraint violation. Can consist of fixed cost for fact of violation and per-minute costs"""

    # Cost for fact of violation
    fixed: NonNegativeInt = 0
    # Cost for each minute of violation. Per minute is used to keep it as integer
    per_minute: NonNegativeInt = 0
