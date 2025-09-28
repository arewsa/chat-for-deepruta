import enum
import re
from typing import Annotated, Optional, Self

from pydantic import BaseModel, NonNegativeInt, StringConstraints, model_validator

SECONDS_IN_HOUR = 60 * 60
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR

# format: [D.]HH:MM-[D.]HH:MM
# D - optional non-negative int
# HH - 00-23 (leading zero optional)
# MM - 00-59 (leading zero optional)
HOURS_PATTERN = r"(?:[0-9]|[01][0-9]|2[0-3])"
MINUTES_PATTERN = r"[0-5][0-9]"
DAYS_PREFIX_PATTERN = r"(?:\d+\.)?"
TIME_PATTERN = f"{DAYS_PREFIX_PATTERN}{HOURS_PATTERN}:{MINUTES_PATTERN}"
TIME_PATTERN_WITH_GROUPS = f"(?:(?P<days>\\d+)\\.)?(?:(?P<hours>{HOURS_PATTERN})):(?P<minutes>{MINUTES_PATTERN})"
TIME_WINDOW_PATTERN = f"^\\s*{TIME_PATTERN}\\s*-\\s*{TIME_PATTERN}\\s*$"

TimeWindowString = Annotated[
    str,
    StringConstraints(pattern=TIME_WINDOW_PATTERN),
]


class TimeWindowViolationType(str, enum.Enum):
    EARLY = "EARLY"
    LATE = "LATE"


class TimeWindowViolation(BaseModel):
    violation_s: NonNegativeInt
    violation_type: TimeWindowViolationType


class TimeWindow(BaseModel):
    start: NonNegativeInt
    end: NonNegativeInt

    @model_validator(mode="after")
    def check_start_before_end(self) -> Self:
        if self.start > self.end:
            raise ValueError(f"start={self.start} must be before end={self.end}")
        return self

    def __lt__(self, other: "TimeWindow") -> bool:
        return self.start < other.start

    def to_string(self, format_with_superscript: bool = False) -> str:
        start_d = self.start // SECONDS_IN_DAY
        start_h = (self.start % SECONDS_IN_DAY) // SECONDS_IN_HOUR
        start_m = (self.start % SECONDS_IN_HOUR) // 60
        end_d = self.end // SECONDS_IN_DAY
        end_h = (self.end % SECONDS_IN_DAY) // SECONDS_IN_HOUR
        end_m = (self.end % SECONDS_IN_HOUR) // 60
        start_part = f"{start_d}.{start_h:02d}:{start_m:02d}" if start_d else f"{start_h:02d}:{start_m:02d}"
        end_part = f"{end_d}.{end_h:02d}:{end_m:02d}" if end_d else f"{end_h:02d}:{end_m:02d}"
        tw_str = f"{start_part}-{end_part}"
        return self._format(tw_str) if format_with_superscript else tw_str

    def _format(self, time_window_string: str) -> str:
        # Format: [D].HH:MM-[D].HH:MM -> HH:MMᐩᴰ-HH:MMᐩᴰ
        if not time_window_string:
            return ""

        parts = time_window_string.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid time window format: {time_window_string}. Expected format: [D.]HH:MM-HH:MM")

        start = parts[0]
        end = parts[1]

        return f"{self._format_time(start)}-{self._format_time(end)}"

    def _format_time(self, time_string: str) -> str:
        superscript_map = {
            "0": "⁰",
            "1": "¹",
            "2": "²",
            "3": "³",
            "4": "⁴",
            "5": "⁵",
            "6": "⁶",
            "7": "⁷",
            "8": "⁸",
            "9": "⁹",
        }

        if "." in time_string:
            day, time = time_string.split(".")
            superscript_day = "".join(superscript_map[d] for d in str(day))
            return f"{time}ᐩ{superscript_day}"
        return time_string

    @staticmethod
    def from_string(time_window_string: TimeWindowString) -> "TimeWindow":
        times = time_window_string.strip().split("-")
        if len(times) != 2:
            raise ValueError(f"Invalid time window format: {time_window_string}. Expected format: [D.]HH:MM-HH:MM")

        match1 = re.match(TIME_PATTERN_WITH_GROUPS, times[0].strip())
        match2 = re.match(TIME_PATTERN_WITH_GROUPS, times[1].strip())

        if not match1 or not match2:
            raise ValueError(f"Invalid time window format: {time_window_string}. Expected format: [D.]HH:MM-HH:MM")

        start_time = (
            int(match1.group("days") or 0) * SECONDS_IN_DAY
            + int(match1.group("hours")) * SECONDS_IN_HOUR
            + int(match1.group("minutes")) * 60
        )
        end_time = (
            int(match2.group("days") or 0) * SECONDS_IN_DAY
            + int(match2.group("hours")) * SECONDS_IN_HOUR
            + int(match2.group("minutes")) * 60
        )

        return TimeWindow(start=start_time, end=end_time)


class TimeWindowList(BaseModel):
    time_windows: list[TimeWindow]

    @model_validator(mode="after")
    def check_time_windows_sorted(self) -> Self:
        if any(self.time_windows[i] > self.time_windows[i + 1] for i in range(len(self.time_windows) - 1)):
            raise ValueError("Time windows must be sorted in ascending order")
        return self

    def __len__(self) -> int:
        return len(self.time_windows)

    def get_time_window_by_time(self, time_s: int) -> Optional[TimeWindow]:
        for time_window in self.time_windows:
            if time_window.start <= time_s <= time_window.end:
                return time_window

        return None

    @staticmethod
    def from_list_of_strings(time_window_strings: list[TimeWindowString]) -> "TimeWindowList":
        unsorted_windows = [TimeWindow.from_string(time_window_string) for time_window_string in time_window_strings]
        return TimeWindowList(time_windows=sorted(unsorted_windows))
