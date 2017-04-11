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
        self.in_morning_rushhour, self.in_evening_rushhour = self.evaluate_time(self.date)
        # self.connections = self.validate_post_data_field(occupancy_data, 'connection')
        self.entering_station = self.assign_station(self.validate_post_data_field(occupancy_data, 'from'), stations)
        self.exiting_station = self.assign_station(self.validate_post_data_field(occupancy_data, 'to'), stations)
        self.vehicle = Vehicle(self.validate_post_data_field(occupancy_data, 'vehicle'))
        self.day_zone = self.evaluate_day_period()
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
        existing_station = "None" if self.exiting_station is None else self.exiting_station.number
        return self.date.strftime("%Y%m%d%H%M%S") + entering_station + existing_station + self.vehicle.number

    def evaluate_time(self, date):
        morning_rushhour_start = 6
        morning_rushhour_end = 9
        evening_rushhour_start = 15
        evening_rushhour_end = 19

        in_morning_rushhour = 0
        in_evening_rushhour = 0

        if morning_rushhour_start <= date.hour <= morning_rushhour_end:
            in_morning_rushhour = 1
        elif evening_rushhour_start <= date.hour <= evening_rushhour_end:
            in_evening_rushhour = 1

        return in_morning_rushhour, in_evening_rushhour

    def evaluate_day_period(self):
        # DAY PERIOD :
        # 0 -> early morning,
        # 1 -> morning rushour
        # 2 -> mid day hours,
        # 3 -> afternoon rush
        # 4 -> late night

        day_period = 0
        if 2 <= self.date.hour < 6:
            day_period = 0
        elif 6 <= self.date.hour < 10:
            day_period = 1
        elif 10 <= self.date.hour < 15:
            day_period = 2
        elif 15 <= self.date.hour < 19:
            day_period = 3
        elif 19 <= self.date.hour <= 24 or 0 <= self.date.hour < 2:
            day_period = 4

        return day_period

    def print_data(self):
        entering_station = self.entering_station if self.entering_station is None else self.entering_station.number
        exiting_station = self.exiting_station if self.exiting_station is None else self.exiting_station.number
        occupancy_level = self.occupancy_level if self.occupancy_level is None else OccupancyLevel(
            self.occupancy_level).name
        print(
            "Date: {0} WeekDay: {1} From: {2} From in city?: {3} To: {4} To in city?: {5} Vehicle: {6} Vehicle Type: {7} Occupancy: {8}".format(
                self.date, Weekday(self.weekday).name, entering_station, self.entering_station.in_city, exiting_station,
                self.exiting_station.in_city, self.vehicle.number, self.vehicle.type.name, occupancy_level))

    def to_detailed_list(self):
        entering_station = self.entering_station if self.entering_station is None else self.entering_station.number
        exiting_station = self.exiting_station if self.exiting_station is None else self.exiting_station.number
        occupancy_level = self.occupancy_level if self.occupancy_level is None else OccupancyLevel(
            self.occupancy_level).name

        fake_date = datetime(1999, 1, 1, self.date.hour, self.date.minute, 0, 0)

        if self.date.hour < 10:
            hours = "0" + str(self.date.hour)
        else:
            hours = str(self.date.hour)

        seconds_since_midnight = (fake_date - fake_date.replace(hour=0, minute=0, second=0,
                                                                microsecond=0)).total_seconds() / 3600

        return [seconds_since_midnight, hours, Weekday(self.weekday).value,
                entering_station, self.entering_station.in_city, exiting_station, self.exiting_station.in_city,
                self.in_morning_rushhour, self.in_evening_rushhour,
                self.vehicle.type.value, occupancy_level]

    def to_numerical_attribute_list(self):
        occupancy_level = self.occupancy_level if self.occupancy_level is None else OccupancyLevel(
            self.occupancy_level).name

        fake_date = datetime(1999, 1, 1, self.date.hour, self.date.minute, 0, 0)

        hours = (fake_date - fake_date.replace(hour=0, minute=0, second=0,
                                               microsecond=0)).total_seconds() / 3600

        return [hours, self.day_zone, Weekday(self.weekday).name,
                self.entering_station.in_city, self.exiting_station.in_city,
                self.vehicle.type.value, occupancy_level]
