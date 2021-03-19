
import math


def RemoveCurrentLaneOtherVehilces(vehicles):
    res = []
    res.append(vehicles[0])
    ego_y = vehicles[0].destination[1]
    for i in range(1, len(vehicles)):
        y = vehicles[i].destination[1]
        if abs(y-ego_y)<2:
            continue
        res.append(vehicles[i])
    vehicles[:] = res