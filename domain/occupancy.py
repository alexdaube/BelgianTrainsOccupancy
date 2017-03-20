from enum import Enum
from datetime import datetime, timedelta
from dateutil import parser
from domain.vehicle import Vehicle
from utils.uri_utils import strip_uri_last_element


class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class OccupancyLevel(Enum):
    UNDEFINED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def assign_level_from_uri(uri):
        if "low" in uri:
            return OccupancyLevel.LOW
        elif "medium" in uri:
            return OccupancyLevel.MEDIUM
        elif "high" in uri:
            return OccupancyLevel.HIGH
        else:
            return OccupancyLevel.UNDEFINED


class Occupancy:
    def __init__(self, occupancy_data, stations):  # , stations_data):
        self.date = self.string_to_date(occupancy_data['querytime'])
        self.weekday = self.date.weekday()
        # self.connections = self.validate_post_data_field(occupancy_data, 'connection')
        self.entering_station = self.assign_station(self.validate_post_data_field(occupancy_data, 'from'), stations)
        self.exiting_station = self.assign_station(self.validate_post_data_field(occupancy_data, 'to'), stations)
        self.vehicle = Vehicle(self.validate_post_data_field(occupancy_data, 'vehicle'))
        self.occupancy_level = OccupancyLevel.assign_level_from_uri(
            self.validate_post_data_field(occupancy_data, 'occupancy'))
        self.unique_key = self.compose_unique_key()

    def validate_post_data_field(self, occupancy_data, field):
        return occupancy_data['post'][field] if field in occupancy_data['post'] else None

    def assign_station(self, station_uri, stations):
        if station_uri is not None:
            station_id = strip_uri_last_element(station_uri)
            return stations[station_id] if len(station_id) > 8 else None
        return station_uri

    def ceil_to_quarter(self, date):
        return date + (datetime.min - date) % timedelta(minutes=15)

    def string_to_date(self, datestr):
        if datestr is not None:
            # Rounding up for now
            return self.ceil_to_quarter(parser.parse(datestr).replace(tzinfo=None))
        return None

    def compose_unique_key(self):
        entering_station = "None" if self.entering_station is None else self.entering_station.number
        return self.date.strftime("%Y%m%d%H%M%S") + entering_station + self.vehicle.number

    def print_data(self):
        entering_station = self.entering_station if self.entering_station is None else self.entering_station.number
        exiting_station = self.exiting_station if self.exiting_station is None else self.exiting_station.number
        occupancy_level = self.occupancy_level if self.occupancy_level is None else OccupancyLevel(
            self.occupancy_level).name
        print(
            "Date: {0} WeekDay: {1} From: {2} To: {3} Vehicle: {4} Vehicle Type: {5} Occupancy: {6}".format(
                self.date, Weekday(self.weekday).name, entering_station, exiting_station,
                self.vehicle.number, self.vehicle.type.name, occupancy_level))

    def to_dict(self):
        entering_station = self.entering_station if self.entering_station is None else self.entering_station.number
        exiting_station = self.exiting_station if self.exiting_station is None else self.exiting_station.number
        occupancy_level = self.occupancy_level if self.occupancy_level is None else OccupancyLevel(
            self.occupancy_level).name

        return {"Date": self.date, "WeekDay": Weekday(self.weekday).name,
                "From": entering_station, "To": exiting_station, "Vehicle": self.vehicle.number,
                "Vehicle Type": self.vehicle.type.name, "Occupancy": occupancy_level}
