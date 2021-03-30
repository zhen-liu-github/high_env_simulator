from simulator.solver.base_solver import BaseSolver
from highway_env.envs.common.action import ContinuousAction
from .utils import LaneChangeWindow, GetWindowByIndex, PID, CheckReady
from ..config import env_config
import math
import numpy as np


class TimeOptimalSolver(BaseSolver):
    def __init__(self, method_config, constrains):
        super(TimeOptimalSolver, self).__init__(method_config, constrains)
        self.target_window, self.best_time = None, None
        self.if_window_unchangeable = False

    def preprocess(self, observation):
        # Get front near obs and target route obs.
        # If have left lane, left lane change, otherwise right lane change.
        '''
        paras:
            observation: [verhicle_num, feature_dim]. The first verhicle is ego car.
        '''
        observation = np.array(observation)
        index = np.arange(0, observation.shape[0])
        observation = np.concatenate(
            [observation, index.reshape([-1, 1])], axis=-1)
        observation = [
            obs for obs in observation
            if obs[0] > 0 and obs[2] >= 2 and obs[2] <= 6
        ]
        self.front_obs = [
            obs for obs in observation if obs[1] > self.ego_car[1]
        ]
        self.rear_obs = [
            obs for obs in observation if obs[1] <= self.ego_car[1]
        ]
        self.rear_obs = sorted(self.rear_obs, key=lambda x: x[1], reverse=True)
        # Only consider 5 near lane change window
        window_list = []
        num_window = 5
        for i in range(int(-num_window / 2),
                       int(num_window - int(num_window / 2))):
            window = GetWindowByIndex(self.front_obs, self.rear_obs, i,
                                      self.env)
            if window:
                window.getWindowInfo(self.ego_car)
                window_list.append(window)
        return window_list

    def postprocess(self, data):
        [self.target_window, self.best_time] = data
        self.action['target_window'] = self.target_window
        self.action['time'] = self.best_time
        self.action['is_ready'] = False
        if self.target_window.is_ready:
            self.action['is_ready'] = True
            # return self.action
        self.GetControlOutput(self.ego_car[1], self.ego_car[3],
                              self.action['target_window'].window_s,
                              self.action['target_window'].window_v)
        return self.action

    def _solve(self, window_list):
        best_time = float('inf')
        best_window = None
        min_error = float('inf')
        have_same_window = False
        if self.if_window_unchangeable and self.target_window is not None:
            # This logic is for PID controler gain choice and can chase a unchangeable window.
            min_error = float('inf')
            interval = int(env_config['simulation_frequency'] /
                           env_config['policy_frequency'])
            for window in window_list:
                if (window.front_vehicle is None)!= (self.target_window.front_vehicle is None) or \
                    (window.rear_vehicle is None)!=(self.target_window.rear_vehicle is None):
                    continue

                if ((window.front_vehicle is not None
                     or interval < len(window.front_vehicle.history)
                     and self.IsTheSameWindowWithLast(
                         window.front_vehicle.history[interval],
                         self.target_window.front_vehicle) and
                     (window.rear_vehicle is not None
                      or interval < len(window.rear_vehicle.history)
                      and self.IsTheSameWindowWithLast(
                          window.rear_vehicle.history[interval],
                          self.target_window.rear_vehicle)))):
                    have_same_window = True
                    best_window = window
                    best_time = -1
        if not have_same_window:
            for window in window_list:
                if CheckReady(window, self.ego_car, env_config['ego_min_a'],
                              env_config['vehicle_min_a']):
                    # If window is ready, break.
                    window.is_ready = True
                    best_window = window
                    best_time = 0
                    break
                time = self._getOptimalTime(window.window_v - self.ego_car[3],
                                            window.window_s - self.ego_car[1])
                if best_time > time:
                    best_window = window
                    best_time = time
        best_time = -1 if best_time == float('inf') else best_time
        return best_window, best_time

    def IsTheSameWindowWithLast(self, obs1, obs2):
        front_error = 0 if obs1 is None else abs(obs1.position[0] -
                                                 obs2.position[0])
        rear_error = 0 if obs1 is None else abs(obs1.position[1] -
                                                obs2.position[1])
        return front_error + rear_error < 1e-5

    def _getOptimalTime(self, relative_v, relative_s) -> float:
        x1 = relative_s
        x2 = relative_v
        # Split the boundary.
        if x2 < 0 and x1 < x2**2 / self.ego_a_max * 0.5 or x2 >= 0 and x1 < -x2**2 / (
                2 * self.ego_a_min):
            flag = False
        else:
            flag = True
        a_first = self.ego_a_min if flag else self.ego_a_max
        a_second = self.ego_a_max if flag else self.ego_a_min
        a = (a_second - a_first) / 2 + a_second * (a_second - a_first) * (
            a_second - a_first - 2) / 2
        b = relative_v * (-1 + a_second / 2 * (-2 * (a_second - a_first - 1)))
        c = a_second * relative_v**2 / 2 - relative_s
        delta = b**2 - 4 * a * c
        assert (delta >= 0,
                'error: bangbang control get a non-compute solution.')
        ts = (-b + delta**0.5) / 2 / a
        tf = (a_second - a_first) * ts - relative_v
        assert (tf >= 0, 'error: get a negative solution.')
        return tf
