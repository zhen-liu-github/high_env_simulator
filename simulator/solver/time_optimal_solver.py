from solver.base_solver import BaseSolver
from highway_env.envs.common.action import ContinuousAction
from utils import LaneChangeWindow


class TimeOptimalSolver(BaseSolver):
    def __init__(self, constrains):
        super(TimeOptimalSolver, self).__init__(constrains)

    def preprocess(self, observation):
        # Get front near obs and target route obs.
        # If have left lane, left lane change, otherwise right lane change.
        '''
        paras:
            observation: [verhicle_num, feature_dim]. The first verhicle is ego car.
        '''
        self.front_obs = [
            obs for obs in observation if obs[1] > observation[0][1]
        ]
        self.rear_obs = [
            obs for obs in observation if obs[1] <= observation[0][1]
        ]
        sorted(self.rear_obs, cmp=lambda x, y: cmp(x[1], y[1]))
        # Only consider 5 near lane change window
        window_list = []
        for i in range(-2, 3):
            window = self.GetWindowByIndex(self.front_obs, self.rear_obs, i)
            if window:
                window_list.append(window)
        return window_list

    def postprocess(self, target_window):
        return action

    def _solve(self, window_list):
        for window in window_list:
            pass
        return [0., 0]

    def GetWindowByIndex(self, front_obs, rear_obs, index):
        front_size = len(front_obs)
        rear_size = len(rear_obs)
