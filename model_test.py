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
from highway_env.vehicle.behavior import IDMVehicle

from simulator.solver.time_optimal_solver import TimeOptimalSolver
from simulator.solver.data_driven_solver import DataDrivenSolver
from simulator.config import env_config, model_config
from simulator.simulator import simulator
from simulator.solver import solver_config

 
if __name__ == '__main__':
    env = load_environment(env_config)
    # unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()
    # method = 'data-driven'
    method = model_config['type']
    solver = solver_config[method](model_config, None)

    simulator = simulator(env, solver, 200, True)
    simulator.simulate()