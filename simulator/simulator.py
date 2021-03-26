import datetime
import os
import functools

import numpy as np
import matplotlib.pyplot as plt
from gym.envs.classic_control import rendering
import gym
from rl_agents.agents.common.factory import load_agent, load_environment
from rl_agents.trainer.monitor import MonitorV2
from gym.envs.classic_control import rendering
from highway_env.vehicle.behavior import IDMVehicle
from highway_env.vehicle.controller import ControlledVehicle
from highway_env.vehicle.kinematics import Vehicle

from config import env_config
from solver.time_optimal_solver import TimeOptimalSolver
from solver.graphic import SolverGraphic
from utils.utils import RemoveCurrentLaneOtherVehilces


class simulator(object):
    def __init__(self, env, solver, num_episodes, display_env=True):
        self.env = env
        self.solver = solver
        self.num_episodes = num_episodes
        self.display_env = display_env
        # Inner attributes
        self.episode = 0
        self.observation = None
        self.monitor = MonitorV2(
            # env, None, video_callable=(None if self.display_env else False))
            env,
            None,
            video_callable=(False))

    def simulate(self):
        total_observations = []
        self.monitor.render()
        for self.episode in range(self.num_episodes):
            terminal = False
            # self.seed(self.episodes)
            self.reset()
            observations = []
            self.results = {}
            self.results['theta'] = 0
            if env_config['action']['type'] == 'ContinuousAction':
                self.results['a'] = 0
                self.results['v'] = 0
                self.results['s'] = 0
            elif env_config['action']['type'] == 'DiscreteMetaAction':
                self.results['output'] = 0
            self.results['is_ready'] = False
            # for vis
            self.v = []
            self.s = []
            while not terminal:
                if self.observation is None or len(self.observation) == 0:
                    # Update observation.
                    self.observation, reward, terminal, info = self.monitor.step(
                        [0, 0])
                    continue
                if self.results['is_ready']:
                    # Get exist near lane to trigger lane change
                    y = self.env.vehicle.position[1]
                    if y < 3.8:
                        action = 2
                    elif y > 4.2:
                        action = 0
                elif env_config['action']['type'] == 'ContinuousAction':
                    action = [self.results['a'], self.results['theta']]
                    self.v.append(self.results['v'])
                    self.s.append(self.results['s'])
                elif env_config['action']['type'] == 'DiscreteMetaAction':
                    action = self.results['output']
                self.observation, reward, terminal, info = self.monitor.step(
                    action)
                
                self.results = self.solver.solve(self.observation, self.env)
                observations.append(self.observation)
                if self.display_env:
                    self.drawWindow()
                self.monitor.render()
            plt.figure(figsize=(200, 400))
            fig, axes = plt.subplots(1, 2)
            axes[0].scatter(np.arange(len(self.v)), self.v)
            axes[1].scatter(np.arange(len(self.s)), self.s)
            plt.savefig('./1.png')
            total_observations.append(observations)
        return total_observations

    def reset(self):
        self.observation = self.monitor.reset()

    # Draw window information(confidences or chasing window time)
    def drawWindow(self):
        self.env.viewer.set_agent_display(
            SolverGraphic.wrapper(solver=self.solver))


if __name__ == '__main__':
    env = load_environment(env_config)
    # unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()

    solver = TimeOptimalSolver(None)

    simulator = simulator(env, solver, 200, True)
    simulator.simulate()
