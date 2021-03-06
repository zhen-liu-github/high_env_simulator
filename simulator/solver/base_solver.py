from abc import ABC, abstractmethod
from simulator.config import env_config
from .utils import PID


class BaseSolver(ABC):
    def __init__(self, model_config, constrains):
        self.model_config = model_config
        self.constrains = constrains
        # Control window display consistancy.
        self.window_is_display = False
        # Ego info.
        self.ego_a_max = env_config['ego_max_a']
        self.ego_a_min = env_config['ego_min_a']
        # Control config.
        self.S_PID = PID(P_value=1, I_value=0.0, D_value=0.00)
        self.V_PID = PID(P_value=20, I_value=0.0, D_value=0.0)
        self.S_PID.inter_PID = self.V_PID
        # result initialization.
        self.action = {}
        self.action['a'] = 0
        self.action['theta'] = 0
        if env_config['action']['type'] == 'ContinuousAction':
            self.action['a'] = 0
            self.action['v'] = 0
            self.action['s'] = 0
        elif env_config['action']['type'] == 'DiscreteMetaAction':
            self.action['output'] = 0
        # Ego_car info.
        self.ego_car = None
        # Env
        self.env = None
        # Solve epoch num.
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
        obs_observations = observations[1:]
        obs_observations = self.preprocess(obs_observations)
        action = self._solve(obs_observations)
        self.window_is_display = True
        return self.postprocess(action)

    @abstractmethod
    def _solve(self, observation):
        raise NotImplementedError()

    def GetControlOutput(self, ego_s, ego_v, window_s, window_v):
        self.S_PID.update_ego(ego_v, window_s, window_v)
        # self.S_PID.update_ego(self.ego_car[3], 300+1.5*self.time_stamp,
        #                       15)
        self.S_PID.update(ego_s)
        output = self.V_PID.output
        a = max(output, self.ego_a_min)
        a = min(a, self.ego_a_max)
        self.action['a'] = a
        if env_config['action']['type'] == 'ContinuousAction':
            self.action['v'] = self.ego_car[3]
            self.action['s'] = self.ego_car[1]
        elif env_config['action']['type'] == 'DiscreteMetaAction':
            if a == 0:
                self.action['output'] = 1
            elif a < 0:
                self.action['output'] = 4
            else:
                self.action['output'] = 3
