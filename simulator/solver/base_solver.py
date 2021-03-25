from abc import ABC, abstractmethod
from config import env_config

class BaseSolver(ABC):
    def __init__(self, constrains):
        self.constrains = constrains
        self.action = {}
        self.action['a'] = 0
        self.action['theta'] = 0
        if env_config['action']['type'] == 'ContinuousAction':
            self.action['a'] = 0
            self.action['v'] = 0
            self.action['s'] = 0
        elif env_config['action']['type'] == 'DiscreteMetaAction':
            self.action['output'] = 0
        self.ego_car = None
        self.env = None
        self.time_stamp = 0
    @abstractmethod
    def preprocess(self, observation):
        # For preprocess to observation.
        raise NotImplementedError()

    @abstractmethod
    def postprocess(self, observation):
        # For postprocess to action.
        raise NotImplementedError()

    def solve(self, observations, env):
        # if len(observations) == 0:
        #     action = {}
        self.time_stamp += 1
        self.env = env
        self.action['is_ready'] = False
        #     return action
        self.ego_car = observations[0]
        observations = observations[1:]
        pre_observations = self.preprocess(observations)
        action = self._solve(pre_observations)
        return self.postprocess(action)

    @abstractmethod
    def _solve(self, observation):
        raise NotImplementedError()