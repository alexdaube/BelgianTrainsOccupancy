from enum import Enum
from utils.uri_utils import strip_uri_last_element


class VehicleType(Enum):
    UNDEFINED = 0
    IC = 1
    L = 2
    P = 3
    S = 4
    THA = 5

    def assign_vehicle_type(vehicle_number):
        if "IC" in vehicle_number[:3]:
            return VehicleType.IC
        elif "L" in vehicle_number[:3]:
            return VehicleType.L
        elif "P" in vehicle_number[:3]:
            return VehicleType.P
        elif "S" in vehicle_number[:3]:
            return VehicleType.S
        elif "THA" in vehicle_number[:3]:
            return VehicleType.THA
        else:
            return VehicleType.UNDEFINED


class Vehicle:
    API_BASE_VEHICLE_URL = "http://irail.be/vehicle/"

    def __init__(self, uri):
        self.number = strip_uri_last_element(uri)
        self.type = VehicleType.assign_vehicle_type(self.number)
