import numpy as np
import matplotlib.pyplot as plt
from rl_agents.agents.common.factory import load_environment
from rl_agents.trainer.monitor import MonitorV2

from simulator.config import env_config, model_config
from simulator.solver.time_optimal_solver import TimeOptimalSolver
from simulator.solver.graphic import SolverGraphic
from simulator.solver.utils import LaneChangeWindow
from simulator.utils.utils import AverageMetric
from simulator.utils.utils import MetricDict


class simulator(object):
    def __init__(self,
                 env,
                 solver,
                 num_episodes,
                 seed=None,
                 begin_episode=0,
                 display_env=True,
                 if_render=True,
                 draw_v_fig=False,
                 save_data=False):
        self.env = env
        self.solver = solver
        self.num_episodes = num_episodes
        self.sim_seed = seed
        self.begin_episode = begin_episode
        self.display_env = display_env
        self.if_render = if_render
        self.draw_v_fig = draw_v_fig
        self.save_data = save_data
        # Inner attributes
        self.episode = 0
        self.observation = None
        self.monitor = MonitorV2(
            # env, None, video_callable=(None if self.display_env else False))
            env,
            None,
            video_callable=(False))
        if self.if_render:
            self.monitor.render()
            if self.display_env:
                self.drawWindow()
        self.lane_change_time = MetricDict()
        self.lane_change_success_rate = MetricDict()
        self.lane_change_time_index = 0

    def simulate(self):
        total_observations = []
        all_data = []
        for self.episode in range(self.begin_episode, self.num_episodes):
            terminal = False
            self.seed(self.episode)
            self.reset()
            observations = []
            self.results = {}
            self.results['theta'] = 0
            # Initialize action outputs.
            if env_config['action']['type'] == 'ContinuousAction':
                self.results['a'] = 0
                self.results['v'] = 0
                self.results['s'] = 0
            elif env_config['action']['type'] == 'DiscreteMetaAction':
                self.results['output'] = 0
            self.results['is_ready'] = False
            # for speed figure vis.
            self.v = []
            self.s = []
            epoch_data = []
            while not terminal:
                # Lane change time indexing.
                self.lane_change_time_index += 1

                if self.save_data:
                    epoch_data.append(np.array(self.observation))

                if self.results['is_ready']:
                    # If the window is ready, do lat motion.
                    y = self.env.vehicle.position[1]
                    if y < 3.8:
                        action = 2
                    elif y > 4.2:
                        action = 0
                    else:
                        action = self.results['output']
                elif env_config['action']['type'] == 'ContinuousAction':
                    action = [self.results['a'], self.results['theta']] # a, theta
                elif env_config['action']['type'] == 'DiscreteMetaAction':
                    action = self.results['output'] # Discrete high-level motion.
                
                self.observation, _, terminal, info = self.monitor.step(
                        action)
                self.results = self.solver.solve(self.observation, self.env)
                observations.append(self.observation)

                if self.draw_v_fig:
                    # Draw and save  
                    self.v.append(self.monitor.env.controlled_vehicles[0].speed)
                    self.s.append(
                        self.monitor.env.controlled_vehicles[0].target_speed)
                    
                if self.if_render:
                    self.monitor.render()

            if self.draw_v_fig:   
                plt.figure(figsize=(200, 400))
                _, ax = plt.subplots(1, 1)
                ax.scatter(np.arange(len(self.v)), self.v, label='real_v')
                ax.scatter(np.arange(len(self.s)), self.s, label='target_v')
                plt.title(model_config['type'])
                plt.legend()
                plt.savefig('./2.png')
                plt.close()

            if not info['crashed']:
                # Statistic lane change info.
                # Currently, we only statistic no crashed case.
                if model_config['type'] == 'rule-based':
                    obs_num = len(self.solver.front_obs + self.solver.rear_obs)
                elif model_config['type'] == 'data-driven':
                    obs_num = len(self.solver.window_list) - 1
                if self.observation[0][2] > 3:
                    if obs_num not in self.lane_change_time.keys():
                        self.lane_change_time[obs_num] = AverageMetric(
                            'Obs_num:{} lane change time'.format(obs_num))
                    self.lane_change_time[obs_num].add(
                        self.lane_change_time_index /
                        env_config['vehicles_count'], 1)
                if obs_num not in self.lane_change_success_rate.keys():
                    self.lane_change_success_rate[obs_num] = AverageMetric(
                        'Obs_num{}: lane change success rate'.formta(obs_num))
                self.lane_change_success_rate[obs_num].add(
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

    def seed(self, seed_value):
        seed = (self.sim_seed if self.sim_seed else 0) + seed_value 
        self.monitor.seed(seed)
        np.random.seed(seed)



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
        last_window = None
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
        # This method aims to find last frame GT window from current frame GT window.
        # Cause we only have the GT window after ego car did the lane change.
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
        GT_window = LaneChangeWindow(None if window_index == len(current_data) else \
            current_data[window_index], None if window_index == 0 else current_data[window_index-1])
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
