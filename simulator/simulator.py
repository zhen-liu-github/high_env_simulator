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

from simulator.config import env_config, model_config
from simulator.solver.time_optimal_solver import TimeOptimalSolver
from simulator.solver.graphic import SolverGraphic
from simulator.utils.utils import RemoveCurrentLaneOtherVehilces
from simulator.solver.utils import LaneChangeWindow
from simulator.utils.utils import AverageMetric


class simulator(object):
    def __init__(self,
                 env,
                 solver,
                 num_episodes,
                 display_env=True,
                 if_render = True,
                 save_data=False):
        self.env = env
        self.solver = solver
        self.num_episodes = num_episodes
        self.if_render = if_render
        self.display_env = display_env
        # Inner attributes
        self.episode = 0
        self.observation = None
        self.save_data = save_data
        self.monitor = MonitorV2(
            # env, None, video_callable=(None if self.display_env else False))
            env,
            None,
            video_callable=(False))
        if self.if_render:
            self.monitor.render()
            if self.display_env:
                self.drawWindow()
        self.lane_change_time = AverageMetric('lane_change_time')
        self.lane_change_success_rate = AverageMetric(
            'lane_change_success_rate')
        self.lane_change_time_index = 0

    def simulate(self):
        total_observations = []
        all_data = []
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
            epoch_data = []
            while not terminal:
                self.lane_change_time_index += 1
                if self.save_data:
                    epoch_data.append(np.array(self.observation))

                if self.results['is_ready']:
                    # Get exist near lane to trigger lane change
                    y = self.env.vehicle.position[1]
                    if y < 3.8:
                        action = 2
                    elif y > 4.2:
                        action = 0
                    else:
                        action = self.results['output']
                elif env_config['action']['type'] == 'ContinuousAction':
                    action = [self.results['a'], self.results['theta']]
                elif env_config['action']['type'] == 'DiscreteMetaAction':
                    action = self.results['output']
                
                self.v.append(self.monitor.env.controlled_vehicles[0].speed)
                self.s.append(self.monitor.env.controlled_vehicles[0].target_speed)
                self.observation, reward, terminal, info = self.monitor.step(
                    action)
                if self.if_render:
                    self.monitor.render()

                self.results = self.solver.solve(self.observation, self.env)
                observations.append(self.observation)
            plt.figure(figsize=(200, 400))
            fig, ax=plt.subplots(1, 1)
            ax.scatter(np.arange(len(self.v)), self.v, label='real_v')
            ax.scatter(np.arange(len(self.s)), self.s, label='target_v')
            plt.title('current')
            plt.legend()
            plt.savefig('./2.png')
            plt.close()

            # Statistic lane change info.
            # Currently, we only statistic no crashed case.
            if not info['crashed']:
                if self.observation[0][2] > 3:
                    self.lane_change_time.add(
                        self.lane_change_time_index /
                        env_config['vehicles_count'], 1)
                self.lane_change_success_rate.add(
                    1 if self.observation[0][2] > 3 else 0, 1)
            total_observations.append(observations)
            if self.save_data:
                sample = self.GetTrainWindowSelectionData(
                    epoch_data, self.episode)
                if sample:
                    all_data.append(np.concatenate(sample))
            print(self.lane_change_time)
            print(self.lane_change_success_rate)
        if self.save_data:
            save_data = np.concatenate(all_data, axis=0)
            np.save(model_config['data_save_path'] + 'sample_data', save_data)
        return total_observations

    def reset(self):
        obs_num = int(np.random.normal(loc=8, scale=2, size=1)[0])
        obs_num = max(1, obs_num)
        self.monitor.configure({"vehicles_count": obs_num})
        self.observation = self.monitor.reset()
        # Initialize window state and lane change time.
        self.solver.window_is_display = False
        self.lane_change_time_index = 0

    # Draw window information(confidences or chasing window time)
    def drawWindow(self):
        self.monitor.env.viewer.set_agent_display(
            SolverGraphic.wrapper(solver=self.solver))

    def GetTrainWindowSelectionData(self, episode_data, episode):
        tail_data = episode_data[-1]
        if tail_data[0][2] < 3:
            return None
        window_index = -1
        result = []
        for i, data in enumerate(episode_data):
            obs_data = data[1:]
            # Add ego car feature.
            obs_data = [
                np.concatenate([obs, data[0][1:]]) for obs in obs_data
                if obs[2] > 3 and obs[2] < 5
            ]
            # Filter lane change sample
            if data[0][2] < 3:
                result.append(obs_data)
        # Reverse frame data.
        result = result[::-1]
        for index, data in enumerate(result):
            if window_index < 0:
                # Initialize window_index, LaneChangeWindow
                window_index, current_window = self.GetGTWindow(data, None)
            else:
                window_index, current_window = self.GetGTWindow(
                    data, last_window)
            data = np.concatenate([data, np.ones([len(data), 2])], axis=1)
            # Add episode index and frame index.
            data[:, -2:] = [episode, len(result) - index]
            # Add GT window index.
            data = np.concatenate(
                [data, np.ones([data.shape[0], 1]) * window_index], axis=1)
            last_window = current_window
            result[index] = data
        # Reverse the frame data.
        result = result[::-1]
        return result

    def GetGTWindow(self, current_data, last_window):
        # Get current GT window from last GT window.
        ego_car = current_data[0][7:]
        if not last_window:
            current_window_s = ego_car[0]
        else:
            current_window_s = last_window.window_s - last_window.window_v / env_config[
                'simulation_frequency']
        window_index = -1
        for i, obs_data in enumerate(current_data):
            s = obs_data[1]
            if s > current_window_s:
                window_index = i
                break
        window_index = len(
            current_data[1:]) if window_index == -1 else window_index
        GT_window = LaneChangeWindow(None if window_index==len(current_data) else \
            current_data[window_index], None if window_index==0 else current_data[window_index-1])
        ego_car = np.concatenate([[1], ego_car])
        GT_window.getWindowInfo(ego_car)
        return window_index, GT_window


if __name__ == '__main__':
    env = load_environment(env_config)
    # Unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()
    solver = TimeOptimalSolver(None)
    simulator = simulator(env, solver, 200, True)
    simulator.simulate()
