import enum

# Feature and Point are reimported in other schemas to keep geo objects in the same place
from geojson_pydantic import Feature, Point  # noqa: F401


class AddressType(str, enum.Enum):
    LOCATION = "LOCATION"
    STREET = "STREET"
    AREA = "AREA"


class RoutingMode(str, enum.Enum):
    AUTO = "AUTO"
    TRUCK = "TRUCK"
    PEDESTRIAN = "PEDESTRIAN"
    MULTIMODAL = "MULTIMODAL"
    TAXI = "TAXI"
    BICYCLE = "BICYCLE"
