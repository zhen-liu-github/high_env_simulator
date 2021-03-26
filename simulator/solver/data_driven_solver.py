from .base_solver import BaseSolver
from highway_env.envs.common.action import ContinuousAction
from .utils import LaneChangeWindow, GetWindowByIndex, PID, CheckReady
from ..config import env_config, model_config
import math
import numpy as np

class DataDrivenSolver(BaseSolver):
    def __init__(self, model_config, constrains):
        super(DataDrivenSolver, self).__init__(constrains)
        self.model_config = model_config


    def preprocess(self, observations):
        return observations
    def postprocess(self, observation):
        window_list, best_index = observation
        self.action['target_window'] =  window_list[best_index]
        self.action['is_ready'] = False
        if self.target_window.is_ready:
            self.action['is_ready'] = True
            return self.action
        self.GetControlOutput(self.ego_car[1], self.ego_car[3], self.action['target_window'].window_s, self.action['target_window'].window_v)
        return self.action


    def _solve(self, observations):
        # Get sample feature.
        feature_index = list(model_config['feature_index'].values())
        feature = observations[:, feature_index]
        feature = feature.reshape([-1, *feature.shape])
        # Load model.
        self.model = self._load_model()
        window_confidence = self.model(feature)
        best_window_index = np.argmax(window_confidence)
        self.window_list = []
        for i in range(len(window_confidence)):
            window = self.GetWindowByIndex(observations, i)
            self.window_list.append(window)
        return window_list, best_window_index
    def _load_model(self):
        self.model = torch.load(model_config['model_path'])