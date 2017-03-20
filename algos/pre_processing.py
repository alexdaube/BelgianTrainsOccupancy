from itertools import groupby, filterfalse
from operator import attrgetter
from domain.occupancy import OccupancyLevel
from domain.vehicle import VehicleType


def record_is_erroneous(occupancy):
    return (occupancy.vehicle.type == VehicleType.UNDEFINED
            or occupancy.entering_station is None or occupancy.exiting_station is None
            or occupancy.occupancy_level == OccupancyLevel.UNDEFINED)


def occupancy_level_average(occupancies, ):
    total = sum(occupancy.occupancy_level.value for occupancy in occupancies)
    return OccupancyLevel(round(total / len(occupancies)))


def filter_erroneous(occupancies):
    occupancies[:] = filterfalse(lambda o: record_is_erroneous(o), occupancies)
    return occupancies


def filter_duplicates(occupancies):
    tmp_occupancies = []
    for key, items in groupby(occupancies, key=attrgetter("unique_key")):
        occupancies_list = list(items)

        if len(occupancies_list) > 1:
            occupancies_list[0].occupancy_level = occupancy_level_average(occupancies_list)

        tmp_occupancies.append(occupancies_list[0])

    return tmp_occupancies


def removeDate(row):
    data = row['date']
    print(data)
