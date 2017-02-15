import json
import csv
import dateutil.parser
from enum import Enum
from itertools import filterfalse, groupby
from operator import attrgetter
from datetime import datetime, timedelta


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


def strip_uri_last_element(uri):
    return uri.split('/')[-1].strip()


def record_is_erroneous(occupancy):
    return (occupancy.vehicle.type == VehicleType.UNDEFINED
            or occupancy.entering_station is None or occupancy.exiting_station is None
            or occupancy.occupancy_level == OccupancyLevel.UNDEFINED)


def filter_duplicates(occupancies):
    tmp_occupancies = []
    for key, items in groupby(occupancies, key=attrgetter("unique_key")):
        occupancies_list = list(items)

        if len(occupancies_list) > 1:
            occupancies_list[0].occupancy_level = occupancy_level_average(occupancies_list)

        tmp_occupancies.append(occupancies_list[0])

    return tmp_occupancies


def occupancy_level_average(occupancies, ):
    total = sum(occupancy.occupancy_level.value for occupancy in occupancies)
    return OccupancyLevel(round(total / len(occupancies)))


class Station:
    API_BASE_STATION_URL = "http://irail.be/stations/NMBS/"

    def __init__(self, stations_data):
        self.number = strip_uri_last_element(stations_data[0])
        self.name = stations_data[1]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.number == other.number
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Vehicle:
    API_BASE_VEHICLE_URL = "http://irail.be/vehicle/"

    def __init__(self, uri):
        self.number = strip_uri_last_element(uri)
        self.type = VehicleType.assign_vehicle_type(self.number)


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
            return self.ceil_to_quarter(dateutil.parser.parse(datestr).replace(tzinfo=None))
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


def main():
    # Open the occupancy data
    with open('occupancy-until-20161029.newlinedelimitedjsonobjects') as occupancy_data_file:
        lines = occupancy_data_file.readlines()
        occupancies_data = [json.loads(line) for line in lines]

    # Open the Station data
    with open('stations.csv') as stations_file:
        reader = csv.reader(stations_file)
        stations_data = [row for row in reader]

    stations = {station.number: station for station in
                [Station(station_data) for station_data in stations_data[1:]]}
    occupancies = [Occupancy(occupancy_data, stations) for occupancy_data in occupancies_data]

    occupancies[:] = filterfalse(lambda o: record_is_erroneous(o), occupancies)

    occupancies = filter_duplicates(occupancies)

    for occupancy in occupancies:
        occupancy.print_data()
    print("Number of records after merging duplicates: ", len(occupancies))


if __name__ == "__main__":
    main()
