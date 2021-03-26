from solver.base_solver import BaseSolver
from highway_env.envs.common.action import ContinuousAction
from .utils import LaneChangeWindow, GetWindowByIndex, PID, CheckReady
from config import env_config
import math
import numpy as np

class MLPDataDrivenSolver(BaseSolver):
    def __init__(self, model_config, constrains):
        super(MLPDataDrivenSolver, self).__init__(constrains)
        self.model_config = model_config


    def preprocess(self, observations):


    def postprecess(self, observation):

    def _solve(self, observations):
    
