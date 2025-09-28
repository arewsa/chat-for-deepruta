from typing import Annotated, Optional

from pydantic import BaseModel, NonNegativeInt, PositiveFloat, PositiveInt, StringConstraints
from pydantic_extra_types.color import Color

from models.cost import ViolationCost
from models.geo import RoutingMode
from models.time import TimeWindowString


class WorkerCosts(BaseModel):
    """Costs associated with a worker"""

    # Cost if a worker is used
    usage: NonNegativeInt = 1000
    # Cost for each km traveled. Km is used to keep it as integer and make it more readable for users
    per_km: NonNegativeInt = 10
    # Cost for each hour of work. Hour is used to keep it as integer and make it more readable for users
    per_hour: NonNegativeInt = 100
    # Cost for each completed job
    per_job: NonNegativeInt = 0


class WorkerSpecifications(BaseModel):
    """Specifications associated with a worker such as dimensions or motion speed"""

    length_m: Optional[PositiveFloat] = None
    width_m: Optional[PositiveFloat] = None
    height_m: Optional[PositiveFloat] = None

    routing_mode: Optional[RoutingMode] = RoutingMode.AUTO

    # Speeds of the worker. Km/h is used to keep it as integer and make it more readable for users
    max_transit_speed_kmh: Optional[PositiveInt] = None
    max_service_speed_kmh: Optional[PositiveInt] = None

    # If some workers are faster or slower than others, we can use this multiplier to adjust their transit duration
    transit_duration_multiplier: PositiveFloat = 1.0
    # If some workers are faster or slower than others, we can use this multiplier to adjust their service duration
    service_duration_multiplier: PositiveFloat = 1.0

    fuel_tank_capacity_ml: Optional[PositiveInt] = None
    initial_fuel_capacity_ml: Optional[PositiveInt] = None
    # ml / 100m is used since it is equivalent to l / 100km
    fuel_consumption_rate_ml_per_100m: Optional[PositiveFloat] = None

    reagent_tank_capacity_l: Optional[PositiveInt] = None
    initial_reagent_capacity_l: Optional[PositiveInt] = None

    # GPS tracker IMEI number
    imei: Optional[int] = None


class RecessPenalties(BaseModel):
    """Penalties for a recess"""

    # Fixed penalty for dropping the recess
    drop: NonNegativeInt = 1000000
    time_window: ViolationCost = ViolationCost()
    time_window_early: ViolationCost = ViolationCost()
    time_window_late: ViolationCost = ViolationCost()
    min_duration: ViolationCost = ViolationCost()
    max_duration: ViolationCost = ViolationCost()


class Recess(BaseModel):
    """Recess"""

    # Duration of recess
    duration_s: PositiveInt
    # Physical location of the recess. If not set, the recess will be performed at an arbitrary location
    recess_service_point_id: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Hard time window for the recess
    hard_time_window: Optional[TimeWindowString] = None
    # Time window for the recess
    time_window: Optional[TimeWindowString] = None
    # Minimal duration of uninterrupted work after which a recess should be taken
    min_work_duration_s: Optional[PositiveInt] = None
    # Hard limit on the minimum duration of uninterrupted work after which a recess should be taken
    hard_min_work_duration_s: Optional[PositiveInt] = None
    # Hard limit on the maximum duration of uninterrupted work after which a recess should be taken
    hard_max_work_duration_s: Optional[PositiveInt] = None
    # Maximum duration of uninterrupted work after which a recess should be taken
    max_work_duration_s: Optional[PositiveInt] = None
    
    # Penalties for the recess
    penalties: RecessPenalties = RecessPenalties()


