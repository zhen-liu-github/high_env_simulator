import math


class AverageMetric():
    def __init__(self, name):
        self.name = name
        self.sample_num = 0
        self.value_sum = 0

    def add(self, value, sample_num=None):
        if not sample_num:
            sample_num = len(value)
            value = sum(value)
        self.sample_num += sample_num
        self.value_sum += value

    def __str__(self):
        return '{}: average_value:{:.4f}, sample_num:{}'.format(
            self.name, self.value_sum / (self.sample_num + 1e-10),
            self.sample_num)


class MetricDict(dict):
    def __init__(self):
        super(MetricDict, self).__init__()
    # Restructure "__str__" and "__repr__" methods.
    def __str__(self):
        res = ''
        for key in self.keys():
            res += str(self[key])
            res += '\n'
        return res
    def __repr__(self):
        return self.__init__()

        
def RemoveCurrentLaneOtherVehilces(vehicles):
    res = []
    res.append(vehicles[0])
    ego_y = vehicles[0].destination[1]
    for i in range(1, len(vehicles)):
        y = vehicles[i].destination[1]
        if abs(y - ego_y) < 2:
            continue
        res.append(vehicles[i])
    vehicles[:] = res