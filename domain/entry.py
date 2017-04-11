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


class Entry:
    def __init__(self, occupancy_data, stations):  # , stations_data):

        self.date = occupancy_data['date']

        self.time = occupancy_data['time']

        string_date = str(self.date.day) + " " + str(self.date.month) + " " + str(self.date.year) + " " + self.time

        self.datetime_object = datetime.strptime(string_date, '%d %m %Y %I:%M:%S %p')

        self.weekday = self.date.weekday()
        self.in_morning_rush, self.in_evening_rush = self.evaluate_time()
        self.day_zone = self.evaluate_day_period()

        # self.exiting_station = str(occupancy_data['from'])
        # self.entering_station = str(occupancy_data['to'])

        self.entering_station = self.assign_station((occupancy_data['from']), stations)
        self.exiting_station = self.assign_station((occupancy_data['to']), stations)

        self.vehicle = Vehicle(occupancy_data['vehicle'])

    def evaluate_day_period(self):
        # DAY PERIOD :
        # 0 -> early morning,
        # 1 -> morning rushour
        # 2 -> mid day hours,
        # 3 -> afternoon rush
        # 4 -> late night

        day_period = 0
        if 2 <= self.datetime_object.hour < 6:
            day_period = 0
        elif 6 <= self.datetime_object.hour < 10:
            day_period = 1
        elif 10 <= self.datetime_object.hour < 15:
            day_period = 2
        elif 15 <= self.datetime_object.hour < 19:
            day_period = 3
        elif 19 <= self.datetime_object.hour <= 24 or 0 <= self.datetime_object.hour < 2:
            day_period = 4

        return day_period

    def assign_station(self, station_uri, stations):
        if station_uri is not None:
            station_id = int(station_uri)
            return stations[station_id] if len(str(station_id)) > 6 else None
        return station_uri

    def evaluate_time(self):
        morning_rushhour_start = 7
        morning_rushhour_end = 9
        evening_rushhour_start = 16
        evening_rushhour_end = 19

        in_morning_rush = 0
        in_evening_rush = 0

        if morning_rushhour_start <= self.datetime_object.hour <= morning_rushhour_end:
            in_morning_rush = 1
        elif evening_rushhour_start <= self.datetime_object.hour <= evening_rushhour_end:
            in_evening_rush = 1

        return in_morning_rush, in_evening_rush

    def ceil_to_quarter(self, date):
        return date + (datetime.min - date) % timedelta(minutes=15)

    def string_to_date(self, datestr):
        if datestr is not None:
            # Rounding up for now
            return self.ceil_to_quarter(parser.parse(datestr).replace(tzinfo=None))
        return None

    def to_list(self):
        return [self.datetime_object, Weekday(self.weekday).name, self.entering_station.number,
                self.exiting_station.number,
                self.entering_station.in_city, self.exiting_station.in_city,
                self.day_zone,
                self.in_morning_rush, self.in_evening_rush,
                self.vehicle.number,
                self.vehicle.type.name]

    def to_attribute_list(self):
        hours = (self.datetime_object - self.datetime_object.replace(hour=0, minute=0, second=0,
                                                                     microsecond=0)).total_seconds() / 3600
        isWeekday = 0
        if Weekday(self.weekday).value < 5:
            isWeekday = 1

        return [hours, self.day_zone, Weekday(self.weekday).value,
                self.entering_station.in_city, self.exiting_station.in_city,
                self.vehicle.type.value]
