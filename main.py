from pandas.io.json import json_normalize
import json
import csv
import dateutil.parser
from datetime import datetime, timedelta


class Occupancy:
    def __init__(self, occupancy_data):  # , stations_data):
        self.date = self.string_to_date(self.validate_data_field(occupancy_data, 'querytime'))
        self.isWeekday = "tuesday"
        self.connection = self.validate_data_field(occupancy_data, 'post.connection')
        self.entering_station = self.validate_data_field(occupancy_data, 'post.from')
        self.exiting_station = self.validate_data_field(occupancy_data, 'post.to')
        self.vehicle = self.validate_data_field(occupancy_data, 'post.vehicle')
        self.occupancy = self.validate_data_field(occupancy_data, 'post.occupancy"')

    def validate_data_field(self, occupancy_data, field):
        return occupancy_data[field].values[0] if field in occupancy_data.columns else None

    def ceil_to_quarter(self, date):
        return date + (datetime.min - date) % timedelta(minutes=15)

    def string_to_date(self, datestr):
        if datestr is not None:
            # Rounding up for now
            return self.ceil_to_quarter(dateutil.parser.parse(datestr).replace(tzinfo=None))
        return None


def main():
    # json_normalize(sample_object)

    # Open the occupancy data
    with open('occupancy-until-20161029.newlinedelimitedjsonobjects') as occupancy_data_file:
        lines = occupancy_data_file.readlines()
    occupancy_data = [json_normalize(json.loads(line)) for line in lines]

    # Flatten or Normalize the data
    # for obj in occupancy_data:
    #     json_normalize(obj)

    # Open the Station data
    with open('stations.csv') as stations_file:
        reader = csv.reader(stations_file)
        stations = [row for row in reader]

    print(stations[0])
    a = occupancy_data[0]["post.connection"].values[0]

    occupancies = [Occupancy(data) for data in occupancy_data]
    print(occupancies[1].date)

if __name__ == "__main__":
    main()
