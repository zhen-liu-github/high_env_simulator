from abc import ABC, abstractmethod
from config import env_config

class BaseSolver(ABC):
    def __init__(self, constrains):
        self.constrains = constrains
        # Ego info.
        self.ego_a_max = env_config['ego_max_a']
        self.ego_a_min = env_config['ego_min_a']
        # Control config.
        self.S_PID = PID(P=1, I=0.0, D=0.0)
        self.V_PID = PID(P=10, D=0.0)
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
        observations = observations[1:]
        self.GetFrontRearObs(observations)
        pre_observations = self.preprocess(observations)
        action = self._solve(pre_observations)
        return self.postprocess(action)

    @abstractmethod
    def _solve(self, observation):
        raise NotImplementedError()

    def GetFrontRearObs(self, observations):
        # Get front obstacles and rear obstacles.
        observations = np.array(observations)
        index = np.arange(0, observations.shape[0])
        observations = np.concatenate(
            [observations, index.reshape([-1, 1])], axis=-1)
        observations = [
            obs for obs in observations
            if obs[0] > 0 and obs[2] >= 2 and obs[2] <= 6
        ]
        self.front_obs = [
            obs for obs in observations if obs[1] > self.ego_car[1]
        ]
        self.rear_obs = [
            obs for obs in observations if obs[1] <= self.ego_car[1]
        ]
        self.rear_obs = sorted(self.rear_obs, key=lambda x: x[1], reverse=True)