class ShiftPenalties(BaseModel):
    """Penalties for a shift"""

    # Penalty for any shift time window violation
    time_window: ViolationCost = ViolationCost()
    # Penalty for early shift time window violation. Applies both to early start and early finish
    time_window_early: ViolationCost = ViolationCost()
    # Penalty for late shift time window violation. Applies both to late start and late finish
    time_window_late: ViolationCost = ViolationCost()
    # Penalty for exceeding the maximum duration of a shift
    max_duration: ViolationCost = ViolationCost()
    # Penalty for exceeding the maximum distance
    max_distance: ViolationCost = ViolationCost()
    # Penalty for exceeding the maximum number of jobs
    excessive_jobs: ViolationCost = ViolationCost()
    # Penalty for insufficient number of jobs
    insufficient_jobs: ViolationCost = ViolationCost()


class Shift(BaseModel):
    """Shift"""

    # Reference book template name is for cases when shift is defined in reference book and we need to take info from there
    template_name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Hard time window for the shift
    hard_time_window: Optional[TimeWindowString] = None
    # Time window for the shift
    time_window: Optional[TimeWindowString] = None
    # Shift end service duration for shift transitions such as change of a driver
    end_service_duration_s: Optional[PositiveInt] = None
    # Maximum duration of the shift without a penalty
    max_duration_s: Optional[PositiveInt] = None
    # Hard limit on the duration of the shift
    hard_max_duration_s: Optional[PositiveInt] = None
    # Maximum total distance that can be traveled in a shift without a penalty
    max_total_distance_m: Optional[PositiveFloat] = None
    # Minimum number of jobs that should be completed within a shift to avoid penalties
    min_jobs: Optional[NonNegativeInt] = None
    # Maximum number of jobs that can be completed within a shift to avoid penalties
    max_jobs: Optional[PositiveInt] = None
    # Maximum number of fuel refills that can be made during a shift to avoid penalties
    hard_max_fuel_refills: Optional[NonNegativeInt] = None
    # Maximum number of reagent refills that can be made during a shift to avoid penalties
    hard_max_reagent_refills: Optional[NonNegativeInt] = None
    # Balancing group id. If set, the shift will be balanced with other shifts in the same group
    balancing_group_id: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Penalties for the shift
    penalties: ShiftPenalties = ShiftPenalties()
    # Recesses
    recesses: list[Recess] = []


class Worker(BaseModel):
    # Worker id. Should be unique within a planning. The only required field. Basically it is required to identify
    # the number of available workers if all other fields are not set
    worker_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    # Reference book template name is for cases when worker is defined in reference book and we need to take info from there
    template_name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Name is for cases when we need to separate specific person from a vehicle
    # License plate can be used as name, for example
    name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Color of the worker. Can be used to track the same worker between plannings
    color: Optional[Color] = None
    # Starting and ending depot id. Can be overwritten by start_depot_id, end_depot_id
    depot_id: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Starting depot id. Can be overwritten by start_location
    start_depot_id: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Ending depot id. Can be overwritten by end_location
    end_depot_id: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # A worker might need to spend some additional time both at the start and end depots
    extra_depot_service_duration_s: Optional[NonNegativeInt] = None
    # A worker might need to spend some additional time at the start depot
    extra_start_depot_service_duration_s: Optional[NonNegativeInt] = None
    # A worker might need to spend some additional time at the end depot
    extra_end_depot_service_duration_s: Optional[NonNegativeInt] = None
    # A worker can start their work at a location different from depot_id or start_depot_id
    # If the start_depot_id is set, start_garage_id will override it
    start_garage_id: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # A worker can finish their work at a location different from depot_id or end_depot_id
    # If the end_depot_id is set, end_garage_id will override it
    end_garage_id: Optional[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = None
    # Shifts
    shifts: list[Shift] = []
    # List of tag names for the worker. Defines which jobs can be assigned to the worker or which jobs will add reward
    tags: list[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = []
    # List of excluded tag names for the worker. Defines which jobs will incur penalties
    excluded_tags: list[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = []
    # List of allowed zone names for the worker
    allowed_zones: list[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = []
    # List of forbidden zone names for the worker
    forbidden_zones: list[Annotated[str, StringConstraints(min_length=1, max_length=128)]] = []
    # Specifications of the worker
    specifications: WorkerSpecifications = WorkerSpecifications()
    # Cost of the worker
    costs: WorkerCosts = WorkerCosts()
