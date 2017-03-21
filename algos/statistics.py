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
