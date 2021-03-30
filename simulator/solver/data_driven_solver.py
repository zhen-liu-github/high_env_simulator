from .base_solver import BaseSolver
from ..config import env_config, model_config
import numpy as np
import torch
from .utils import LaneChangeWindow, CheckReady


class DataDrivenSolver(BaseSolver):
    def __init__(self, model_config, constrains):
        super(DataDrivenSolver, self).__init__(model_config, constrains)

        self._load_model()

    def preprocess(self, obs_observations):
        return obs_observations

    def postprocess(self, observation):
        _, best_index = observation
        self.target_window = self.window_list[best_index]
        self.action['is_ready'] = False
        if CheckReady(self.target_window, self.ego_car,
                      env_config['ego_min_a'], env_config['vehicle_min_a']):
            self.target_window.is_ready = True
            self.action['is_ready'] = True
        self.GetControlOutput(self.ego_car[1], self.ego_car[3],
                              self.target_window.window_s,
                              self.target_window.window_v)
        return self.action

    def _solve(self, obs_observations):
        # Get sample feature.
        # Need to improve the selected feature representation.
        obs_list = obs_observations[:, 1:]
        obs_list = [obs for obs in obs_list if obs[0] > 0 and obs[1] > 3]
        feature = np.array(obs_list)
        samples = np.zeros([feature.shape[0], feature.shape[1] * 2])
        samples[:, :feature.shape[1]] = feature
        samples[:, feature.shape[1]:] = self.ego_car[1:]
        samples = torch.from_numpy(samples).float()
        samples = samples.reshape([1, 1, *samples.shape])
        # Load model.
        window_confidence = self.model(samples)
        window_confidence = torch.softmax(window_confidence, -1)
        self.window_confidence = window_confidence.data.numpy()[0]
        self.best_window_index = np.argmax(self.window_confidence)
        self.window_list = []
        target_obs_list = [
            obs for obs in obs_observations if obs[0] > 0 and obs[2] > 3
        ]
        for i in range(len(self.window_confidence)):
            window = self.GetWindowByIndex(target_obs_list, i)
            window.getWindowInfo(self.ego_car)
            self.window_list.append(window)
        return self.window_list, self.best_window_index

    def _load_model(self):
        self.model = torch.load(model_config['model_path'])

    def GetWindowByIndex(self, obs_observation, index):
        window = LaneChangeWindow(
            None if index == len(obs_observation) else obs_observation[index],
            None if index == 0 else obs_observation[index - 1])
        return window
