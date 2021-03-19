from abc import ABC, abstractmethod

class BaseSolver(ABC):

    def __init__(self, constrains):
        self.constrains = constrains


    @abstractmethod
    def preprocess(self, observation):
        # For preprocess to observation.
        raise NotImplementedError()

    @abstractmethod
    def postprocess(self, observation):
        # For postprocess to action.
        raise NotImplementedError()
    
    def solve(self, observations, env):
        pre_observations = self.preprocess(observations)
        action = self._solve(pre_observations)
        return self.postprocess(action)
    
    @abstractmethod
    def _solve(self, observation):
        raise NotImplementedError()