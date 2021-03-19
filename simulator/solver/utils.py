from config import env_config


def kinematic(v, a):

    return


class LaneChangeWindow(object):
    car_length = 5

    def __init__(self, front_vehicle, rear_vehicle):
        '''
        Default car width: 2
        Default car length: 5
        '''
        self.front_vehicle = front_vehicle
        self.rear_vehicle = rear_vehicle
        self.front_s = front_vehicle[1] - car_length / 2
        self.rear_s = rear_vehicle[1] + car_length / 2

