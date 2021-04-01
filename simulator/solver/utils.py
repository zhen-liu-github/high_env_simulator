from ..config import env_config


def kinematic(v, a):

    return


def GetVehicleX(vehicle) -> float:
    return vehicle.position[0]


def GetVehicleY(vehicle) -> float:
    return vehicle.position[1]


def GetVelocityX(vehicle) -> float:
    return vehicle.velocity[0]


def GetVelocityY(vehicle) -> float:
    return vehicle.velocity[1]


class LaneChangeWindow(object):
    def __init__(self, front_vehicle, rear_vehicle):
        '''
        Default car width: 2
        Default car length: 5
        '''
        self.car_length = 5
        self.front_vehicle = front_vehicle
        self.front_is_valid = True if front_vehicle is not None else False
        self.rear_vehicle = rear_vehicle
        self.rear_is_valid = True if rear_vehicle is not None else False
        self.front_s = None
        self.rear_s = None
        self.rear_v = None
        self.front_s = None
        self.is_ready = False
        self.window_v = None
        self.window_s = None

    @classmethod
    def GetVehicleFromIndex(cls, index, env):
        return env.road.vehicles[1 + index]

    def getWindowInfo(self, ego_car):
        # Get the window information.
        # Some attribute rely on ego_car, may a bad logic.
        # Currently, when the window has no both front and rear obs,
        # the s and velocity of window will be set to same with ego_car.
        if self.front_is_valid:
            self.front_s = self.front_vehicle[1] - self.car_length / 2
            self.front_v = self.front_vehicle[3]
        if self.rear_is_valid:
            self.rear_s = self.rear_vehicle[1] + self.car_length / 2
            self.rear_v = self.rear_vehicle[3] if self.rear_is_valid else None
        if not self.front_is_valid and not self.rear_is_valid:
            self.is_ready = True
        self.window_v = (self.front_v if self.front_is_valid else 0 +
                         self.rear_v if self.rear_is_valid else 0) / (
                             1 if self.front_is_valid else 0 +
                             1 if self.rear_is_valid else 0 + 1e-10)
        v_ego = ego_car[3]
        self.window_v = v_ego if not self.front_is_valid and not self.rear_is_valid else self.window_v
        a_min_vehicle = env_config['vehicle_min_a']
        t_react = env_config['T_react']
        if self.front_is_valid:
            v_front = self.front_v
            front_safe_dis = v_front**2 / abs(
                a_min_vehicle) * 0.5 + v_front * t_react
        if self.rear_is_valid:
            v_rear = self.rear_v
            rear_safe_dis = v_rear**2 / abs(
                a_min_vehicle) * 0.5 + v_rear * t_react
        if not self.front_is_valid:
            self.window_s = ego_car[
                1] if not self.rear_is_valid else self.rear_s + rear_safe_dis
            return
        elif not self.rear_is_valid:
            self.window_s = self.front_s - front_safe_dis
            return
        self.window_s = self.rear_s + rear_safe_dis + env_config['ego_car'][
            'length'] / 2 if self.front_s - self.rear_s > env_config[
                'ego_car']['length'] + front_safe_dis + rear_safe_dis else (
                    self.front_s + self.rear_s) / 2

    def update(self, ego_car):
        # When we debug window chasign controller, we may want the ego_car to chase one
        # unchangeable window. Here, we dont change front_obs and rear_obs and update window
        # information.
        self.getWindowInfo(ego_car)

    def __str__(self):
        res = ''
        if self.front_is_valid:
            res += 'front s: {}, front v: {}'.format(self.front_s,
                                                     self.front_v)
        else:
            res += 'No front window'
        if self.rear_is_valid:
            res += 'rear s:{}, rear v: {}'.format(self.rear_s, self.rear_v)
        else:
            res += 'No rear window'
        return res


def GetWindowByIndex(front_obs, rear_obs, index, env):
    front_size = len(front_obs)
    rear_size = len(rear_obs)
    if index < -rear_size or index > front_size:
        return None
    if index >= 0:
        window_front = None if index == front_size else front_obs[index]
        window_rear = None if rear_size == 0 else rear_obs[0]\
            if index == 0 else front_obs[index - 1]
    else:
        window_rear = None if index == -rear_size else rear_obs[-index]
        window_front = rear_obs[-index - 1]
    return LaneChangeWindow(window_front, window_rear)


def GetSafetyDis(v_front, v_rear, a_front, a_rear, t_react, is_front=False):
    if is_front:
        return max(
            0, v_rear**2 / a_rear * 0.5 + t_react * v_rear -
            v_front**2 / a_front * 0.5)
    return max(
        0, v_rear**2 / (2 * a_rear) -
        (v_front**2 / a_front * 0.5 + t_react * v_front))


def CheckReady(window, ego_car, ego_min_a, vehicle_min_a, react_T=0.0):
    ego_length = env_config['ego_car']['length']
    ego_s = ego_car[1]
    ego_v = ego_car[3]
    if window.front_is_valid:
        D_front = GetSafetyDis(window.front_v, ego_v, vehicle_min_a, ego_min_a,
                               react_T, False) + ego_length / 2
    if window.rear_is_valid:
        D_rear = GetSafetyDis(ego_v, window.rear_v, ego_min_a, vehicle_min_a,
                              react_T, True) + ego_length / 2
    front_ready = not window.front_is_valid or window.front_s - ego_s - ego_length / 2 > D_front
    rear_ready = not window.rear_is_valid or ego_s - ego_length / 2 - window.rear_s > D_rear
    return front_ready and rear_ready


class PID:
    # Copied from https://www.jb51.net/article/167234.htm
    def __init__(self,
                 P_value=0.1,
                 I_value=0.0,
                 D_value=0.0,
                 time_interval=0.1):
        self.Kp = P_value
        self.Ki = I_value
        self.Kd = D_value
        self.time_interval = time_interval
        self.clear()
        self.feedback_sum = 0
        self.inter_PID = None

    def clear(self):
        self.SetPoint = 0.0
        self.Pterm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.int_error = 0.0
        self.windup_guard = 20.0
        self.output = 0.0

    def update_ego(self, ego_v, target_s, target_v):
        self.current_v = ego_v
        self.SetPoint = target_s
        if self.inter_PID is not None:
            self.inter_PID.SetPoint = target_v

    def update(self, feedback_value):
        error = self.SetPoint - feedback_value
        delta_time = self.time_interval
        delta_error = error - self.last_error
        self.PTerm = self.Kp * error  # 比例
        self.ITerm += error * delta_time  # 积分
        if (self.ITerm < -self.windup_guard):
            self.ITerm = -self.windup_guard
        elif (self.ITerm > self.windup_guard):
            self.ITerm = self.windup_guard
        self.DTerm = 0.0
        if delta_time > 0:
            self.DTerm = delta_error / delta_time
        self.last_error = error
        self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd *
                                                             self.DTerm)
        if self.inter_PID is not None:
            self.inter_PID.SetPoint = self.inter_PID.SetPoint + self.output
            self.inter_PID.update(self.current_v)

    def setKp(self, proportional_gain):
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        self.Kd = derivative_gain

    def setWindup(self, windup):
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time
