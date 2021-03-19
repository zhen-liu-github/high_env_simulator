
import datetime 
import os 

import gym
from rl_agents.agents.common.factory import load_agent, load_environment
from rl_agents.trainer.monitor import MonitorV2
from gym.envs.classic_control import rendering
from highway_env.vehicle.behavior import IDMVehicle
from highway_env.vehicle.controller import ControlledVehicle
from highway_env.vehicle.kinematics import Vehicle


from config import env_config
from solver.time_optimal_solver import TimeOptimalSolver
from utils.utils import RemoveCurrentLaneOtherVehilces 


class simulator(object):
    

    def __init__(self, env, solver, num_episodes, display_env=True):
        self.env = env
        self.solver = solver
        self.num_episodes = num_episodes
        self.episode = 0
        self.observation = None
        self.display_env = display_env
        self.monitor = MonitorV2(env,
                                 None,
                                 video_callable=(None if self.display_env else False))
          
    def simulate(self):
        total_observations = []
        for self.episode in range(self.num_episodes):
            observation = []
            terminal = False
            # self.seed(self.episodes)
            self.reset()
            self.monitor.render()
            while not terminal:
                # Get exist near lane to trigger lane change
                action = self.solver.solve(observation, self.env)
                self.observation, reward, terminal, info = self.monitor.step(action)
                observation.append(self.observation)
                self.monitor.render()
            total_observations.append(observation)
        return total_observations    
    
    def reset(self):        
        self.observation = self.monitor.reset()

    # Draw window information(confidences or chasing window time)
    def drawWindow(self, windows):
        front, rear = windows[0].front, windows[-1].rear
        top, down = 200, 500
        line1 = rendering.Line((top, front), (top, rear))

        for window in windows:
            self.env.viewing.add_geom(self.getDraw(window))

    def getDraw(window):
        pass

if __name__ == '__main__':
    env = load_environment(env_config)
    # unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()

    solver = TimeOptimalSolver(None)

    simulator = simulator(env, solver, 200, True)
    simulator.simulate()

    
