class City:
    def __init__(self, name, min_latitude, max_latitude, min_longitude, max_longitude):
        self.name = name
        self.min_latitude = min_latitude
        self.max_latitude = max_latitude
        self.min_longitude = min_longitude
        self.max_longitude = max_longitude

    def station_in_city(self, station):
        if (self.min_longitude <= station.longitude <= self.max_longitude) and (
                        self.min_latitude <= station.latitude <= self.max_latitude):
            return True
        return False
