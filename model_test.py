import numpy as np
import matplotlib.pyplot as plt
import argparse

from gym.envs.classic_control import rendering
import gym
from rl_agents.agents.common.factory import load_agent, load_environment
from rl_agents.trainer.monitor import MonitorV2
from gym.envs.classic_control import rendering
from highway_env.vehicle.behavior import IDMVehicle
from highway_env.vehicle.controller import ControlledVehicle
from highway_env.vehicle.kinematics import Vehicle
from highway_env.vehicle.behavior import IDMVehicle

from simulator.solver.time_optimal_solver import TimeOptimalSolver
from simulator.solver.data_driven_solver import DataDrivenSolver
from simulator.config import env_config, model_config
from simulator.simulator import simulator
from simulator.solver import solver_config


parser = argparse.ArgumentParser()
parser.add_argument('--type', default='data-driven')
args = parser.parse_args()
if __name__ == '__main__':
    env = load_environment(env_config)
    # unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()
    # method = 'data-driven'
    model_config.update({'type': args.type})
    solver = solver_config[args.type](model_config, None)

    simulator = simulator(env, solver,  200, True, save_data=True)
    simulator.simulate()