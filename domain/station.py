from utils.uri_utils import strip_uri_last_element


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
