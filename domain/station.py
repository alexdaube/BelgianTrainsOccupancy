from utils.uri_utils import strip_uri_last_element


class Station:
    API_BASE_STATION_URL = "http://irail.be/stations/NMBS/"

    def __init__(self, stations_data, cities):
        self.number = int(strip_uri_last_element(stations_data[0]))
        self.name = stations_data[1]
        self.longitude = float(stations_data[7])
        self.latitude = float(stations_data[8])
        self.in_city = self.is_in_city(cities)

    def is_in_city(self, cities):
        for city in cities:
            in_city = city.station_in_city(self)
            if in_city:
                return 1
        return 0

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.number == other.number
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
