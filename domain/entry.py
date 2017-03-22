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

        self.in_morning_rushhour, self.in_evening_rushhour = self.evaluate_time()

        # self.exiting_station = str(occupancy_data['from'])
        # self.entering_station = str(occupancy_data['to'])

        self.entering_station = self.assign_station((occupancy_data['from']), stations)
        self.exiting_station = self.assign_station((occupancy_data['to']), stations)

        self.vehicle = Vehicle(occupancy_data['vehicle'])

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

        # DAY PERIOD : 0 -> early morning, 1 -> morning rush, 2 ->between, 3 -> evening_rush, 4 -> late_night

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
        return [self.datetime_object, Weekday(self.weekday).name, self.entering_station.number, self.exiting_station.number,
                self.entering_station.in_city,self.exiting_station.in_city,
                self.in_morning_rushhour, self.in_evening_rushhour,
                self.vehicle.number,
                self.vehicle.type.name]
