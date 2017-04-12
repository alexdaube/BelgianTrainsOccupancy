def isWeekend(row):
    if row['weekday'] == 'SATURDAY' or row['weekday'] == 'SUNDAY':
        return True
    else:
        return False

def isMonday(row):
    return row['weekday'] == 'MONDAY'

def isSunday(row):
    return row['weekday'] == 'SUNDAY'

def isSaturday(row):
    return row['weekday'] == 'SATURDAY'

def isWednesday(row):
    return row['weekday'] == 'WEDNESDAY'

def isTuesday(row):
    return row['weekday'] == 'TUESDAY'


def isThursday(row):
    return row['weekday'] == 'THURSDAY'


def isFriday(row):
    return row['weekday'] == 'FRIDAY'

def isMorningRush(row):
    return row['in_morning_rush'] == 1


def isEveningRush(row):
    return row['in_evening_rush'] == 1


def isEarlyMorning(row):
    return row['day_period'] == 0


def isBeforeNoon(row):
    return row['day_period'] == 1


def isAfternoon(row):
    return row['day_period'] == 2


def isLateEvening(row):
    return row['day_period'] == 3


def isFromUrban(row):
    return row['from_urban'] == 1


def isGoingUrban(row):
    return row['to_urban'] == 1


def extractRushHourEntries(entries):
    morning_rushhour_start = 7
    morning_rushhour_end = 9
    evening_rushhour_start = 16
    evening_rushhour_end = 19

    entries_in_rushhour = entries.where(
        lambda row: morning_rushhour_start <= row['date'].hour <= morning_rushhour_end or evening_rushhour_start <= row[
            'date'].hour <= evening_rushhour_end)

    return entries_in_rushhour


def calculateRushHourConfidence(occupancies):
    entries_in_rushhour = extractRushHourEntries(occupancies)

    # Calculate % of HIGH level during rushhour period
    high_occ = occupancies.where(lambda row: 'HIGH' == row['occupancy'])
    high_entries_in_rushhour = extractRushHourEntries(high_occ)

    ratio_high_rushhour = len(high_entries_in_rushhour) / len(entries_in_rushhour)

    # Calculate % of MEDIUM level during rushhour period
    avg_occ = occupancies.where(lambda row: 'MEDIUM' == row['occupancy'])
    medium_entries_in_rushhour = extractRushHourEntries(avg_occ)

    ratio_medium_rushhour = len(medium_entries_in_rushhour) / len(entries_in_rushhour)

    # Calculate % of LOW level during rushhour period
    low_occ = occupancies.where(lambda row: 'LOW' == row['occupancy'])
    low_entries_in_rushhour = extractRushHourEntries(low_occ)

    ratio_low_rushhour = len(low_entries_in_rushhour) / len(entries_in_rushhour)

    print("CONFIDENCE")
    print(
        "RUSHHOUR --> LOW: {0} \nRUSHHOUR --> MEDIUM: {1} \nRUSHHOUR --> HIGH: {2} ".format(ratio_low_rushhour,
                                                                                            ratio_medium_rushhour,
                                                                                            ratio_high_rushhour))
    # Print graph of LOW occ / hour
    print("LOW OCCUPANCY")
    low_occ.bins('hour', 23, 0, 23).print_bars('hour', width=80)

    # Print graph of MEDIUM occ / hour
    print("MEDIUM OCCUPANCY")
    avg_occ.bins('hour', 23, 0, 23).print_bars('hour', width=80)

    # Print graph of HIGH occ / hour
    print("HIGH OCCUPANCY")
    high_occ.bins('hour', 23, 0, 23).print_bars('hour', width=80)
