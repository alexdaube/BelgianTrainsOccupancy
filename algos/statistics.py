import agate


def percent_occupancy_for_column(table, column, column_type):
    total = table.aggregate(agate.Count(column, column_type))
    high_count = table.where(lambda row: column_type == row[column]).aggregate(agate.Count('occupancy', "HIGH"))
    medium_count = table.where(lambda row: column_type == row[column]).aggregate(agate.Count('occupancy', "MEDIUM"))
    low_count = table.where(lambda row: column_type == row[column]).aggregate(agate.Count('occupancy', "LOW"))
    print("\tCount => Low: {0}, Medium: {1}, High: {2}".format(low_count, medium_count, high_count))
    print("\tPercentage => Low: {0}, Medium: {1}, High: {2}".format(round((low_count / total) * 100, 2),
                                                                    round((medium_count / total) * 100, 2),
                                                                    round((high_count / total) * 100, 2)))
    print("\tTotal {0} of {1} : {2}\n".format(column_type, column, total))

# Brussels long: 4.276428 to 4.449463 lat: 50.862690 to 50.786350
# Antwerp long: 4.507141 to 4.290161 lat: 51.173693 to 51.290640
# Ghent long: 3.69072 to 3.766251 lat: 51.002832 to 51.103832
# Charleroi long: 4.434013 to 4.457359 lat: 50.418660 to 50.403524
# Liège long: 5.557022 to 5.596504 lat: 50.581055 to 50.647440
# Bruges long: 3.212128 to 3.24337 lat: 51.195129 to 51.223843
# Namur long: 4.848919 to 4.878101 lat: 50.461298 to 50.470258
# Leuven long: 4.681377 to 4.716396 lat: 50.890551 to 50.867048
# Mons long: 3.961773 to 3.9382, 55 lat: 50.445013 to 50.461189
# Aalst long: 4.015331 to 4.054985 lat: 50.927354 to 50.949854
# Lille long: 3.028107 to 3.08527 lat: 50.615894 to 50.651607

